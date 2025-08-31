"""
Game state management with all global variables
"""
import time
from config import *

# Timing variables
AppStart_T = time.time()  # Starting time of the application
L_frame_T = AppStart_T  # Time of the last frame
elapsed_T = 0.0  # Time elapsed since last frame
ani_Time = 0.0  # Accumulated time for animations

# Coin system
coin_pos = []  # List of (x, z) tuples for coin positions
collected_coins = [set(), set()]  # List of sets for each level's collected coins

# Camera-related variables - positioned to view the full expanded maze
view_angle = INITIAL_VIEW_ANGLE
cam_point = INITIAL_CAM_POINT
camera_angle = 0  # Track camera angle for rotation
field_of_view = FIELD_OF_VIEW

# Game level and maze data
crnt_lev = 0
act_mode = "collect"
k_collect = False
view_mode = "overhead"

# Player state
p_position = [0, 0]  # Will be set by find_player_start()
p_angle = 0.0  # 0 = facing north
p_health = INITIAL_PLAYER_HEALTH
p_last_hit_time = 0  # Track when player was last hit for invincibility frames
game_over = False  # Track if the game is over due to player death
P_Immobilized = False
P_Immobilized_T = 0
P_END_SHOT_T = 0  # Track when player last fired

# Enemy system
enemies = []  # Format: [[row, col, direction, last_move_time], ...]
# direction: 0=north, 1=east, 2=south, 3=west
enemy_rotations = []  # Store rotation angle for each enemy
ene_freeze_T = []  # When each enemy was frozen (0 = not frozen)
body_radius = None  # Will be set dynamically based on wall size
Gun_Len = None  # Will be set dynamically based on wall size

# Bullet system
bullets = []  # Format: [x, y, z, dx, dy, dz, creation_time, is_player_bullet]
p_bullets = []  # Format: [x, y, z, dx, dy, dz, creation_time]
Tracks_bullets = 0  # Tracks how many bullets the player has fired
bullet_limit = INITIAL_BULLET_LIMIT

# Item system
freeze_traps_C = 0  # Number of freeze traps the player has
S_item = ""  # Currently selected item ("key" or "freeze_trap")
freeze_trap_pos = []  # Positions of deployed freeze traps
clk_collected = False  # Tracks if the cloak has been collected
clk_active = False  # Tracks if the cloak is currently active
clk_start_T = 0  # Tracks when the cloak was activated

# Special modes and states
cheat_mode = False
original_Bullet_S = BULLET_SPEED
mouse_left_down = False
wall_phasing = False  # Track if wall phasing is active
game_paused = False  # Track if the game is paused

# Menu and UI state
game_state = "menu"  # Can be "menu" or "playing"
show_instructions = False  # Track if instructions are being shown
victory = False  # Track if player has won the game

# Bonus tracking
fifty_coin_bonus_given = False  # Track if 50 coin bonus has been given
hundred_coin_bonus_given = False  # Track if 100 coin bonus has been given

# Current bullet speed (can be modified by cheat mode)
Bullet_S = BULLET_SPEED
