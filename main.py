"""
Main game file as entry point with game loop and initialization
"""
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from config import *
import game_state
from utils import get_elapsed_time, update_delta_time, find_player_start, generate_coin_positions
from enemies import initialize_enemies, update_enemies, draw_enemies
from bullets import update_bullets, draw_bullets
from renderer import draw_text, draw_boundary_walls, draw_maze, draw_freeze_traps, draw_coins
from camera import setupCamera
from input_handler import keyboardListener, specialKeyListener, mouseListener
from menu import draw_menu
from player import draw_player, player_shoot

def idle():
    """Main game loop idle function"""
    # Handle pause state first
    if _is_game_paused():
        _handle_paused_state()
        return
    
    # Update timing systems
    _update_game_timing()
    
    # Get current time for calculations
    current_time = get_elapsed_time()
    
    # Handle time-based game mechanics
    _handle_cloak_deactivation(current_time)
    _handle_immobilization_timeout(current_time)
    _handle_continuous_shooting(current_time)
    
    # Update game systems
    _update_game_systems()
    
    # Request display refresh
    _request_display_update()

def _is_game_paused():
    """Check if the game is currently paused"""
    return game_state.game_paused

def _handle_paused_state():
    """Handle game state when paused"""
    glutPostRedisplay()

def _update_game_timing():
    """Update game timing systems"""
    update_delta_time()

def _handle_cloak_deactivation(current_time):
    """Handle cloak deactivation when not in cheat mode"""
    # Handle cloak deactivation only when not in cheat mode
    if _should_deactivate_cloak(current_time):
        game_state.clk_active = False

def _should_deactivate_cloak(current_time):
    """Check if cloak should be deactivated"""
    is_not_cheat_mode = not game_state.cheat_mode
    is_cloak_active = game_state.clk_active
    cloak_expired = current_time - game_state.clk_start_T > CLOAK_DURATION
    return is_not_cheat_mode and is_cloak_active and cloak_expired

def _handle_immobilization_timeout(current_time):
    """Handle immobilization timeout"""
    if _should_end_immobilization(current_time):
        game_state.P_Immobilized = False

def _should_end_immobilization(current_time):
    """Check if immobilization should end"""
    is_immobilized = game_state.P_Immobilized
    timeout_reached = current_time - game_state.P_Immobilized_T > IMMOBILIZE_DURATION
    return is_immobilized and timeout_reached

def _handle_continuous_shooting(current_time):
    """Handle continuous shooting in cheat mode"""
    if _should_continuous_shoot(current_time):
        player_shoot()

def _should_continuous_shoot(current_time):
    """Check if continuous shooting should occur"""
    in_cheat_mode = game_state.cheat_mode
    mouse_held = game_state.mouse_left_down
    fire_rate_ready = current_time - game_state.P_END_SHOT_T > P_FIRE_INT
    return in_cheat_mode and mouse_held and fire_rate_ready

def _update_game_systems():
    """Update all game systems"""
    update_enemies()  # Update enemy positions and handle shooting
    update_bullets()  # Update bullet positions

def _request_display_update():
    """Request display refresh"""
    glutPostRedisplay()

def showScreen():
    """Main display function"""
    # Handle menu state first
    if _is_in_menu_state():
        _draw_menu_screen()
        return
    
    # Initialize OpenGL display settings
    _initialize_display_settings()
    
    # Draw main floor base
    _draw_main_floor()
    
    # Handle game over state
    if _is_game_over():
        _handle_game_over_display()
        return
    
    # Draw game world elements
    _draw_game_world()
    
    # Finalize display
    _finalize_display()

def _is_in_menu_state():
    """Check if game is in menu state"""
    return game_state.game_state == "menu"

def _draw_menu_screen():
    """Draw the menu screen"""
    draw_menu()

def _initialize_display_settings():
    """Initialize OpenGL display settings"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    _set_viewport_settings()
    setupCamera()

def _set_viewport_settings():
    """Set OpenGL viewport settings"""
    viewport_width = 1000
    viewport_height = 800
    glViewport(0, 0, viewport_width, viewport_height)

def _draw_main_floor():
    """Draw the main floor beneath everything"""
    glBegin(GL_QUADS)
    _set_floor_color()
    _draw_floor_vertices()
    glEnd()

def _set_floor_color():
    """Set the floor color"""
    floor_red = 0.2
    floor_green = 0.45
    floor_blue = 0.3  # More greenish moss green for base floor
    glColor3f(floor_red, floor_green, floor_blue)

def _draw_floor_vertices():
    """Draw floor quad vertices"""
    glVertex3f(-GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, 0, GRID_LENGTH)
    glVertex3f(-GRID_LENGTH, 0, GRID_LENGTH)

def _is_game_over():
    """Check if game is in game over state"""
    return game_state.game_over

def _handle_game_over_display():
    """Handle game over display rendering"""
    if _is_victory_condition():
        _draw_victory_screen()
    else:
        _draw_game_over_screen()
    
    glutSwapBuffers()

def _is_victory_condition():
    """Check if player has won the game"""
    from maze_data import mazes
    is_final_level = game_state.crnt_lev == 2
    player_alive = game_state.p_health > 0
    bullets_within_limit = game_state.Tracks_bullets <= game_state.bullet_limit
    has_key = game_state.k_collect
    
    player_row = game_state.p_position[0]
    player_col = game_state.p_position[1]
    on_exit_tile = mazes[game_state.crnt_lev][player_row][player_col] == 4
    
    return is_final_level and player_alive and bullets_within_limit and has_key and on_exit_tile

def _draw_victory_screen():
    """Draw victory screen messages"""
    draw_text(400, 400, "YOU WIN!", GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text(350, 350, "Congratulations on finishing the game!", GLUT_BITMAP_HELVETICA_18)
    draw_text(350, 300, "Press 'R' to restart", GLUT_BITMAP_HELVETICA_18)

def _draw_game_over_screen():
    """Draw game over screen with fallen player"""
    # Draw player lying down for game over
    player_coords = _calculate_game_over_player_position()
    x = player_coords[0]
    z = player_coords[1]
    
    _draw_fallen_player(x, z)
    _draw_game_over_messages()

def _calculate_game_over_player_position():
    """Calculate player position for game over display"""
    from maze_data import mazes
    wall_size = GRID_LENGTH * 2 // 15
    maze = mazes[game_state.crnt_lev]
    offset = len(maze) * wall_size // 2
    
    row = game_state.p_position[0]
    col = game_state.p_position[1]
    x = col * wall_size - offset + wall_size / 2
    z = row * wall_size - offset + wall_size / 2
    
    return (x, z)

def _draw_fallen_player(x, z):
    """Draw the fallen player model"""
    glPushMatrix()
    fallen_y_position = 10.0
    glTranslatef(x, fallen_y_position, z)
    
    # Rotate to lie down
    rotation_angle = 90
    rotation_x = 1
    rotation_y = 0
    rotation_z = 0
    glRotatef(rotation_angle, rotation_x, rotation_y, rotation_z)
    
    draw_player(0, 0, 0)
    glPopMatrix()

def _draw_game_over_messages():
    """Draw game over text messages"""
    draw_text(400, 400, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text(350, 350, "Press 'R' to restart", GLUT_BITMAP_HELVETICA_18)

def _draw_game_world():
    """Draw all game world elements in order"""
    # Draw boundary walls
    draw_boundary_walls()
    
    # Draw maze walls, floor, key, exit
    draw_maze()
    
    # Draw enemies (separately after the maze)
    draw_enemies()
    draw_bullets()
    
    # Draw coins and freeze traps
    draw_coins()
    draw_freeze_traps()
    
    # Draw UI text
    draw_ui()

def _finalize_display():
    """Finalize display rendering"""
    glutSwapBuffers()

def draw_ui():
    """Draw the game UI text"""
    # Calculate coin statistics
    coin_stats = _calculate_coin_statistics()
    total_coins = coin_stats[0]
    crnt_lev_coins = coin_stats[1]
    total_possible_coins = coin_stats[2]
    
    # Draw basic game statistics
    _draw_basic_game_stats(total_coins, crnt_lev_coins, total_possible_coins)
    
    # Draw boss health if applicable
    _draw_boss_health_if_applicable()
    
    # Draw status messages
    _draw_status_messages()
    
    # Draw item and cheat mode information
    _draw_item_and_cheat_info()
    
    # Draw pause message if paused
    _draw_pause_message_if_paused()

def _calculate_coin_statistics():
    """Calculate coin collection statistics safely"""
    # Calculate total coins safely
    total_coins = _calculate_total_coins()
    
    # Calculate current level coins safely
    crnt_lev_coins = _calculate_current_level_coins()
    
    # Calculate total possible coins safely
    total_possible_coins = _calculate_total_possible_coins()
    
    return (total_coins, crnt_lev_coins, total_possible_coins)

def _calculate_total_coins():
    """Calculate total coins collected across all levels"""
    total_coins = 0
    coin_set_index = 0
    while coin_set_index < len(game_state.collected_coins):
        coins = game_state.collected_coins[coin_set_index]
        if coins is not None:  # Safety check
            total_coins += len(coins)
        coin_set_index += 1
    return total_coins

def _calculate_current_level_coins():
    """Calculate coins collected in current level"""
    crnt_lev_coins = 0
    level_within_bounds = game_state.crnt_lev < len(game_state.collected_coins)
    current_level_coins_exist = (level_within_bounds and 
                               game_state.collected_coins[game_state.crnt_lev] is not None)
    
    if current_level_coins_exist:
        crnt_lev_coins = len(game_state.collected_coins[game_state.crnt_lev])
    
    return crnt_lev_coins

def _calculate_total_possible_coins():
    """Calculate total possible coins in the game"""
    coin_multiplier = 2
    total_possible_coins = NUM_COINS * coin_multiplier if game_state.coin_pos else 0
    return total_possible_coins

def _draw_basic_game_stats(total_coins, crnt_lev_coins, total_possible_coins):
    """Draw basic game statistics text"""
    draw_text(10, 770, f"Level: {game_state.crnt_lev + 1}")
    draw_text(10, 740, f"Health: {game_state.p_health}")
    draw_text(10, 710, f"Coins Collected: {total_coins} / {total_possible_coins}")
    
    level_coin_total = len(game_state.coin_pos) if game_state.coin_pos else 0
    draw_text(10, 680, f"Level Coins: {crnt_lev_coins} / {level_coin_total}")
    
    key_status = 'Yes' if game_state.k_collect else 'No'
    draw_text(10, 650, f"Key Collected: {key_status}")
    draw_text(10, 620, f"Freeze Traps: {game_state.freeze_traps_C}")
    draw_text(10, 590, f"Bullets Used: {game_state.Tracks_bullets} / {game_state.bullet_limit}")

def _draw_boss_health_if_applicable():
    """Draw boss health if in boss level and boss exists"""
    if _should_show_boss_health():
        boss_health = game_state.enemies[0][5]
        draw_text(10, 560, f"Boss Health: {boss_health}")

def _should_show_boss_health():
    """Check if boss health should be displayed"""
    in_boss_level = game_state.crnt_lev == 2
    enemies_exist = game_state.enemies and len(game_state.enemies) > 0
    boss_has_health = enemies_exist and len(game_state.enemies[0]) > 5
    return in_boss_level and boss_has_health

def _draw_status_messages():
    """Draw various status messages"""
    # Draw immobilization status
    if game_state.P_Immobilized:
        _draw_immobilization_status()
    
    # Draw cloak status
    _draw_cloak_status()

def _draw_immobilization_status():
    """Draw immobilization countdown"""
    elapsed_time = get_elapsed_time() - game_state.P_Immobilized_T
    remaining_time = (IMMOBILIZE_DURATION - elapsed_time) // 1000
    draw_text(400, 750, f"IMMOBILIZED! ({remaining_time}s)", GLUT_BITMAP_HELVETICA_18)

def _draw_cloak_status():
    """Draw cloak status information"""
    if game_state.clk_active:
        _draw_active_cloak_status()
    elif game_state.clk_collected > 0:
        _draw_collected_cloak_status()
    else:
        _draw_no_cloak_status()

def _draw_active_cloak_status():
    """Draw status when cloak is active"""
    draw_text(10, 530, "Cloak Active: Yes")
    if not game_state.cheat_mode:
        elapsed_cloak_time = get_elapsed_time() - game_state.clk_start_T
        remaining_time = (CLOAK_DURATION - elapsed_cloak_time) // 1000
        draw_text(10, 500, f"Cloak Duration: {remaining_time}s")

def _draw_collected_cloak_status():
    """Draw status when cloak is collected but not active"""
    draw_text(10, 530, f"Cloak Collected: {game_state.clk_collected}")

def _draw_no_cloak_status():
    """Draw status when no cloak is available"""
    draw_text(10, 530, "Cloak Collected: No")

def _draw_item_and_cheat_info():
    """Draw selected item and cheat mode information"""
    # Selected item status
    if game_state.S_item:
        draw_text(10, 470, f"Selected Item: {game_state.S_item}")
    else:
        draw_text(10, 470, "No item selected")
    
    # Cheat mode status
    if game_state.cheat_mode:
        _draw_cheat_mode_status()

def _draw_cheat_mode_status():
    """Draw cheat mode status information"""
    draw_text(10, 440, "CHEAT MODE ACTIVE", GLUT_BITMAP_HELVETICA_18)
    if game_state.wall_phasing:
        draw_text(10, 410, "WALL PHASING ACTIVE", GLUT_BITMAP_HELVETICA_18)

def _draw_pause_message_if_paused():
    """Draw pause message if game is paused"""
    if game_state.game_paused:
        draw_text(400, 400, "GAME PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(350, 350, "Press SPACE to continue", GLUT_BITMAP_HELVETICA_18)

def main():
    """Main function to initialize and start the game"""
    # Initialize OpenGL and create window
    _initialize_opengl_system()
    
    # Configure OpenGL settings
    _configure_opengl_settings()
    
    # Initialize game state and components
    _initialize_game_state()
    
    # Set up callback functions
    _setup_callback_functions()
    
    # Start the main game loop
    _start_main_loop()

def _initialize_opengl_system():
    """Initialize OpenGL system and create window"""
    glutInit()
    _set_display_mode()
    _create_game_window()

def _set_display_mode():
    """Set OpenGL display mode"""
    display_flags = GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH
    glutInitDisplayMode(display_flags)

def _create_game_window():
    """Create the game window with specified dimensions"""
    window_width = 1000
    window_height = 800
    window_x = 0
    window_y = 0
    window_title = b"3D Maze Escape: Hunter's Chase"
    
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(window_x, window_y)
    glutCreateWindow(window_title)

def _configure_opengl_settings():
    """Configure OpenGL rendering settings"""
    # Enhanced depth testing settings
    _enable_depth_testing()
    _set_background_color()

def _enable_depth_testing():
    """Enable and configure depth testing"""
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    depth_clear_value = 1.0
    glClearDepth(depth_clear_value)

def _set_background_color():
    """Set the background color for better contrast"""
    bg_red = 0.2
    bg_green = 0.25
    bg_blue = 0.35  # Soft slate blue background
    bg_alpha = 1.0
    glClearColor(bg_red, bg_green, bg_blue, bg_alpha)

def _initialize_game_state():
    """Initialize game state and components"""
    # Set initial game state
    game_state.game_state = "menu"
    game_state.p_position = find_player_start()
    
    # Initialize game components
    _initialize_game_components()

def _initialize_game_components():
    """Initialize various game components"""
    initialize_enemies()
    generate_coin_positions()

def _setup_callback_functions():
    """Set up all GLUT callback functions"""
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

def _start_main_loop():
    """Start the main GLUT loop"""
    glutMainLoop()

if __name__ == "__main__":
    main()
