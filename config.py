"""
Game configuration constants and settings
"""

# Timing constants
P_INVINCIBILITY_T = 1200  # Increased invincibility time
IMMOBILIZE_DURATION = 2500  # Reduced immobilize duration
FREEZE_DURATION = 6000  # Increased freeze duration
BULLET_LIFETIME = 4000  # Increased bullet lifetime
P_FIRE_INT = 80  # Faster player firing
ENEMY_FIRE_INT = 150  # Faster enemy firing

# Movement and speed constants
ENEMY_MOVEMENT = 1000  # Faster enemy movement
BULLET_SPEED = 8  # Increased bullet speed
BOSS_BULLET_SPEED = 6 # Adjusted boss bullet speed
BOSS_MOVEMENT = 0.002 # Slightly faster boss movement
ENEMY_ROT_SPEED = 1.5  # Faster enemy rotation

# Game constants
NUM_COINS = 50
GRID_LENGTH = 2000  # Adjusted grid size for better proportions
RANDOM_SEED = 789  # Changed random seed
MAX_PLAYER_HEALTH = 100  # Maximum health cap

# Player constants
INITIAL_PLAYER_HEALTH = 15  # Increased starting health
INITIAL_BULLET_LIMIT = 20  # Increased starting bullet limit
CLOAK_DURATION = 7000  # Increased cloak duration

# Camera constants
INITIAL_VIEW_ANGLE = (0, 3800, 3800)  # Adjusted for better view
INITIAL_CAM_POINT = (0, 0, 0)  # Point camera is looking at
FIELD_OF_VIEW = 65  # Slightly wider field of view

# Menu button rectangles (x, y, width, height) - coordinates match menu.py button positions
MENU_BUTTON_RECT = (350, 380, 300, 60)  # START GAME button
INSTRUCTIONS_BUTTON_RECT = (350, 310, 300, 60)  # INSTRUCTIONS button
EXIT_BUTTON_RECT = (350, 240, 300, 60)  # EXIT button

# Direction vectors for the four guns: North, East, South, West
GUN_OFFSETS = [(0, 0, -1), (1, 0, 0), (0, 0, 1), (-1, 0, 0)]

# Colors
BOUNDARY_COLOR = (0.75, 0.85, 0.7)  # Soft sage green
DARKER_BOUNDARY = (0.65, 0.75, 0.6)  # Slightly darker sage green for side faces
SAGE_COLOR = (0.5059, 0.5647, 0.4039)  # Sage (rgb 129,144,103)
