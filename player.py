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

# Player appearance constants
PLAYER_LEG_RADIUS_RATIO = 1/12
PLAYER_LEG_HEIGHT_RATIO = 1/3
PLAYER_TORSO_HEIGHT_RATIO = 1/2
PLAYER_HAND_LENGTH_RATIO = 1/3
PLAYER_TORSO_RADIUS_RATIO = 1/6
PLAYER_HEAD_RADIUS_RATIO = 1/5
PLAYER_GUN_RADIUS_RATIO = 1/15
PLAYER_GUN_LENGTH_RATIO = 1/2

# Player colors - cloaked state
CLOAKED_LIMB_COLOR = (0.95, 0.95, 0.95)
CLOAKED_TORSO_COLOR = (0.6, 0.8, 0.7)
CLOAKED_HAND_COLOR = (0.92, 0.92, 0.92)
CLOAKED_HEAD_COLOR = (0.92, 0.92, 0.92)
CLOAKED_GUN_COLOR = (0.92, 0.92, 0.92)

# Player colors - normal state
NORMAL_LEG_COLOR = (0.9, 0.7, 0.6)
NORMAL_TORSO_COLOR = (0.6, 0.8, 0.7)
NORMAL_HAND_COLOR = (0.9, 0.7, 0.6)
NORMAL_HEAD_COLOR = (0.75, 0.55, 0.45)
NORMAL_GUN_COLOR = (0.55, 0.65, 0.55)

# Rendering constants
LEG_SEGMENTS = 12
LEG_RINGS = 3
TORSO_SEGMENTS = 16
TORSO_RINGS = 4
HEAD_SLICES = 16
HEAD_STACKS = 16
GUN_SEGMENTS = 12
GUN_RINGS = 3


def _calculate_player_dimensions(wall_size):
    """Calculate all player body part dimensions based on wall size"""
    return {
        'leg_radius': wall_size * PLAYER_LEG_RADIUS_RATIO,
        'leg_height': wall_size * PLAYER_LEG_HEIGHT_RATIO,
        'torso_height': wall_size * PLAYER_TORSO_HEIGHT_RATIO,
        'hand_length': wall_size * PLAYER_HAND_LENGTH_RATIO,
        'torso_radius': wall_size * PLAYER_TORSO_RADIUS_RATIO,
        'head_radius': wall_size * PLAYER_HEAD_RADIUS_RATIO,
        'gun_radius': wall_size * PLAYER_GUN_RADIUS_RATIO,
        'gun_length': wall_size * PLAYER_GUN_LENGTH_RATIO
    }


def _draw_player_legs(quadric, dimensions, is_cloaked):
    """Draw both player legs"""
    color = CLOAKED_LIMB_COLOR if is_cloaked else NORMAL_LEG_COLOR
    glColor3f(*color)
    
    for dx in [-dimensions['torso_radius'] / 2, dimensions['torso_radius'] / 2]:
        glPushMatrix()
        glTranslatef(dx, 0, 0)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quadric, dimensions['leg_radius'], dimensions['leg_radius'], 
                   dimensions['leg_height'], LEG_SEGMENTS, LEG_RINGS)
        glPopMatrix()


def _draw_player_torso(quadric, dimensions, is_cloaked):
    """Draw player torso"""
    color = CLOAKED_TORSO_COLOR if is_cloaked else NORMAL_TORSO_COLOR
    glColor3f(*color)
    
    glPushMatrix()
    glTranslatef(0, dimensions['leg_height'], 0)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quadric, dimensions['torso_radius'], dimensions['torso_radius'], 
               dimensions['torso_height'], TORSO_SEGMENTS, TORSO_RINGS)
    glPopMatrix()


def _draw_player_hands(quadric, dimensions, is_cloaked):
    """Draw both player hands"""
    color = CLOAKED_HAND_COLOR if is_cloaked else NORMAL_HAND_COLOR
    glColor3f(*color)
    
    for dx in [-dimensions['torso_radius'] * 1.5, dimensions['torso_radius'] * 1.5]:
        glPushMatrix()
        glTranslatef(dx, dimensions['leg_height'] + dimensions['torso_height'] * 0.8, 0)
        glRotatef(180, 0, 1, 0)  # Rotate to point arms forward
        gluCylinder(quadric, dimensions['leg_radius'] * 0.8, dimensions['leg_radius'] * 0.8, 
                   dimensions['hand_length'], LEG_SEGMENTS, LEG_RINGS)
        glPopMatrix()


def _draw_player_head(dimensions, is_cloaked):
    """Draw player head"""
    color = CLOAKED_HEAD_COLOR if is_cloaked else NORMAL_HEAD_COLOR
    glColor3f(*color)
    
    glPushMatrix()
    glTranslatef(0, dimensions['leg_height'] + dimensions['torso_height'] + dimensions['head_radius'], 0)
    glutSolidSphere(dimensions['head_radius'], HEAD_SLICES, HEAD_STACKS)
    glPopMatrix()


def _draw_player_gun(quadric, dimensions, is_cloaked):
    """Draw player gun"""
    color = CLOAKED_GUN_COLOR if is_cloaked else NORMAL_GUN_COLOR
    glColor3f(*color)
    
    glPushMatrix()
    glTranslatef(0, dimensions['leg_height'] + dimensions['torso_height'] * 0.7, 0)
    glRotatef(180, 0, 1, 0)
    gluCylinder(quadric, dimensions['gun_radius'], dimensions['gun_radius'], 
               dimensions['gun_length'], GUN_SEGMENTS, GUN_RINGS)
    glPopMatrix()


def draw_player(x, y, z):
    """Draw the player character at the specified position"""
    wall_size = GRID_LENGTH * 2 // 15
    dimensions = _calculate_player_dimensions(wall_size)
    
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(game_state.p_angle, 0, 1, 0)  # Apply player rotation
    
    quadric = gluNewQuadric()
    is_cloaked = game_state.clk_active
    
    # Draw all player body parts
    _draw_player_legs(quadric, dimensions, is_cloaked)
    _draw_player_torso(quadric, dimensions, is_cloaked)
    _draw_player_hands(quadric, dimensions, is_cloaked)
    _draw_player_head(dimensions, is_cloaked)
    _draw_player_gun(quadric, dimensions, is_cloaked)
    
    glPopMatrix()  # Final pop to match the initial push

def _can_player_shoot():
    """Check if the player is allowed to shoot right now"""
    if game_state.P_Immobilized:
        return False
    
    current_time = get_elapsed_time()
    if current_time - game_state.P_END_SHOT_T < P_FIRE_INT:
        return False  # Don't shoot if we fired too recently
    
    return True


def _check_bullet_limit_exceeded():
    """Check if bullet limit is exceeded and handle game over"""
    if not game_state.cheat_mode and game_state.Tracks_bullets >= game_state.bullet_limit:
        game_state.game_over = True  # End the game if bullet limit is exceeded
        return True
    return False


def _calculate_bullet_starting_position():
    """Calculate the bullet's starting position in front of the player's gun"""
    wall_size = GRID_LENGTH * 2 // 15
    offset = len(mazes[game_state.crnt_lev]) * wall_size // 2
    row, col = game_state.p_position
    
    x = col * wall_size - offset + wall_size / 2
    z = row * wall_size - offset + wall_size / 2
    y = 10.0 + wall_size / 3  # Height of gun
    
    return x, y, z, wall_size


def _calculate_bullet_direction():
    """Calculate bullet direction based on player angle"""
    # FIX: Flip the angle calculation so up/down directions match the visual direction
    corrected_angle = (360 - game_state.p_angle) % 360  # Invert the angle orientation
    angle_rad = math.radians(corrected_angle)
    
    # Calculate direction vector with the corrected angle
    dx = math.sin(angle_rad)
    dz = -math.cos(angle_rad)
    
    return dx, dz


def _create_and_add_bullet(x, y, z, dx, dz, gun_length, current_time):
    """Create bullet and add it to the game state"""
    # Start bullet a bit in front of the player. Positioning the Bullet in Front of the Gun:
    x += dx * gun_length
    z += dz * gun_length
    
    # Add bullet to p_bullets list with corrected direction
    bullet_data = [x, y, z, dx * game_state.Bullet_S, 0, dz * game_state.Bullet_S, current_time]
    game_state.p_bullets.append(bullet_data)


def player_shoot():
    """Make the player shoot a bullet in the direction they're facing, considering bullet limits."""
    # Check if player can shoot
    if not _can_player_shoot():
        return
    
    # Check if bullet limit is exceeded
    if _check_bullet_limit_exceeded():
        return
    
    # Update shooting state
    current_time = get_elapsed_time()
    # Only increment bullet count if not in cheat mode
    if not game_state.cheat_mode:
        game_state.Tracks_bullets += 1
    game_state.P_END_SHOT_T = current_time
    
    # Calculate bullet position and direction
    x, y, z, wall_size = _calculate_bullet_starting_position()
    dx, dz = _calculate_bullet_direction()
    
    # Create and add bullet
    gun_length = wall_size / 2  # Sets how far the gun extends
    _create_and_add_bullet(x, y, z, dx, dz, gun_length, current_time)

