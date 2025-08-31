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
    # Initialize OpenGL matrices
    _initialize_matrices()
    
    # Determine camera mode and configure accordingly
    camera_mode = _get_camera_mode()
    
    if camera_mode:
        _setup_overhead_camera()
    else:
        _setup_first_person_camera()

def _initialize_matrices():
    """Initialize OpenGL projection and modelview matrices"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def _get_camera_mode():
    """Check if camera is in overhead mode"""
    return game_state.view_mode == "overhead"

def _setup_overhead_camera():
    """Configure camera for overhead view"""
    # Set projection parameters
    glMatrixMode(GL_PROJECTION)
    fov = game_state.field_of_view
    aspect_ratio = 1.25
    near_plane = 10.0
    far_plane = 20000
    gluPerspective(fov, aspect_ratio, near_plane, far_plane)
    
    # Switch to modelview for camera positioning
    glMatrixMode(GL_MODELVIEW)
    
    # Extract camera position coordinates
    cx = game_state.view_angle[0]
    cy = game_state.view_angle[1]
    cz = game_state.view_angle[2]
    
    # Extract look-at target coordinates
    lx = game_state.cam_point[0]
    ly = game_state.cam_point[1]
    lz = game_state.cam_point[2]
    
    # Apply camera transformation
    up_x, up_y, up_z = 0, 1, 0
    gluLookAt(cx, cy, cz, lx, ly, lz, up_x, up_y, up_z)

def _setup_first_person_camera():
    """Configure camera for first-person view"""
    # Configure projection with wider field of view
    _set_first_person_projection()
    
    # Calculate world coordinate parameters
    world_params = _calculate_world_parameters()
    wall_size, maze, offset = world_params
    
    # Get player position in world coordinates
    player_coords = _get_player_world_position(wall_size, offset)
    px, py, pz = player_coords
    
    # Calculate camera eye level and viewing direction
    eye_height = _calculate_eye_height(wall_size)
    look_coords = _calculate_look_direction(px, py, pz, eye_height)
    look_x, look_y, look_z = look_coords
    
    # Set up first-person camera view
    camera_y = py + eye_height
    up_vector = (0, 1, 0)
    gluLookAt(px, camera_y, pz, look_x, look_y, look_z, up_vector[0], up_vector[1], up_vector[2])

def _set_first_person_projection():
    """Set projection matrix for first-person view"""
    glMatrixMode(GL_PROJECTION)
    fov = 90
    aspect = 1.25
    near = 1.0
    far = 20000
    gluPerspective(fov, aspect, near, far)
    glMatrixMode(GL_MODELVIEW)

def _calculate_world_parameters():
    """Calculate basic world coordinate system parameters"""
    wall_size = GRID_LENGTH * 2 // 15
    maze = mazes[game_state.crnt_lev]
    offset = len(maze) * wall_size // 2
    return wall_size, maze, offset

def _get_player_world_position(wall_size, offset):
    """Convert player grid position to world coordinates"""
    player_row = game_state.p_position[0]
    player_col = game_state.p_position[1]
    
    px = player_col * wall_size - offset + wall_size / 2
    pz = player_row * wall_size - offset + wall_size / 2
    py = 10.0  # Floor level
    
    return px, py, pz

def _calculate_eye_height(wall_size):
    """Calculate camera eye level height"""
    return wall_size * 2  # Approximately head height

def _calculate_look_direction(px, py, pz, eye_height):
    """Calculate where the camera should look based on player angle"""
    # Process player viewing angle
    corrected_angle = (360 - game_state.p_angle) % 360
    angle_rad = math.radians(corrected_angle)
    
    # Calculate look-ahead distance
    look_distance = 100
    
    # Compute look target coordinates
    look_x = px + math.sin(angle_rad) * look_distance
    look_z = pz - math.cos(angle_rad) * look_distance  # North is negative z
    look_y = py + eye_height
    
    return look_x, look_y, look_z

def updateCameraPosition():
    """Update camera x,z position based on current angle while maintaining height"""
    # Compute radius from center point to camera position
    radius = _compute_camera_radius()
    
    # Generate new coordinates based on current camera angle
    new_x, new_z = _calculate_new_camera_coordinates(radius)
    
    # Apply the updated position while preserving y-axis value
    _apply_camera_position_update(new_x, new_z)

def _compute_camera_radius():
    """Calculate the distance from camera center to current position"""
    # Extract coordinate differences in horizontal plane
    dx = game_state.view_angle[0] - game_state.cam_point[0]
    dz = game_state.view_angle[2] - game_state.cam_point[2]
    
    # Compute radial distance using Pythagorean theorem
    radius = math.sqrt(dx ** 2 + dz ** 2)
    return radius

def _calculate_new_camera_coordinates(radius):
    """Determine new x,z coordinates based on camera angle and radius"""
    # Calculate x coordinate using sine component
    new_x = game_state.cam_point[0] + radius * math.sin(game_state.camera_angle)
    
    # Calculate z coordinate using cosine component
    new_z = game_state.cam_point[2] + radius * math.cos(game_state.camera_angle)
    
    return new_x, new_z

def _apply_camera_position_update(new_x, new_z):
    """Update the camera position while maintaining the y coordinate"""
    # Preserve existing y-coordinate value
    current_y = game_state.view_angle[1]
    
    # Set new camera position with updated x,z and preserved y
    game_state.view_angle = (new_x, current_y, new_z)
