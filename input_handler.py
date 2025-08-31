"""
Input handling for keyboard and mouse events
"""
import math
from OpenGL.GLUT import *
from config import *
import game_state
from maze_data import mazes, get_initial_mazes
from utils import get_elapsed_time, find_player_start, generate_coin_positions, load_next_level
from player import player_shoot
from camera import updateCameraPosition
from enemies import initialize_enemies

def keyboardListener(key, x, y):
    """Handle keyboard input events"""
    # Convert key to proper format
    key = _convert_key_input(key)
    
    # Handle system keys that work regardless of game state
    if _handle_system_keys(key):
        return
    
    # Handle pause state
    if _is_game_paused():
        return
    
    # Handle game over state
    if _handle_game_over_keys(key):
        return
    
    # Handle immobilization state
    if _handle_immobilization_keys(key):
        return
    
    # Get current game context
    game_context = _get_keyboard_game_context()
    current_time = game_context[0]
    row = game_context[1]
    col = game_context[2]
    maze = game_context[3]
    
    # Handle cheat system keys
    if _handle_cheat_keys(key, current_time):
        return
    
    # Handle player movement and rotation
    _handle_movement_keys(key)
    
    # Handle trap detection
    _handle_trap_detection(maze, current_time)
    
    # Handle coin collection
    handle_coin_collection()
    
    # Handle item system keys
    _handle_item_keys(key)
    
    # Handle camera system keys
    _handle_camera_keys(key)

def _convert_key_input(key):
    """Convert key input to proper string format"""
    return key.decode('utf-8') if isinstance(key, bytes) else chr(key)

def _handle_system_keys(key):
    """Handle system-level keys that work regardless of game state"""
    # Handle ESC key to return to menu
    if key == '\x1b':  # ESC key
        reset_to_menu()
        return True
    
    # Handle pause toggle with space bar
    if key == ' ':
        game_state.game_paused = not game_state.game_paused
        return True
    
    return False

def _is_game_paused():
    """Check if game is paused and should skip processing"""
    return game_state.game_paused

def _handle_game_over_keys(key):
    """Handle keys during game over state"""
    if game_state.game_over and (key == 'r' or key == 'R'):
        reset_to_menu()
        return True
    
    if game_state.game_over:
        return True
    
    return False

def _handle_immobilization_keys(key):
    """Handle keys while player is immobilized"""
    if not game_state.P_Immobilized:
        return False
    
    current_time = get_elapsed_time()
    if current_time - game_state.P_Immobilized_T > IMMOBILIZE_DURATION:
        game_state.P_Immobilized = False  # Player is free
        return False
    
    # Allow only specific keys while immobilized
    allowed_keys = ['+', '=', '-', '_', 'r', 'R', '1', '2', '3', '4']
    if key in allowed_keys:
        return False  # Allow processing of these keys
    else:
        return True  # Block other keys

def _get_keyboard_game_context():
    """Get current game context data for keyboard processing"""
    current_time = get_elapsed_time()
    row = game_state.p_position[0]
    col = game_state.p_position[1]
    maze = mazes[game_state.crnt_lev]
    return (current_time, row, col, maze)

def _handle_cheat_keys(key, current_time):
    """Handle cheat mode related keys"""
    # Handle cheat mode toggle
    if key == 'c' or key == 'C':
        _toggle_cheat_mode(current_time)
        return True
    
    # Handle wall phasing toggle
    if key == 'v' or key == 'V':
        _toggle_wall_phasing()
        return True
    
    return False

def _toggle_cheat_mode(current_time):
    """Toggle cheat mode and handle related state changes"""
    game_state.cheat_mode = not game_state.cheat_mode
    game_state.wall_phasing = False  # Reset wall phasing when toggling cheat mode
    
    if game_state.cheat_mode:
        _activate_cheat_mode()
    else:
        _deactivate_cheat_mode(current_time)
    
    print(f"Cheat mode {'activated' if game_state.cheat_mode else 'deactivated'}")

def _activate_cheat_mode():
    """Activate cheat mode settings"""
    game_state.Bullet_S = game_state.original_Bullet_S * 2  # Double bullet speed in cheat mode

def _deactivate_cheat_mode(current_time):
    """Deactivate cheat mode and reset related timers"""
    game_state.Bullet_S = game_state.original_Bullet_S  # Reset to original speed when cheat mode is off
    
    # Reset cloak timer when cheat mode is turned off
    if game_state.clk_active:
        game_state.clk_start_T = get_elapsed_time()  # Reset to current time to start normal duration
    
    # Handle enemy freeze timers
    _reset_enemy_freeze_timers(current_time)

def _reset_enemy_freeze_timers(current_time):
    """Reset enemy freeze timers when exiting cheat mode"""
    enemy_index = 0
    while enemy_index < len(game_state.ene_freeze_T):
        if game_state.ene_freeze_T[enemy_index] > 0:
            if current_time - game_state.ene_freeze_T[enemy_index] < FREEZE_DURATION:
                # Keep the enemy frozen with the current elapsed time preserved
                pass
            else:
                # Enemy has been frozen longer than the freeze duration, so unfreeze it
                game_state.ene_freeze_T[enemy_index] = 0
        enemy_index += 1

def _toggle_wall_phasing():
    """Toggle wall phasing if cheat mode is active"""
    if game_state.cheat_mode:  # Only allow wall phasing in cheat mode
        game_state.wall_phasing = not game_state.wall_phasing
        print(f"Wall phasing {'activated' if game_state.wall_phasing else 'deactivated'}")

def _handle_movement_keys(key):
    """Handle player movement and rotation keys"""
    # Handle rotation
    if key == 'a' or key == 'A':  # Rotate left
        _rotate_player_left()
    elif key == 'd' or key == 'D':  # Rotate right
        _rotate_player_right()
    
    # Handle movement
    elif key == 'w' or key == 'W':  # Forward in facing direction
        handle_player_movement(forward=True)
    elif key == 's' or key == 'S':  # Backward (opposite of facing direction)
        handle_player_movement(forward=False)

def _rotate_player_left():
    """Rotate player to the left"""
    rotation_amount = 15  # Increased from 5 to 15 degrees
    game_state.p_angle = (game_state.p_angle + rotation_amount) % 360

def _rotate_player_right():
    """Rotate player to the right"""
    rotation_amount = 15  # Increased from 5 to 15 degrees
    game_state.p_angle = (game_state.p_angle - rotation_amount) % 360

def _handle_trap_detection(maze, current_time):
    """Handle trap detection and effects"""
    # Only check for traps if not in cheat mode
    if game_state.cheat_mode:
        return
    
    player_row = game_state.p_position[0]
    player_col = game_state.p_position[1]
    current_cell = maze[player_row][player_col]
    
    if current_cell == 8:  # Immobilize trap
        _trigger_immobilize_trap(current_time)
    elif current_cell == 9:  # Deadly trap
        _trigger_deadly_trap()

def _trigger_immobilize_trap(current_time):
    """Trigger immobilization trap effect"""
    game_state.P_Immobilized = True
    game_state.P_Immobilized_T = current_time

def _trigger_deadly_trap():
    """Trigger deadly trap effect"""
    game_state.game_over = True

def _handle_item_keys(key):
    """Handle item selection and interaction keys"""
    # Item Selection
    if key == '5':
        _select_key_item()
    elif key == '6':
        _select_freeze_trap_item()
    elif key == '7':  # Select the cloak
        _select_cloak_item()
    
    # Item interaction
    elif key == 'e' or key == 'E':
        handle_item_interaction()

def _select_key_item():
    """Select key item if available"""
    game_state.act_mode = "key"
    if game_state.k_collect:
        game_state.S_item = "key"

def _select_freeze_trap_item():
    """Select freeze trap item if available"""
    game_state.act_mode = "freeze_trap"
    if game_state.freeze_traps_C > 0:
        game_state.S_item = "freeze_trap"

def _select_cloak_item():
    """Select cloak item if available"""
    game_state.act_mode = "cloak"
    if game_state.clk_collected > 0:
        game_state.S_item = "cloak"

def _handle_camera_keys(key):
    """Handle camera control keys"""
    # Camera zoom
    if key == '+' or key == '=':
        handle_camera_zoom(zoom_in=True)
    elif key == '-' or key == '_':
        handle_camera_zoom(zoom_in=False)
    
    # Camera presets
    elif key == 'r' or key == 'R':
        _set_camera_preset_r()
    elif key == '1':
        _set_camera_preset_1()
    elif key == '2':
        _set_camera_preset_2()
    elif key == '3':
        _set_camera_preset_3()
    elif key == '4':
        _set_camera_preset_4()

def _set_camera_preset_r():
    """Set camera to preset R position"""
    game_state.view_angle = (0, 4800, 4800)
    game_state.cam_point = (0, 0, 0)

def _set_camera_preset_1():
    """Set camera to preset 1 position"""
    game_state.view_angle = (0, 2400, 5200)
    game_state.cam_point = (0, 0, 0)

def _set_camera_preset_2():
    """Set camera to preset 2 position"""
    game_state.view_angle = (5200, 2400, 0)
    game_state.cam_point = (0, 0, 0)

def _set_camera_preset_3():
    """Set camera to preset 3 position"""
    game_state.view_angle = (3600, 3000, 3600)
    game_state.cam_point = (0, 0, 0)

def _set_camera_preset_4():
    """Set camera to preset 4 position"""
    game_state.view_angle = (1800, 5200, 1800)
    game_state.cam_point = (0, 0, 0)

def specialKeyListener(key, x, y):
    """Handle special key input events (arrow keys)"""
    # Determine which arrow key was pressed and handle accordingly
    if key == GLUT_KEY_LEFT:
        _handle_left_arrow_key()
    elif key == GLUT_KEY_RIGHT:
        _handle_right_arrow_key()
    elif key == GLUT_KEY_UP:
        _handle_up_arrow_key()
    elif key == GLUT_KEY_DOWN:
        _handle_down_arrow_key()

def _handle_left_arrow_key():
    """Handle left arrow key press for camera rotation"""
    # Rotate camera left around the center point - smoothed rotation
    rotation_amount = _get_camera_rotation_amount()
    game_state.camera_angle -= rotation_amount
    _update_camera_after_rotation()

def _handle_right_arrow_key():
    """Handle right arrow key press for camera rotation"""
    # Rotate camera right around the center point - smoothed rotation
    rotation_amount = _get_camera_rotation_amount()
    game_state.camera_angle += rotation_amount
    _update_camera_after_rotation()

def _get_camera_rotation_amount():
    """Get the amount to rotate camera for smooth movement"""
    return 0.03  # Smaller angle for smoother rotation

def _update_camera_after_rotation():
    """Update camera position after rotation angle change"""
    updateCameraPosition()

def _handle_up_arrow_key():
    """Handle up arrow key press for camera elevation"""
    # Move camera position up (increase y-coordinate)
    current_coords = _get_current_view_coordinates()
    current_x = current_coords[0]
    current_y = current_coords[1]
    current_z = current_coords[2]
    
    elevation_change = _get_camera_elevation_change()
    new_y = current_y + elevation_change
    
    _set_camera_view_coordinates(current_x, new_y, current_z)

def _handle_down_arrow_key():
    """Handle down arrow key press for camera elevation"""
    # Move camera position down (decrease y-coordinate), with a minimum height
    current_coords = _get_current_view_coordinates()
    current_x = current_coords[0]
    current_y = current_coords[1]
    current_z = current_coords[2]
    
    elevation_change = _get_camera_elevation_change()
    minimum_height = _get_minimum_camera_height()
    new_y = max(minimum_height, current_y - elevation_change)
    
    _set_camera_view_coordinates(current_x, new_y, current_z)

def _get_current_view_coordinates():
    """Get current camera view angle coordinates"""
    current_x = game_state.view_angle[0]
    current_y = game_state.view_angle[1]
    current_z = game_state.view_angle[2]
    return (current_x, current_y, current_z)

def _get_camera_elevation_change():
    """Get the amount to change camera elevation"""
    return 100

def _get_minimum_camera_height():
    """Get the minimum allowed camera height"""
    return 400  # Don't go below height of 400

def _set_camera_view_coordinates(x, y, z):
    """Set new camera view angle coordinates"""
    game_state.view_angle = (x, y, z)

def mouseListener(button, state, x, y):
    """Handle mouse input events"""
    # Convert y coordinate to OpenGL coordinate system
    y = _convert_mouse_y_coordinate(y)
    
    # Determine current game mode and handle accordingly
    if _is_in_menu_mode():
        _handle_menu_mouse_input(button, state, x, y)
    else:
        _handle_game_mouse_input(button, state, x, y)

def _convert_mouse_y_coordinate(y):
    """Convert y coordinate to OpenGL coordinate system"""
    return 800 - y

def _is_in_menu_mode():
    """Check if the game is currently in menu state"""
    return game_state.game_state == "menu"

def _handle_menu_mouse_input(button, state, x, y):
    """Handle mouse input while in menu mode"""
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if game_state.show_instructions:
            _handle_instructions_mouse_input(x, y)
        else:
            _handle_main_menu_mouse_input(x, y)

def _handle_instructions_mouse_input(x, y):
    """Handle mouse input on instructions screen"""
    # Check if back button is clicked
    button_data = _get_back_button_data()
    bx = button_data[0]
    by = button_data[1]
    bw = button_data[2]
    bh = button_data[3]
    
    if _is_mouse_in_button_area(x, y, bx, by, bw, bh):
        game_state.show_instructions = False

def _get_back_button_data():
    """Get back button position and size data"""
    # Coordinates match the back button in menu.py draw_instructions_panel()
    bx = 400
    by = 80
    bw = 200
    bh = 60
    return (bx, by, bw, bh)

def _handle_main_menu_mouse_input(x, y):
    """Handle mouse input on main menu screen"""
    # Check start button
    if _check_start_button_click(x, y):
        return
    
    # Check instructions button
    if _check_instructions_button_click(x, y):
        return
    
    # Check exit button
    if _check_exit_button_click(x, y):
        return

def _check_start_button_click(x, y):
    """Check if start button was clicked"""
    button_rect = MENU_BUTTON_RECT
    bx = button_rect[0]
    by = button_rect[1]
    bw = button_rect[2]
    bh = button_rect[3]
    
    if _is_mouse_in_button_area(x, y, bx, by, bw, bh):
        game_state.game_state = "playing"
        return True
    return False

def _check_instructions_button_click(x, y):
    """Check if instructions button was clicked"""
    button_rect = INSTRUCTIONS_BUTTON_RECT
    bx = button_rect[0]
    by = button_rect[1]
    bw = button_rect[2]
    bh = button_rect[3]
    
    if _is_mouse_in_button_area(x, y, bx, by, bw, bh):
        game_state.show_instructions = True
        return True
    return False

def _check_exit_button_click(x, y):
    """Check if exit button was clicked"""
    button_rect = EXIT_BUTTON_RECT
    bx = button_rect[0]
    by = button_rect[1]
    bw = button_rect[2]
    bh = button_rect[3]
    
    if _is_mouse_in_button_area(x, y, bx, by, bw, bh):
        glutLeaveMainLoop()  # Exit the game
        return True
    return False

def _is_mouse_in_button_area(x, y, bx, by, bw, bh):
    """Check if mouse coordinates are within button boundaries"""
    return (bx <= x <= bx + bw and by <= y <= by + bh)

def _handle_game_mouse_input(button, state, x, y):
    """Handle mouse input while in game mode"""
    if button == GLUT_LEFT_BUTTON:
        _handle_left_mouse_button(state)
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        _handle_right_mouse_button()

def _handle_left_mouse_button(state):
    """Handle left mouse button press and release"""
    if state == GLUT_DOWN:
        _handle_left_mouse_down()
    elif state == GLUT_UP:
        _handle_left_mouse_up()

def _handle_left_mouse_down():
    """Handle left mouse button press"""
    game_state.mouse_left_down = True  # Start continuous shooting
    if not game_state.cheat_mode:
        player_shoot()  # Single shot for non-cheat mode

def _handle_left_mouse_up():
    """Handle left mouse button release"""
    game_state.mouse_left_down = False  # Stop continuous shooting

def _handle_right_mouse_button():
    """Handle right mouse button click to toggle view mode"""
    if game_state.view_mode == "overhead":
        game_state.view_mode = "first_person"
    else:
        game_state.view_mode = "overhead"

def handle_player_movement(forward=True):
    """Handle player movement in forward or backward direction"""
    # Get current position and maze data
    movement_data = _get_movement_data()
    row = movement_data[0]
    col = movement_data[1]
    maze = movement_data[2]
    
    # Calculate movement direction vector
    movement_vector = _calculate_movement_direction(forward)
    dx = movement_vector[0]
    dz = movement_vector[1]
    
    # Normalize the movement vector
    normalized_vector = _normalize_movement_vector(dx, dz)
    dx = normalized_vector[0]
    dz = normalized_vector[1]
    
    # Calculate new position based on movement
    new_position = _calculate_new_position(row, col, dx, dz)
    next_row = new_position[0]
    next_col = new_position[1]
    
    # Validate and apply movement if allowed
    if _is_movement_valid(next_row, next_col, maze):
        _apply_player_movement(next_row, next_col)

def _get_movement_data():
    """Get current player position and maze data for movement calculation"""
    row = game_state.p_position[0]
    col = game_state.p_position[1]
    maze = mazes[game_state.crnt_lev]
    return (row, col, maze)

def _calculate_movement_direction(forward):
    """Calculate movement direction vector based on player angle and direction"""
    angle_rad = math.radians(game_state.p_angle)
    if forward:
        dx = -math.sin(angle_rad)  # X-axis movement
        dz = math.cos(angle_rad)  # Z-axis movement (negative because north is -z)
    else:
        dx = math.sin(angle_rad)  # Reverse X-axis movement
        dz = -math.cos(angle_rad)  # Reverse Z-axis movement
    return (dx, dz)

def _normalize_movement_vector(dx, dz):
    """Normalize the movement vector to unit length"""
    length = math.sqrt(dx * dx + dz * dz)
    if length > 0:
        dx = dx / length
        dz = dz / length
    return (dx, dz)

def _calculate_new_position(row, col, dx, dz):
    """Calculate the potential new position with movement speed applied"""
    next_row = row - int(round(dz * 1.25))  # Movement speed
    next_col = col + int(round(dx * 1.25))  # Movement speed
    return (next_row, next_col)

def _is_movement_valid(next_row, next_col, maze):
    """Check if the proposed movement is valid based on boundaries and walls"""
    # Check boundary conditions
    within_bounds = (0 <= next_row < len(maze) and 0 <= next_col < len(maze[0]))
    
    # Check wall collision (with wall phasing consideration)
    can_pass_through = (game_state.wall_phasing or 
                       maze[next_row][next_col] in [0, 2, 3, 4, 6, 7, 8, 9])
    
    return within_bounds and can_pass_through

def _apply_player_movement(next_row, next_col):
    """Apply the validated movement to player position"""
    game_state.p_position[0] = next_row
    game_state.p_position[1] = next_col

def handle_coin_collection():
    """Handle coin collection logic"""
    # Calculate world coordinate parameters
    world_params = _calculate_coin_world_parameters()
    wall_size = world_params[0]
    offset = world_params[1]
    
    # Get player position in world coordinates
    player_coords = _get_player_world_coordinates(wall_size, offset)
    player_x = player_coords[0]
    player_z = player_coords[1]
    
    # Check each coin for collection
    _process_coin_collection(player_x, player_z, wall_size)

def _calculate_coin_world_parameters():
    """Calculate world coordinate system parameters for coin collection"""
    wall_size = GRID_LENGTH * 2 // 15
    offset = len(mazes[game_state.crnt_lev]) * wall_size // 2
    return (wall_size, offset)

def _get_player_world_coordinates(wall_size, offset):
    """Convert player grid position to world coordinates for coin detection"""
    player_row = game_state.p_position[0]
    player_col = game_state.p_position[1]
    player_x = player_col * wall_size - offset + wall_size / 2
    player_z = player_row * wall_size - offset + wall_size / 2
    return (player_x, player_z)

def _process_coin_collection(player_x, player_z, wall_size):
    """Process coin collection for all coins in current level"""
    coin_index = 0
    while coin_index < len(game_state.coin_pos):
        coin_position = game_state.coin_pos[coin_index]
        coin_x = coin_position[0]
        coin_z = coin_position[1]
        
        # Check if player is close enough to collect coin
        if _is_coin_collectable(player_x, player_z, coin_x, coin_z, wall_size, coin_index):
            _collect_coin(coin_index)
        
        coin_index += 1

def _is_coin_collectable(player_x, player_z, coin_x, coin_z, wall_size, coin_index):
    """Check if a coin can be collected by the player"""
    dist_sq = (player_x - coin_x) ** 2 + (player_z - coin_z) ** 2
    collection_distance = (wall_size / 2.5) ** 2
    is_not_collected = coin_index not in game_state.collected_coins[game_state.crnt_lev]
    return dist_sq < collection_distance and is_not_collected

def _collect_coin(coin_index):
    """Collect a coin and handle bonus rewards"""
    game_state.collected_coins[game_state.crnt_lev].add(coin_index)
    total_collected = sum(len(coins) for coins in game_state.collected_coins)
    
    # Process coin collection bonuses
    _process_coin_bonuses(total_collected)

def _process_coin_bonuses(total_collected):
    """Process bonus rewards for coin collection milestones"""
    # Check for 50 coin bonus
    if total_collected >= 50 and not game_state.fifty_coin_bonus_given:
        _apply_fifty_coin_bonus()
    
    # Check for 100 coin bonus
    if total_collected >= 100 and not game_state.hundred_coin_bonus_given:
        _apply_hundred_coin_bonus()

def _apply_fifty_coin_bonus():
    """Apply the 50 coin collection bonus"""
    game_state.bullet_limit = 30
    game_state.p_health = game_state.p_health + 5
    game_state.fifty_coin_bonus_given = True
    print("Bullet limit increased to 30 and health increased!")

def _apply_hundred_coin_bonus():
    """Apply the 100 coin collection bonus"""
    game_state.bullet_limit = 50
    game_state.p_health = game_state.p_health + 5
    game_state.hundred_coin_bonus_given = True
    print("Bullet limit increased to 50 and health increased!")

def handle_item_interaction():
    """Handle item interaction (E key)"""
    # Get current player position
    position_data = _get_interaction_position_data()
    row = position_data[0]
    col = position_data[1]
    maze = position_data[2]
    
    # Determine interaction type based on maze cell content
    cell_type = maze[row][col]
    
    # Handle different types of interactions
    if cell_type == 4:  # Black cube
        _handle_black_cube_interaction(row, col)
    elif cell_type == 2 and not game_state.k_collect:
        _handle_key_pickup(row, col, maze)
    elif cell_type == 7:
        _handle_cloak_pickup(row, col, maze)
    elif cell_type == 6:
        _handle_freeze_trap_pickup(row, col, maze)
    elif game_state.act_mode == "key" and game_state.k_collect:
        _handle_key_placement(row, col, maze)
    elif game_state.act_mode == "cloak" and game_state.clk_collected > 0 and not game_state.clk_active:
        _handle_cloak_activation(row, col, maze)
    elif game_state.act_mode == "freeze_trap" and game_state.freeze_traps_C > 0:
        _handle_freeze_trap_placement(row, col, maze)

def _get_interaction_position_data():
    """Get player position and maze data for interactions"""
    row = game_state.p_position[0]
    col = game_state.p_position[1]
    maze = mazes[game_state.crnt_lev]
    return (row, col, maze)

def _handle_black_cube_interaction(row, col):
    """Handle interaction with black cube (exit/level progression)"""
    if game_state.crnt_lev == 2 and game_state.k_collect and game_state.S_item == "key":
        _complete_final_level()
    elif game_state.k_collect and game_state.S_item == "key":
        _progress_to_next_level()
    else:
        _display_key_requirement_message()

def _complete_final_level():
    """Complete the final level of the game"""
    print("You have completed the game! Congratulations!")
    game_state.game_over = True

def _progress_to_next_level():
    """Progress to the next level"""
    load_next_level()

def _display_key_requirement_message():
    """Display message about key requirement"""
    print("You need to select and have the key to progress!")

def _handle_key_pickup(row, col, maze):
    """Handle picking up a key from the maze"""
    game_state.k_collect = True
    maze[row][col] = 0  # Remove key from maze
    game_state.S_item = "key"
    game_state.act_mode = "key"

def _handle_cloak_pickup(row, col, maze):
    """Handle picking up a cloak from the maze"""
    game_state.clk_collected += 1
    maze[row][col] = 0  # Remove cloak from maze
    game_state.S_item = "cloak"
    game_state.act_mode = "cloak"

def _handle_freeze_trap_pickup(row, col, maze):
    """Handle picking up a freeze trap from the maze"""
    game_state.freeze_traps_C += 1
    maze[row][col] = 0
    game_state.S_item = "freeze_trap"
    game_state.act_mode = "freeze_trap"

def _handle_key_placement(row, col, maze):
    """Handle placing a key back into the maze"""
    if maze[row][col] == 0:
        game_state.k_collect = False
        maze[row][col] = 2
        game_state.S_item = ""

def _handle_cloak_activation(row, col, maze):
    """Handle activating a cloak item"""
    # Only allow cloak activation if not standing on black cube
    if maze[row][col] != 4:
        _activate_cloak()

def _activate_cloak():
    """Activate the cloak with timing and inventory management"""
    game_state.clk_active = True
    game_state.clk_collected -= 1  # Use up the cloak
    game_state.clk_start_T = get_elapsed_time()  # Start the cloak timer
    if game_state.clk_collected == 0:
        game_state.S_item = "key" if game_state.k_collect else ""

def _handle_freeze_trap_placement(row, col, maze):
    """Handle placing a freeze trap in the maze"""
    if maze[row][col] == 0:
        _place_freeze_trap(row, col)
        _freeze_nearby_enemies(row, col)

def _place_freeze_trap(row, col):
    """Place freeze trap at specified location"""
    game_state.freeze_traps_C -= 1
    game_state.freeze_trap_pos.append([row, col])
    if game_state.freeze_traps_C == 0:
        game_state.S_item = "key" if game_state.k_collect else ""

def _freeze_nearby_enemies(row, col):
    """Freeze enemies within range of the trap"""
    current_time = get_elapsed_time()
    enemy_index = 0
    while enemy_index < len(game_state.enemies):
        enemy = game_state.enemies[enemy_index]
        enemy_row = enemy[0]
        enemy_col = enemy[1]
        
        # Check if enemy is within 2 cells of the trap
        if abs(enemy_row - row) + abs(enemy_col - col) <= 2:
            game_state.ene_freeze_T[enemy_index] = current_time
            print(f"Enemy {enemy_index} frozen at time {current_time}")  # Debug print
        
        enemy_index += 1

def handle_camera_zoom(zoom_in=True):
    """Handle camera zoom in/out"""
    # Calculate direction vector from camera to target
    direction_vector = _calculate_zoom_direction_vector()
    dx = direction_vector[0]
    dy = direction_vector[1]
    dz = direction_vector[2]
    
    # Calculate the magnitude of the direction vector
    length = _calculate_vector_length(dx, dy, dz)
    
    # Apply zoom movement if direction vector is valid
    if length > 0:
        _apply_zoom_movement(dx, dy, dz, length, zoom_in)

def _calculate_zoom_direction_vector():
    """Calculate the direction vector from camera to target point"""
    dx = game_state.cam_point[0] - game_state.view_angle[0]
    dy = game_state.cam_point[1] - game_state.view_angle[1]
    dz = game_state.cam_point[2] - game_state.view_angle[2]
    return (dx, dy, dz)

def _calculate_vector_length(dx, dy, dz):
    """Calculate the length of a 3D vector using distance formula"""
    length = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
    return length

def _apply_zoom_movement(dx, dy, dz, length, zoom_in):
    """Apply zoom movement by normalizing vector and updating camera position"""
    # Normalize the direction vector and scale by zoom step
    dx = dx / length * 100
    dy = dy / length * 100
    dz = dz / length * 100
    
    # Calculate new camera position based on zoom direction
    if zoom_in:
        _move_camera_towards_target(dx, dy, dz)
    else:
        _move_camera_away_from_target(dx, dy, dz)

def _move_camera_towards_target(dx, dy, dz):
    """Move camera closer to the target point"""
    new_x = game_state.view_angle[0] + dx
    new_y = game_state.view_angle[1] + dy
    new_z = game_state.view_angle[2] + dz
    game_state.view_angle = (new_x, new_y, new_z)

def _move_camera_away_from_target(dx, dy, dz):
    """Move camera further from the target point"""
    new_x = game_state.view_angle[0] - dx
    new_y = game_state.view_angle[1] - dy
    new_z = game_state.view_angle[2] - dz
    game_state.view_angle = (new_x, new_y, new_z)

def reset_to_menu():
    """Reset game to menu state"""
    # Set game state to menu mode
    _set_game_to_menu_mode()
    
    # Reset maze data to initial state
    _reset_maze_system()
    
    # Reset player-related state variables
    _reset_player_state()
    
    # Reset item and collection systems
    _reset_item_systems()
    
    # Reset combat and projectile systems
    _reset_combat_systems()
    
    # Initialize game components
    _initialize_game_components()
    
    # Reset game flags and bonuses
    _reset_game_flags()

def _set_game_to_menu_mode():
    """Set the game state to menu mode"""
    game_state.game_state = "menu"

def _reset_maze_system():
    """Reset maze data to initial configuration"""
    from maze_data import mazes
    mazes.clear()
    mazes.extend(get_initial_mazes())

def _reset_player_state():
    """Reset all player-related state variables"""
    # Reset level and position
    game_state.crnt_lev = 0
    game_state.p_position = find_player_start()
    game_state.p_angle = 0.0
    
    # Reset health and hit timing
    game_state.p_health = 10
    game_state.p_last_hit_time = 0
    
    # Reset immobilization state
    game_state.P_Immobilized = False
    game_state.P_Immobilized_T = 0

def _reset_item_systems():
    """Reset item collection and inventory systems"""
    # Reset key collection
    game_state.k_collect = False
    game_state.S_item = "key"
    
    # Reset coin collection system
    from maze_data import mazes
    game_state.collected_coins = [set() for _ in range(len(mazes))]
    
    # Reset freeze trap system
    game_state.freeze_traps_C = 0
    game_state.freeze_trap_pos = []
    
    # Reset cloak system
    game_state.clk_active = False
    game_state.clk_collected = 0

def _reset_combat_systems():
    """Reset combat-related systems and projectiles"""
    # Clear all projectiles
    game_state.enemies = []
    game_state.p_bullets = []
    game_state.bullets = []
    
    # Reset bullet tracking
    game_state.Tracks_bullets = 0

def _initialize_game_components():
    """Initialize game components that need setup"""
    initialize_enemies()
    generate_coin_positions()

def _reset_game_flags():
    """Reset various game flags and bonus states"""
    # Reset game state flags
    game_state.game_over = False
    game_state.wall_phasing = False
    game_state.show_instructions = False
    
    # Reset bonus achievement flags
    game_state.fifty_coin_bonus_given = False
    game_state.hundred_coin_bonus_given = False
