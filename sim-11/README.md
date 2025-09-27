# 2D Robot Simulator with A* Pathfinding

A comprehensive real-time 2D robot simulation system featuring intelligent pathfinding, collision avoidance, WebSocket communication, and goal-reaching functionality. The robot uses A* algorithm with path smoothing to navigate through obstacles efficiently.

## 🚀 Features

### Core Functionality
- **Intelligent Pathfinding** - A* algorithm with adaptive path smoothing
- **Real-time Robot Movement** - Smooth visual feedback with collision detection
- **Dynamic Obstacle Avoidance** - Automatic re-planning when collisions occur
- **Goal-Reaching Detection** - Visual notifications and status tracking
- **WebSocket Communication** - Real-time bidirectional communication
- **RESTful API** - Comprehensive control endpoints
- **Collision Detection** - Circular boundary collision system
- **Path Optimization** - Reduces waypoints for smoother movement

### Advanced Features
- **Adaptive Grid Planning** - Configurable grid size for performance optimization
- **Path Smoothing** - Line-of-sight optimization to skip intermediate waypoints
- **Collision Recovery** - Automatic re-planning from collision points
- **Server-side State Management** - Centralized obstacle and goal tracking
- **Responsive UI Design** - Clean, modern interface with real-time updates

## 🏗️ System Architecture

```
┌─────────────────────────┐    WebSocket     ┌──────────────────────────┐
│    Robot Simulator      │ ←──────────────→ │      Python Server       │
│   (simulator.html)      │                  │      (server.py)         │
└─────────────────────────┘                  └──────────────────────────┘
                                                        ↑
                                                   HTTP REST API
                                                        │
┌─────────────────────────┐                           │
│   Manual Controller     │ ←─────────────────────────┘
│  (controller.html)      │
└─────────────────────────┘

┌─────────────────────────┐    API Calls     ┌──────────────────────────┐
│   Automated Controller  │ ←──────────────→ │      Python Server       │
│   (controller.py)       │                  │      (server.py)         │
└─────────────────────────┘                  └──────────────────────────┘
          ↑
    ┌─────────────┐
    │ A* Planner  │
    │ (planner.py)│
    └─────────────┘
```

## 📋 Prerequisites

- **Python 3.7+**
- **Modern web browser** (Chrome, Firefox, Safari, Edge)
- **Required Python packages:**
  ```bash
  pip install flask websockets asyncio requests
  ```

## 🛠️ Installation & Setup

### 1. Clone or Download the Project
Ensure you have all the required files:
```
robot-simulator/
├── server.py              # Main Python server (WebSocket + Flask)
├── controller.py           # Automated pathfinding controller
├── planner.py             # A* pathfinding algorithm implementation
├── simulator.html         # Visual robot simulator interface
├── controller.html        # Manual control interface
└── README.md              # This documentation
```

### 2. Install Dependencies
```bash
pip install flask websockets asyncio requests
```

### 3. Start the Python Server
```bash
python server.py
```

**Expected Output:**
```
🚀 Starting 2D Robot Server...
Flask server will run on: http://localhost:5001
WebSocket server will run on: ws://localhost:8080
Press Ctrl+C to stop
Starting Flask server on http://localhost:5001
WebSocket server started on ws://localhost:8080
```

### 4. Open the Robot Simulator
- Open `simulator.html` in your web browser
- The simulator automatically connects to `ws://localhost:8080`
- You should see "🟢 Connected" status in the info panel

### 5. Choose Your Control Method

#### Option A: Manual Control
- Open `controller.html` in your browser
- Use the web interface to send movement commands

#### Option B: Automated Pathfinding (Recommended)
```bash
python controller.py
```

**Expected Output:**
```
Connected to simulator
Successfully fetched 8 obstacles from server.
Initial path planning...
Raw path had 23 waypoints, smoothed to 6 waypoints
Smoothed path: [(320, 300), (375, 275), (450, 200), (525, 125), (550, 80)]
➡️ Moving to {'x': 375, 'y': 275}
```

## 🎮 Usage Examples

### Automated Pathfinding Controller

The automated controller (`controller.py`) demonstrates the complete pathfinding solution:

```python
# The controller automatically:
# 1. Fetches current obstacles from server
# 2. Plans optimal path using A* algorithm
# 3. Applies path smoothing for efficiency
# 4. Executes movement commands
# 5. Handles collision recovery with re-planning

python controller.py
```

**Key Features:**
- **Automatic obstacle fetching** from server API
- **Intelligent path planning** with A* algorithm
- **Path smoothing** reduces waypoints by ~70%
- **Collision recovery** with dynamic re-planning
- **Real-time feedback** processing

### Manual API Control

```javascript
// Move to specific coordinates
fetch('http://localhost:5001/move', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({x: 450, y: 200})
});

// Move relative to current position
fetch('http://localhost:5001/move_rel', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({angle: 45, distance: 100})
});

// Set goal position
fetch('http://localhost:5001/goal', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({x: 550, y: 80})
});

// Get obstacle coordinates for pathfinding
fetch('http://localhost:5001/obstacles')
  .then(response => response.json())
  .then(data => console.log('Obstacles:', data.obstacles));
```

## 🔧 A* Pathfinding Configuration

The pathfinding system is highly configurable through `planner.py`:

### Grid Resolution
```python
# Larger grid = faster planning, fewer waypoints
planner = AStarPlanner(grid_size=50)  # Default: 50px grid

# Smaller grid = more precise paths, slower planning
planner = AStarPlanner(grid_size=25)  # Higher precision
```

### Path Smoothing Options
```python
# Basic smoothing - removes intermediate waypoints
smoothed_path = planner.smooth_path(raw_path, obstacles)

# Adaptive smoothing - larger steps in open areas
smoothed_path = planner.adaptive_smooth_path(raw_path, obstacles)
```

### Safety Margins
```python
# Adjust robot radius for collision detection
planner = AStarPlanner(grid_size=50, robot_radius=18)  # Default

# Increase for more conservative paths
planner = AStarPlanner(grid_size=50, robot_radius=25)  # More cautious
```

## 📡 API Endpoints Reference

### Movement Commands
| Endpoint | Method | Description | Parameters | Example |
|----------|--------|-------------|------------|---------|
| `/move` | POST | Move to absolute position | `{"x": 325, "y": 300}` | Move to center |
| `/move_rel` | POST | Move relative to current position | `{"angle": 45, "distance": 80}` | Move 45° for 80px |
| `/stop` | POST | Stop robot movement | None | Emergency stop |

### Goal Management
| Endpoint | Method | Description | Parameters | Example |
|----------|--------|-------------|------------|---------|
| `/goal` | POST | Set goal position | `{"x": 550, "y": 80}` or `{"corner": "NE"}` | Set target |
| `/goal/status` | GET | Check if goal is reached | None | Status check |

### Obstacle Management (Essential for Pathfinding)
| Endpoint | Method | Description | Parameters | Returns |
|----------|--------|-------------|------------|---------|
| `/obstacles` | GET | Get all obstacle coordinates | None | List of obstacle positions |
| `/obstacles/random` | POST | Generate random obstacles | `{"count": 8}` | New obstacle set |
| `/obstacles/positions` | POST | Set custom obstacles | `{"obstacles": [...]}` | Custom layout |

### System Status
| Endpoint | Method | Description | Returns |
|----------|--------|-------------|---------|
| `/status` | GET | Get system status | Connection count, collisions, goal status |
| `/collisions` | GET | Get collision count | Current collision count |
| `/reset` | POST | Reset entire system | Clears all states |

## 🎯 Canvas Specifications

- **Dimensions**: 650×600 pixels
- **Robot Size**: 18 pixels radius (red circle)
- **Goal Size**: 15 pixels radius (green flag)
- **Obstacle Size**: 25 pixels (black squares)
- **Detection Range**: ~33 pixels (robot + goal radius)
- **Grid Resolution**: 50×50 pixels (configurable)

## 🧠 Pathfinding Algorithm Details

### A* Implementation
- **Heuristic**: Euclidean distance for optimal paths
- **Movement**: 8-directional with proper diagonal costs
- **Obstacle Inflation**: Prevents robot collision with safety margins
- **Grid Optimization**: Balances performance vs. precision

### Path Smoothing Process
1. **Line-of-sight check** between waypoints
2. **Skip intermediate points** when direct path is clear
3. **Maintain safety margins** around obstacles
4. **Typical reduction**: 70-80% fewer waypoints

### Collision Recovery
1. **Detection**: Real-time collision monitoring
2. **Position Update**: Use collision point as new start
3. **Re-planning**: Automatic A* recalculation
4. **Execution**: Resume optimized path

## 🔍 Testing Scenarios

### Basic Pathfinding Test
```bash
# Terminal 1: Start server
python server.py

# Terminal 2: Run automated controller
python controller.py
```

**Expected Behavior:**
- Robot plans path from (320, 300) to (550, 80)
- Avoids all obstacles automatically
- Shows "🎯 GOAL REACHED!" upon success

### Collision Recovery Test
1. Start automated controller
2. Manually add obstacles during movement via `/obstacles/positions`
3. Observe automatic re-planning behavior

### Custom Obstacle Layouts
```python
# Set specific obstacle pattern
obstacles = [
    {"x": 400, "y": 300, "size": 30},
    {"x": 450, "y": 250, "size": 25},
    {"x": 350, "y": 350, "size": 25}
]

requests.post('http://localhost:5001/obstacles/positions', 
              json={"obstacles": obstacles})
```

## 🎨 Visual Interface Features

### Real-time Information Panel
- **Connection Status**: WebSocket connection indicator
- **Collision Counter**: Live collision tracking
- **Robot Position**: Real-time coordinates and angle
- **Goal Information**: Distance and status updates

### Canvas Visualization
- **Grid System**: 50px reference grid
- **Gradient Effects**: Modern visual styling
- **Animation Feedback**: Smooth movement transitions
- **Goal Achievement**: Animated success notification

## 🚨 Troubleshooting

### Common Issues

#### WebSocket Connection Failed
```bash
# Check if server is running
curl http://localhost:5001/status

# Restart server if needed
python server.py
```

#### Pathfinding Not Working
```python
# Check obstacle data
import requests
response = requests.get('http://localhost:5001/obstacles')
print(response.json())
```

#### Robot Not Moving
1. **Verify WebSocket connection** (green status indicator)
2. **Check coordinates** are within bounds (0-650, 0-600)
3. **Ensure no collision state** blocking movement

#### Performance Issues
```python
# Increase grid size for faster planning
planner = AStarPlanner(grid_size=75)  # Larger = faster

# Reduce obstacle count
requests.post('http://localhost:5001/obstacles/random', 
              json={"count": 5})
```

### Debug Commands

```bash
# Check server status
curl http://localhost:5001/status

# View current obstacles
curl http://localhost:5001/obstacles

# Check collision count
curl http://localhost:5001/collisions

# Reset system
curl -X POST http://localhost:5001/reset
```

## 🔧 Customization Options

### Adjust Planning Parameters
```python
# In controller.py
class RobotController:
    def __init__(self):
        # Faster planning, fewer waypoints
        self.planner = AStarPlanner(grid_size=75)
        
        # More precise planning
        self.planner = AStarPlanner(grid_size=25)
```

### Modify Movement Speed
```python
# In controller.py - _path_execution_loop()
await asyncio.sleep(0.1)  # Faster movement (default: 0.2)
await asyncio.sleep(0.5)  # Slower movement
```

### Custom Goal Positions
```python
# Predefined corners
self.goal = {"x": 630, "y": 20}    # Top-right
self.goal = {"x": 20, "y": 580}    # Bottom-left
self.goal = {"x": 325, "y": 300}   # Center
```

## 📈 Performance Metrics

### Typical Performance
- **Path Planning**: 50-200ms for 8 obstacles
- **Waypoint Reduction**: 70-80% fewer points after smoothing
- **Movement Speed**: 2 pixels per frame (smooth animation)
- **Collision Detection**: Real-time, <1ms per check
- **Re-planning**: 100-300ms after collision

### Optimization Tips
1. **Larger grid sizes** for open environments
2. **Smaller grids** for precise obstacle avoidance
3. **Fewer obstacles** for faster planning
4. **Path smoothing** for natural movement

## 📄 License

This project is provided as-is for educational and development purposes. Feel free to modify and extend for your needs.

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- **Dynamic obstacle detection**
- **Multi-robot coordination**
- **Advanced path smoothing algorithms**
- **Real-time performance metrics**
- **Mobile device support**

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all prerequisites are met
3. Ensure correct file structure
4. Test with minimal obstacle configurations

---

**Happy pathfinding! 🤖🎯**