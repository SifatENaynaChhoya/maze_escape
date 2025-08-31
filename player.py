# """
# Player management functions including drawing, shooting, and movement
# """
# import math
# from OpenGL.GL import *
# from OpenGL.GLUT import *
# from OpenGL.GLU import *
# from config import *
# import game_state
# from maze_data import mazes
# from utils import get_elapsed_time

# def draw_player(x, y, z):
#     """Draw the player character at the specified position"""
#     wall_size = GRID_LENGTH * 2 // 15
#     leg_radius = wall_size / 12
#     leg_height = wall_size / 3
#     torso_height = wall_size / 2
#     hand_length = wall_size / 3
#     torso_radius = wall_size / 6
#     head_radius = wall_size / 5
#     gun_radius = wall_size / 15
#     Gun_Len = wall_size / 2

#     glPushMatrix()
#     glTranslatef(x, y, z)
#     glRotatef(game_state.p_angle, 0, 1, 0)  # Apply player rotation

#     quadric = gluNewQuadric()

#     if game_state.clk_active:
#         glColor3f(0.95, 0.95, 0.95)  # Soft white for cloaked view
#         for dx in [-torso_radius / 2, torso_radius / 2]:
#             glPushMatrix()
#             glTranslatef(dx, 0, 0)
#             glRotatef(-90, 1, 0, 0)
#             gluCylinder(quadric, leg_radius, leg_radius, leg_height, 12, 3)
#             glPopMatrix()

#         # Draw torso (soft mint cylinder) - slightly darker
#         glPushMatrix()
#         glTranslatef(0, leg_height, 0)
#         glColor3f(0.6, 0.8, 0.7)  # Darker mint green
#         glRotatef(-90, 1, 0, 0)
#         gluCylinder(quadric, torso_radius, torso_radius, torso_height, 16, 4)
#         glPopMatrix()

#         # Draw hands (soft white cylinders) on both sides of torso - pointing forward
#         glColor3f(0.92, 0.92, 0.92)  # Slightly dimmer white
#         for dx in [-torso_radius * 1.5, torso_radius * 1.5]:
#             glPushMatrix()
#             glTranslatef(dx, leg_height + torso_height * 0.8, 0)
#             glRotatef(180, 0, 1, 0)  # Rotate to point arms forward
#             gluCylinder(quadric, leg_radius * 0.8, leg_radius * 0.8, hand_length, 12, 3)
#             glPopMatrix()

#         # Draw head (soft white sphere when cloaked)
#         glColor3f(0.92, 0.92, 0.92)
#         glPushMatrix()
#         glTranslatef(0, leg_height + torso_height + head_radius, 0)
#         glutSolidSphere(head_radius, 16, 16)
#         glPopMatrix()

#         # Draw gun (soft white cylinder when cloaked) attached to the center of the torso, pointing forward
#         glPushMatrix()
#         glColor3f(0.92, 0.92, 0.92)
#         glTranslatef(0, leg_height + torso_height * 0.7, 0)
#         glRotatef(180, 0, 1, 0)
#         gluCylinder(quadric, gun_radius, gun_radius, Gun_Len, 12, 3)
#         glPopMatrix()
#     else:
#         # Draw legs (2 soft peach cylinders) - slightly darker
#         glColor3f(0.9, 0.7, 0.6)  # Darker peach
#         for dx in [-torso_radius / 2, torso_radius / 2]:
#             glPushMatrix()
#             glTranslatef(dx, 0, 0)
#             glRotatef(-90, 1, 0, 0)
#             gluCylinder(quadric, leg_radius, leg_radius, leg_height, 12, 3)
#             glPopMatrix()

#         # Draw torso (soft mint cylinder) - slightly darker
#         glPushMatrix()
#         glTranslatef(0, leg_height, 0)
#         glColor3f(0.6, 0.8, 0.7)  # Darker mint green
#         glRotatef(-90, 1, 0, 0)
#         gluCylinder(quadric, torso_radius, torso_radius, torso_height, 16, 4)
#         glPopMatrix()

#         # Draw hands (soft peach cylinders) - slightly darker
#         glColor3f(0.9, 0.7, 0.6)
#         for dx in [-torso_radius * 1.5, torso_radius * 1.5]:
#             glPushMatrix()
#             glTranslatef(dx, leg_height + torso_height * 0.8, 0)
#             glRotatef(180, 0, 1, 0)  # Rotate to point arms forward
#             gluCylinder(quadric, leg_radius * 0.8, leg_radius * 0.8, hand_length, 12, 3)
#             glPopMatrix()

#         # Draw head (soft caramel sphere) - slightly darker
#         glColor3f(0.75, 0.55, 0.45)  # Darker caramel
#         glPushMatrix()
#         glTranslatef(0, leg_height + torso_height + head_radius, 0)
#         glutSolidSphere(head_radius, 16, 16)
#         glPopMatrix()

#         # Draw gun (soft sage cylinder) - slightly darker
#         glPushMatrix()
#         glColor3f(0.55, 0.65, 0.55)
#         glTranslatef(0, leg_height + torso_height * 0.7, 0)
#         glRotatef(180, 0, 1, 0)
#         gluCylinder(quadric, gun_radius, gun_radius, Gun_Len, 12, 3)
#         glPopMatrix()

#     glPopMatrix()  # Final pop to match the initial push

# def player_shoot():
#     """Make the player shoot a bullet in the direction they're facing, considering bullet limits."""
#     if game_state.P_Immobilized:
#         return
#     current_time = get_elapsed_time()

#     if current_time - game_state.P_END_SHOT_T < P_FIRE_INT:
#         return  # Don't shoot if we fired too recently
    
#     # Check if bullets fired exceed the limit
#     if not game_state.cheat_mode and game_state.Tracks_bullets >= game_state.bullet_limit:
#         game_state.game_over = True  # End the game if bullet limit is exceeded
#         return
    
#     # Increment bullets fired
#     game_state.Tracks_bullets += 1
#     game_state.P_END_SHOT_T = current_time

#     # Calculate the bullet's starting position (in front of the player's gun)
#     wall_size = GRID_LENGTH * 2 // 15
#     offset = len(mazes[game_state.crnt_lev]) * wall_size // 2
#     row, col = game_state.p_position
#     x = col * wall_size - offset + wall_size / 2
#     z = row * wall_size - offset + wall_size / 2
#     y = 10.0 + wall_size / 3  # Height of gun

#     # FIX: Flip the angle calculation so up/down directions match the visual direction
#     corrected_angle = (360 - game_state.p_angle) % 360  # Invert the angle orientation
#     angle_rad = math.radians(corrected_angle)
#     # Calculate direction vector with the corrected angle
#     dx = math.sin(angle_rad)
#     dz = -math.cos(angle_rad)

#     # Start bullet a bit in front of the player. Positioning the Bullet in Front of the Gun:
#     Gun_Len = wall_size / 2  # Sets how far the gun extend
#     x += dx * Gun_Len
#     z += dz * Gun_Len
#     # Add bullet to p_bullets list with corrected direction
#     game_state.p_bullets.append([x, y, z, dx * game_state.Bullet_S, 0, dz * game_state.Bullet_S, current_time])


"""
Player management functions including drawing, shooting, and movement
"""
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from config import *
import game_state
from maze_data import mazes
from utils import get_elapsed_time

def draw_player(x, y, z):
    """Draw the player character at the specified position"""
    wall_size = GRID_LENGTH * 2 // 15
    leg_radius = wall_size / 12
    leg_height = wall_size / 3
    torso_height = wall_size / 2
    hand_length = wall_size / 3
    torso_radius = wall_size / 6
    head_radius = wall_size / 5
    gun_radius = wall_size / 15
    Gun_Len = wall_size / 2

    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(game_state.p_angle, 0, 1, 0)  # Apply player rotation

    quadric = gluNewQuadric()

    if game_state.clk_active:
        glColor3f(0.95, 0.95, 0.95)  # Soft white for cloaked view
        for side in [-1, 1]:
            dx = side * torso_radius / 2
            glPushMatrix()
            glTranslatef(dx, 0, 0)
            glRotatef(-90, 1, 0, 0)
            gluCylinder(quadric, leg_radius, leg_radius, leg_height, 12, 3)
            glPopMatrix()

        # Torso
        glPushMatrix()
        glTranslatef(0, leg_height, 0)
        glColor3f(0.6, 0.8, 0.7)  # Darker mint green
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quadric, torso_radius, torso_radius, torso_height, 16, 4)
        glPopMatrix()

        # Draw hands (soft white cylinders) on both sides of torso - pointing forward
        glColor3f(0.92, 0.92, 0.92)  # Slightly dimmer white
        for side_offset in [-torso_radius * 1.5, torso_radius * 1.5]:
            side_displacement = side_offset * torso_radius
            glPushMatrix()
            glTranslatef(side_displacement, leg_height + torso_height * 0.8, 0)
            glRotatef(180, 0, 1, 0)  # Rotate to point arms forward
            gluCylinder(quadric, leg_radius * 0.8, leg_radius * 0.8, hand_length, 12, 3)
            glPopMatrix()

        # Draw head (soft white sphere when cloaked)
        glColor3f(0.92, 0.92, 0.92)
        glPushMatrix()
        glTranslatef(0, leg_height + torso_height + head_radius, 0)
        glutSolidSphere(head_radius, 16, 16)
        glPopMatrix()

        # Draw gun (soft white cylinder when cloaked) attached to the center of the torso, pointing forward
        glPushMatrix()
        glColor3f(0.92, 0.92, 0.92)
        glTranslatef(0, leg_height + torso_height * 0.7, 0)
        glRotatef(180, 0, 1, 0)
        gluCylinder(quadric, gun_radius, gun_radius, Gun_Len, 12, 3)
        glPopMatrix()
    else:
        # Draw legs (2 soft peach cylinders) - slightly darker
        glColor3f(0.9, 0.7, 0.6)  # Darker peach
        for side in [-1, 1]:
            dx = side * torso_radius / 2
            glPushMatrix()
            glTranslatef(dx, 0, 0)
            glRotatef(-90, 1, 0, 0)
            gluCylinder(quadric, leg_radius, leg_radius, leg_height, 12, 3)
            glPopMatrix()

        # Torso
        glPushMatrix()
        glTranslatef(0, leg_height, 0)
        glColor3f(0.6, 0.8, 0.7)  # Darker mint green
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quadric, torso_radius, torso_radius, torso_height, 16, 4)
        glPopMatrix()

        # Hands
        for side in [-1, 1]:
            side_displacement = side * torso_radius * 1.5
            glPushMatrix()
            glTranslatef(side_displacement, leg_height + torso_height * 0.8, 0)
            glRotatef(180, 0, 1, 0)  # Rotate to point arms forward
            glColor3f(0.9, 0.7, 0.6)
            gluCylinder(quadric, leg_radius * 0.8, leg_radius * 0.8, hand_length, 12, 3)
            glPopMatrix()

        # Head
        glPushMatrix()
        glTranslatef(0, leg_height + torso_height + head_radius, 0)
        glColor3f(0.75, 0.55, 0.45)  # Darker caramel
        glutSolidSphere(head_radius, 16, 16)
        glPopMatrix()

        # Gun
        glPushMatrix()
        glColor3f(0.55, 0.65, 0.55)
        glTranslatef(0, leg_height + torso_height * 0.7, 0)
        glRotatef(180, 0, 1, 0)
        gluCylinder(quadric, gun_radius, gun_radius, Gun_Len, 12, 3)
        glPopMatrix()

    glPopMatrix()  # Final pop to match the initial push

def player_shoot():
    """Make the player shoot a bullet in the direction they're facing, considering bullet limits."""
    # Check if player is immobilized
    if game_state.P_Immobilized:
        return

    # Calculate time since last shot
    current_time = get_elapsed_time()
    time_since_last_shot = current_time - game_state.P_END_SHOT_T

    # Return if not enough time has passed since last shot
    if time_since_last_shot < P_FIRE_INT:
        return

    # Check if bullet limit has been reached
    bullet_count = game_state.Tracks_bullets
    if not game_state.cheat_mode and bullet_count >= game_state.bullet_limit:
        game_state.game_over = True
        return

    game_state.Tracks_bullets += 1
    game_state.P_END_SHOT_T = get_elapsed_time()

    # Calculate player position for bullet
    wall_width = GRID_LENGTH * 2 // 15
    maze_length = len(mazes[game_state.crnt_lev])
    maze_offset = maze_length * wall_width // 2
    col, row = game_state.p_position
    x_pos = col * wall_width - maze_offset + wall_width / 2
    z_pos = row * wall_width - maze_offset + wall_width / 2
    y_pos = 10.0 + wall_width / 3

    # Calculate player direction for bullet
    angle = (360 - game_state.p_angle) % 360
    angle_rad = math.radians(angle)
    dx = math.sin(angle_rad)
    dz = -math.cos(angle_rad)

    # Adjust player position for bullet
    bullet_length = wall_width / 2
    x_pos += dx * bullet_length
    z_pos += dz * bullet_length

    dx, dz = dx * game_state.Bullet_S, dz * game_state.Bullet_S
    new_pos = x_pos + dx, y_pos, z_pos + dz
    game_state.p_bullets.append(
        [*new_pos, dx, 0, dz, get_elapsed_time()]
    )