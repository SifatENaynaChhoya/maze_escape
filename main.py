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
    # Don't update game state if paused
    if game_state.game_paused:
        glutPostRedisplay()
        return

    update_delta_time()
    current_time = get_elapsed_time()

    # Handle cloak deactivation only when not in cheat mode
    if not game_state.cheat_mode and game_state.clk_active and current_time - game_state.clk_start_T > CLOAK_DURATION:
        game_state.clk_active = False

    # Handle immobilization timeout
    if game_state.P_Immobilized and current_time - game_state.P_Immobilized_T > IMMOBILIZE_DURATION:
        game_state.P_Immobilized = False

    # Continuous shooting in cheat mode
    if game_state.cheat_mode and game_state.mouse_left_down:
        if current_time - game_state.P_END_SHOT_T > P_FIRE_INT:
            player_shoot()

    update_enemies()  # Update enemy positions and handle shooting
    update_bullets()  # Update bullet positions
    glutPostRedisplay()

def showScreen():
    """Main display function"""
    if game_state.game_state == "menu":
        draw_menu()
        return
        
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()

    # --- Main Floor (beneath everything) ---
    glBegin(GL_QUADS)
    glColor3f(0.2, 0.45, 0.3)  # More greenish moss green for base floor
    glVertex3f(-GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, 0, GRID_LENGTH)
    glVertex3f(-GRID_LENGTH, 0, GRID_LENGTH)
    glEnd()

    # --- Game Over ---
    if game_state.game_over:
        from maze_data import mazes
        if game_state.crnt_lev == 2 and game_state.p_health > 0 and game_state.Tracks_bullets <= game_state.bullet_limit and game_state.k_collect and mazes[game_state.crnt_lev][game_state.p_position[0]][game_state.p_position[1]] == 4:
            draw_text(400, 400, "YOU WIN!", GLUT_BITMAP_TIMES_ROMAN_24)
            draw_text(350, 350, "Congratulations on finishing the game!", GLUT_BITMAP_HELVETICA_18)
            draw_text(350, 300, "Press 'R' to restart", GLUT_BITMAP_HELVETICA_18)
        else:
            # Draw player lying down for game over
            wall_size = GRID_LENGTH * 2 // 15
            maze = mazes[game_state.crnt_lev]
            offset = len(maze) * wall_size // 2
            row, col = game_state.p_position
            x = col * wall_size - offset + wall_size / 2
            z = row * wall_size - offset + wall_size / 2
            
            glPushMatrix()
            glTranslatef(x, 10.0, z)
            glRotatef(90, 1, 0, 0)  # Rotate to lie down
            draw_player(0, 0, 0)
            glPopMatrix()
            
            draw_text(400, 400, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
            draw_text(350, 350, "Press 'R' to restart", GLUT_BITMAP_HELVETICA_18)
        glutSwapBuffers()
        return

    # --- Boundary Walls ---
    draw_boundary_walls()

    # --- Maze Walls, Floor, Key, Exit ---
    draw_maze()

    # --- Draw Enemies (separately after the maze) ---
    draw_enemies()
    draw_bullets()

    # --- Coins ---
    draw_coins()
    draw_freeze_traps()

    # --- UI Text ---
    draw_ui()
    
    glutSwapBuffers()

def draw_ui():
    """Draw the game UI text"""
    # Calculate total coins safely
    total_coins = 0
    for coins in game_state.collected_coins:
        if coins is not None:  # Safety check
            total_coins += len(coins)
    
    # Calculate current level coins safely
    crnt_lev_coins = 0
    if game_state.crnt_lev < len(game_state.collected_coins) and game_state.collected_coins[game_state.crnt_lev] is not None:
        crnt_lev_coins = len(game_state.collected_coins[game_state.crnt_lev])
    
    # Calculate total possible coins safely
    total_possible_coins = NUM_COINS * 2 if game_state.coin_pos else 0
    
    draw_text(10, 770, f"Level: {game_state.crnt_lev + 1}")
    draw_text(10, 740, f"Health: {game_state.p_health}")
    draw_text(10, 710, f"Coins Collected: {total_coins} / {total_possible_coins}")
    draw_text(10, 680, f"Level Coins: {crnt_lev_coins} / {len(game_state.coin_pos) if game_state.coin_pos else 0}")
    draw_text(10, 650, f"Key Collected: {'Yes' if game_state.k_collect else 'No'}")
    draw_text(10, 620, f"Freeze Traps: {game_state.freeze_traps_C}")
    draw_text(10, 590, f"Bullets Used: {game_state.Tracks_bullets} / {game_state.bullet_limit}")
    
    # Show boss health only in level 3
    if game_state.crnt_lev == 2 and game_state.enemies and len(game_state.enemies) > 0 and len(game_state.enemies[0]) > 5:  # Safety check
        boss_health = game_state.enemies[0][5]
        draw_text(10, 560, f"Boss Health: {boss_health}")
    
    if game_state.P_Immobilized:
        remaining_time = (IMMOBILIZE_DURATION - (get_elapsed_time() - game_state.P_Immobilized_T)) // 1000
        draw_text(400, 750, f"IMMOBILIZED! ({remaining_time}s)", GLUT_BITMAP_HELVETICA_18)
    
    # Cloak status
    if game_state.clk_active:
        draw_text(10, 530, "Cloak Active: Yes")
        if not game_state.cheat_mode:
            remaining_time = (CLOAK_DURATION - (get_elapsed_time() - game_state.clk_start_T)) // 1000
            draw_text(10, 500, f"Cloak Duration: {remaining_time}s")
    elif game_state.clk_collected > 0:
        draw_text(10, 530, f"Cloak Collected: {game_state.clk_collected}")
    else:
        draw_text(10, 530, "Cloak Collected: No")

    # Selected item and action mode
    if game_state.S_item:
        draw_text(10, 470, f"Selected Item: {game_state.S_item}")
    else:
        draw_text(10, 470, "No item selected")
    
    # Cheat mode status
    if game_state.cheat_mode:
        draw_text(10, 440, "CHEAT MODE ACTIVE", GLUT_BITMAP_HELVETICA_18)
        if game_state.wall_phasing:
            draw_text(10, 410, "WALL PHASING ACTIVE", GLUT_BITMAP_HELVETICA_18)

    # Add pause message to UI
    if game_state.game_paused:
        draw_text(400, 400, "GAME PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(350, 350, "Press SPACE to continue", GLUT_BITMAP_HELVETICA_18)

def main():
    """Main function to initialize and start the game"""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Maze Escape: Hunter's Chase")
    
    # Enhanced depth testing settings
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glClearDepth(1.0)

    # Initialize game state
    game_state.game_state = "menu"
    game_state.p_position = find_player_start()
    
    # Set a nice background color for better contrast
    glClearColor(0.2, 0.25, 0.35, 1.0)  # Soft slate blue background
    
    initialize_enemies()
    generate_coin_positions()
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
