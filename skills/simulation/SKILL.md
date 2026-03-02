# Simulation Skill

Bridge agents to RL environments and game worlds for testing.

## Gym Environments

```python
from skills.simulation import GymEnvironment

env = GymEnvironment("CartPole-v1")
state = env.get_state()
result = env.step(action=1)
env.reset()
```

## Game Bridge (Minecraft)

```python
from skills.simulation import GameBridge

bridge = GameBridge("minecraft")
bridge.connect("localhost", 25565)
state = bridge.get_state()
bridge.action("move_forward")
```

## Available Tools

- `get_env_state(env_name)` - Get current Gym state
- `take_action(env_name, action)` - Execute action
- `reset_env(env_name)` - Reset environment
- `connect_game(game, host)` - Connect to game
- `get_game_state(game)` - Get game state
- `execute_action(game, action)` - Execute game action
