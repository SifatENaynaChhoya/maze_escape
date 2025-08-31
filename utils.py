"""
Utility functions for time management and game helpers
"""
import time
import random
from config import *
import game_state
from maze_data import mazes

def get_elapsed_time():
    """Get elapsed time since application start in milliseconds"""
    return int((time.time() - game_state.AppStart_T) * 1000)

def update_delta_time():
    """Update delta time calculations"""
    current_time = time.time()
    game_state.elapsed_T = current_time - game_state.L_frame_T
    game_state.L_frame_T = current_time
    game_state.ani_Time += game_state.elapsed_T  # Accumulate time for animations
    return game_state.elapsed_T

def find_player_start():
    """Find the player start position in the current maze"""
    maze = mazes[game_state.crnt_lev]
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            if maze[row][col] == 3:
                return [row, col]
    return [0, 0]  # Fallback if not found

def generate_coin_positions():
    """Generate coin positions for the current level."""
    maze = mazes[game_state.crnt_lev]
    wall_size = GRID_LENGTH * 2 // 15
    offset = len(maze) * wall_size // 2
    empty_cells = []

    # Only skip coins for level 3 (index 2)
    if game_state.crnt_lev == 2:  # Level 3 (Boss Fight) - no coins in boss level
        game_state.coin_pos = []
        return

    # Generate coins for levels 1 and 2
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            # Check for empty floor and not a special cell
            if maze[row][col] == 0:  # Empty floor
                x = col * wall_size - offset + wall_size / 2
                z = row * wall_size - offset + wall_size / 2
                empty_cells.append((x, z))

    # Use different seeds for different levels to ensure different coin patterns
    random.seed(423 + game_state.crnt_lev)  # Different seed for each level
    game_state.coin_pos = random.sample(empty_cells, min(NUM_COINS, len(empty_cells)))

def load_next_level():
    """Transition the game to the next level."""
    if game_state.crnt_lev >= len(mazes) - 1:
        print("You have reached the final level. Game completed!")
        return

    # Increment the level
    game_state.crnt_lev += 1

    # Reset player position
    game_state.p_position = find_player_start()

    # Reset enemies, bullets, and other level-specific variables
    game_state.enemies = []
    game_state.bullets = []
    game_state.p_bullets = []
    game_state.Tracks_bullets = 0

    # Reset traps deployed in the current level
    game_state.freeze_trap_pos = []  # Clear deployed traps, but keep collected traps
    game_state.k_collect = False

    # Preserve player attributes
    # Reset temporary states
    game_state.p_last_hit_time = 0
    game_state.P_Immobilized = False
    game_state.P_Immobilized_T = 0
    game_state.clk_start_T = 0 if not game_state.clk_active else game_state.clk_start_T  # Preserve cloak state across levels

    # Initialize enemies and coins for the new level
    from enemies import initialize_enemies
    initialize_enemies()
    generate_coin_positions()

    # Ensure collected_coins list has enough elements for the new level
    while len(game_state.collected_coins) <= game_state.crnt_lev:
        game_state.collected_coins.append(set())

    print(f"Level {game_state.crnt_lev + 1} loaded!")
