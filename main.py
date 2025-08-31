"""
Main game file as entry point with game loop and initialization
"""
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from config import *
import game_state
import math
import time
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
    # Check for victory condition first
    if hasattr(game_state, 'victory') and game_state.victory or _is_victory_condition():
        _draw_victory_screen()
    else:
        _draw_game_over_screen()
    
    glutSwapBuffers()

def _is_victory_condition():
    """Check if player has won the game by either reaching the exit or defeating all enemies in final level"""
    # If victory flag is already set, return True
    if hasattr(game_state, 'victory') and game_state.victory:
        return True
        
    from maze_data import mazes
    
    # Only check for victory in the final level (level 2, 0-indexed)
    is_final_level = game_state.crnt_lev == 2
    if not is_final_level:
        return False
        
    player_alive = game_state.p_health > 0
    bullets_within_limit = game_state.cheat_mode or game_state.Tracks_bullets <= game_state.bullet_limit  # Allow cheat mode bypass
    has_key = game_state.k_collect
    
    # Check if all enemies are defeated (boss killed)
    all_enemies_defeated = len(game_state.enemies) == 0
    
    # Check if player is on exit tile
    player_row = game_state.p_position[0]
    player_col = game_state.p_position[1]
    on_exit_tile = mazes[game_state.crnt_lev][player_row][player_col] == 4
    
    # Update victory state if conditions are met (either boss killed OR on exit with key)
    if player_alive and bullets_within_limit and (all_enemies_defeated or (has_key and on_exit_tile)):
        if not hasattr(game_state, 'victory'):
            game_state.victory = True
        game_state.victory = True
        game_state.game_over = True  # Ensure game over state is set
        return True
    
    return False

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
    """Draw enhanced game statistics with colorful HUD and warnings"""
    # Draw HUD background panel
    _draw_hud_background_panel()
    
    # Enhanced level display
    _draw_enhanced_level_display()
    
    # Enhanced health display with warnings
    _draw_enhanced_health_display()
    
    # Enhanced bullet counter with threshold warnings
    _draw_enhanced_bullet_display()
    
    # Enhanced coin displays
    _draw_enhanced_coin_displays(total_coins, crnt_lev_coins, total_possible_coins)
    
    # Enhanced key and item displays
    _draw_enhanced_key_and_items_display()

def _draw_hud_background_panel():
    """Draw a semi-transparent background panel for the HUD"""
    # Setup for 2D rendering
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Enable blending for transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Draw main HUD panel background
    glColor4f(0.05, 0.05, 0.15, 0.8)  # Dark blue with transparency
    glBegin(GL_QUADS)
    glVertex2f(5, 580)
    glVertex2f(350, 580)
    glVertex2f(350, 785)
    glVertex2f(5, 785)
    glEnd()
    
    # Draw HUD border with gradient effect
    current_time = time.time()
    border_pulse = 0.5 + 0.2 * math.sin(current_time * 2)
    glColor3f(0.3 * border_pulse, 0.6 * border_pulse, 0.9 * border_pulse)
    glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    glVertex2f(5, 580)
    glVertex2f(350, 580)
    glVertex2f(350, 785)
    glVertex2f(5, 785)
    glEnd()
    glLineWidth(1)
    
    glDisable(GL_BLEND)
    
    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def _draw_enhanced_level_display():
    """Draw enhanced level display with progress indicators"""
    level_num = game_state.crnt_lev + 1
    total_levels = 3  # Assuming 3 levels total
    
    # Level title with icon
    glColor3f(0.4, 0.8, 1.0)  # Bright cyan
    draw_text(15, 770, f"🏆 LEVEL {level_num} / {total_levels}", GLUT_BITMAP_HELVETICA_18)
    
    # Draw level progress bar
    _draw_level_progress_bar(level_num, total_levels)

def _draw_level_progress_bar(current_level, total_levels):
    """Draw a visual progress bar for level completion"""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Progress bar background
    glColor3f(0.2, 0.2, 0.3)
    glBegin(GL_QUADS)
    glVertex2f(200, 770)
    glVertex2f(330, 770)
    glVertex2f(330, 780)
    glVertex2f(200, 780)
    glEnd()
    
    # Progress bar fill
    progress = current_level / total_levels
    fill_width = 130 * progress
    glColor3f(0.2, 0.9, 0.4)  # Bright green
    glBegin(GL_QUADS)
    glVertex2f(200, 770)
    glVertex2f(200 + fill_width, 770)
    glVertex2f(200 + fill_width, 780)
    glVertex2f(200, 780)
    glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def _draw_enhanced_health_display():
    """Draw enhanced health display with color-coded warnings"""
    health = game_state.p_health
    max_health = INITIAL_PLAYER_HEALTH  # Use actual starting health as maximum
    health_percentage = health / max_health
    
    # Determine health status and color
    if health_percentage > 0.6:
        health_color = (0.2, 0.9, 0.3)  # Healthy green
        health_icon = "💚"
        status_text = ""
    elif health_percentage > 0.3:
        health_color = (0.9, 0.7, 0.2)  # Warning yellow
        health_icon = "💛"
        status_text = " ⚠️ LOW HEALTH!"
    else:
        # Critical health - flashing red
        current_time = time.time()
        flash_intensity = 0.5 + 0.5 * math.sin(current_time * 8)  # Fast flashing
        health_color = (0.9 + 0.1 * flash_intensity, 0.1, 0.1)
        health_icon = "💔"
        status_text = " 🚨 CRITICAL!"
    
    # Draw health text with appropriate color
    glColor3f(*health_color)
    draw_text(15, 740, f"{health_icon} Health: {health}/{max_health}{status_text}", GLUT_BITMAP_HELVETICA_18)
    
    # Draw health bar
    _draw_health_bar(health, max_health, health_color)

def _draw_health_bar(current_health, max_health, health_color):
    """Draw a visual health bar"""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    bar_x, bar_y = 15, 720
    bar_width, bar_height = 200, 12
    
    # Health bar background
    glColor3f(0.3, 0.1, 0.1)  # Dark red background
    glBegin(GL_QUADS)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + bar_width, bar_y)
    glVertex2f(bar_x + bar_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()
    
    # Health bar fill
    health_ratio = current_health / max_health
    fill_width = bar_width * health_ratio
    glColor3f(*health_color)
    glBegin(GL_QUADS)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + fill_width, bar_y)
    glVertex2f(bar_x + fill_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()
    
    # Health bar border
    glColor3f(0.8, 0.8, 0.8)
    glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + bar_width, bar_y)
    glVertex2f(bar_x + bar_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()
    glLineWidth(1)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def _draw_enhanced_bullet_display():
    """Draw enhanced bullet counter with threshold warnings and death warning"""
    bullets_used = game_state.Tracks_bullets
    bullet_limit = game_state.bullet_limit
    
    # Check if cheat mode is active
    if game_state.cheat_mode:
        # Show unlimited ammo display with special styling
        current_time = time.time()
        rainbow_r = 0.5 + 0.5 * math.sin(current_time * 2)
        rainbow_g = 0.5 + 0.5 * math.sin(current_time * 2 + 2)
        rainbow_b = 0.5 + 0.5 * math.sin(current_time * 2 + 4)
        bullet_color = (rainbow_r, rainbow_g, rainbow_b)  # Rainbow effect
        bullet_icon = "♾️"
        warning_text = " UNLIMITED!"
        
        # Draw bullets text with rainbow color
        glColor3f(*bullet_color)
        draw_text(15, 690, f"{bullet_icon} Ammo: UNLIMITED{warning_text}", GLUT_BITMAP_HELVETICA_18)
        
        # Skip the progress bar and usage stats in cheat mode
        glColor3f(0.8, 0.8, 0.2)  # Gold color
        draw_text(15, 670, f"💥 CHEAT MODE: Infinite Ammo Active", GLUT_BITMAP_HELVETICA_12)
        return
    
    # Normal ammo display (non-cheat mode)
    bullets_remaining = bullet_limit - bullets_used
    usage_percentage = bullets_used / bullet_limit
    
    # Determine bullet status and color
    if usage_percentage < 0.7:
        bullet_color = (0.3, 0.9, 0.5)  # Safe green
        bullet_icon = "🔫"
        warning_text = ""
    elif usage_percentage < 0.9:
        bullet_color = (0.9, 0.7, 0.2)  # Warning yellow
        bullet_icon = "⚠️"
        warning_text = " AMMO LOW!"
    else:
        # Critical/Death threshold - flashing red
        current_time = time.time()
        flash_intensity = 0.5 + 0.5 * math.sin(current_time * 10)  # Very fast flashing
        bullet_color = (0.9 + 0.1 * flash_intensity, 0.1, 0.1)
        bullet_icon = "💀"
        if bullets_remaining == 0:
            warning_text = " DEAD - NO AMMO!"
        else:
            warning_text = f" DEATH IN {bullets_remaining}!"
    
    # Draw bullets text with appropriate color
    glColor3f(*bullet_color)
    draw_text(15, 690, f"{bullet_icon} Ammo: {bullets_remaining}/{bullet_limit}{warning_text}", GLUT_BITMAP_HELVETICA_18)
    
    # Draw bullet threshold indicator
    _draw_bullet_threshold_indicator(bullets_used, bullet_limit)
    
    # Show exact bullet usage
    glColor3f(0.7, 0.7, 0.9)  # Light blue-gray
    draw_text(15, 670, f"📊 Used: {bullets_used} | Limit: {bullet_limit}", GLUT_BITMAP_HELVETICA_12)

def _draw_bullet_threshold_indicator(bullets_used, bullet_limit):
    """Draw a visual indicator showing bullet usage and death threshold"""
    # Skip drawing progress bar in cheat mode
    if game_state.cheat_mode:
        return
        
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    bar_x, bar_y = 15, 650
    bar_width, bar_height = 200, 12
    usage_ratio = bullets_used / bullet_limit
    
    # Bullet usage bar background
    glColor3f(0.1, 0.3, 0.1)  # Dark green background
    glBegin(GL_QUADS)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + bar_width, bar_y)
    glVertex2f(bar_x + bar_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()
    
    # Draw usage fill with gradient colors
    fill_width = bar_width * usage_ratio
    if usage_ratio < 0.7:
        glColor3f(0.2, 0.8, 0.3)  # Green zone
    elif usage_ratio < 0.9:
        glColor3f(0.9, 0.7, 0.2)  # Yellow warning zone
    else:
        # Red danger zone with flashing
        current_time = time.time()
        flash = 0.7 + 0.3 * math.sin(current_time * 12)
        glColor3f(0.9 * flash, 0.1, 0.1)
    
    glBegin(GL_QUADS)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + fill_width, bar_y)
    glVertex2f(bar_x + fill_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()
    
    # Draw death threshold marker (90% mark)
    death_threshold_x = bar_x + (bar_width * 0.9)
    glColor3f(1.0, 0.2, 0.2)  # Bright red
    glLineWidth(3)
    glBegin(GL_LINES)
    glVertex2f(death_threshold_x, bar_y - 3)
    glVertex2f(death_threshold_x, bar_y + bar_height + 3)
    glEnd()
    glLineWidth(1)
    
    # Draw bar border
    glColor3f(0.8, 0.8, 0.8)
    glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + bar_width, bar_y)
    glVertex2f(bar_x + bar_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()
    glLineWidth(1)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def _draw_enhanced_coin_displays(total_coins, crnt_lev_coins, total_possible_coins):
    """Draw enhanced coin collection displays with progress bars"""
    level_coin_total = len(game_state.coin_pos) if game_state.coin_pos else 0
    
    # Total coins with treasure chest icon
    total_coin_ratio = total_coins / total_possible_coins if total_possible_coins > 0 else 0
    if total_coin_ratio > 0.8:
        coin_color = (1.0, 0.8, 0.2)  # Gold
        coin_icon = "💰"
    elif total_coin_ratio > 0.5:
        coin_color = (0.8, 0.8, 0.2)  # Yellow
        coin_icon = "🪙"
    else:
        coin_color = (0.6, 0.6, 0.6)  # Gray
        coin_icon = "🔘"
    
    glColor3f(*coin_color)
    draw_text(15, 620, f"{coin_icon} Total Coins: {total_coins}/{total_possible_coins}", GLUT_BITMAP_HELVETICA_18)
    
    # Level coins with completion percentage
    level_coin_ratio = crnt_lev_coins / level_coin_total if level_coin_total > 0 else 0
    level_percentage = int(level_coin_ratio * 100)
    
    if level_coin_ratio == 1.0:
        level_coin_color = (0.2, 1.0, 0.3)  # Bright green for completion
        level_icon = "✅"
    elif level_coin_ratio > 0.5:
        level_coin_color = (0.9, 0.7, 0.2)  # Yellow for progress
        level_icon = "🟡"
    else:
        level_coin_color = (0.8, 0.5, 0.2)  # Orange for low progress
        level_icon = "🟠"
    
    glColor3f(*level_coin_color)
    draw_text(15, 600, f"{level_icon} Stage Coins: {crnt_lev_coins}/{level_coin_total} ({level_percentage}%)", GLUT_BITMAP_HELVETICA_18)

def _draw_enhanced_key_and_items_display():
    """Draw enhanced key and items display with better visual feedback"""
    # Key status with lock/unlock icons
    if game_state.k_collect:
        key_color = (0.3, 0.9, 0.3)  # Bright green
        key_icon = "🔓"
        key_status = "COLLECTED"
    else:
        # Flashing orange for missing key
        current_time = time.time()
        flash = 0.7 + 0.3 * math.sin(current_time * 4)
        key_color = (0.9 * flash, 0.5 * flash, 0.1)
        key_icon = "🔒"
        key_status = "MISSING"
    
    glColor3f(*key_color)
    draw_text(15, 580, f"{key_icon} Key: {key_status}", GLUT_BITMAP_HELVETICA_18)
    
    # Freeze traps with ice icon
    if game_state.freeze_traps_C > 0:
        freeze_color = (0.4, 0.9, 0.9)  # Cyan
        freeze_icon = "❄️"
    else:
        freeze_color = (0.5, 0.5, 0.7)  # Gray
        freeze_icon = "🚫"
    
    glColor3f(*freeze_color)
    draw_text(200, 580, f"{freeze_icon} Freeze Traps: {game_state.freeze_traps_C}", GLUT_BITMAP_HELVETICA_18)

def _draw_boss_health_if_applicable():
    """Draw enhanced boss health display with dramatic effects"""
    if _should_show_boss_health():
        boss_health = game_state.enemies[0][5]
        max_boss_health = 10  # Assuming max boss health
        
        # Calculate boss health status
        boss_health_ratio = boss_health / max_boss_health
        current_time = time.time()
        
        # Determine boss health color and effects
        if boss_health_ratio > 0.7:
            boss_color = (0.8, 0.2, 0.2)  # Menacing red
            boss_icon = "👹"
            status_text = " STRONG"
        elif boss_health_ratio > 0.3:
            boss_color = (0.9, 0.5, 0.2)  # Orange warning
            boss_icon = "😠"
            status_text = " WEAKENING"
        else:
            # Critical boss health - flashing
            flash = 0.6 + 0.4 * math.sin(current_time * 6)
            boss_color = (0.9 * flash, 0.1, 0.9 * flash)  # Flashing purple
            boss_icon = "💀"
            status_text = " CRITICAL!"
        
        # Draw boss health with dramatic styling
        glColor3f(*boss_color)
        draw_text(10, 560, f"{boss_icon} BOSS: {boss_health}/{max_boss_health}{status_text}", GLUT_BITMAP_HELVETICA_18)
        
        # Draw boss health bar
        _draw_boss_health_bar(boss_health, max_boss_health, boss_color)

def _draw_boss_health_bar(current_health, max_health, boss_color):
    """Draw a dramatic boss health bar"""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    bar_x, bar_y = 10, 540
    bar_width, bar_height = 250, 15
    
    # Boss health bar background with menacing dark red
    glColor3f(0.2, 0.05, 0.05)
    glBegin(GL_QUADS)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + bar_width, bar_y)
    glVertex2f(bar_x + bar_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()
    
    # Boss health bar fill with pulsing effect
    health_ratio = current_health / max_health
    fill_width = bar_width * health_ratio
    current_time = time.time()
    pulse = 0.8 + 0.2 * math.sin(current_time * 4)
    enhanced_boss_color = (boss_color[0] * pulse, boss_color[1] * pulse, boss_color[2] * pulse)
    
    glColor3f(*enhanced_boss_color)
    glBegin(GL_QUADS)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + fill_width, bar_y)
    glVertex2f(bar_x + fill_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()
    
    # Boss health bar border with intimidating effect
    glColor3f(0.9, 0.1, 0.1)
    glLineWidth(3)
    glBegin(GL_LINE_LOOP)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + bar_width, bar_y)
    glVertex2f(bar_x + bar_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()
    glLineWidth(1)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

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
    """Draw enhanced status when cloak is active with glowing effects"""
    current_time = time.time()
    
    # Cloak active with shimmering effect
    shimmer = 0.7 + 0.3 * math.sin(current_time * 4)
    cloak_color = (0.8 * shimmer, 0.9 * shimmer, 1.0)
    
    glColor3f(*cloak_color)
    draw_text(10, 530, "🌟 Cloak: ACTIVE (Invisible!)", GLUT_BITMAP_HELVETICA_18)
    
    if not game_state.cheat_mode:
        elapsed_cloak_time = get_elapsed_time() - game_state.clk_start_T
        remaining_time = (CLOAK_DURATION - elapsed_cloak_time) // 1000
        
        # Color-code the remaining time
        if remaining_time > 3:
            time_color = (0.4, 0.9, 0.9)  # Cyan - plenty of time
        elif remaining_time > 1:
            time_color = (0.9, 0.7, 0.2)  # Yellow - warning
        else:
            # Red flashing for critical time
            flash = 0.5 + 0.5 * math.sin(current_time * 8)
            time_color = (0.9 * flash, 0.1, 0.1)
        
        glColor3f(*time_color)
        draw_text(10, 500, f"⏰ Duration: {remaining_time}s remaining", GLUT_BITMAP_HELVETICA_18)

def _draw_collected_cloak_status():
    """Draw enhanced status when cloak is collected but not active"""
    current_time = time.time()
    pulse = 0.6 + 0.4 * math.sin(current_time * 2)
    
    glColor3f(0.5 * pulse, 0.8 * pulse, 0.9)
    draw_text(10, 530, f"👤 Cloak Ready: {game_state.clk_collected} available", GLUT_BITMAP_HELVETICA_18)

def _draw_no_cloak_status():
    """Draw enhanced status when no cloak is available"""
    glColor3f(0.6, 0.4, 0.5)  # Muted purple-gray
    draw_text(10, 530, "👤 Cloak: Not Found", GLUT_BITMAP_HELVETICA_18)

def _draw_item_and_cheat_info():
    """Draw enhanced selected item and cheat mode information with colorful display"""
    # Enhanced selected item status
    _draw_enhanced_selected_item_display()
    
    # Enhanced cheat mode status
    if game_state.cheat_mode:
        _draw_enhanced_cheat_mode_status()

def _draw_enhanced_selected_item_display():
    """Draw enhanced selected item display with icons and colors"""
    if game_state.S_item:
        # Determine item icon and color based on selected item
        if game_state.S_item.lower() == "freeze_trap":
            item_color = (0.4, 0.9, 0.9)  # Cyan for freeze trap
            item_icon = "❄️"
            item_name = "FREEZE TRAP"
        elif game_state.S_item.lower() == "key":
            item_color = (1.0, 0.8, 0.2)  # Gold for key
            item_icon = "🔑"
            item_name = "KEY"
        else:
            item_color = (0.8, 0.6, 0.9)  # Purple for other items
            item_icon = "🎁"
            item_name = game_state.S_item.upper()
        
        # Draw with pulsing effect
        current_time = time.time()
        pulse = 0.8 + 0.2 * math.sin(current_time * 3)
        enhanced_color = (item_color[0] * pulse, item_color[1] * pulse, item_color[2] * pulse)
        
        glColor3f(*enhanced_color)
        draw_text(10, 470, f"{item_icon} Selected: {item_name}", GLUT_BITMAP_HELVETICA_18)
    else:
        # No item selected - subtle gray with appropriate icon
        glColor3f(0.5, 0.5, 0.6)
        draw_text(10, 470, "📦 No item selected", GLUT_BITMAP_HELVETICA_18)

def _draw_enhanced_cheat_mode_status():
    """Draw enhanced cheat mode status information with colorful animations"""
    current_time = time.time()
    
    # Cheat mode main indicator with rainbow effect
    rainbow_r = 0.5 + 0.5 * math.sin(current_time * 2)
    rainbow_g = 0.5 + 0.5 * math.sin(current_time * 2 + 2.09)  # 120 degrees phase shift
    rainbow_b = 0.5 + 0.5 * math.sin(current_time * 2 + 4.18)  # 240 degrees phase shift
    
    glColor3f(rainbow_r, rainbow_g, rainbow_b)
    draw_text(10, 440, "🎮 CHEAT MODE ACTIVE", GLUT_BITMAP_HELVETICA_18)
    
    # Wall phasing indicator with special effects
    if game_state.wall_phasing:
        # Flashing purple/blue for wall phasing
        phase_flash = 0.6 + 0.4 * math.sin(current_time * 6)
        glColor3f(0.8 * phase_flash, 0.4, 0.9 * phase_flash)
        draw_text(10, 410, "👻 WALL PHASING ACTIVE", GLUT_BITMAP_HELVETICA_18)
    
    # Add cheat mode benefits indicator
    glColor3f(0.7, 0.9, 0.4)  # Light green
    draw_text(10, 380, "⚡ Unlimited Health & Ammo", GLUT_BITMAP_HELVETICA_12)

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
    window_title = b"MAZE ESCAPE - 3D Adventure"
    
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
