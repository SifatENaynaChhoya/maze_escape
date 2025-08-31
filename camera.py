"""
Camera management functions for view setup and positioning
"""
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from config import *
import game_state
from maze_data import mazes

def setupCamera():
    """Setup camera projection and view matrices"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    if game_state.view_mode == "overhead":
        # Original overhead camera setup
        gluPerspective(game_state.field_of_view, 1.25, 10.0, 20000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        cx, cy, cz = game_state.view_angle
        lx, ly, lz = game_state.cam_point
        gluLookAt(cx, cy, cz, lx, ly, lz, 0, 1, 0)
    else:  # First-person mode
        gluPerspective(90, 1.25, 1.0, 20000)  # Wider FOV for first person
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Calculate player's position in world coordinates
        wall_size = GRID_LENGTH * 2 // 15
        maze = mazes[game_state.crnt_lev]
        offset = len(maze) * wall_size // 2
        player_row, player_col = game_state.p_position

        # Player's feet position
        px = player_col * wall_size - offset + wall_size / 2
        pz = player_row * wall_size - offset + wall_size / 2
        py = 10.0  # Floor level

        # Eye position (on top of head)
        eye_height = wall_size * 2  # Approximately head height

        # Calculate look direction based on player angle
        corrected_angle = (360 - game_state.p_angle) % 360
        angle_rad = math.radians(corrected_angle)
        look_x = px + math.sin(angle_rad) * 100  # Look 100 units ahead
        look_z = pz - math.cos(angle_rad) * 100  # Negative because north is -z
        look_y = py + eye_height  # Maintain eye level while looking forward

        # Position camera at player's eye level
        gluLookAt(px, py + eye_height, pz,  # From (player's eye position)
                  look_x, look_y, look_z,  # To (point ahead based on angle)
                  0, 1, 0)  # Up vector

def updateCameraPosition():
    """Update camera x,z position based on current angle while maintaining height"""
    # Calculate distance from center to camera (in xz plane)
    dx = game_state.view_angle[0] - game_state.cam_point[0]
    dz = game_state.view_angle[2] - game_state.cam_point[2]
    radius = math.sqrt(dx ** 2 + dz ** 2)

    # Calculate new camera position based on angle
    new_x = game_state.cam_point[0] + radius * math.sin(game_state.camera_angle)
    new_z = game_state.cam_point[2] + radius * math.cos(game_state.camera_angle)

    # Update camera position, keeping y coordinate the same
    game_state.view_angle = (new_x, game_state.view_angle[1], new_z)
