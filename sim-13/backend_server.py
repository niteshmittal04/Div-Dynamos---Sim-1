# backend_server.py
import asyncio
import websockets
import json
import random
import math
import time
from collections import deque
import heapq
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

# Canvas size used by your HTML simulator
CANVAS_W = 650
CANVAS_H = 600

# Discretize into a grid for A*
GRID_RES = 10  # pixels per cell (makes grid 65x60)
GRID_W = CANVAS_W // GRID_RES
GRID_H = CANVAS_H // GRID_RES

# Robot params
ROBOT_RADIUS = 18
ROBOT_SPEED = 90.0  # pixels per second - tune
SIM_FPS = 20.0
DT = 1.0 / SIM_FPS

# Obstacle params
NUM_OBSTACLES = 8
OBSTACLE_MIN_SIZE = 18
OBSTACLE_MAX_SIZE = 30
OBSTACLE_MAX_SPEED = 30.0  # pixels / second (slow)

# Server state
clients = set()
simulation_task = None

# Simulation entities
robot = {"x": 320.0, "y": 300.0, "vx": 0.0, "vy": 0.0}
goal = {"x": 550.0, "y": 80.0}
obstacles = []

is_running = False
collision_count = 0

# Path following
current_path = []  # list of (x,y) nodes in pixels
path_idx = 0
planning = False

# Utilities
def clamp(v, a, b):
    return max(a, min(b, v))

def dist(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def to_grid(p):
    gx = int(p[0] // GRID_RES)
    gy = int(p[1] // GRID_RES)
    gx = clamp(gx, 0, GRID_W-1)
    gy = clamp(gy, 0, GRID_H-1)
    return (gx, gy)

def to_pixel(g):
    return (g[0]*GRID_RES + GRID_RES//2, g[1]*GRID_RES + GRID_RES//2)

# A* on grid
def astar(start_px, goal_px, obs_list):
    start = to_grid(start_px)
    goal_g = to_grid(goal_px)

    # Build obstacle occupancy set
    occ = set()
    for o in obs_list:
        ox, oy = to_grid((o['x'], o['y']))
        # mark a small neighborhood based on obstacle size
        rad_cells = max(1, int((o['size'] // 2) / GRID_RES) + 1)
        for dx in range(-rad_cells, rad_cells+1):
            for dy in range(-rad_cells, rad_cells+1):
                nx, ny = ox+dx, oy+dy
                if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                    occ.add((nx, ny))

    # A*
    open_heap = []
    heapq.heappush(open_heap, (0 + heuristic(start, goal_g), 0, start, None))
    came_from = {}
    gscore = {start: 0}
    visited = set()

    while open_heap:
        f, g, current, parent = heapq.heappop(open_heap)
        if current in visited:
            continue
        visited.add(current)
        came_from[current] = parent

        if current == goal_g:
            # reconstruct path
            path = []
            node = current
            while node:
                path.append(to_pixel(node))
                node = came_from.get(node)
            path.reverse()
            return path

        cx, cy = current
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
            nx, ny = cx+dx, cy+dy
            if not (0 <= nx < GRID_W and 0 <= ny < GRID_H):
                continue
            neigh = (nx, ny)
            if neigh in occ:
                continue
            tentative_g = g + math.hypot(dx,dy)
            if tentative_g < gscore.get(neigh, float('inf')):
                gscore[neigh] = tentative_g
                heapq.heappush(open_heap, (tentative_g + heuristic(neigh, goal_g), tentative_g, neigh, current))
    return None

def heuristic(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

# Candidate generation: produce slight deviations of goal to avoid local obstacles
def generate_candidate_goals(goal_px, k=6, radius=40):
    # include straight goal
    candidates = [goal_px]
    for i in range(1, k):
        angle = (i / k) * math.pi * 2
        ox = goal_px[0] + math.cos(angle) * radius * (0.5 + random.random()*0.8)
        oy = goal_px[1] + math.sin(angle) * radius * (0.5 + random.random()*0.8)
        ox = clamp(ox, 0, CANVAS_W)
        oy = clamp(oy, 0, CANVAS_H)
        candidates.append((ox, oy))
    return candidates

def score_path(path, obs_list):
    if not path: return float('inf')
    # collisions count along path
    collisions = 0
    for px, py in path:
        for o in obs_list:
            if math.hypot(px - o['x'], py - o['y']) < (ROBOT_RADIUS + o['size']/2) - 2:
                collisions += 1
    length = sum(math.hypot(path[i+1][0]-path[i][0], path[i+1][1]-path[i][1]) for i in range(len(path)-1)) if len(path)>1 else 0
    # penalize collisions heavily
    return length + collisions * 1000

# Initialize obstacles
def reset_scene():
    global robot, goal, obstacles, current_path, path_idx, collision_count
    robot = {"x": 320.0, "y": 300.0, "vx": 0.0, "vy": 0.0}
    goal = {"x": 550.0, "y": 80.0}
    obstacles = []
    collision_count = 0
    current_path = []
    path_idx = 0
    for _ in range(NUM_OBSTACLES):
        ox = random.uniform(50, CANVAS_W-50)
        oy = random.uniform(50, CANVAS_H-50)
        size = random.uniform(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(0, OBSTACLE_MAX_SPEED * 0.7)  # relatively slow
        obstacles.append({"x": ox, "y": oy, "size": size, "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed})
    logger.info("Scene reset: robot at (%.1f,%.1f) goal at (%.1f,%.1f)", robot["x"], robot["y"], goal["x"], goal["y"])

async def broadcast(msg: dict):
    if clients:
        dead = []
        payload = json.dumps(msg)
        for ws in clients:
            try:
                await ws.send(payload)
            except Exception:
                dead.append(ws)
        for d in dead:
            clients.discard(d)

async def handle_client(ws, path):
    logger.info("Client connected")
    clients.add(ws)
    try:
        async for message in ws:
            try:
                data = json.loads(message)
            except:
                continue
            # handle incoming commands
            mtype = data.get("type")
            if mtype == "start":
                global is_running
                is_running = True
                logger.info("Received start command")
            elif mtype == "stop":
                is_running = False
                logger.info("Received stop command")
            elif mtype == "reset":
                reset_scene()
                await broadcast({"type": "reset_ack"})
            elif mtype == "set_goal":
                gx = data.get("x"); gy = data.get("y")
                if gx is not None and gy is not None:
                    goal['x'] = clamp(float(gx), 0, CANVAS_W)
                    goal['y'] = clamp(float(gy), 0, CANVAS_H)
                    logger.info("Goal updated to %.1f, %.1f", goal['x'], goal['y'])
            # ignore other messages
    except websockets.ConnectionClosed:
        logger.info("Client disconnected")
    finally:
        clients.discard(ws)

# Helper: will the robot collide if it moves to (nx,ny)?
def will_collide_at(nx, ny):
    for o in obstacles:
        if math.hypot(nx - o['x'], ny - o['y']) < (ROBOT_RADIUS + o['size']/2) - 2:
            return True
    return False

async def simulation_loop():
    global robot, obstacles, current_path, path_idx, planning, collision_count, is_running

    last_time = time.time()
    replan_interval = 0.4  # seconds (replan often enough)
    last_plan_time = 0.0

    while True:
        now = time.time()
        elapsed = now - last_time
        if elapsed < DT:
            await asyncio.sleep(DT - elapsed)
            continue
        last_time = now

        # update obstacles (slow random motion)
        for o in obstacles:
            o['x'] += o['vx'] * DT
            o['y'] += o['vy'] * DT
            # bounce at walls
            if o['x'] < 10 or o['x'] > CANVAS_W - 10:
                o['vx'] *= -1
                o['x'] = clamp(o['x'], 10, CANVAS_W-10)
            if o['y'] < 10 or o['y'] > CANVAS_H - 10:
                o['vy'] *= -1
                o['y'] = clamp(o['y'], 10, CANVAS_H-10)

        if is_running:
            # Replan periodically or if path is exhausted
            if (not current_path) or (path_idx >= len(current_path)) or (now - last_plan_time > replan_interval):
                # Try multiple candidate goals, pick best path by score
                candidate_goals = generate_candidate_goals((goal['x'], goal['y']), k=7, radius=60)
                best = None
                best_score = float('inf')
                for cg in candidate_goals:
                    path = astar((robot['x'], robot['y']), cg, obstacles)
                    if path:
                        sc = score_path(path, obstacles)
                        if sc < best_score:
                            best_score = sc
                            best = path
                if best:
                    current_path = best
                    path_idx = 0
                last_plan_time = now

            # Follow current path node-by-node
            if current_path and path_idx < len(current_path):
                node = current_path[path_idx]
                dx = node[0] - robot['x']
                dy = node[1] - robot['y']
                dist_to_node = math.hypot(dx, dy)
                if dist_to_node < 6.0:  # reached node
                    path_idx += 1
                else:
                    # move towards node but check immediate collision
                    max_step = ROBOT_SPEED * DT
                    step = min(max_step, dist_to_node)
                    nx = robot['x'] + (dx / dist_to_node) * step
                    ny = robot['y'] + (dy / dist_to_node) * step

                    # If immediate move collides, attempt small sidestep then request replan next tick
                    if will_collide_at(nx, ny):
                        # perpendicular sidestep
                        perp_dx = -dy
                        perp_dy = dx
                        plen = math.hypot(perp_dx, perp_dy)
                        if plen == 0:
                            # try small random step
                            nx = robot['x'] + (random.random() - 0.5) * 10
                            ny = robot['y'] + (random.random() - 0.5) * 10
                        else:
                            nx = robot['x'] + (perp_dx / plen) * 12
                            ny = robot['y'] + (perp_dy / plen) * 12
                        # don't advance path_idx; next loop will replan
                    # commit move
                    robot['x'] = clamp(nx, 0, CANVAS_W)
                    robot['y'] = clamp(ny, 0, CANVAS_H)

            # collision detection (if robot intersects obstacle)
            for o in obstacles:
                if math.hypot(robot['x'] - o['x'], robot['y'] - o['y']) < (ROBOT_RADIUS + o['size']/2) - 2:
                    collision_count += 1
                    # broadcast collision event
                    await broadcast({"type": "collision", "robot_position": {"x": robot['x'], "y": robot['y']},
                                     "obstacle_position": {"x": o['x'], "y": o['y']}})
                    # respond by sidestepping a bit
                    robot['x'] += (robot['x'] - o['x']) * 0.2
                    robot['y'] += (robot['y'] - o['y']) * 0.2

            # goal check
            if math.hypot(robot['x'] - goal['x'], robot['y'] - goal['y']) < (ROBOT_RADIUS + 8):
                is_running = False
                await broadcast({"type": "goal_reached", "robot_position": {"x": robot['x'], "y": robot['y']},
                                 "goal_position": {"x": goal['x'], "y": goal['y']}})
                logger.info("Goal reached.")

        # send frequent state updates for rendering clients
        await broadcast({
            "type": "state_update",
            "robot": {"x": robot['x'], "y": robot['y']},
            "goal": {"x": goal['x'], "y": goal['y']},
            "obstacles": [{"x": o['x'], "y": o['y'], "size": o['size']} for o in obstacles],
            "is_running": is_running,
            "collision_count": collision_count,
            "path": current_path[path_idx:path_idx+8] if current_path and path_idx < len(current_path) else []
        })

async def main():
    reset_scene()
    # start websocket server
    server = await websockets.serve(handle_client, "0.0.0.0", 8080)
    logger.info("WebSocket server started at ws://localhost:8080")

    # start simulation loop
    sim_task = asyncio.create_task(simulation_loop())
    await server.wait_closed()
    await sim_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutting down")
