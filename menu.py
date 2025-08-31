"""
Menu system for game start screen and instructions
"""
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from config import *
import game_state
from renderer import draw_text

def draw_menu():
    """Draw the start menu screen"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    # Set up orthographic projection for 2D rendering
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Draw title
    draw_text(350, 600, "3D Maze Escape: Hunter's Chase", GLUT_BITMAP_TIMES_ROMAN_24)
    
    if not game_state.show_instructions:
        # Draw start button
        x, y, w, h = MENU_BUTTON_RECT
        glColor3f(0.2, 0.6, 0.2)  # Green color for button
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
        draw_text(x + 50, y + 15, "Start Game", GLUT_BITMAP_HELVETICA_18)
        
        # Draw instructions button
        x, y, w, h = INSTRUCTIONS_BUTTON_RECT
        glColor3f(0.2, 0.4, 0.8)  # Blue color for button
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
        draw_text(x + 50, y + 15, "Instructions", GLUT_BITMAP_HELVETICA_18)
        
        # Draw exit button
        x, y, w, h = EXIT_BUTTON_RECT
        glColor3f(0.8, 0.2, 0.2)  # Red color for button
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
        draw_text(x + 70, y + 15, "Exit", GLUT_BITMAP_HELVETICA_18)
    else:
        # Draw instructions
        glColor3f(0.2, 0.4, 0.8)  # Blue background for instructions
        glBegin(GL_QUADS)
        glVertex2f(200, 100)
        glVertex2f(800, 100)
        glVertex2f(800, 700)
        glVertex2f(200, 700)
        glEnd()
        
        # Draw instructions text with adjusted spacing - starting lower
        draw_text(350, 600, "3D Maze Escape: Hunter's Chase", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(300, 550, "Controls:", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 520, "WASD - Move", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 490, "Mouse - Look around", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 460, "Left Click - Shoot", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 430, "Right Click - Toggle view", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 400, "E - Interact/Collect", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 370, "5,6,7 - Select items", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 340, "Space - Pause", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 310, "C - Toggle Cheat Mode", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 280, "V - Toggle Wall Phasing (Cheat Mode)", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 250, "ESC - Return to Menu", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 220, "R - Reset Camera View", GLUT_BITMAP_HELVETICA_18)
        
        # Draw back button
        x, y = 400, 150
        w, h = 200, 50
        glColor3f(0.2, 0.6, 0.2)  # Green color for button
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
        draw_text(x + 70, y + 15, "Back", GLUT_BITMAP_HELVETICA_18)
    
    glutSwapBuffers()
