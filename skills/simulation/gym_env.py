"""OpenAI Gym / Gymnasium integration for agent testing."""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

class GymEnvironment:
    """Bridge OpenPango to RL environments."""
    
    def __init__(self, env_name: str = "CartPole-v1"):
        self.env_name = env_name
        self.env = None
        self.state = None
    
    def _ensure_env(self):
        """Lazy load the gym environment."""
        if self.env is None:
            try:
                import gymnasium as gym
                self.env = gym.make(self.env_name)
                self.state = self.env.reset()
            except ImportError:
                # Fallback: return mock state if gym not available
                self.state = {"mock": True, "env": self.env_name}
    
    def get_state(self) -> Dict[str, Any]:
        """Get current environment state as JSON."""
        self._ensure_env()
        if self.env is None:
            return self.state
        return {
            "observation": self.state.tolist() if hasattr(self.state, "tolist") else self.state,
            "env": self.env_name
        }
    
    def step(self, action: int) -> Dict[str, Any]:
        """Take action, return new state, reward, done."""
        self._ensure_env()
        if self.env is None:
            return {"error": "Environment not available"}
        
        self.state, reward, terminated, truncated, info = self.env.step(action)
        done = terminated or truncated
        
        return {
            "observation": self.state.tolist() if hasattr(self.state, "tolist") else self.state,
            "reward": float(reward),
            "done": done,
            "info": info
        }
    
    def reset(self) -> Dict[str, Any]:
        """Reset environment."""
        self._ensure_env()
        if self.env is None:
            return self.state
        self.state, info = self.env.reset()
        return {
            "observation": self.state.tolist() if hasattr(self.state, "tolist") else self.state,
            "info": info
        }
    
    def available_environments(self) -> List[str]:
        """List available gym environments."""
        try:
            import gymnasium as gym
            return list(gym.envs.registry.keys())[:20]
        except:
            return ["CartPole-v1", "MountainCar-v0", "Pendulum-v1"]

# Tool functions for agent use
def get_env_state(env_name: str = "CartPole-v1") -> Dict[str, Any]:
    """Get current environment state."""
    env = GymEnvironment(env_name)
    return env.get_state()

def take_action(env_name: str, action: int) -> Dict[str, Any]:
    """Take action in environment."""
    env = GymEnvironment(env_name)
    return env.step(action)

def reset_env(env_name: str) -> Dict[str, Any]:
    """Reset environment."""
    env = GymEnvironment(env_name)
    return env.reset()
