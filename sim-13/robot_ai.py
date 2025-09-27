import numpy as np
import cv2
from dqn_agent import DQNAgent
import math

class RobotAI:
    def __init__(self, initial_pos, target_pos, frame_shape=(84, 84)):
        self.initial_pos = initial_pos
        self.target_pos = target_pos
        self.frame_shape = frame_shape
        
        # Actions: [forward, backward, left, right]
        self.n_actions = 4
        self.state_shape = (3, *frame_shape)  # 3 channels (RGB) image
        
        # Initialize DQN agent
        self.agent = DQNAgent(self.state_shape, self.n_actions)
        
        # Parameters
        self.max_steps = 1000
        self.current_step = 0
        self.collision_penalty = -10
        self.goal_reward = 100
        self.step_penalty = -0.1
        self.prev_distance = None
        
    def preprocess_frame(self, frame):
        """Convert frame to grayscale and resize"""
        frame = cv2.resize(frame, self.frame_shape)
        frame = frame.transpose(2, 0, 1)  # Convert to channel-first format
        return frame / 255.0  # Normalize
        
    def get_distance_to_goal(self, current_pos):
        """Calculate Euclidean distance to goal"""
        return math.sqrt(
            (current_pos['x'] - self.target_pos['x'])**2 +
            (current_pos['z'] - self.target_pos['z'])**2
        )
        
    def calculate_reward(self, current_pos, collision):
        """Calculate reward based on current state"""
        # High penalty for collision
        if collision:
            return self.collision_penalty
            
        # Check if reached goal (within threshold)
        distance = self.get_distance_to_goal(current_pos)
        if distance < 2.0:  # 2 units threshold
            return self.goal_reward
            
        # Reward for moving closer to goal
        if self.prev_distance is not None:
            reward = self.prev_distance - distance
        else:
            reward = 0
            
        self.prev_distance = distance
        return reward + self.step_penalty
        
    def select_action(self, frame, training=True):
        """Select action based on current state"""
        state = self.preprocess_frame(frame)
        action = self.agent.select_action(state) if training else self.agent.select_action(state)
        return action
        
    def update(self, frame, action, current_pos, collision):
        """Update agent's knowledge"""
        state = self.preprocess_frame(frame)
        reward = self.calculate_reward(current_pos, collision)
        
        # Get next state
        next_state = state
        
        # Check if episode is done
        done = collision or self.get_distance_to_goal(current_pos) < 2.0 or self.current_step >= self.max_steps
        
        # Store transition and train
        self.agent.store_transition(state, action, reward, next_state, done)
        self.agent.train()
        
        self.current_step += 1
        return done
        
    def reset(self):
        """Reset episode-specific variables"""
        self.current_step = 0
        self.prev_distance = None
        
    def save(self, path):
        """Save agent's state"""
        self.agent.save(path)
        
    def load(self, path):
        """Load agent's state"""
        self.agent.load(path)