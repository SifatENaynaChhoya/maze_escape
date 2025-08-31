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
    key = key.decode('utf-8') if isinstance(key, bytes) else chr(key)

    # Handle ESC key to return to menu
    if key == '\x1b':  # ESC key
        reset_to_menu()
        return

    # Add pause toggle with space bar
    if key == ' ':
        game_state.game_paused = not game_state.game_paused
        return

    # Don't process other keys if game is paused (except for unpausing)
    if game_state.game_paused:
        return

    if game_state.game_over and (key == 'r' or key == 'R'):
        reset_to_menu()
        return

    if game_state.game_over:
        return

    current_time = get_elapsed_time()
    if game_state.P_Immobilized:
        if current_time - game_state.P_Immobilized_T > IMMOBILIZE_DURATION:
            game_state.P_Immobilized = False  # Player is free
        else:
            if key in ['+', '=', '-', '_', 'r', 'R', '1', '2', '3', '4']:
                pass
            else:
                return

    row, col = game_state.p_position
    maze = mazes[game_state.crnt_lev]
    
    # Handle cheat mode toggle
    if key == 'c' or key == 'C':
        game_state.cheat_mode = not game_state.cheat_mode
        game_state.wall_phasing = False  # Reset wall phasing when toggling cheat mode
        if game_state.cheat_mode:
            game_state.Bullet_S = game_state.original_Bullet_S * 2  # Double bullet speed in cheat mode
        else:
            game_state.Bullet_S = game_state.original_Bullet_S  # Reset to original speed when cheat mode is off
            # Reset cloak timer when cheat mode is turned off
            if game_state.clk_active:
                game_state.clk_start_T = get_elapsed_time()  # Reset to current time to start normal duration
            current_time = get_elapsed_time()
            for i in range(len(game_state.ene_freeze_T)):
                if game_state.ene_freeze_T[i] > 0:
                    if current_time - game_state.ene_freeze_T[i] < FREEZE_DURATION:
                        # Keep the enemy frozen with the current elapsed time preserved
                        pass
                    else:
                        # Enemy has been frozen longer than the freeze duration, so unfreeze it
                        game_state.ene_freeze_T[i] = 0
        print(f"Cheat mode {'activated' if game_state.cheat_mode else 'deactivated'}")
        return

    # Handle wall phasing toggle
    if key == 'v' or key == 'V':
        if game_state.cheat_mode:  # Only allow wall phasing in cheat mode
            game_state.wall_phasing = not game_state.wall_phasing
            print(f"Wall phasing {'activated' if game_state.wall_phasing else 'deactivated'}")
        return

    # --- Rotation ---
    if key == 'a' or key == 'A':  # Rotate left
        game_state.p_angle = (game_state.p_angle + 15) % 360  # Increased from 5 to 15 degrees
    elif key == 'd' or key == 'D':  # Rotate right
        game_state.p_angle = (game_state.p_angle - 15) % 360  # Increased from 5 to 15 degrees

    # --- Movement ---
    if key == 'w' or key == 'W':  # Forward in facing direction
        handle_player_movement(forward=True)
    elif key == 's' or key == 'S':  # Backward (opposite of facing direction)
        handle_player_movement(forward=False)

    # Only check for traps if not in cheat mode
    if not game_state.cheat_mode:
        if maze[game_state.p_position[0]][game_state.p_position[1]] == 8:  # Immobilize trap
            game_state.P_Immobilized = True
            game_state.P_Immobilized_T = current_time
        elif maze[game_state.p_position[0]][game_state.p_position[1]] == 9:  # Deadly trap
            game_state.game_over = True

    # Handle coin collection
    handle_coin_collection()

    # --- Item Selection and Actions ---
    if key == '5':
        game_state.act_mode = "key"
        if game_state.k_collect:
            game_state.S_item = "key"
    elif key == '6':
        game_state.act_mode = "freeze_trap"
        if game_state.freeze_traps_C > 0:
            game_state.S_item = "freeze_trap"
    elif key == '7':  # Select the cloak
        game_state.act_mode = "cloak"
        if game_state.clk_collected > 0:
            game_state.S_item = "cloak"

    # --- Item Collection and Actions ---
    if key == 'e' or key == 'E':
        handle_item_interaction()

    # --- Camera Zoom In/Out ---
    if key == '+' or key == '=':
        handle_camera_zoom(zoom_in=True)
    elif key == '-' or key == '_':
        handle_camera_zoom(zoom_in=False)

    # --- Camera Presets ---
    if key == 'r' or key == 'R':
        game_state.view_angle = (0, 4800, 4800)
        game_state.cam_point = (0, 0, 0)
    elif key == '1':
        game_state.view_angle = (0, 2400, 5200)
        game_state.cam_point = (0, 0, 0)
    elif key == '2':
        game_state.view_angle = (5200, 2400, 0)
        game_state.cam_point = (0, 0, 0)
    elif key == '3':
        game_state.view_angle = (3600, 3000, 3600)
        game_state.cam_point = (0, 0, 0)
    elif key == '4':
        game_state.view_angle = (1800, 5200, 1800)
        game_state.cam_point = (0, 0, 0)

def specialKeyListener(key, x, y):
    """Handle special key input events (arrow keys)"""
    # Arrow keys control camera rotation (left/right) and elevation (up/down)
    if key == GLUT_KEY_LEFT:
        # Rotate camera left around the center point - smoothed rotation
        game_state.camera_angle -= 0.03  # Smaller angle for smoother rotation
        updateCameraPosition()

    if key == GLUT_KEY_RIGHT:
        # Rotate camera right around the center point - smoothed rotation
        game_state.camera_angle += 0.03  # Smaller angle for smoother rotation
        updateCameraPosition()

    if key == GLUT_KEY_UP:
        # Move camera position up (increase y-coordinate)
        game_state.view_angle = (game_state.view_angle[0], game_state.view_angle[1] + 100, game_state.view_angle[2])

    if key == GLUT_KEY_DOWN:
        # Move camera position down (decrease y-coordinate), with a minimum height
        new_y = max(400, game_state.view_angle[1] - 100)  # Don't go below height of 400
        game_state.view_angle = (game_state.view_angle[0], new_y, game_state.view_angle[2])

def mouseListener(button, state, x, y):
    """Handle mouse input events"""
    # Convert y coordinate to OpenGL coordinate system
    y = 800 - y
    
    if game_state.game_state == "menu":
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            if game_state.show_instructions:
                # Check if back button is clicked
                bx, by = 400, 150
                bw, bh = 200, 50
                if (bx <= x <= bx + bw and by <= y <= by + bh):
                    game_state.show_instructions = False
                    return
            else:
                # Check if start button is clicked
                bx, by, bw, bh = MENU_BUTTON_RECT
                if (bx <= x <= bx + bw and by <= y <= by + bh):
                    game_state.game_state = "playing"
                    return
                
                # Check if instructions button is clicked
                bx, by, bw, bh = INSTRUCTIONS_BUTTON_RECT
                if (bx <= x <= bx + bw and by <= y <= by + bh):
                    game_state.show_instructions = True
                    return
                
                # Check if exit button is clicked
                bx, by, bw, bh = EXIT_BUTTON_RECT
                if (bx <= x <= bx + bw and by <= y <= by + bh):
                    glutLeaveMainLoop()  # Exit the game
                    return
        return
    
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            game_state.mouse_left_down = True  # Start continuous shooting
            if not game_state.cheat_mode:
                player_shoot()  # Single shot for non-cheat mode
        elif state == GLUT_UP:
            game_state.mouse_left_down = False  # Stop continuous shooting

    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # Toggle view mode
        game_state.view_mode = "first_person" if game_state.view_mode == "overhead" else "overhead"

def handle_player_movement(forward=True):
    """Handle player movement in forward or backward direction"""
    row, col = game_state.p_position
    maze = mazes[game_state.crnt_lev]
    
    # Calculate movement direction
    angle_rad = math.radians(game_state.p_angle)
    if forward:
        dx = -math.sin(angle_rad)  # X-axis movement
        dz = math.cos(angle_rad)  # Z-axis movement (negative because north is -z)
    else:
        dx = math.sin(angle_rad)  # Reverse X-axis movement
        dz = -math.cos(angle_rad)  # Reverse Z-axis movement

    # Normalize the movement vector
    length = math.sqrt(dx * dx + dz * dz)
    if length > 0:
        dx = dx / length
        dz = dz / length

    # Calculate the potential new position with normalized movement
    next_row = row - int(round(dz * 1.25))  # Movement speed
    next_col = col + int(round(dx * 1.25))  # Movement speed

    # Check if movement is valid
    # Even in wall phasing mode, don't allow going through boundary walls
    if (0 <= next_row < len(maze) and 0 <= next_col < len(maze[0]) and
        (game_state.wall_phasing or maze[next_row][next_col] in [0, 2, 3, 4, 6, 7, 8, 9])):
        game_state.p_position[0], game_state.p_position[1] = next_row, next_col

def handle_coin_collection():
    """Handle coin collection logic"""
    wall_size = GRID_LENGTH * 2 // 15
    offset = len(mazes[game_state.crnt_lev]) * wall_size // 2
    player_row, player_col = game_state.p_position
    player_x = player_col * wall_size - offset + wall_size / 2
    player_z = player_row * wall_size - offset + wall_size / 2

    for i, (coin_x, coin_z) in enumerate(game_state.coin_pos):
        dist_sq = (player_x - coin_x) ** 2 + (player_z - coin_z) ** 2
        if dist_sq < (wall_size / 2.5) ** 2 and i not in game_state.collected_coins[game_state.crnt_lev]:
            game_state.collected_coins[game_state.crnt_lev].add(i)
            total_collected = sum(len(coins) for coins in game_state.collected_coins)
            
            # Check for 50 coin bonus
            if total_collected >= 50 and not game_state.fifty_coin_bonus_given:
                game_state.bullet_limit = 30
                game_state.p_health = game_state.p_health + 5
                game_state.fifty_coin_bonus_given = True
                print("Bullet limit increased to 30 and health increased!")
            
            # Check for 100 coin bonus
            if total_collected >= 100 and not game_state.hundred_coin_bonus_given:
                game_state.bullet_limit = 50
                game_state.p_health = game_state.p_health + 5
                game_state.hundred_coin_bonus_given = True
                print("Bullet limit increased to 50 and health increased!")

def handle_item_interaction():
    """Handle item interaction (E key)"""
    row, col = game_state.p_position
    maze = mazes[game_state.crnt_lev]
    
    if maze[row][col] == 4:  # Black cube
        if game_state.crnt_lev == 2 and game_state.k_collect and game_state.S_item == "key":
            print("You have completed the game! Congratulations!")
            game_state.game_over = True
        elif game_state.k_collect and game_state.S_item == "key":
            load_next_level()
        else:
            print("You need to select and have the key to progress!")
    elif maze[row][col] == 2 and not game_state.k_collect:
        game_state.k_collect = True
        maze[row][col] = 0  # Remove key from maze
        game_state.S_item = "key"
        game_state.act_mode = "key"
    elif maze[row][col] == 7:
        game_state.clk_collected += 1
        maze[row][col] = 0  # Remove cloak from maze
        game_state.S_item = "cloak"
        game_state.act_mode = "cloak"
    elif maze[row][col] == 6:
        game_state.freeze_traps_C += 1
        maze[row][col] = 0
        game_state.S_item = "freeze_trap"
        game_state.act_mode = "freeze_trap"
    elif game_state.act_mode == "key" and game_state.k_collect:
        if maze[row][col] == 0:
            game_state.k_collect = False
            maze[row][col] = 2
            game_state.S_item = ""
    elif game_state.act_mode == "cloak" and game_state.clk_collected > 0 and not game_state.clk_active:
        # Only allow cloak activation if not standing on black cube
        if maze[row][col] != 4:
            game_state.clk_active = True
            game_state.clk_collected -= 1  # Use up the cloak
            game_state.clk_start_T = get_elapsed_time()  # Start the cloak timer
            if game_state.clk_collected == 0:
                game_state.S_item = "key" if game_state.k_collect else ""
    elif game_state.act_mode == "freeze_trap" and game_state.freeze_traps_C > 0:
        if maze[row][col] == 0:
            game_state.freeze_traps_C -= 1
            game_state.freeze_trap_pos.append([row, col])
            if game_state.freeze_traps_C == 0:
                game_state.S_item = "key" if game_state.k_collect else ""

            current_time = get_elapsed_time()
            for i, enemy in enumerate(game_state.enemies):
                enemy_row, enemy_col = enemy[0], enemy[1]
                # Check if enemy is within 2 cells of the trap
                if abs(enemy_row - row) + abs(enemy_col - col) <= 2:
                    game_state.ene_freeze_T[i] = current_time
                    print(f"Enemy {i} frozen at time {current_time}")  # Debug print

def handle_camera_zoom(zoom_in=True):
    """Handle camera zoom in/out"""
    dx = game_state.cam_point[0] - game_state.view_angle[0]
    dy = game_state.cam_point[1] - game_state.view_angle[1]
    dz = game_state.cam_point[2] - game_state.view_angle[2]
    length = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
    if length > 0:
        dx, dy, dz = dx / length * 100, dy / length * 100, dz / length * 100
        if zoom_in:
            game_state.view_angle = (game_state.view_angle[0] + dx, game_state.view_angle[1] + dy, game_state.view_angle[2] + dz)
        else:
            game_state.view_angle = (game_state.view_angle[0] - dx, game_state.view_angle[1] - dy, game_state.view_angle[2] - dz)

def reset_to_menu():
    """Reset game to menu state"""
    game_state.game_state = "menu"
    from maze_data import mazes
    mazes.clear()
    mazes.extend(get_initial_mazes())
    
    game_state.crnt_lev = 0
    game_state.p_position = find_player_start()
    game_state.p_angle = 0.0
    game_state.p_health = 10
    game_state.p_last_hit_time = 0
    game_state.P_Immobilized = False
    game_state.P_Immobilized_T = 0
    game_state.k_collect = False
    game_state.collected_coins = [set() for _ in range(len(mazes))]
    game_state.freeze_traps_C = 0
    game_state.freeze_trap_pos = []
    game_state.S_item = "key"
    game_state.enemies = []
    game_state.p_bullets = []
    game_state.bullets = []
    game_state.Tracks_bullets = 0
    initialize_enemies()
    generate_coin_positions()
    game_state.game_over = False
    game_state.wall_phasing = False
    game_state.clk_active = False
    game_state.clk_collected = 0
    game_state.show_instructions = False
    game_state.fifty_coin_bonus_given = False
    game_state.hundred_coin_bonus_given = False
