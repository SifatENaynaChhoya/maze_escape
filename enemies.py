"""
Enemy management functions including AI, movement, and rendering
"""
import math
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from config import *
import game_state
from maze_data import mazes
from utils import get_elapsed_time

def initialize_enemies():
    """Find all enemies in the maze and initialize their data"""
    game_state.enemies = []
    game_state.enemy_rotations = []
    game_state.ene_freeze_T = []  # Initialize as empty list

    current_time = get_elapsed_time()

    maze = mazes[game_state.crnt_lev]
    if not maze:  # Safety check
        return
        
    if game_state.crnt_lev == 2:  # Level 3 (Boss Fight)
        # Add a single boss enemy at the center of the arena
        boss_row = len(maze) // 2
        boss_col = len(maze[0]) // 2
        boss_health = 10  # Boss health
        game_state.enemies.append([boss_row, boss_col, 0, 0, current_time, boss_health])  # Add health as the last parameter
        game_state.enemy_rotations.append(0.0)  # Initial rotation angle
        game_state.ene_freeze_T.append(0)  # Not frozen
        return

    for row in range(len(maze)):
        for col in range(len(maze[0])):
            if maze[row][col] == 5:
                # Check if this enemy has valid movement options
                has_valid_move = False
                for dr, dc in [(-1, 0), (0, 1), (1, 0), (0, -1)]:  # Check in all 4 directions
                    nr, nc = row + dr, col + dc
                    if (0 <= nr < len(maze) and
                            0 <= nc < len(maze[0]) and
                            maze[nr][nc] == 0):
                        has_valid_move = True
                        break

                # Store the direction that leads to an open cell if possible
                if has_valid_move:
                    # Find a valid direction to start with
                    valid_directions = []
                    for d, (dr, dc) in enumerate([(-1, 0), (0, 1), (1, 0), (0, -1)]):
                        nr, nc = row + dr, col + dc
                        if (0 <= nr < len(maze) and
                                0 <= nc < len(maze[0]) and
                                maze[nr][nc] == 0):
                            valid_directions.append(d)

                    direction = random.choice(valid_directions) if valid_directions else random.randint(0, 3)
                else:
                    direction = random.randint(0, 3)

                game_state.enemies.append([row, col, direction, 0, current_time])  # Added last shot time
                game_state.enemy_rotations.append(0.0)  # Initial rotation angle
                game_state.ene_freeze_T.append(0)  # Not frozen
                # Replace enemy marker with floor in the maze
                maze[row][col] = 0

    # Initialize ene_freeze_T with 0 for each enemy
    game_state.ene_freeze_T = [0] * len(game_state.enemies)

def is_player_in_line_of_sight(enemy_row, enemy_col):
    """Check if player is in direct line of sight (same row or column) with no walls in between"""
    if game_state.clk_active:
        return False
    player_row, player_col = game_state.p_position
    maze = mazes[game_state.crnt_lev]

    # Convert positions to integers for range function
    enemy_row = int(enemy_row)
    enemy_col = int(enemy_col)
    player_row = int(player_row)
    player_col = int(player_col)

    # Same row
    if enemy_row == player_row:
        start_col = min(enemy_col, player_col)
        end_col = max(enemy_col, player_col)
        # Check all cells between enemy and player for walls
        for col in range(start_col + 1, end_col):
            if maze[enemy_row][col] == 1:  # Wall
                return False
        return True

    # Same column
    if enemy_col == player_col:
        start_row = min(enemy_row, player_row)
        end_row = max(enemy_row, player_row)
        # Check all cells between enemy and player for walls
        for row in range(start_row + 1, end_row):
            if maze[row][enemy_col] == 1:  # Wall
                return False
        return True

    return False

def update_enemies():
    """Move enemies and handle shooting"""
    if not game_state.enemies or not game_state.enemy_rotations or not game_state.ene_freeze_T:  # Safety check
        return
        
    current_time = get_elapsed_time()
    maze = mazes[game_state.crnt_lev]
    wall_size = GRID_LENGTH * 2 // 15
    offset = len(maze) * wall_size // 2

    # Initialize enemy dimensions if not set
    if game_state.body_radius is None or game_state.Gun_Len is None:
        game_state.body_radius = wall_size / 3  # Red sphere
        game_state.Gun_Len = wall_size / 2  # Grey gun cylinder

    for i, enemy in enumerate(game_state.enemies):
        if not enemy or len(enemy) < 5:  # Check if enemy data is valid
            continue
            
        row, col, direction, last_move_time, last_shot_time, *health = enemy
        is_boss = len(health) > 0  # Check if this is the boss
        health = health[0] if is_boss else None

        # Check if enemy is on a freeze trap
        if game_state.freeze_trap_pos:
            for trap_index, trap_pos in enumerate(game_state.freeze_trap_pos):
                if trap_pos[0] == row and trap_pos[1] == col:
                    if i < len(game_state.ene_freeze_T):  # Safety check
                        game_state.ene_freeze_T[i] = current_time
                        print(f"Enemy {i} stepped on freeze trap at time {current_time}")  # Debug print
                        # Remove the trap after it's triggered
                        game_state.freeze_trap_pos.pop(trap_index)
                        break

        # Check if the enemy is frozen
        is_frozen = False
        if i < len(game_state.ene_freeze_T):
            if game_state.ene_freeze_T[i] > 0:  # Enemy was previously frozen
                time_since_frozen = current_time - game_state.ene_freeze_T[i]

                if game_state.cheat_mode:
                    is_frozen = True  # Enemies remain frozen indefinitely in cheat mode
                elif time_since_frozen < FREEZE_DURATION:
                    is_frozen = True  # Freeze duration not expired
                else:
                    # Reset freeze time when duration expires
                    game_state.ene_freeze_T[i] = 0

        if is_frozen:
            # Enemy is frozen - rotate more slowly and don't shoot or move
            game_state.enemy_rotations[i] = (game_state.enemy_rotations[i] + ENEMY_ROT_SPEED * 0.2) % 360
            continue

        # Boss logic
        if is_boss:
            # Rotate the boss
            game_state.enemy_rotations[i] = (game_state.enemy_rotations[i] + ENEMY_ROT_SPEED) % 360
            player_row, player_col = game_state.p_position
            boss_x, boss_z = col, row
            player_x, player_z = player_col, player_row

            # Only move toward player if not cloaked
            if not game_state.clk_active:
                dx = player_x - boss_x
                dz = player_z - boss_z
                distance = max(1, (dx ** 2 + dz ** 2) ** 0.5)  # Avoid division by zero
                dx /= distance
                dz /= distance

                # Move the boss slightly toward the player
                move_speed = BOSS_MOVEMENT  # Use boss-specific movement speed
                new_row = boss_z + dz * move_speed
                new_col = boss_x + dx * move_speed

                # Check if new position has a freeze trap
                new_row_int = int(round(new_row))
                new_col_int = int(round(new_col))
                for trap_index, trap_pos in enumerate(game_state.freeze_trap_pos):
                    if trap_pos[0] == new_row_int and trap_pos[1] == new_col_int:
                        game_state.ene_freeze_T[i] = current_time
                        print(f"Boss about to step on freeze trap at time {current_time}")  # Debug print
                        # Remove the trap after it's triggered
                        game_state.freeze_trap_pos.pop(trap_index)
                        continue

                # Update boss position
                game_state.enemies[i][0] = new_row
                game_state.enemies[i][1] = new_col

            # Only skip shooting if cloaked
            if game_state.clk_active:
                continue

            # Boss continuously fires at player if not cloaked
            if current_time - last_shot_time > ENEMY_FIRE_INT:
                enemy_x = col * wall_size - offset + wall_size / 2
                enemy_z = row * wall_size - offset + wall_size / 2
                enemy_y = 200  # Boss height

                # Calculate direction to player
                player_row, player_col = game_state.p_position
                player_x = player_col * wall_size - offset + wall_size / 2
                player_z = player_row * wall_size - offset + wall_size / 2
                
                # Calculate direction vector
                dx = player_x - enemy_x
                dz = player_z - enemy_z
                distance = max(1, (dx ** 2 + dz ** 2) ** 0.5)  # Avoid division by zero
                dx /= distance
                dz /= distance

                # Create bullet with direction towards player using boss bullet speed
                game_state.bullets.append([enemy_x, enemy_y, enemy_z, dx * BOSS_BULLET_SPEED, 0, dz * BOSS_BULLET_SPEED, current_time, False])
                game_state.enemies[i][4] = current_time  # Update last shot time
            continue

        # Regular enemy logic
        # Rotate the enemy
        game_state.enemy_rotations[i] = (game_state.enemy_rotations[i] + ENEMY_ROT_SPEED) % 360

        # Check if player is in line of sight for shooting (skip if cloaked)
        player_in_sight = not game_state.clk_active and is_player_in_line_of_sight(row, col)
        
        if player_in_sight:
            # Calculate direction to player
            player_row, player_col = game_state.p_position
            if row == player_row:  # Same row
                new_direction = 1 if player_col > col else 3  # East or West
            elif col == player_col:  # Same column
                new_direction = 2 if player_row > row else 0  # South or North
            else:
                # If not in direct line, move towards player's row or column
                if abs(player_row - row) > abs(player_col - col):
                    new_direction = 2 if player_row > row else 0  # Move vertically
                else:
                    new_direction = 1 if player_col > col else 3  # Move horizontally
            
            # Update enemy direction
            game_state.enemies[i][2] = new_direction

            # Only move if enough time has passed since last move
            if current_time - last_move_time >= ENEMY_MOVEMENT:
                # Try to move in the new direction
                new_row, new_col = row, col
                if new_direction == 0:  # North
                    new_row -= 1
                elif new_direction == 1:  # East
                    new_col += 1
                elif new_direction == 2:  # South
                    new_row += 1
                elif new_direction == 3:  # West
                    new_col -= 1

                # Check if new position is valid
                if (0 <= new_row < len(maze) and
                        0 <= new_col < len(maze[0]) and
                        (maze[new_row][new_col] == 0 or maze[new_row][new_col] == 3)):
                    # Valid move, update position
                    game_state.enemies[i][0] = new_row
                    game_state.enemies[i][1] = new_col
                    game_state.enemies[i][3] = current_time  # Update last move time

                    # Check for collision with player
                    if abs(new_row - player_row) < 0.5 and abs(new_col - player_col) < 0.5:
                        if not game_state.cheat_mode and current_time - game_state.p_last_hit_time > P_INVINCIBILITY_T:
                            game_state.p_health -= 1  # Decrease health by 1 when colliding with boss
                            game_state.p_last_hit_time = current_time
                            if game_state.p_health <= 0:
                                game_state.game_over = True
                                game_state.p_health = 0

                    # Check if enemy stepped on a freeze trap
                    if [new_row, new_col] in game_state.freeze_trap_pos:
                        game_state.ene_freeze_T[i] = current_time

            # Shoot at player if in line of sight
            if current_time - last_shot_time > ENEMY_FIRE_INT:
                # Calculate enemy position
                enemy_x = col * wall_size - offset + wall_size / 2
                enemy_z = row * wall_size - offset + wall_size / 2
                enemy_y = 200 + 20 * math.sin(current_time * 0.003)

                # Calculate bullet direction
                if row == player_row:  # Same row
                    direction_x = 1 if player_col > col else -1
                    direction_z = 0
                    gun_idx = 1 if direction_x > 0 else 3
                elif col == player_col:  # Same column
                    direction_x = 0
                    direction_z = 1 if player_row > row else -1
                    gun_idx = 2 if direction_z > 0 else 0

                # Get the gun position
                dx, dy, dz = GUN_OFFSETS[gun_idx]
                start_x = enemy_x + dx * (game_state.body_radius + game_state.Gun_Len)
                start_y = enemy_y
                start_z = enemy_z + dz * (game_state.body_radius + game_state.Gun_Len)

                # Create bullet
                bullet_dx = direction_x * game_state.Bullet_S
                bullet_dz = direction_z * game_state.Bullet_S
                game_state.bullets.append([start_x, start_y, start_z, bullet_dx, 0, bullet_dz, current_time, False])
                game_state.enemies[i][4] = current_time

        else:
            # Not in line of sight or cloaked, use normal patrol movement
            if current_time - last_move_time < ENEMY_MOVEMENT:
                continue

            # Try to move in current direction
            new_row, new_col = row, col
            if direction == 0:  # North
                new_row -= 1
            elif direction == 1:  # East
                new_col += 1
            elif direction == 2:  # South
                new_row += 1
            elif direction == 3:  # West
                new_col -= 1

            # Check if new position is valid
            if (0 <= new_row < len(maze) and
                    0 <= new_col < len(maze[0]) and
                    (maze[new_row][new_col] == 0 or maze[new_row][new_col] == 3)):
                # Valid move, update position
                game_state.enemies[i][0] = new_row
                game_state.enemies[i][1] = new_col
                game_state.enemies[i][3] = current_time  # Update last move time

                # Check for collision with player
                player_row, player_col = game_state.p_position
                if abs(new_row - player_row) < 0.5 and abs(new_col - player_col) < 0.5:
                    if not game_state.cheat_mode and current_time - game_state.p_last_hit_time > P_INVINCIBILITY_T:
                        game_state.p_health -= 1
                        game_state.p_last_hit_time = current_time
                        if game_state.p_health <= 0:
                            game_state.game_over = True
                            game_state.p_health = 0

                # Check if enemy stepped on a freeze trap
                if [new_row, new_col] in game_state.freeze_trap_pos:
                    game_state.ene_freeze_T[i] = current_time
            else:
                # Blocked, try turning around
                opposite_dir = (direction + 2) % 4
                test_row, test_col = row, col

                if opposite_dir == 0:  # North
                    test_row -= 1
                elif opposite_dir == 1:  # East
                    test_col += 1
                elif opposite_dir == 2:  # South
                    test_row += 1
                elif opposite_dir == 3:  # West
                    test_col -= 1

                # Check if we can move in the opposite direction
                if (0 <= test_row < len(maze) and
                        0 <= test_col < len(maze[0]) and
                        (maze[test_row][test_col] == 0 or maze[test_row][test_col] == 3)):
                    # Can move in opposite direction
                    game_state.enemies[i][0] = test_row
                    game_state.enemies[i][1] = test_col
                    game_state.enemies[i][2] = opposite_dir
                    game_state.enemies[i][3] = current_time  # Update last move time

                    # Check if enemy stepped on a freeze trap
                    if [test_row, test_col] in game_state.freeze_trap_pos:
                        game_state.ene_freeze_T[i] = current_time
                else:
                    # Can't backtrack, try other directions
                    for offset in [1, 3, 2]:  # Try right, left, then opposite
                        test_dir = (direction + offset) % 4
                        test_row, test_col = row, col

                        if test_dir == 0:  # North
                            test_row -= 1
                        elif test_dir == 1:  # East
                            test_col += 1
                        elif test_dir == 2:  # South
                            test_row += 1
                        elif test_dir == 3:  # West
                            test_col -= 1

                        if (0 <= test_row < len(maze) and
                                0 <= test_col < len(maze[0]) and
                                (maze[test_row][test_col] == 0 or maze[test_row][test_col] == 3)):
                            # Found another valid direction
                            game_state.enemies[i][0] = test_row
                            game_state.enemies[i][1] = test_col
                            game_state.enemies[i][2] = test_dir
                            game_state.enemies[i][3] = current_time  # Update last move time

                            # Check if enemy stepped on a freeze trap
                            if [test_row, test_col] in game_state.freeze_trap_pos:
                                game_state.ene_freeze_T[i] = current_time
                            break

        # Update move timer
        game_state.enemies[i][3] = current_time

def draw_enemies():
    """Draw all enemies at their current positions"""
    if not game_state.enemies:  # Check if enemies list is empty
        return
        
    wall_size = GRID_LENGTH * 2 // 15
    maze = mazes[game_state.crnt_lev]
    offset = len(maze) * wall_size // 2

    for i, enemy in enumerate(game_state.enemies):
        if not enemy or len(enemy) < 3:  # Check if enemy data is valid
            continue
            
        row, col, direction = enemy[0], enemy[1], enemy[2]
        # Calculate center position of this cell
        x = col * wall_size - offset + wall_size / 2
        z = row * wall_size - offset + wall_size / 2

        # More pronounced hovering and bobbing effect
        current_time = get_elapsed_time() % 2000
        height_offset = 200 + 20 * math.sin(current_time * 0.003)

        # Get rotation angle for this enemy
        rotation_angle = game_state.enemy_rotations[i] if i < len(game_state.enemy_rotations) else 0.0

        # Draw enemy with rotation
        draw_enemy(x, height_offset, z, rotation_angle, i)

        # Draw shadow beneath enemy
        glPushMatrix()
        glTranslatef(x, 11.0, z)  # Just above floor
        glColor4f(0.0, 0.0, 0.0, 0.5)  # Semi-transparent black
        glScalef(1.0, 0.1, 1.0)  # Flatten to make a shadow
        glutSolidSphere(wall_size / 3, 12, 8)
        glPopMatrix()

def draw_enemy(x, y, z, rotation_angle, i):
    """Draw an enemy at the specified position with rotating guns - using different shapes"""
    if not game_state.ene_freeze_T or i >= len(game_state.ene_freeze_T):  # Safety check
        return
        
    current_time = get_elapsed_time()
    is_frozen = game_state.ene_freeze_T[i] > 0 and (game_state.cheat_mode or current_time - game_state.ene_freeze_T[i] < FREEZE_DURATION)
    wall_size = GRID_LENGTH * 2 // 15

    # Check if this is the boss (level 3)
    is_boss = game_state.crnt_lev == 2 and game_state.enemies and len(game_state.enemies) > 0 and len(game_state.enemies[0]) > 5

    # Increase size for better visibility, make boss bigger
    if is_boss:
        body_radius = wall_size / 1.5  # Much larger for boss
        head_radius = wall_size / 3  # Larger for boss
        gun_radius = wall_size / 8  # Larger for boss
        Gun_Len = wall_size  # Longer guns for boss
    else:
        body_radius = wall_size / 3  # Normal size for regular enemies
        head_radius = wall_size / 5
        gun_radius = wall_size / 14
        Gun_Len = wall_size / 2

    glPushMatrix()
    glTranslatef(x, y, z)  # Apply the position

    # Apply rotation for spinning effect
    glRotatef(rotation_angle, 0, 1, 0)

    quadric = gluNewQuadric()
    if not quadric:  # Safety check for quadric
        glPopMatrix()
        return

    # Body - Unified new shape: Icosahedron with richer red
    glColor3f(0.85, 0.12, 0.12)  # Richer reddish tone for enemy body
    glPushMatrix()
    glScalef(body_radius, body_radius, body_radius)
    glutSolidIcosahedron()  # New enemy body shape
    glPopMatrix()

    # Head - Use different shapes for different enemies
    glPushMatrix()
    glTranslatef(0, body_radius + head_radius * 0.5, 0)
    
    if i % 3 == 0:  # First type: Cone head
        glColor3f(0.4, 0.3, 0.3)  # Charcoal with warm tint
        glRotatef(-90, 1, 0, 0)  # Point cone upward
        glutSolidCone(head_radius, head_radius * 1.5, 8, 3)
    elif i % 3 == 1:  # Second type: Sphere head
        glColor3f(0.35, 0.3, 0.3)  # Warm dark gray
        glutSolidSphere(head_radius, 16, 16)
    else:  # Third type: Cube head
        glColor3f(0.4, 0.32, 0.32)  # Warm medium gray
        glutSolidCube(head_radius * 1.5)
    
    glPopMatrix()

    # Guns - Use different shapes and colors for different enemies
    if i % 3 == 0:  # First type: Cylindrical guns
        glColor3f(0.8, 0.75, 0.75)  # Light gray with warm tint
        gun_shape = "cylinder"
    elif i % 3 == 1:  # Second type: Conical guns
        glColor3f(0.9, 0.7, 0.6)  # Warm peach
        gun_shape = "cone"
    else:  # Third type: Cuboid guns
        glColor3f(0.8, 0.7, 0.75)  # Lavender-rose gray
        gun_shape = "cube"

    # Guns attached to all four sides of body
    # Gun on right side (+X)
    glPushMatrix()
    glTranslatef(body_radius * 0.5, 0, 0)
    glRotatef(90, 0, 1, 0)  # Rotate to point right (+X)
    if gun_shape == "cylinder":
        gluCylinder(quadric, gun_radius, gun_radius, Gun_Len, 12, 2)
    elif gun_shape == "cone":
        glutSolidCone(gun_radius, Gun_Len, 8, 3)
    else:  # cube
        glutSolidCube(Gun_Len * 0.8)
    glPopMatrix()

    # Gun on left side (-X)
    glPushMatrix()
    glTranslatef(-body_radius * 0.5, 0, 0)
    glRotatef(-90, 0, 1, 0)  # Rotate to point left (-X)
    if gun_shape == "cylinder":
        gluCylinder(quadric, gun_radius, gun_radius, Gun_Len, 12, 2)
    elif gun_shape == "cone":
        glutSolidCone(gun_radius, Gun_Len, 8, 3)
    else:  # cube
        glutSolidCube(Gun_Len * 0.8)
    glPopMatrix()

    # Gun on front side (+Z)
    glPushMatrix()
    glTranslatef(0, 0, body_radius * 0.5)
    glRotatef(0, 0, 1, 0)  # Rotate to point forward (+Z)
    if gun_shape == "cylinder":
        gluCylinder(quadric, gun_radius, gun_radius, Gun_Len, 12, 2)
    elif gun_shape == "cone":
        glutSolidCone(gun_radius, Gun_Len, 8, 3)
    else:  # cube
        glutSolidCube(Gun_Len * 0.8)
    glPopMatrix()

    # Gun on back side (-Z)
    glPushMatrix()
    glTranslatef(0, 0, -body_radius * 0.5)
    glRotatef(180, 0, 1, 0)  # Rotate to point backward (-Z)
    if gun_shape == "cylinder":
        gluCylinder(quadric, gun_radius, gun_radius, Gun_Len, 12, 2)
    elif gun_shape == "cone":
        glutSolidCone(gun_radius, Gun_Len, 8, 3)
    else:  # cube
        glutSolidCube(Gun_Len * 0.8)
    glPopMatrix()

    if is_frozen:
        glColor4f(0.7, 0.9, 0.95, 0.6)  # Soft sky blue
        glutSolidSphere(body_radius * 1.2, 12, 12)

        # Draw ice crystals on the enemy
        for j in range(4):
            angle = j * 90
            glPushMatrix()
            glRotatef(angle, 0, 1, 0)
            glTranslatef(body_radius * 0.8, 0, 0)
            glColor4f(0.8, 0.95, 0.98, 0.8)  # Soft ice crystal color
            glutSolidCone(body_radius * 0.3, body_radius * 0.6, 6, 3)
            glPopMatrix()
    glPopMatrix()
