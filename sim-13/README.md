# Robot Simulator Project

A comprehensive robotics simulation environment featuring intelligent path planning, obstacle avoidance, and machine learning capabilities. The project includes both 2D and 3D visualizations with real-time WebSocket communication and REST API control.

## 🎯 Overview

This project provides a complete robotics simulation platform with:
- *Real-time path planning* using A* algorithm with dynamic replanning
- *Intelligent obstacle avoidance* with predictive collision detection
- *3D visualization* using Three.js with realistic robot models
- *2D top-down view* for algorithmic visualization
- *Deep Q-Network (DQN)* reinforcement learning agent
- *WebSocket communication* for real-time updates
- *REST API* for programmatic control
- *Moving obstacles* with configurable physics

## 🏗 Architecture


┌─────────────────┐    WebSocket     ┌──────────────────┐
│   Frontend      │ ←──────────────→ │  Backend Server  │
│                 │      8080        │                  │
│ • 3D Simulator  │                  │ • A* Planning    │
│ • 2D Simulator  │                  │ • Collision Det. │
│ • Visual UI     │                  │ • State Manager  │
└─────────────────┘                  └──────────────────┘
         │                                     │
         │            HTTP REST API            │
         └─────────────────────────────────────┘
                        5000


## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari)
- Required Python packages:

bash
pip install websockets torch numpy opencv-python


### Installation & Setup

1. *Clone the repository*
bash
git clone <repository-url>
cd robot-simulator


2. *Install dependencies*
bash
pip install websockets torch numpy opencv-python


3. *Start the backend server*
bash
python backend_server.py

The server will start:
- WebSocket server on ws://localhost:8080
- (Optional) REST API on port 5000 (if using server.py)

4. *Open the simulator*
- *3D Simulator*: Open index.html in your browser
- *2D Simulator*: Open simulator_ws.html in your browser

Or serve via HTTP:
bash
python -m http.server 8000
# Then visit http://localhost:8000


## 🎮 Usage

### Web Interface Controls

#### 3D Simulator (index.html)
- *Start Navigation*: Begin autonomous navigation
- *Stop Navigation*: Pause the robot
- *Reset*: Reset robot position and generate new goal
- *Mouse Controls*: 
  - Left drag: Rotate camera
  - Right drag: Pan camera
  - Scroll: Zoom in/out

#### 2D Simulator (simulator_ws.html)
- Real-time visualization of A* pathfinding
- Shows planned path as blue line with waypoints
- Displays collision detection and avoidance

### Programmatic Control (REST API)

If using the full server setup with Flask API:

#### Basic Movement
bash
# Absolute positioning
curl -X POST -H "Content-Type: application/json" \
  -d '{"x": 10, "z": -5}' \
  http://localhost:5000/move

# Relative movement  
curl -X POST -H "Content-Type: application/json" \
  -d '{"turn": 45, "distance": 10}' \
  http://localhost:5000/move_rel

# Stop robot
curl -X POST http://localhost:5000/stop


#### Goal Setting
bash
# Set goal to corner
curl -X POST -H "Content-Type: application/json" \
  -d '{"corner":"NE"}' \
  http://localhost:5000/goal

# Set goal to specific coordinates
curl -X POST -H "Content-Type: application/json" \
  -d '{"x": 45, "z": -45}' \
  http://localhost:5000/goal


#### Obstacle Control
bash
# Enable moving obstacles
curl -X POST -H "Content-Type: application/json" \
  -d '{"enabled":true, "speed":0.08, "bounce":true}' \
  http://localhost:5000/obstacles/motion

# Disable obstacle motion
curl -X POST -H "Content-Type: application/json" \
  -d '{"enabled":false}' \
  http://localhost:5000/obstacles/motion


#### System Status
bash
# Get collision count
curl http://localhost:5000/collisions

# Reset simulation
curl -X POST http://localhost:5000/reset


## 🧠 AI & Algorithms

### Path Planning
The system uses *A pathfinding** with several enhancements:
- *Grid-based discretization* for efficient computation
- *Dynamic replanning* every 0.4 seconds
- *Multi-candidate goal generation* to avoid local obstacles
- *Path scoring* based on length and collision risk

### Obstacle Avoidance
- *Predictive collision detection* using future obstacle positions
- *Dynamic force fields* with goal attraction and obstacle repulsion
- *Emergency sidestepping* for immediate collision avoidance
- *Adaptive replanning* when paths become invalid

### Machine Learning (DQN Agent)
The project includes a Deep Q-Network implementation for reinforcement learning:

python
from robot_ai import RobotAI

# Initialize AI agent
ai = RobotAI(
    initial_pos={'x': 0, 'z': 0}, 
    target_pos={'x': 40, 'z': 40}
)

# Training loop
frame = capture_camera_view()  # Your camera capture function
action = ai.select_action(frame)
# ... execute action ...
done = ai.update(frame, action, robot_position, collision_occurred)


## 📁 Project Structure


robot-simulator/
├── backend_server.py      # Main WebSocket server with A* planning
├── index.html            # 3D Three.js simulator
├── simulator_ws.html     # 2D pathfinding visualizer
├── dqn_agent.py         # Deep Q-Network implementation
├── robot_ai.py          # AI control system
├── server.py            # Flask REST API (optional)
├── .gitignore           # Python gitignore
└── README.md            # This file


## 🔧 Configuration

### Robot Parameters
python
ROBOT_RADIUS = 18          # Robot collision radius (pixels)
ROBOT_SPEED = 90.0         # Movement speed (pixels/second)
SIM_FPS = 20.0            # Simulation update rate


### Environment Settings
python
CANVAS_W = 650            # Simulation width
CANVAS_H = 600            # Simulation height
NUM_OBSTACLES = 8         # Number of obstacles
OBSTACLE_MAX_SPEED = 30.0 # Maximum obstacle speed


### Planning Parameters
python
GRID_RES = 10             # A* grid resolution
REPLAN_INTERVAL = 0.4     # Seconds between replanning
SAFE_DISTANCE = 6.0       # Obstacle avoidance threshold


## 🎯 Features in Detail

### Real-time Path Planning
- *A Algorithm**: Optimal pathfinding on discretized grid
- *Dynamic Replanning*: Adapts to moving obstacles
- *Multi-goal Evaluation*: Tests multiple candidate destinations
- *Collision-aware Scoring*: Penalizes paths through obstacles

### 3D Visualization
- *Realistic Robot Model*: Detailed humanoid robot with animations
- *Dynamic Environment*: Moving obstacles with physics
- *Goal Markers*: Visual indicators for navigation targets
- *Camera Controls*: Interactive 3D navigation

### Collision System
- *Real-time Detection*: Continuous collision monitoring
- *Visual Feedback*: Color changes and effects on collision
- *Statistical Tracking*: Collision counting and reporting
- *Recovery Behaviors*: Automatic collision avoidance

### WebSocket Communication
json
{
  "type": "state_update",
  "robot": {"x": 320, "y": 300},
  "goal": {"x": 550, "y": 80},
  "obstacles": [{"x": 100, "y": 150, "size": 25}],
  "is_running": true,
  "collision_count": 3,
  "path": [[325, 295], [330, 285]]
}


## 🤖 Machine Learning Integration

### DQN Agent Features
- *Convolutional Neural Network* for visual processing
- *Experience Replay* for stable learning
- *Target Network* for improved convergence
- *Epsilon-greedy Exploration* with decay
- *Reward Engineering* for navigation tasks

### Training Process
1. *State Representation*: First-person camera view (84x84 RGB)
2. *Action Space*: [Forward, Backward, Left, Right]
3. *Reward Function*: 
   - Goal reached: +100
   - Collision: -10  
   - Movement towards goal: positive
   - Step penalty: -0.1

## 🔧 Troubleshooting

### Connection Issues
- *WebSocket fails*: Check if port 8080 is available
- *No robot movement*: Ensure simulation is started via UI or API
- *Path not showing*: Verify WebSocket connection in browser console

### Performance Issues
- *Low framerate*: Reduce number of obstacles or lower FPS
- *Stuttering movement*: Increase ROBOT_SPEED or decrease SIM_FPS
- *Planning delays*: Increase GRID_RES for coarser planning

### Common Errors
bash
# Port already in use
OSError: [Errno 48] Address already in use

# Solution: Find and kill process using port
lsof -ti:8080 | xargs kill -9


## 🚀 Advanced Usage

### Custom Obstacle Patterns
python
# Add obstacles programmatically
obstacles = [
    {"x": 100, "y": 100, "size": 30, "vx": 0.5, "vy": 0.3},
    {"x": 200, "y": 150, "size": 25, "vx": -0.2, "vy": 0.4}
]


### AI Training Script
python
# Train the DQN agent
ai = RobotAI(initial_pos, target_pos)

for episode in range(1000):
    ai.reset()
    # ... training loop ...
    if episode % 100 == 0:
        ai.save(f'model_episode_{episode}.pth')


### Multi-Robot Scenarios
The architecture supports multiple robots by extending the WebSocket protocol:
json
{
  "type": "multi_robot_update",
  "robots": [
    {"id": "robot1", "x": 100, "y": 100},
    {"id": "robot2", "x": 200, "y": 200}
  ]
}


## 📈 Performance Metrics

The system tracks various performance metrics:
- *Path Efficiency*: Ratio of optimal to actual path length
- *Collision Rate*: Collisions per unit time
- *Planning Time*: Average time for path computation
- *Success Rate*: Percentage of goals reached

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: git checkout -b feature-name
3. Commit changes: git commit -am 'Add feature'
4. Push to branch: git push origin feature-name
5. Submit a Pull Request

## 📄 License

This project is open source. Please check the license file for details.

## 🙏 Acknowledgments

- *Three.js* for 3D graphics rendering
- *PyTorch* for deep learning capabilities
- *WebSocket* protocol for real-time communication
- *A Algorithm** for optimal pathfinding

---

For questions or support, please open an issue on the project repository.
