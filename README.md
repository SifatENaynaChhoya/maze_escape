# 3D Maze Escape: Hunter's Chase - Refactored

This is a refactored version of the 3D Maze Escape game, broken down into multiple organized modules for better maintainability and code organization.

## File Structure

- **`main.py`** - Entry point and main game loop
- **`config.py`** - Game configuration constants and settings
- **`game_state.py`** - Global game state variables
- **`maze_data.py`** - Maze level definitions
- **`utils.py`** - Utility functions (timing, level management, etc.)
- **`player.py`** - Player character rendering and shooting
- **`enemies.py`** - Enemy AI, movement, and rendering
- **`bullets.py`** - Bullet physics and collision detection
- **`renderer.py`** - Maze, walls, and collectibles rendering
- **`camera.py`** - Camera management and view setup
- **`input_handler.py`** - Keyboard and mouse input handling
- **`menu.py`** - Main menu and instructions screen

## Requirements

- Python 3.x
- PyOpenGL library
- OpenGL folder (should be available in the parent directory)

## How to Run

### Option 1: PowerShell Script
```powershell
.\run_game.ps1
```

### Option 2: Batch File
```cmd
run_game.bat
```

### Option 3: Direct Python
```cmd
python main.py
```

## Game Controls

- **WASD** - Move player
- **Mouse** - Look around
- **Left Click** - Shoot
- **Right Click** - Toggle view mode
- **E** - Interact/Collect items
- **5, 6, 7** - Select items (key, freeze trap, cloak)
- **Space** - Pause game
- **C** - Toggle cheat mode
- **V** - Toggle wall phasing (cheat mode only)
- **ESC** - Return to menu
- **R** - Reset camera view

## Features

- 3 levels with increasing difficulty
- Enemy AI with line-of-sight shooting
- Collectible items (keys, freeze traps, cloaks)
- Coin collection system with bonuses
- Boss fight in level 3
- Multiple camera modes (overhead/first-person)
- Cheat mode with enhanced abilities

## Code Organization

The refactored code separates concerns into logical modules:
- **Configuration** is centralized in `config.py`
- **State management** is handled by `game_state.py`
- **Rendering** is split between specific modules
- **Game logic** is distributed across specialized files
- **Input handling** is centralized for better maintainability


