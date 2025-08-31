"""
Bullet system management for player and enemy bullets
"""
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from config import *
import game_state
from maze_data import mazes
from utils import get_elapsed_time

def update_bullets():
    """Update position of all bullets and check collisions"""
    update_p_bullets()
    update_enemy_bullets()

def update_p_bullets():
    """Update player bullets and check for enemy hits."""
    current_time = get_elapsed_time()
    wall_size = GRID_LENGTH * 2 // 15
    offset = len(mazes[game_state.crnt_lev]) * wall_size // 2

    new_bullets = []
    maze = mazes[game_state.crnt_lev]

    for bullet in game_state.p_bullets:
        x, y, z, dx, dy, dz, creation_time = bullet

        # Update position
        x += dx
        y += dy
        z += dz

        # Convert to maze coordinates
        col = int((x + offset) / wall_size)
        row = int((z + offset) / wall_size)

        # Check if out of bounds or hit wall
        if (row < 0 or row >= len(maze) or
                col < 0 or col >= len(maze[0]) or
                maze[row][col] == 1):
            continue  # Skip this bullet

        # Check if bullet lifetime expired
        if current_time - creation_time > BULLET_LIFETIME:
            continue  # Skip this bullet

        # Check for enemy hit
        enemy_hit = False
        for i, enemy in enumerate(game_state.enemies):
            enemy_row, enemy_col = enemy[0], enemy[1]
            is_boss = len(enemy) > 5  # Check if this is the boss
            enemy_x = enemy_col * wall_size - offset + wall_size / 2
            enemy_z = enemy_row * wall_size - offset + wall_size / 2
            enemy_y = 200 if is_boss else 150  # Boss is taller

            # Calculate distance to enemy
            if ((enemy_x - x) ** 2 + (enemy_z - z) ** 2 < (wall_size / 3) ** 2 and
                    abs(y - enemy_y) < wall_size / 2):
                if is_boss:
                    game_state.enemies[i][5] -= 1  # Decrease boss health
                    if game_state.enemies[i][5] <= 0:
                        game_state.enemies.pop(i)  # Remove boss when health is zero
                        game_state.enemy_rotations.pop(i)
                        game_state.ene_freeze_T.pop(i)
                        print("Boss defeated!")
                else:
                    game_state.enemies.pop(i)  # Regular enemy dies instantly
                    game_state.enemy_rotations.pop(i)
                    game_state.ene_freeze_T.pop(i)
                enemy_hit = True
                break

        if enemy_hit:
            continue  # Skip this bullet

        # Bullet still active, keep it
        new_bullets.append([x, y, z, dx, dy, dz, creation_time])

    game_state.p_bullets = new_bullets

def update_enemy_bullets():
    """Update enemy bullets and check for player hits"""
    current_time = get_elapsed_time()
    wall_size = GRID_LENGTH * 2 // 15
    offset = len(mazes[game_state.crnt_lev]) * wall_size // 2

    new_bullets = []
    maze = mazes[game_state.crnt_lev]

    for bullet in game_state.bullets:
        x, y, z, dx, dy, dz, creation_time, is_player_bullet = bullet

        # Update position
        x += dx
        y += dy
        z += dz

        # Convert to maze coordinates
        col = int((x + offset) / wall_size)
        row = int((z + offset) / wall_size)

        # Check if out of bounds or hit wall
        if (row < 0 or row >= len(maze) or
                col < 0 or col >= len(maze[0]) or
                maze[row][col] == 1):
            continue  # Skip this bullet

        # Check if bullet lifetime expired
        if current_time - creation_time > BULLET_LIFETIME:
            continue  # Skip this bullet

        # Check for player hit
        player_row, player_col = game_state.p_position
        player_x = player_col * wall_size - offset + wall_size / 2
        player_z = player_row * wall_size - offset + wall_size / 2
        player_y = 150  # Approximate player height

        if ((player_x - x) ** 2 + (player_z - z) ** 2 < (wall_size / 3) ** 2 and
                abs(y - player_y) < wall_size / 2):
            # Player hit logic
            if not game_state.cheat_mode and current_time - game_state.p_last_hit_time > P_INVINCIBILITY_T:
                game_state.p_health -= 1  # Decrease health by 1 when hit
                game_state.p_last_hit_time = current_time
                if game_state.p_health <= 0:
                    game_state.game_over = True
                    game_state.p_health = 0
            continue  # Skip this bullet

        # Bullet still active, keep it
        new_bullets.append([x, y, z, dx, dy, dz, creation_time, is_player_bullet])

    game_state.bullets = new_bullets

def draw_bullets():
    """Draw all active bullets"""
    wall_size = GRID_LENGTH * 2 // 15
    bullet_size = wall_size / 15

    # Draw enemy bullets (red cubes)
    for bullet in game_state.bullets:
        x, y, z = bullet[0], bullet[1], bullet[2]
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(1.0, 0.0, 0.0)  # Red for enemy bullets
        glutSolidCube(bullet_size)
        glPopMatrix()

    # Draw player bullets (pleasant periwinkle spheres)
    for bullet in game_state.p_bullets:
        x, y, z = bullet[0], bullet[1], bullet[2]
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(0.7, 0.8, 0.95)  # Soft periwinkle for player bullets
        glutSolidSphere(bullet_size * 0.8, 8, 8)  # Use sphere for player bullets
        glPopMatrix()
