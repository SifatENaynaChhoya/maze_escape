"""
Advanced enemy management system with AI behaviors, positioning logic, and visual rendering
"""
import math
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from config import *
import game_state
from maze_data import mazes
from utils import get_elapsed_time

# Movement direction constants
DIRECTION_NORTH = 0
DIRECTION_EAST = 1
DIRECTION_SOUTH = 2
DIRECTION_WEST = 3

# Movement offset mappings
MOVEMENT_VECTORS = {
    DIRECTION_NORTH: (-1, 0),
    DIRECTION_EAST: (0, 1),
    DIRECTION_SOUTH: (1, 0),
    DIRECTION_WEST: (0, -1)
}

def reset_enemy_tracking_systems():
    """Clear all enemy-related tracking and state management systems"""
    game_state.enemies = []
    game_state.enemy_rotations = []
    game_state.ene_freeze_T = []

def get_current_maze_layout():
    """Retrieve current level's maze configuration"""
    return mazes[game_state.crnt_lev]

def is_maze_layout_valid(maze):
    """Verify maze data integrity and structure"""
    if maze is None:
        return False
    if len(maze) == 0:
        return False
    return True

def determine_current_level_type():
    """Identify if current level requires special enemy handling"""
    return game_state.crnt_lev == 2  # Boss level identifier

def calculate_maze_center_coordinates(maze):
    """Find the central position within maze boundaries"""
    maze_height = len(maze)
    maze_width = len(maze[0])
    center_row = maze_height // 2
    center_col = maze_width // 2
    return center_row, center_col

def get_boss_initial_configuration():
    """Define boss enemy starting parameters and attributes"""
    boss_health = 10
    boss_direction = 0  # Initial facing direction
    boss_last_move = 0
    return boss_health, boss_direction, boss_last_move

def construct_boss_entity_data(center_row, center_col, current_time):
    """Assemble complete boss enemy data structure"""
    boss_health, boss_direction, boss_last_move = get_boss_initial_configuration()
    boss_entity = [center_row, center_col, boss_direction, boss_last_move, current_time, boss_health]
    return boss_entity

def register_boss_in_systems(boss_entity):
    """Add boss enemy to all relevant tracking systems"""
    game_state.enemies.append(boss_entity)
    game_state.enemy_rotations.append(0.0)
    game_state.ene_freeze_T.append(0)

def setup_boss_level_enemies():
    """Complete boss level enemy initialization process"""
    maze = get_current_maze_layout()
    current_time = get_elapsed_time()
    center_row, center_col = calculate_maze_center_coordinates(maze)
    boss_entity = construct_boss_entity_data(center_row, center_col, current_time)
    register_boss_in_systems(boss_entity)

def is_valid_cell_for_movement(maze, row, col):
    """Determine if a cell can be moved into by an enemy"""
    if not (0 <= row < len(maze)):
        return False
    if not (0 <= col < len(maze[0])):
        return False
    return maze[row][col] == 0

def check_movement_viability(maze, row, col):
    """Assess whether an enemy at given position has valid movement options"""
    for direction_vector in MOVEMENT_VECTORS.values():
        dr = direction_vector[0]
        dc = direction_vector[1]
        target_row = row + dr
        target_col = col + dc
        
        if is_valid_cell_for_movement(maze, target_row, target_col):
            return True
    return False

def find_valid_directions(maze, row, col):
    """Get list of all valid movement directions from current position"""
    valid_directions = []
    
    for direction_id, direction_vector in MOVEMENT_VECTORS.items():
        dr = direction_vector[0]
        dc = direction_vector[1]
        target_row = row + dr
        target_col = col + dc
        
        if is_valid_cell_for_movement(maze, target_row, target_col):
            valid_directions.append(direction_id)
    
    return valid_directions

def select_enemy_direction(maze, row, col):
    """Choose appropriate starting direction for enemy"""
    if not check_movement_viability(maze, row, col):
        return random.randint(0, 3)
    
    valid_directions = find_valid_directions(maze, row, col)
    if len(valid_directions) == 0:
        return random.randint(0, 3)
    
    return random.choice(valid_directions)

def get_regular_enemy_defaults():
    """Define default parameters for regular enemy entities"""
    default_last_move_time = 0
    default_rotation_angle = 0.0
    default_freeze_status = 0
    return default_last_move_time, default_rotation_angle, default_freeze_status

def build_regular_enemy_entity(row, col, direction, current_time):
    """Construct data structure for regular enemy"""
    last_move_time, rotation_angle, freeze_status = get_regular_enemy_defaults()
    enemy_entity = [row, col, direction, last_move_time, current_time]
    return enemy_entity, rotation_angle, freeze_status

def register_regular_enemy_in_systems(enemy_entity, rotation_angle, freeze_status):
    """Add regular enemy to all tracking systems"""
    game_state.enemies.append(enemy_entity)
    game_state.enemy_rotations.append(rotation_angle)
    game_state.ene_freeze_T.append(freeze_status)

def create_regular_enemy_complete(row, col, direction, current_time):
    """Full regular enemy creation process"""
    enemy_entity, rotation_angle, freeze_status = build_regular_enemy_entity(row, col, direction, current_time)
    register_regular_enemy_in_systems(enemy_entity, rotation_angle, freeze_status)

def is_enemy_spawn_marker(maze_cell_value):
    """Check if maze cell contains enemy spawn marker"""
    return maze_cell_value == 5

def clear_spawn_marker_from_maze(maze, row, col):
    """Remove enemy spawn marker and replace with floor"""
    maze[row][col] = 0

def handle_individual_spawn_location(maze, row, col, current_time):
    """Process single maze cell for enemy spawning"""
    if not is_enemy_spawn_marker(maze[row][col]):
        return False
    
    selected_direction = select_enemy_direction(maze, row, col)
    create_regular_enemy_complete(row, col, selected_direction, current_time)
    clear_spawn_marker_from_maze(maze, row, col)
    return True

def iterate_through_maze_rows(maze, current_time):
    """Process all rows in maze for enemy spawning"""
    maze_height = len(maze)
    spawned_enemies = []
    
    for row in range(maze_height):
        row_spawns = process_single_maze_row(maze, row, current_time)
        spawned_enemies.extend(row_spawns)
    
    return spawned_enemies

def process_single_maze_row(maze, row, current_time):
    """Handle enemy spawning for one maze row"""
    maze_width = len(maze[0])
    row_spawns = []
    
    for col in range(maze_width):
        spawn_success = handle_individual_spawn_location(maze, row, col, current_time)
        if spawn_success:
            row_spawns.append((row, col))
    
    return row_spawns

def execute_regular_enemy_scan():
    """Perform comprehensive maze scan for regular enemies"""
    maze = get_current_maze_layout()
    current_time = get_elapsed_time()
    spawned_locations = iterate_through_maze_rows(maze, current_time)
    return spawned_locations

def synchronize_enemy_data_structures():
    """Ensure all enemy tracking arrays have matching lengths"""
    total_enemy_count = len(game_state.enemies)
    game_state.ene_freeze_T = [0] * total_enemy_count

def execute_enemy_system_initialization():
    """Coordinate complete enemy initialization sequence"""
    reset_enemy_tracking_systems()
    
    maze = get_current_maze_layout()
    if not is_maze_layout_valid(maze):
        return False
        
    is_boss_level = determine_current_level_type()
    
    if is_boss_level:
        setup_boss_level_enemies()
    else:
        execute_regular_enemy_scan()
    
    synchronize_enemy_data_structures()
    return True

def initialize_enemies():
    """Primary interface for enemy system setup and configuration"""
    initialization_success = execute_enemy_system_initialization()
    return initialization_success

def check_horizontal_line_clear(maze, enemy_row, enemy_col, player_row, player_col):
    """Verify no walls exist between enemy and player on same row"""
    if enemy_row != player_row:
        return False
    
    col_start = min(enemy_col, player_col)
    col_end = max(enemy_col, player_col)
    
    for col in range(col_start + 1, col_end):
        if maze[enemy_row][col] == 1:
            return False
    
    return True

def check_vertical_line_clear(maze, enemy_row, enemy_col, player_row, player_col):
    """Verify no walls exist between enemy and player on same column"""
    if enemy_col != player_col:
        return False
    
    row_start = min(enemy_row, player_row)
    row_end = max(enemy_row, player_row)
    
    for row in range(row_start + 1, row_end):
        if maze[row][enemy_col] == 1:
            return False
    
    return True

def get_player_position_integers():
    """Extract and convert player position to integer coordinates"""
    player_position = game_state.p_position
    player_row = int(player_position[0])
    player_col = int(player_position[1])
    return player_row, player_col

def is_player_cloaked():
    """Check if player is currently using cloaking ability"""
    return game_state.clk_active

def convert_enemy_coordinates_to_integers(enemy_row, enemy_col):
    """Transform enemy position coordinates into integer values for processing"""
    enemy_row = int(enemy_row)
    enemy_col = int(enemy_col)
    return enemy_row, enemy_col

def retrieve_current_level_maze():
    """Get the maze layout for the current game level"""
    maze = mazes[game_state.crnt_lev]
    return maze

def attempt_horizontal_sight_line_check(maze, enemy_row, enemy_col, player_row, player_col):
    """Try to establish horizontal line of sight between enemy and player"""
    horizontal_clear = check_horizontal_line_clear(maze, enemy_row, enemy_col, player_row, player_col)
    return horizontal_clear

def attempt_vertical_sight_line_check(maze, enemy_row, enemy_col, player_row, player_col):
    """Try to establish vertical line of sight between enemy and player"""
    vertical_clear = check_vertical_line_clear(maze, enemy_row, enemy_col, player_row, player_col)
    return vertical_clear

def perform_comprehensive_sight_analysis(maze, enemy_row, enemy_col, player_row, player_col):
    """Execute complete line of sight analysis in both directions"""
    # Test horizontal sight line first
    if attempt_horizontal_sight_line_check(maze, enemy_row, enemy_col, player_row, player_col):
        return True
    
    # Test vertical sight line if horizontal fails
    if attempt_vertical_sight_line_check(maze, enemy_row, enemy_col, player_row, player_col):
        return True
    
    return False

def is_player_in_line_of_sight(enemy_row, enemy_col):
    """Determine if player is visible in direct line from enemy position using comprehensive analysis"""
    # Early exit if player is cloaked
    if is_player_cloaked():
        return False
    
    player_row, player_col = get_player_position_integers()
    enemy_row, enemy_col = convert_enemy_coordinates_to_integers(enemy_row, enemy_col)
    maze = retrieve_current_level_maze()

    sight_analysis_result = perform_comprehensive_sight_analysis(maze, enemy_row, enemy_col, player_row, player_col)
    return sight_analysis_result

def get_required_enemy_system_references():
    """Retrieve references to all critical enemy management systems"""
    required_systems = [game_state.enemies, game_state.enemy_rotations, game_state.ene_freeze_T]
    return required_systems

def check_system_initialization_status(system):
    """Verify that individual system component is properly initialized"""
    return system is not None

def perform_complete_system_validation():
    """Execute comprehensive validation of all enemy system components"""
    required_systems = get_required_enemy_system_references()
    validation_results = [check_system_initialization_status(system) for system in required_systems]
    all_systems_valid = all(validation_results)
    return all_systems_valid

def validate_enemy_systems():
    """Check if all enemy-related systems are properly initialized using comprehensive validation"""
    system_validation_result = perform_complete_system_validation()
    return system_validation_result

def check_enemy_dimension_initialization_status():
    """Determine if enemy physical dimensions have been previously configured"""
    body_radius_set = game_state.body_radius is not None
    gun_length_set = game_state.Gun_Len is not None
    both_dimensions_configured = body_radius_set and gun_length_set
    return both_dimensions_configured

def calculate_wall_size_for_dimensions():
    """Compute wall size parameter used for enemy dimension calculations"""
    wall_size = GRID_LENGTH * 2 // 15
    return wall_size

def compute_enemy_body_radius(wall_size):
    """Calculate appropriate body radius for enemy entities"""
    game_state.body_radius = wall_size / 3

def compute_enemy_gun_length(wall_size):
    """Calculate appropriate gun length for enemy entities"""
    game_state.Gun_Len = wall_size / 2

def apply_enemy_dimension_calculations():
    """Execute dimension calculations and apply them to game state"""
    wall_size = calculate_wall_size_for_dimensions()
    compute_enemy_body_radius(wall_size)
    compute_enemy_gun_length(wall_size)

def initialize_enemy_dimensions():
    """Set up enemy physical dimensions if not already configured using comprehensive approach"""
    if check_enemy_dimension_initialization_status():
        return
    
    apply_enemy_dimension_calculations()

def validate_enemy_data_integrity(enemy):
    """Check if enemy data structure contains required minimum components"""
    if not enemy:
        return False
    if len(enemy) < 5:
        return False
    return True

def extract_core_enemy_attributes(enemy):
    """Parse basic enemy positioning and behavior data"""
    row = enemy[0]
    col = enemy[1]
    direction = enemy[2]
    last_move_time = enemy[3]
    last_shot_time = enemy[4]
    return row, col, direction, last_move_time, last_shot_time

def extract_optional_health_data(enemy):
    """Parse optional health information for boss enemies"""
    health_data = enemy[5:] if len(enemy) > 5 else []
    return health_data

def determine_enemy_boss_status(health_data):
    """Check if enemy is a boss based on health data presence"""
    is_boss = len(health_data) > 0
    return is_boss

def extract_health_value(health_data, is_boss):
    """Get health value if enemy is a boss, otherwise return None"""
    health = health_data[0] if is_boss else None
    return health

def construct_enemy_data_dictionary(row, col, direction, last_move_time, last_shot_time, health_data, is_boss, health):
    """Build comprehensive enemy data structure as dictionary"""
    enemy_data = {
        'row': row,
        'col': col, 
        'direction': direction,
        'last_move_time': last_move_time,
        'last_shot_time': last_shot_time,
        'health_data': health_data,
        'is_boss': is_boss,
        'health': health
    }
    return enemy_data

def extract_enemy_data_components(enemy):
    """Parse enemy data structure into individual components using comprehensive extraction"""
    if not validate_enemy_data_integrity(enemy):
        return None
    
    row, col, direction, last_move_time, last_shot_time = extract_core_enemy_attributes(enemy)
    health_data = extract_optional_health_data(enemy)
    is_boss = determine_enemy_boss_status(health_data)
    health = extract_health_value(health_data, is_boss)
    
    enemy_data = construct_enemy_data_dictionary(row, col, direction, last_move_time, last_shot_time, health_data, is_boss, health)
    return enemy_data

def process_freeze_trap_interaction(enemy_index, row, col, current_time):
    """Handle enemy stepping on freeze traps"""
    if not game_state.freeze_trap_pos:
        return
        
    for trap_index, trap_pos in enumerate(game_state.freeze_trap_pos):
        trap_row = trap_pos[0]
        trap_col = trap_pos[1]
        
        if trap_row == row and trap_col == col:
            if enemy_index < len(game_state.ene_freeze_T):
                game_state.ene_freeze_T[enemy_index] = current_time
                print(f"Enemy {enemy_index} stepped on freeze trap at time {current_time}")
                game_state.freeze_trap_pos.pop(trap_index)
                break

def calculate_enemy_freeze_status(enemy_index, current_time):
    """Determine if enemy is currently frozen and handle freeze timing"""
    if enemy_index >= len(game_state.ene_freeze_T):
        return False
    
    freeze_time = game_state.ene_freeze_T[enemy_index]
    if freeze_time <= 0:
        return False
    
    time_since_frozen = current_time - freeze_time
    
    if game_state.cheat_mode:
        return True
    
    if time_since_frozen < FREEZE_DURATION:
        return True
    
    # Reset freeze time when duration expires
    game_state.ene_freeze_T[enemy_index] = 0
    return False

def apply_continuous_collision_detection(enemy_index, row, col, current_time):
    """Check for player-enemy collision regardless of movement state"""
    player_position = game_state.p_position
    player_row = player_position[0]
    player_col = player_position[1]
    
    distance_row = abs(row - player_row)
    distance_col = abs(col - player_col)
    
    if distance_row <= 0.5 and distance_col <= 0.5:
        time_since_hit = current_time - game_state.p_last_hit_time
        can_damage_player = not game_state.cheat_mode and time_since_hit > P_INVINCIBILITY_T
        
        if can_damage_player:
            game_state.p_health -= 1
            game_state.p_last_hit_time = current_time
            print(f"Player hit by enemy {enemy_index} at position ({row}, {col}) - Health: {game_state.p_health}")
            
            if game_state.p_health <= 0:
                game_state.game_over = True
                game_state.p_health = 0

def handle_frozen_enemy_rotation(enemy_index):
    """Apply slow rotation for frozen enemies"""
    rotation_speed = ENEMY_ROT_SPEED * 0.2
    current_rotation = game_state.enemy_rotations[enemy_index]
    new_rotation = (current_rotation + rotation_speed) % 360
    game_state.enemy_rotations[enemy_index] = new_rotation

def verify_enemy_system_integrity():
    """Verify that all enemy management systems are properly initialized"""
    systems_valid = (game_state.enemies and 
                    game_state.enemy_rotations and 
                    game_state.ene_freeze_T)
    return systems_valid

def get_current_game_environment():
    """Extract current game environment data for enemy processing"""
    current_time = get_elapsed_time()
    maze = mazes[game_state.crnt_lev]
    wall_size = GRID_LENGTH * 2 // 15
    offset = len(maze) * wall_size // 2
    return current_time, maze, wall_size, offset

def ensure_enemy_dimensions_initialized(wall_size):
    """Initialize enemy dimensions if they haven't been set yet"""
    if game_state.body_radius is None or game_state.Gun_Len is None:
        game_state.body_radius = wall_size / 3  # Red sphere
        game_state.Gun_Len = wall_size / 2  # Grey gun cylinder

def validate_individual_enemy_data(enemy):
    """Check if specific enemy data structure is valid"""
    if not enemy:
        return False
    if len(enemy) < 5:
        return False
    return True

def parse_enemy_position_data(enemy):
    """Extract enemy positioning and timing information"""
    row = enemy[0]
    col = enemy[1]
    direction = enemy[2]
    last_move_time = enemy[3]
    last_shot_time = enemy[4]
    return row, col, direction, last_move_time, last_shot_time

def parse_enemy_boss_information(enemy):
    """Extract boss-specific data from enemy structure"""
    health_data = enemy[5:] if len(enemy) > 5 else []
    is_boss = len(health_data) > 0
    health = health_data[0] if is_boss else None
    return health_data, is_boss, health

def check_enemy_freeze_trap_collision(enemy_index, row, col, current_time):
    """Check if enemy has stepped on freeze trap and handle accordingly"""
    if not game_state.freeze_trap_pos:
        return
        
    for trap_index, trap_pos in enumerate(game_state.freeze_trap_pos):
        if trap_pos[0] == row and trap_pos[1] == col:
            if enemy_index < len(game_state.ene_freeze_T):
                game_state.ene_freeze_T[enemy_index] = current_time
                print(f"Enemy {enemy_index} stepped on freeze trap at time {current_time}")
                game_state.freeze_trap_pos.pop(trap_index)
                break

def determine_enemy_freeze_state(enemy_index, current_time):
    """Calculate whether enemy is currently frozen based on timing"""
    is_frozen = False
    if enemy_index < len(game_state.ene_freeze_T):
        if game_state.ene_freeze_T[enemy_index] > 0:
            time_since_frozen = current_time - game_state.ene_freeze_T[enemy_index]

            if game_state.cheat_mode:
                is_frozen = True
            elif time_since_frozen < FREEZE_DURATION:
                is_frozen = True
            else:
                game_state.ene_freeze_T[enemy_index] = 0
    return is_frozen

def execute_continuous_collision_check(enemy_index, row, col, current_time):
    """Perform collision detection between enemy and player regardless of movement"""
    player_row, player_col = game_state.p_position
    collision_detected = abs(row - player_row) <= 0.5 and abs(col - player_col) <= 0.5
    
    if collision_detected:
        time_condition = current_time - game_state.p_last_hit_time > P_INVINCIBILITY_T
        can_damage = not game_state.cheat_mode and time_condition
        
        if can_damage:
            game_state.p_health -= 1
            game_state.p_last_hit_time = current_time
            print(f"Player hit by enemy {enemy_index} at position ({row}, {col}) - Health: {game_state.p_health}")
            
            if game_state.p_health <= 0:
                game_state.game_over = True
                game_state.p_health = 0

def apply_frozen_enemy_behavior(enemy_index):
    """Handle behavior for frozen enemies including slow rotation"""
    rotation_increment = ENEMY_ROT_SPEED * 0.2
    current_rotation = game_state.enemy_rotations[enemy_index]
    new_rotation = (current_rotation + rotation_increment) % 360
    game_state.enemy_rotations[enemy_index] = new_rotation

def execute_boss_rotation_logic(enemy_index):
    """Apply rotation behavior specifically for boss enemies"""
    rotation_increment = ENEMY_ROT_SPEED
    current_rotation = game_state.enemy_rotations[enemy_index]
    new_rotation = (current_rotation + rotation_increment) % 360
    game_state.enemy_rotations[enemy_index] = new_rotation

def extract_boss_and_player_coordinates(row, col):
    """Get coordinate data for boss and player positioning calculations"""
    player_position = game_state.p_position
    player_row = player_position[0]
    player_col = player_position[1]
    boss_x = col
    boss_z = row
    player_x = player_col
    player_z = player_row
    return player_row, player_col, boss_x, boss_z, player_x, player_z

def calculate_boss_movement_vector(boss_x, boss_z, player_x, player_z):
    """Compute movement direction and distance for boss toward player"""
    dx = player_x - boss_x
    dz = player_z - boss_z
    distance = max(1, (dx ** 2 + dz ** 2) ** 0.5)
    dx /= distance
    dz /= distance
    return dx, dz

def compute_boss_new_position(boss_x, boss_z, dx, dz):
    """Calculate boss's new position based on movement vector"""
    move_speed = BOSS_MOVEMENT
    new_row = boss_z + dz * move_speed
    new_col = boss_x + dx * move_speed
    return new_row, new_col

def check_boss_freeze_trap_interaction(enemy_index, new_row, new_col, current_time):
    """Check if boss is about to step on freeze trap"""
    new_row_int = int(round(new_row))
    new_col_int = int(round(new_col))
    
    for trap_index, trap_pos in enumerate(game_state.freeze_trap_pos):
        if trap_pos[0] == new_row_int and trap_pos[1] == new_col_int:
            game_state.ene_freeze_T[enemy_index] = current_time
            print(f"Boss about to step on freeze trap at time {current_time}")
            game_state.freeze_trap_pos.pop(trap_index)
            return True
    return False

def update_boss_position_in_game_state(enemy_index, new_row, new_col):
    """Apply new boss position to game state"""
    game_state.enemies[enemy_index][0] = new_row
    game_state.enemies[enemy_index][1] = new_col

def check_boss_player_collision(enemy_index, new_row, new_col, player_row, player_col, current_time):
    """Detect and handle boss collision with player"""
    collision_distance = 0.5
    row_collision = abs(new_row - player_row) < collision_distance
    col_collision = abs(new_col - player_col) < collision_distance
    
    if row_collision and col_collision:
        time_condition = current_time - game_state.p_last_hit_time > P_INVINCIBILITY_T
        can_damage = not game_state.cheat_mode and time_condition
        
        if can_damage:
            game_state.p_health -= 1
            game_state.p_last_hit_time = current_time
            
            if game_state.p_health <= 0:
                game_state.game_over = True
                game_state.p_health = 0

def execute_boss_movement_sequence(enemy_index, row, col, current_time):
    """Complete boss movement logic including collision detection"""
    if game_state.clk_active:
        return
    
    player_row, player_col, boss_x, boss_z, player_x, player_z = extract_boss_and_player_coordinates(row, col)
    dx, dz = calculate_boss_movement_vector(boss_x, boss_z, player_x, player_z)
    new_row, new_col = compute_boss_new_position(boss_x, boss_z, dx, dz)
    
    # Check freeze trap interaction
    if check_boss_freeze_trap_interaction(enemy_index, new_row, new_col, current_time):
        return
    
    update_boss_position_in_game_state(enemy_index, new_row, new_col)
    check_boss_player_collision(enemy_index, new_row, new_col, player_row, player_col, current_time)

def should_boss_shoot(current_time, last_shot_time):
    """Determine if boss should fire at player based on timing"""
    return current_time - last_shot_time > ENEMY_FIRE_INT

def calculate_boss_world_position(row, col, wall_size, offset):
    """Convert boss grid position to world coordinates"""
    enemy_x = col * wall_size - offset + wall_size / 2
    enemy_z = row * wall_size - offset + wall_size / 2
    enemy_y = 200  # Boss height
    return enemy_x, enemy_y, enemy_z

def calculate_player_world_position(wall_size, offset):
    """Convert player grid position to world coordinates"""
    player_row, player_col = game_state.p_position
    player_x = player_col * wall_size - offset + wall_size / 2
    player_z = player_row * wall_size - offset + wall_size / 2
    return player_x, player_z

def compute_boss_bullet_direction(enemy_x, enemy_z, player_x, player_z):
    """Calculate normalized direction vector for boss bullet"""
    dx = player_x - enemy_x
    dz = player_z - enemy_z
    distance = max(1, (dx ** 2 + dz ** 2) ** 0.5)
    dx /= distance
    dz /= distance
    return dx, dz

def create_boss_bullet(enemy_x, enemy_y, enemy_z, dx, dz, current_time):
    """Generate and add boss bullet to game state"""
    bullet_data = [enemy_x, enemy_y, enemy_z, 
                  dx * BOSS_BULLET_SPEED, 0, dz * BOSS_BULLET_SPEED, 
                  current_time, False]
    game_state.bullets.append(bullet_data)

def update_boss_last_shot_time(enemy_index, current_time):
    """Record the time of boss's most recent shot"""
    game_state.enemies[enemy_index][4] = current_time

def execute_boss_shooting_sequence(enemy_index, row, col, current_time, last_shot_time, wall_size, offset):
    """Complete boss shooting logic including bullet creation"""
    if not should_boss_shoot(current_time, last_shot_time):
        return
    
    enemy_x, enemy_y, enemy_z = calculate_boss_world_position(row, col, wall_size, offset)
    player_x, player_z = calculate_player_world_position(wall_size, offset)
    dx, dz = compute_boss_bullet_direction(enemy_x, enemy_z, player_x, player_z)
    
    create_boss_bullet(enemy_x, enemy_y, enemy_z, dx, dz, current_time)
    update_boss_last_shot_time(enemy_index, current_time)

def process_complete_boss_logic(enemy_index, row, col, current_time, last_shot_time, wall_size, offset):
    """Execute full boss behavior including movement and shooting"""
    execute_boss_rotation_logic(enemy_index)
    execute_boss_movement_sequence(enemy_index, row, col, current_time)
    
    if game_state.clk_active:
        return
    
    execute_boss_shooting_sequence(enemy_index, row, col, current_time, last_shot_time, wall_size, offset)

def execute_regular_enemy_rotation(enemy_index):
    """Apply rotation behavior for regular enemies"""
    rotation_increment = ENEMY_ROT_SPEED
    current_rotation = game_state.enemy_rotations[enemy_index]
    new_rotation = (current_rotation + rotation_increment) % 360
    game_state.enemy_rotations[enemy_index] = new_rotation

def check_player_visibility_for_shooting(row, col):
    """Determine if player is visible to enemy for shooting purposes"""
    if game_state.clk_active:
        return False
    return is_player_in_line_of_sight(row, col)

def calculate_enemy_direction_toward_player(row, col):
    """Compute the direction enemy should face to target player"""
    player_row, player_col = game_state.p_position
    
    if row == player_row:  # Same row
        new_direction = 1 if player_col > col else 3  # East or West
    elif col == player_col:  # Same column
        new_direction = 2 if player_row > row else 0  # South or North
    else:
        # Move toward player's row or column
        if abs(player_row - row) > abs(player_col - col):
            new_direction = 2 if player_row > row else 0  # Move vertically
        else:
            new_direction = 1 if player_col > col else 3  # Move horizontally
    
    return new_direction

def update_enemy_direction_in_game_state(enemy_index, new_direction):
    """Apply new direction to enemy in game state"""
    game_state.enemies[enemy_index][2] = new_direction

def should_enemy_attempt_movement(current_time, last_move_time):
    """Check if enough time has passed for enemy movement"""
    return current_time - last_move_time >= ENEMY_MOVEMENT

def calculate_enemy_target_position(row, col, direction):
    """Compute where enemy wants to move based on direction"""
    new_row, new_col = row, col
    if direction == 0:  # North
        new_row -= 1
    elif direction == 1:  # East
        new_col += 1
    elif direction == 2:  # South
        new_row += 1
    elif direction == 3:  # West
        new_col -= 1
    return new_row, new_col

def validate_enemy_target_position(new_row, new_col, maze):
    """Check if enemy's target position is valid for movement"""
    row_valid = 0 <= new_row < len(maze)
    col_valid = 0 <= new_col < len(maze[0])
    
    if not (row_valid and col_valid):
        return False
    
    cell_passable = maze[new_row][new_col] == 0 or maze[new_row][new_col] == 3
    return cell_passable

def apply_enemy_position_update(enemy_index, new_row, new_col, current_time):
    """Update enemy position in game state"""
    game_state.enemies[enemy_index][0] = new_row
    game_state.enemies[enemy_index][1] = new_col
    game_state.enemies[enemy_index][3] = current_time

def check_enemy_player_collision_after_movement(enemy_index, new_row, new_col, current_time):
    """Detect collision between enemy and player after movement"""
    player_row, player_col = game_state.p_position
    collision_distance = 0.5
    row_collision = abs(new_row - player_row) < collision_distance
    col_collision = abs(new_col - player_col) < collision_distance
    
    if row_collision and col_collision:
        time_condition = current_time - game_state.p_last_hit_time > P_INVINCIBILITY_T
        can_damage = not game_state.cheat_mode and time_condition
        
        if can_damage:
            game_state.p_health -= 1
            game_state.p_last_hit_time = current_time
            
            if game_state.p_health <= 0:
                game_state.game_over = True
                game_state.p_health = 0

def check_enemy_freeze_trap_after_movement(enemy_index, new_row, new_col, current_time):
    """Check if enemy stepped on freeze trap after movement"""
    if [new_row, new_col] in game_state.freeze_trap_pos:
        game_state.ene_freeze_T[enemy_index] = current_time

def execute_enemy_movement_toward_player(enemy_index, row, col, direction, current_time, last_move_time, maze):
    """Complete enemy movement sequence when player is in sight"""
    new_direction = calculate_enemy_direction_toward_player(row, col)
    update_enemy_direction_in_game_state(enemy_index, new_direction)
    
    if not should_enemy_attempt_movement(current_time, last_move_time):
        return
    
    new_row, new_col = calculate_enemy_target_position(row, col, new_direction)
    
    if validate_enemy_target_position(new_row, new_col, maze):
        apply_enemy_position_update(enemy_index, new_row, new_col, current_time)
        check_enemy_player_collision_after_movement(enemy_index, new_row, new_col, current_time)
        check_enemy_freeze_trap_after_movement(enemy_index, new_row, new_col, current_time)

def should_enemy_shoot_at_player(current_time, last_shot_time):
    """Determine if enemy should fire at visible player"""
    return current_time - last_shot_time > ENEMY_FIRE_INT

def calculate_enemy_world_position_for_shooting(row, col, wall_size, offset, current_time):
    """Compute enemy's world position for bullet generation"""
    enemy_x = col * wall_size - offset + wall_size / 2
    enemy_z = row * wall_size - offset + wall_size / 2
    enemy_y = 200 + 20 * math.sin(current_time * 0.003)
    return enemy_x, enemy_y, enemy_z

def determine_bullet_direction_and_gun_index(row, col):
    """Calculate bullet direction and gun position for enemy shooting with guaranteed normalization"""
    player_row, player_col = game_state.p_position
    
    if row == player_row:  # Same row - horizontal shot
        direction_x = 1.0 if player_col > col else -1.0
        direction_z = 0.0
        gun_idx = 1 if direction_x > 0 else 3
    elif col == player_col:  # Same column - vertical shot
        direction_x = 0.0
        direction_z = 1.0 if player_row > row else -1.0
        gun_idx = 2 if direction_z > 0 else 0
    else:
        # If not in direct line, don't shoot (return zero direction)
        direction_x = 0.0
        direction_z = 0.0
        gun_idx = 0
    
    return direction_x, direction_z, gun_idx

def calculate_bullet_start_position(enemy_x, enemy_y, enemy_z, gun_idx):
    """Compute starting position for enemy bullet from enemy center (ignoring rotation)"""
    # Always start bullets from the enemy center regardless of rotation
    # Add small offset in shooting direction to avoid bullet spawning inside enemy
    start_x = enemy_x
    start_y = enemy_y
    start_z = enemy_z
    return start_x, start_y, start_z

def create_enemy_bullet(start_x, start_y, start_z, direction_x, direction_z, current_time):
    """Generate and add enemy bullet to game state with consistent velocity"""
    # Ensure consistent bullet speed using config constant
    bullet_speed = BULLET_SPEED  # Use consistent speed from config
    bullet_dx = direction_x * bullet_speed
    bullet_dz = direction_z * bullet_speed
    bullet_data = [start_x, start_y, start_z, bullet_dx, 0, bullet_dz, current_time, False]
    game_state.bullets.append(bullet_data)

def update_enemy_last_shot_time(enemy_index, current_time):
    """Record the time of enemy's most recent shot"""
    game_state.enemies[enemy_index][4] = current_time

def execute_enemy_shooting_sequence(enemy_index, row, col, current_time, last_shot_time, wall_size, offset):
    """Complete enemy shooting logic when player is in sight"""
    if not should_enemy_shoot_at_player(current_time, last_shot_time):
        return
    
    # Only shoot if direction is valid (enemy and player are in line)
    direction_x, direction_z, gun_idx = determine_bullet_direction_and_gun_index(row, col)
    if direction_x == 0.0 and direction_z == 0.0:
        return  # Skip shooting if not in direct line
    
    enemy_x, enemy_y, enemy_z = calculate_enemy_world_position_for_shooting(row, col, wall_size, offset, current_time)
    start_x, start_y, start_z = calculate_bullet_start_position(enemy_x, enemy_y, enemy_z, gun_idx)
    
    # Add small offset in the shooting direction to avoid bullet spawning inside enemy
    offset_distance = wall_size / 4  # Small offset to clear the enemy body
    start_x += direction_x * offset_distance
    start_z += direction_z * offset_distance
    
    create_enemy_bullet(start_x, start_y, start_z, direction_x, direction_z, current_time)
    update_enemy_last_shot_time(enemy_index, current_time)

def process_enemy_player_in_sight_behavior(enemy_index, row, col, direction, current_time, last_move_time, last_shot_time, maze, wall_size, offset):
    """Handle complete enemy behavior when player is visible"""
    execute_enemy_movement_toward_player(enemy_index, row, col, direction, current_time, last_move_time, maze)
    execute_enemy_shooting_sequence(enemy_index, row, col, current_time, last_shot_time, wall_size, offset)

def should_enemy_patrol_move(current_time, last_move_time):
    """Check if enemy should move during patrol behavior"""
    return current_time - last_move_time >= ENEMY_MOVEMENT

def execute_enemy_patrol_movement(enemy_index, row, col, direction, current_time, maze):
    """Attempt enemy movement in current direction during patrol"""
    new_row, new_col = calculate_enemy_target_position(row, col, direction)
    
    if validate_enemy_target_position(new_row, new_col, maze):
        apply_enemy_position_update(enemy_index, new_row, new_col, current_time)
        check_enemy_player_collision_after_movement(enemy_index, new_row, new_col, current_time)
        check_enemy_freeze_trap_after_movement(enemy_index, new_row, new_col, current_time)
        return True
    return False

def calculate_opposite_direction(direction):
    """Compute direction opposite to current direction"""
    return (direction + 2) % 4

def try_enemy_opposite_direction_movement(enemy_index, row, col, direction, current_time, maze):
    """Attempt enemy movement in opposite direction when blocked"""
    opposite_dir = calculate_opposite_direction(direction)
    test_row, test_col = calculate_enemy_target_position(row, col, opposite_dir)
    
    if validate_enemy_target_position(test_row, test_col, maze):
        game_state.enemies[enemy_index][0] = test_row
        game_state.enemies[enemy_index][1] = test_col
        game_state.enemies[enemy_index][2] = opposite_dir
        game_state.enemies[enemy_index][3] = current_time
        
        check_enemy_freeze_trap_after_movement(enemy_index, test_row, test_col, current_time)
        return True
    return False

def try_enemy_alternative_directions(enemy_index, row, col, direction, current_time, maze):
    """Try alternative movement directions when blocked and can't backtrack"""
    for offset in [1, 3, 2]:  # Try right, left, then opposite
        test_dir = (direction + offset) % 4
        test_row, test_col = calculate_enemy_target_position(row, col, test_dir)
        
        if validate_enemy_target_position(test_row, test_col, maze):
            game_state.enemies[enemy_index][0] = test_row
            game_state.enemies[enemy_index][1] = test_col
            game_state.enemies[enemy_index][2] = test_dir
            game_state.enemies[enemy_index][3] = current_time
            
            check_enemy_freeze_trap_after_movement(enemy_index, test_row, test_col, current_time)
            return True
    return False

def handle_enemy_blocked_movement(enemy_index, row, col, direction, current_time, maze):
    """Handle enemy behavior when primary movement direction is blocked"""
    # Try opposite direction first
    if try_enemy_opposite_direction_movement(enemy_index, row, col, direction, current_time, maze):
        return
    
    # Try alternative directions if opposite also blocked
    try_enemy_alternative_directions(enemy_index, row, col, direction, current_time, maze)

def process_enemy_patrol_behavior(enemy_index, row, col, direction, current_time, last_move_time, maze):
    """Handle complete enemy patrol behavior when player not in sight"""
    if not should_enemy_patrol_move(current_time, last_move_time):
        return
    
    # Try moving in current direction
    movement_successful = execute_enemy_patrol_movement(enemy_index, row, col, direction, current_time, maze)
    
    if not movement_successful:
        handle_enemy_blocked_movement(enemy_index, row, col, direction, current_time, maze)

def update_enemy_move_timer(enemy_index, current_time):
    """Update the movement timer for enemy"""
    game_state.enemies[enemy_index][3] = current_time

def process_regular_enemy_logic(enemy_index, row, col, direction, current_time, last_move_time, last_shot_time, maze, wall_size, offset):
    """Execute complete logic for regular (non-boss) enemies"""
    execute_regular_enemy_rotation(enemy_index)
    
    player_in_sight = check_player_visibility_for_shooting(row, col)
    
    if player_in_sight:
        process_enemy_player_in_sight_behavior(enemy_index, row, col, direction, current_time, last_move_time, last_shot_time, maze, wall_size, offset)
    else:
        process_enemy_patrol_behavior(enemy_index, row, col, direction, current_time, last_move_time, maze)
    
    # update_enemy_move_timer(enemy_index, current_time)

def process_individual_enemy_update(enemy_index, enemy, current_time, maze, wall_size, offset):
    """Complete update logic for a single enemy entity"""
    if not validate_individual_enemy_data(enemy):
        return
    
    # Extract enemy data
    row, col, direction, last_move_time, last_shot_time = parse_enemy_position_data(enemy)
    health_data, is_boss, health = parse_enemy_boss_information(enemy)
    
    # Handle freeze trap interactions
    check_enemy_freeze_trap_collision(enemy_index, row, col, current_time)
    
    # Check if enemy is frozen
    is_frozen = determine_enemy_freeze_state(enemy_index, current_time)
    
    # Continuous collision detection
    execute_continuous_collision_check(enemy_index, row, col, current_time)
    
    if is_frozen:
        apply_frozen_enemy_behavior(enemy_index)
        return
    
    # Process boss or regular enemy logic
    if is_boss:
        process_complete_boss_logic(enemy_index, row, col, current_time, last_shot_time, wall_size, offset)
    else:
        process_regular_enemy_logic(enemy_index, row, col, direction, current_time, last_move_time, last_shot_time, maze, wall_size, offset)

def execute_all_enemy_updates(current_time, maze, wall_size, offset):
    """Process updates for all enemies in the game"""
    for enemy_index, enemy in enumerate(game_state.enemies):
        process_individual_enemy_update(enemy_index, enemy, current_time, maze, wall_size, offset)

def update_enemies():
    """Primary interface for enemy movement and shooting logic using comprehensive modular approach"""
    if not verify_enemy_system_integrity():
        return
    
    current_time, maze, wall_size, offset = get_current_game_environment()
    ensure_enemy_dimensions_initialized(wall_size)
    execute_all_enemy_updates(current_time, maze, wall_size, offset)

def draw_enemies():
    """Draw all enemies at their current positions"""
    if not game_state.enemies:  # Check if enemies list is empty
        return
        
    wall_size = GRID_LENGTH * 2 // 15
    maze = mazes[game_state.crnt_lev]
    offset = len(maze) * wall_size // 2

    for i, enemy in enumerate(game_state.enemies):
        if not enemy or len(enemy) < 3:  # Check if enemy data is valid
            continue
            
        row, col, direction = enemy[0], enemy[1], enemy[2]
        # Calculate center position of this cell
        x = col * wall_size - offset + wall_size / 2
        z = row * wall_size - offset + wall_size / 2

        # More pronounced hovering and bobbing effect
        current_time = get_elapsed_time() % 2000
        height_offset = 200 + 20 * math.sin(current_time * 0.003)

        # Get rotation angle for this enemy
        rotation_angle = game_state.enemy_rotations[i] if i < len(game_state.enemy_rotations) else 0.0

        # Draw enemy with rotation
        draw_enemy(x, height_offset, z, rotation_angle, i)

        # Draw shadow beneath enemy
        glPushMatrix()
        glTranslatef(x, 11.0, z)  # Just above floor
        glColor4f(0.0, 0.0, 0.0, 0.5)  # Semi-transparent black
        glScalef(1.0, 0.1, 1.0)  # Flatten to make a shadow
        glutSolidSphere(wall_size / 3, 12, 8)
        glPopMatrix()

def draw_enemy(x, y, z, rotation_angle, i):
    """Draw an enemy at the specified position with rotating guns - using different shapes"""
    if not game_state.ene_freeze_T or i >= len(game_state.ene_freeze_T):  # Safety check
        return
        
    current_time = get_elapsed_time()
    is_frozen = game_state.ene_freeze_T[i] > 0 and (game_state.cheat_mode or current_time - game_state.ene_freeze_T[i] < FREEZE_DURATION)
    wall_size = GRID_LENGTH * 2 // 15

    # Check if this is the boss (level 3)
    is_boss = game_state.crnt_lev == 2 and game_state.enemies and len(game_state.enemies) > 0 and len(game_state.enemies[0]) > 5

    # Increase size for better visibility, make boss bigger
    if is_boss:
        body_radius = wall_size / 1.5  # Much larger for boss
        head_radius = wall_size / 3  # Larger for boss
        gun_radius = wall_size / 8  # Larger for boss
        Gun_Len = wall_size  # Longer guns for boss
    else:
        body_radius = wall_size / 3  # Normal size for regular enemies
        head_radius = wall_size / 5
        gun_radius = wall_size / 14
        Gun_Len = wall_size / 2

    glPushMatrix()
    glTranslatef(x, y, z)  # Apply the position

    # Apply rotation for spinning effect
    glRotatef(rotation_angle, 0, 1, 0)

    quadric = gluNewQuadric()
    if not quadric:  # Safety check for quadric
        glPopMatrix()
        return

    # Body - Unified new shape: Icosahedron with richer red
    glColor3f(0.85, 0.12, 0.12)  # Richer reddish tone for enemy body
    glPushMatrix()
    glScalef(body_radius, body_radius, body_radius)
    glutSolidIcosahedron()  # New enemy body shape
    glPopMatrix()

    # Head - Use different shapes for different enemies
    glPushMatrix()
    glTranslatef(0, body_radius + head_radius * 0.5, 0)
    
    if i % 3 == 0:  # First type: Cone head
        glColor3f(0.4, 0.3, 0.3)  # Charcoal with warm tint
        glRotatef(-90, 1, 0, 0)  # Point cone upward
        glutSolidCone(head_radius, head_radius * 1.5, 8, 3)
    elif i % 3 == 1:  # Second type: Sphere head
        glColor3f(0.35, 0.3, 0.3)  # Warm dark gray
        glutSolidSphere(head_radius, 16, 16)
    else:  # Third type: Cube head
        glColor3f(0.4, 0.32, 0.32)  # Warm medium gray
        glutSolidCube(head_radius * 1.5)
    
    glPopMatrix()

    # Guns - Use different shapes and colors for different enemies
    if i % 3 == 0:  # First type: Cylindrical guns
        glColor3f(0.8, 0.75, 0.75)  # Light gray with warm tint
        gun_shape = "cylinder"
    elif i % 3 == 1:  # Second type: Conical guns
        glColor3f(0.9, 0.7, 0.6)  # Warm peach
        gun_shape = "cone"
    else:  # Third type: Cuboid guns
        glColor3f(0.8, 0.7, 0.75)  # Lavender-rose gray
        gun_shape = "cube"

    # Guns attached to all four sides of body
    # Gun on right side (+X)
    glPushMatrix()
    glTranslatef(body_radius * 0.5, 0, 0)
    glRotatef(90, 0, 1, 0)  # Rotate to point right (+X)
    if gun_shape == "cylinder":
        gluCylinder(quadric, gun_radius, gun_radius, Gun_Len, 12, 2)
    elif gun_shape == "cone":
        glutSolidCone(gun_radius, Gun_Len, 8, 3)
    else:  # cube
        glutSolidCube(Gun_Len * 0.8)
    glPopMatrix()

    # Gun on left side (-X)
    glPushMatrix()
    glTranslatef(-body_radius * 0.5, 0, 0)
    glRotatef(-90, 0, 1, 0)  # Rotate to point left (-X)
    if gun_shape == "cylinder":
        gluCylinder(quadric, gun_radius, gun_radius, Gun_Len, 12, 2)
    elif gun_shape == "cone":
        glutSolidCone(gun_radius, Gun_Len, 8, 3)
    else:  # cube
        glutSolidCube(Gun_Len * 0.8)
    glPopMatrix()

    # Gun on front side (+Z)
    glPushMatrix()
    glTranslatef(0, 0, body_radius * 0.5)
    glRotatef(0, 0, 1, 0)  # Rotate to point forward (+Z)
    if gun_shape == "cylinder":
        gluCylinder(quadric, gun_radius, gun_radius, Gun_Len, 12, 2)
    elif gun_shape == "cone":
        glutSolidCone(gun_radius, Gun_Len, 8, 3)
    else:  # cube
        glutSolidCube(Gun_Len * 0.8)
    glPopMatrix()

    # Gun on back side (-Z)
    glPushMatrix()
    glTranslatef(0, 0, -body_radius * 0.5)
    glRotatef(180, 0, 1, 0)  # Rotate to point backward (-Z)
    if gun_shape == "cylinder":
        gluCylinder(quadric, gun_radius, gun_radius, Gun_Len, 12, 2)
    elif gun_shape == "cone":
        glutSolidCone(gun_radius, Gun_Len, 8, 3)
    else:  # cube
        glutSolidCube(Gun_Len * 0.8)
    glPopMatrix()

    if is_frozen:
        glColor4f(0.7, 0.9, 0.95, 0.6)  # Soft sky blue
        glutSolidSphere(body_radius * 1.2, 12, 12)

        # Draw ice crystals on the enemy
        for j in range(4):
            angle = j * 90
            glPushMatrix()
            glRotatef(angle, 0, 1, 0)
            glTranslatef(body_radius * 0.8, 0, 0)
            glColor4f(0.8, 0.95, 0.98, 0.8)  # Soft ice crystal color
            glutSolidCone(body_radius * 0.3, body_radius * 0.6, 6, 3)
            glPopMatrix()
    glPopMatrix()
