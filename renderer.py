import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from config import *
import game_state
from maze_data import mazes
from utils import get_elapsed_time
from player import draw_player

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Draw text at specified screen coordinates"""
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_boundary_walls():
    """Draw tall boundary walls around the entire area with pleasant colors"""
    wall_size = GRID_LENGTH * 2 // 15  # Based on grid length and maze size
    maze = mazes[game_state.crnt_lev]
    maze_size = len(maze) * wall_size
    offset = maze_size // 2

    # Calculate dimensions for boundary walls
    boundary_height = 350  # Slightly reduced height for boundary walls
    boundary_thickness = 180  # Thick walls

    # North boundary wall (negative Z)
    glBegin(GL_QUADS)
    # Top face
    glColor3f(*BOUNDARY_COLOR)
    glVertex3f(-GRID_LENGTH - boundary_thickness, 0, -GRID_LENGTH - boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, 0, -GRID_LENGTH - boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)

    # Inner face (facing the maze)
    glColor3f(*DARKER_BOUNDARY)
    glVertex3f(-GRID_LENGTH - boundary_thickness, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH + boundary_thickness, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, -GRID_LENGTH)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, -GRID_LENGTH)

    # Top surface
    glColor3f(*BOUNDARY_COLOR)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, -GRID_LENGTH)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, -GRID_LENGTH)
    glEnd()

    # South boundary wall (positive Z)
    glBegin(GL_QUADS)
    # Outer face
    glColor3f(*BOUNDARY_COLOR)
    glVertex3f(-GRID_LENGTH - boundary_thickness, 0, GRID_LENGTH + boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, 0, GRID_LENGTH + boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)

    # Inner face
    glColor3f(*DARKER_BOUNDARY)
    glVertex3f(-GRID_LENGTH - boundary_thickness, 0, GRID_LENGTH)
    glVertex3f(GRID_LENGTH + boundary_thickness, 0, GRID_LENGTH)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, GRID_LENGTH)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, GRID_LENGTH)

    # Top surface
    glColor3f(*BOUNDARY_COLOR)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, GRID_LENGTH)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, GRID_LENGTH)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)
    glEnd()

    # West boundary wall (negative X)
    glBegin(GL_QUADS)
    # Outer face
    glColor3f(*BOUNDARY_COLOR)
    glVertex3f(-GRID_LENGTH - boundary_thickness, 0, -GRID_LENGTH - boundary_thickness)
    glVertex3f(-GRID_LENGTH - boundary_thickness, 0, GRID_LENGTH + boundary_thickness)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)

    # Inner face
    glColor3f(*DARKER_BOUNDARY)
    glVertex3f(-GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(-GRID_LENGTH, 0, GRID_LENGTH)
    glVertex3f(-GRID_LENGTH, boundary_height, GRID_LENGTH)
    glVertex3f(-GRID_LENGTH, boundary_height, -GRID_LENGTH)

    # Top surface
    glColor3f(*BOUNDARY_COLOR)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)
    glVertex3f(-GRID_LENGTH, boundary_height, GRID_LENGTH)
    glVertex3f(-GRID_LENGTH, boundary_height, -GRID_LENGTH)
    glEnd()

    # East boundary wall (positive X)
    glBegin(GL_QUADS)
    # Outer face
    glColor3f(*BOUNDARY_COLOR)
    glVertex3f(GRID_LENGTH + boundary_thickness, 0, -GRID_LENGTH - boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, 0, GRID_LENGTH + boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)

    # Inner face
    glColor3f(*DARKER_BOUNDARY)
    glVertex3f(GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, 0, GRID_LENGTH)
    glVertex3f(GRID_LENGTH, boundary_height, GRID_LENGTH)
    glVertex3f(GRID_LENGTH, boundary_height, -GRID_LENGTH)

    # Top surface
    glColor3f(*BOUNDARY_COLOR)
    glVertex3f(GRID_LENGTH, boundary_height, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, boundary_height, GRID_LENGTH)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)
    glEnd()

def draw_freeze_traps():
    """Draw freeze traps on the maze and deployed freeze traps"""
    wall_size = GRID_LENGTH * 2 // 15
    maze = mazes[game_state.crnt_lev]
    offset = len(maze) * wall_size // 2

    # Draw freeze traps in the maze (as cuboids above the floor)
    row = 0
    while row < len(maze):
        col = 0
        while col < len(maze[0]):
            if maze[row][col] == 6:
                x, z = col * wall_size - offset + wall_size / 2, \
                       row * wall_size - offset + wall_size / 2

                # Draw floor under the freeze trap - same as normal floor
                glBegin(GL_QUADS)
                glColor3f(*SAGE_COLOR)  # Same pleasant grass green
                glVertex3f(x - wall_size / 2, 10.0, z - wall_size / 2)
                glVertex3f(x + wall_size / 2, 10.0, z - wall_size / 2)
                glVertex3f(x + wall_size / 2, 10.0, z + wall_size / 2)
                glVertex3f(x - wall_size / 2, 10.0, z + wall_size / 2)
                glEnd()

                # Draw animated freeze trap as a cuboid above the floor
                glPushMatrix()
                current_time = get_elapsed_time() % 800
                height_offset = 40 + 15 * abs(current_time - 400) / 400
                glTranslatef(x, height_offset, z)

                # Freeze trap - pleasant aqua crystal-like cube
                glColor4f(0.6, 0.9, 0.9, 0.8)  # Soft aqua, slightly transparent
                glutSolidCube(wall_size / 3)  # Smaller cube

                # Glowing effect
                glPushMatrix()
                current_time = get_elapsed_time() % 1000
                pulse = 0.3 + 0.2 * abs(current_time - 500) / 500
                glScalef(1.3, 1.3, 1.3)
                glColor4f(0.7, 0.95, 0.95, pulse)  # Pulsing soft mint glow
                glutSolidOctahedron()
                glPopMatrix()

                glPopMatrix()

            col += 1
        row += 1

    # Draw deployed freeze traps
    for pos in game_state.freeze_trap_pos:
        row, col = pos
        x = col * wall_size - offset + wall_size / 2
        z = row * wall_size - offset + wall_size / 2

        # Draw freeze effect on the ground
        glPushMatrix()
        glTranslatef(x, 11, z)  # Just above floor
        glColor4f(0.6, 0.9, 0.9, 0.5)  # Semi-transparent soft aqua
        glScalef(1.0, 0.1, 1.0)  # Flatten
        glutSolidSphere(wall_size / 2, 16, 8)  # Ice patch
        glPopMatrix()

def draw_maze():
    """Draw the complete maze including walls, floors, and special items"""
    wall_size = GRID_LENGTH * 2 // 15
    wall_height = wall_size // 2
    maze = mazes[game_state.crnt_lev]
    offset = len(maze) * wall_size // 2

    # Draw base floor
    glBegin(GL_QUADS)
    glColor3f(0.30, 0.65, 0.45)  # More greenish sage green
    maze_size = len(maze) * wall_size
    glVertex3f(-offset, 5.0, -offset)
    glVertex3f(maze_size - offset, 5.0, -offset)
    glVertex3f(maze_size - offset, 5.0, maze_size - offset)
    glVertex3f(-offset, 5.0, maze_size - offset)
    glEnd()

    # Draw maze cells
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            cell = maze[row][col]
            x = col * wall_size - offset
            z = row * wall_size - offset

            if cell == 0:
                # Floor tile - sage color
                glBegin(GL_QUADS)
                glColor3f(*SAGE_COLOR)
                glVertex3f(x, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z + wall_size)
                glVertex3f(x, 10.0, z + wall_size)
                glEnd()

            elif cell == 1:
                # Wall - darker green top cap
                glBegin(GL_QUADS)
                glColor3f(0.40, 0.60, 0.42)  # Darker green
                glVertex3f(x, wall_height + 10.0, z)
                glVertex3f(x + wall_size, wall_height + 10.0, z)
                glVertex3f(x + wall_size, wall_height + 10.0, z + wall_size)
                glVertex3f(x, wall_height + 10.0, z + wall_size)
                glEnd()

                # Draw visible side faces (inner borders) - even darker green
                if row > 0 and maze[row - 1][col] != 1:
                    glBegin(GL_QUADS)
                    glColor3f(0.30, 0.50, 0.35)  # Darker green inner border
                    glVertex3f(x, 10.0, z)
                    glVertex3f(x + wall_size, 10.0, z)
                    glVertex3f(x + wall_size, wall_height + 10.0, z)
                    glVertex3f(x, 10.0, z)
                    glEnd()
                if row < len(maze) - 1 and maze[row + 1][col] != 1:
                    glBegin(GL_QUADS)
                    glColor3f(0.30, 0.50, 0.35)  # Darker green inner border
                    glVertex3f(x, 10.0, z + wall_size)
                    glVertex3f(x + wall_size, 10.0, z + wall_size)
                    glVertex3f(x + wall_size, wall_height + 10.0, z + wall_size)
                    glVertex3f(x, 10.0, z + wall_size)
                    glEnd()
                if col > 0 and maze[row][col - 1] != 1:
                    glBegin(GL_QUADS)
                    glColor3f(0.30, 0.50, 0.35)  # Darker green inner border
                    glVertex3f(x, 10.0, z)
                    glVertex3f(x, 10.0, z + wall_size)
                    glVertex3f(x, wall_height + 10.0, z + wall_size)
                    glVertex3f(x, 10.0, z)
                    glEnd()
                if col < len(maze[0]) - 1 and maze[row][col + 1] != 1:
                    glBegin(GL_QUADS)
                    glColor3f(0.30, 0.50, 0.35)  # Darker green inner border
                    glVertex3f(x + wall_size, 10.0, z)
                    glVertex3f(x + wall_size, 10.0, z + wall_size)
                    glVertex3f(x + wall_size, wall_height + 10.0, z + wall_size)
                    glVertex3f(x + wall_size, 10.0, z)
                    glEnd()

            elif cell == 2:
                # Floor under key - match surface sage
                glBegin(GL_QUADS)
                glColor3f(*SAGE_COLOR)
                glVertex3f(x, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z + wall_size)
                glVertex3f(x, 10.0, z + wall_size)
                glEnd()
                # Animated key position
                glPushMatrix()
                current_time = get_elapsed_time() % 1000
                height_offset = 50 + 20 * abs(current_time - 500) / 500
                glTranslatef(x + wall_size / 2, height_offset, z + wall_size / 2)
                # --- Glowing Aura (transparent sphere) ---
                glPushMatrix()
                glScalef(1.5, 1.5, 1.5)
                glColor4f(0.6, 0.8, 1.0, 0.8)  # Light blue glow
                glutSolidSphere(wall_size / 4, 16, 16)
                glPopMatrix()
                # --- Solid Key: Light Blue Sphere + Sideways Cylinder ---
                glColor3f(0.7, 0.85, 1.0)  # Light blue key
                glutSolidSphere(wall_size / 4, 16, 16)
                quadric = gluNewQuadric()
                glRotatef(-90, 0, 1, 0)
                gluCylinder(quadric, wall_size / 12, wall_size / 12, wall_size / 2, 12, 3)
                glPopMatrix()

            elif cell == 4:
                # Floor under exit - match surface sage
                glBegin(GL_QUADS)
                glColor3f(*SAGE_COLOR)
                glVertex3f(x, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z + wall_size)
                glVertex3f(x, 10.0, z + wall_size)
                glEnd()
                # Draw black cube (exit block) sitting on top of the floor
                glPushMatrix()
                glTranslatef(x + wall_size / 2, wall_height / 2 + 10.0, z + wall_size / 2)
                glColor3f(0.15, 0.15, 0.15)  # Soft charcoal
                glutSolidCube(wall_size)
                glPopMatrix()

            elif cell == 5:
                # Floor under enemy - match surface sage
                glBegin(GL_QUADS)
                glColor3f(*SAGE_COLOR)
                glVertex3f(x, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z + wall_size)
                glVertex3f(x, 10.0, z + wall_size)
                glEnd()
            elif cell == 7:  # Cloak collectible
                # Floor under the cloak - match surface sage
                glBegin(GL_QUADS)
                glColor3f(*SAGE_COLOR)
                glVertex3f(x, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z + wall_size)
                glVertex3f(x, 10.0, z + wall_size)
                glEnd()

                # Draw animated white sphere for the cloak
                glPushMatrix()

                # Use time to calculate scale and height dynamically
                time_ = get_elapsed_time() % 1000
                scale_factor = 0.75 + 0.25 * math.sin(time_ * 2 * math.pi / 1000)
                height_offset = 50 + 20 * abs(time_ - 500) / 500

                glTranslatef(x + wall_size/2, height_offset, z + wall_size/2)
                glScalef(scale_factor, scale_factor, scale_factor)
                glColor3f(0.95, 0.95, 0.95)
                glutSolidSphere(wall_size / 4, 16, 16)
                glPopMatrix()
            elif cell == 8:  # Immobilize trap
                # Floor - match surface sage
                glBegin(GL_QUADS)
                glColor3f(*SAGE_COLOR)
                glVertex3f(x, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z + wall_size)
                glVertex3f(x, 10.0, z + wall_size)
                glEnd()

                # Draw trap markings (criss-cross pattern) - now red
                glBegin(GL_LINES)
                glColor3f(1.0, 0.0, 0.0)  # Red color
                glVertex3f(x, 11.0, z)
                glVertex3f(x + wall_size, 11.0, z + wall_size)
                glVertex3f(x, 11.0, z + wall_size)
                glVertex3f(x + wall_size, 11.0, z)
                glEnd()

            elif cell == 9:  # Deadly trap
                # Floor - match surface sage
                glBegin(GL_QUADS)
                glColor3f(*SAGE_COLOR)
                glVertex3f(x, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z + wall_size)
                glVertex3f(x, 10.0, z + wall_size)
                glEnd()

                # Draw skull-like pattern with lines
                glBegin(GL_LINES)
                glColor3f(0.2, 0.2, 0.2)  # Soft dark gray
                # X pattern
                glVertex3f(x + wall_size * 0.3, 11.0, z + wall_size * 0.3)
                glVertex3f(x + wall_size * 0.7, 11.0, z + wall_size * 0.7)
                glVertex3f(x + wall_size * 0.3, 11.0, z + wall_size * 0.7)
                glVertex3f(x + wall_size * 0.7, 11.0, z + wall_size * 0.3)
                glEnd()

                # Circle around the X
                glPushMatrix()
                glTranslatef(x + wall_size / 2, 11.0, z + wall_size / 2)
                glColor3f(0.2, 0.2, 0.2)  # Soft dark gray
                glutWireSphere(wall_size / 4, 8, 2)
                glPopMatrix()

    # --- Draw Player at p_position ---
    row, col = game_state.p_position
    x = col * wall_size - offset
    z = row * wall_size - offset

    # Floor under player - EXACTLY the same as normal floor (sage)
    glBegin(GL_QUADS)
    glColor3f(*SAGE_COLOR)
    glVertex3f(x, 10.0, z)
    glVertex3f(x + wall_size, 10.0, z)
    glVertex3f(x + wall_size, 10.0, z + wall_size)
    glVertex3f(x, 10.0, z + wall_size)
    glEnd()

    # Draw player model
    glPushMatrix()
    glTranslatef(x + wall_size / 2, 10.0, z + wall_size / 2)
    draw_player(0, 0, 0)
    glPopMatrix()

def draw_coins():
    """Draw all coins that haven't been collected yet."""
    if not game_state.coin_pos:
        return

    wall_size = GRID_LENGTH * 2 // 15
    current_time = get_elapsed_time() % 1000
    height_offset = 30 + 10 * abs(current_time - 500) / 500
    scale = 0.5 + 0.3 * abs(current_time - 500) / 500

    # Debug print
    lev = game_state.crnt_lev + 1
    c_c = len(game_state.collected_coins[game_state.crnt_lev]) if lev < len(game_state.collected_coins) else 0
    print(f"Drawing coins for level {lev}. Total: {len(game_state.coin_pos)}, Collected: {c_c}")

    i = 0
    while i < len(game_state.coin_pos):
        coin_pos = game_state.coin_pos[i]
        if (lev := game_state.crnt_lev) >= len(game_state.collected_coins) or \
                i in game_state.collected_coins[lev]:
            i += 1
            continue
        x, z = coin_pos

        glPushMatrix()
        glTranslatef(x, height_offset, z)
        glScalef(scale, scale, scale)
        glColor3f(0.90, 0.74, 0.25)
        glutSolidSphere(wall_size / 3, 16, 16)
        glPopMatrix()
        i += 1