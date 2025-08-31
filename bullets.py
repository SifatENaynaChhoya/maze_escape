# """
# Bullet system management for player and enemy bullets
# """
# from OpenGL.GL import *
# from OpenGL.GLUT import *
# from OpenGL.GLU import *
# from config import *
# import game_state
# from maze_data import mazes
# from utils import get_elapsed_time

# def update_bullets():
#     """Update position of all bullets and check collisions"""
#     update_p_bullets()
#     update_enemy_bullets()

# def update_p_bullets():
#     """Update player bullets and check for enemy hits."""
#     current_time = get_elapsed_time()
#     wall_size = GRID_LENGTH * 2 // 15
#     offset = len(mazes[game_state.crnt_lev]) * wall_size // 2

#     new_bullets = []
#     maze = mazes[game_state.crnt_lev]

#     for bullet in game_state.p_bullets:
#         x, y, z, dx, dy, dz, creation_time = bullet

#         # Update position
#         x += dx
#         y += dy
#         z += dz

#         # Convert to maze coordinates
#         col = int((x + offset) / wall_size)
#         row = int((z + offset) / wall_size)

#         # Check if out of bounds or hit wall
#         if (row < 0 or row >= len(maze) or
#                 col < 0 or col >= len(maze[0]) or
#                 maze[row][col] == 1):
#             continue  # Skip this bullet

#         # Check if bullet lifetime expired
#         if current_time - creation_time > BULLET_LIFETIME:
#             continue  # Skip this bullet

#         # Check for enemy hit
#         enemy_hit = False
#         for i, enemy in enumerate(game_state.enemies):
#             enemy_row, enemy_col = enemy[0], enemy[1]
#             is_boss = len(enemy) > 5  # Check if this is the boss
#             enemy_x = enemy_col * wall_size - offset + wall_size / 2
#             enemy_z = enemy_row * wall_size - offset + wall_size / 2
#             enemy_y = 200 if is_boss else 150  # Boss is taller

#             # Calculate distance to enemy
#             if ((enemy_x - x) ** 2 + (enemy_z - z) ** 2 < (wall_size / 3) ** 2 and
#                     abs(y - enemy_y) < wall_size / 2):
#                 if is_boss:
#                     game_state.enemies[i][5] -= 1  # Decrease boss health
#                     if game_state.enemies[i][5] <= 0:
#                         game_state.enemies.pop(i)  # Remove boss when health is zero
#                         game_state.enemy_rotations.pop(i)
#                         game_state.ene_freeze_T.pop(i)
#                         print("Boss defeated!")
#                 else:
#                     game_state.enemies.pop(i)  # Regular enemy dies instantly
#                     game_state.enemy_rotations.pop(i)
#                     game_state.ene_freeze_T.pop(i)
#                 enemy_hit = True
#                 break

#         if enemy_hit:
#             continue  # Skip this bullet

#         # Bullet still active, keep it
#         new_bullets.append([x, y, z, dx, dy, dz, creation_time])

#     game_state.p_bullets = new_bullets

# def update_enemy_bullets():
#     """Update enemy bullets and check for player hits"""
#     current_time = get_elapsed_time()
#     wall_size = GRID_LENGTH * 2 // 15
#     offset = len(mazes[game_state.crnt_lev]) * wall_size // 2

#     new_bullets = []
#     maze = mazes[game_state.crnt_lev]

#     for bullet in game_state.bullets:
#         x, y, z, dx, dy, dz, creation_time, is_player_bullet = bullet

#         # Update position
#         x += dx
#         y += dy
#         z += dz

#         # Convert to maze coordinates
#         col = int((x + offset) / wall_size)
#         row = int((z + offset) / wall_size)

#         # Check if out of bounds or hit wall
#         if (row < 0 or row >= len(maze) or
#                 col < 0 or col >= len(maze[0]) or
#                 maze[row][col] == 1):
#             continue  # Skip this bullet

#         # Check if bullet lifetime expired
#         if current_time - creation_time > BULLET_LIFETIME:
#             continue  # Skip this bullet

#         # Check for player hit
#         player_row, player_col = game_state.p_position
#         player_x = player_col * wall_size - offset + wall_size / 2
#         player_z = player_row * wall_size - offset + wall_size / 2
#         player_y = 150  # Approximate player height

#         if ((player_x - x) ** 2 + (player_z - z) ** 2 < (wall_size / 3) ** 2 and
#                 abs(y - player_y) < wall_size / 2):
#             # Player hit logic
#             if not game_state.cheat_mode and current_time - game_state.p_last_hit_time > P_INVINCIBILITY_T:
#                 game_state.p_health -= 1  # Decrease health by 1 when hit
#                 game_state.p_last_hit_time = current_time
#                 if game_state.p_health <= 0:
#                     game_state.game_over = True
#                     game_state.p_health = 0
#             continue  # Skip this bullet

#         # Bullet still active, keep it
#         new_bullets.append([x, y, z, dx, dy, dz, creation_time, is_player_bullet])

#     game_state.bullets = new_bullets

# def draw_bullets():
#     """Draw all active bullets"""
#     wall_size = GRID_LENGTH * 2 // 15
#     bullet_size = wall_size / 15

#     # Draw enemy bullets (red cubes)
#     for bullet in game_state.bullets:
#         x, y, z = bullet[0], bullet[1], bullet[2]
#         glPushMatrix()
#         glTranslatef(x, y, z)
#         glColor3f(1.0, 0.0, 0.0)  # Red for enemy bullets
#         glutSolidCube(bullet_size)
#         glPopMatrix()

#     # Draw player bullets (pleasant periwinkle spheres)
#     for bullet in game_state.p_bullets:
#         x, y, z = bullet[0], bullet[1], bullet[2]
#         glPushMatrix()
#         glTranslatef(x, y, z)
#         glColor3f(0.7, 0.8, 0.95)  # Soft periwinkle for player bullets
#         glutSolidSphere(bullet_size * 0.8, 8, 8)  # Use sphere for player bullets
#         glPopMatrix()

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

class BulletManager:
    def __init__(self):
        self.wall_size = GRID_LENGTH * 2 // 15

    def update(self):
        self.update_player_bullets()
        self.update_enemy_bullets()

    def update_player_bullets(self):
        current_time = get_elapsed_time()
        offset = len(mazes[game_state.crnt_lev]) * self.wall_size // 2
        maze = mazes[game_state.crnt_lev]
        new_bullets = []
        
        for bullet in game_state.p_bullets:
            old_x, old_y, old_z, dx, dy, dz, creation_time = bullet
            
            # Calculate new position
            new_x, new_y, new_z = self._move_bullet(old_x, old_y, old_z, dx, dy, dz)
            
            # Check if bullet lifetime expired
            if current_time - creation_time > BULLET_LIFETIME:
                continue  # Skip this bullet
            
            # Check for wall collision using proper ray-casting
            if self._check_wall_collision(old_x, old_z, new_x, new_z, offset, maze):
                continue  # Skip this bullet - it hit a wall
            
            # Check for enemy hit
            if self._check_enemy_hit(new_x, new_y, new_z, offset):
                continue  # Skip this bullet - it hit an enemy
            
            # Bullet still active, keep it with new position
            new_bullets.append([new_x, new_y, new_z, dx, dy, dz, creation_time])
        
        game_state.p_bullets = new_bullets

    def update_enemy_bullets(self):
        current_time = get_elapsed_time()
        offset = len(mazes[game_state.crnt_lev]) * self.wall_size // 2
        maze = mazes[game_state.crnt_lev]
        new_bullets = []
        
        for bullet in game_state.bullets:
            old_x, old_y, old_z, dx, dy, dz, creation_time, is_player_bullet = bullet
            
            # Calculate new position
            new_x, new_y, new_z = self._move_bullet(old_x, old_y, old_z, dx, dy, dz)
            
            # Check if bullet lifetime expired
            if current_time - creation_time > BULLET_LIFETIME:
                continue  # Skip this bullet
            
            # Check for wall collision using proper ray-casting
            if self._check_wall_collision(old_x, old_z, new_x, new_z, offset, maze):
                continue  # Skip this bullet - it hit a wall
            
            # Check for player hit
            if self._check_player_hit(new_x, new_y, new_z, offset, current_time):
                continue  # Skip this bullet - it hit the player
            
            # Bullet still active, keep it with new position
            new_bullets.append([new_x, new_y, new_z, dx, dy, dz, creation_time, is_player_bullet])
        
        game_state.bullets = new_bullets

    def draw(self):
        bullet_size = self.wall_size / 15
        idx = 0
        while idx < len(game_state.bullets):
            bullet = game_state.bullets[idx]
            x, y, z = bullet[0], bullet[1], bullet[2]
            glPushMatrix()
            glTranslatef(x, y, z)
            glColor3f(1.0, 0.0, 0.0)
            glutSolidCube(bullet_size)
            glPopMatrix()
            idx += 1
        idx = 0
        while idx < len(game_state.p_bullets):
            bullet = game_state.p_bullets[idx]
            x, y, z = bullet[0], bullet[1], bullet[2]
            glPushMatrix()
            glTranslatef(x, y, z)
            glColor3f(0.7, 0.8, 0.95)
            glutSolidSphere(bullet_size * 0.8, 8, 8)
            glPopMatrix()
            idx += 1

    def _move_bullet(self, x, y, z, dx, dy, dz):
        return x + dx, y + dy, z + dz

    def _maze_coords(self, x, z, offset):
        col = int((x + offset) / self.wall_size)
        row = int((z + offset) / self.wall_size)
        return col, row

    def _is_out_of_bounds(self, row, col, maze):
        return row < 0 or row >= len(maze) or col < 0 or col >= len(maze[0])

    def _is_wall(self, row, col, maze):
        return maze[row][col] == 1
    
    def _check_wall_collision(self, old_x, old_z, new_x, new_z, offset, maze):
        """Check if bullet path from old position to new position intersects with walls"""
        # Get maze coordinates for both positions
        old_col, old_row = self._maze_coords(old_x, old_z, offset)
        new_col, new_row = self._maze_coords(new_x, new_z, offset)
        
        # Check if new position is out of bounds or in a wall
        if (self._is_out_of_bounds(new_row, new_col, maze) or 
            self._is_wall(new_row, new_col, maze)):
            return True
        
        # If bullet didn't change grid cells, no wall collision
        if old_row == new_row and old_col == new_col:
            return False
        
        # Use DDA (Digital Differential Analyzer) algorithm to check all grid cells along the path
        return self._dda_wall_check(old_col, old_row, new_col, new_row, maze)
    
    def _dda_wall_check(self, x0, y0, x1, y1, maze):
        """Digital Differential Analyzer algorithm to check for walls along a line"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        
        x = x0
        y = y0
        
        n = 1 + dx + dy
        x_inc = 1 if x1 > x0 else -1
        y_inc = 1 if y1 > y0 else -1
        error = dx - dy
        
        dx *= 2
        dy *= 2
        
        for _ in range(n):
            # Check current cell for wall
            if (self._is_out_of_bounds(y, x, maze) or self._is_wall(y, x, maze)):
                return True
            
            if error > 0:
                x += x_inc
                error -= dy
            else:
                y += y_inc
                error += dx
        
        return False

    def _check_enemy_hit(self, x, y, z, offset):
        wall_size = self.wall_size
        maze = mazes[game_state.crnt_lev]
        idx = 0
        while idx < len(game_state.enemies):
            enemy = game_state.enemies[idx]
            enemy_row, enemy_col = enemy[0], enemy[1]
            is_boss = len(enemy) > 5
            enemy_x = enemy_col * wall_size - offset + wall_size / 2
            enemy_z = enemy_row * wall_size - offset + wall_size / 2
            enemy_y = 200 if is_boss else 150
            if ((enemy_x - x) ** 2 + (enemy_z - z) ** 2 < (wall_size / 3) ** 2 and
                    abs(y - enemy_y) < wall_size / 2):
                if is_boss:
                    game_state.enemies[idx][5] -= 1
                    if game_state.enemies[idx][5] <= 0:
                        game_state.enemies.pop(idx)
                        game_state.enemy_rotations.pop(idx)
                        game_state.ene_freeze_T.pop(idx)
                        print("Boss defeated!")
                else:
                    game_state.enemies.pop(idx)
                    game_state.enemy_rotations.pop(idx)
                    game_state.ene_freeze_T.pop(idx)
                return True
            idx += 1
        return False

    def _check_player_hit(self, x, y, z, offset, current_time):
        wall_size = self.wall_size
        player_row, player_col = game_state.p_position
        player_x = player_col * wall_size - offset + wall_size / 2
        player_z = player_row * wall_size - offset + wall_size / 2
        player_y = 150
        while ((player_x - x) ** 2 + (player_z - z) ** 2 < (wall_size / 3) ** 2 and
                abs(y - player_y) < wall_size / 2):
            if not game_state.cheat_mode and current_time - game_state.p_last_hit_time > P_INVINCIBILITY_T:
                game_state.p_health -= 1
                game_state.p_last_hit_time = current_time
                if game_state.p_health <= 0:
                    game_state.game_over = True
                    game_state.p_health = 0
            return True
        return False

bullet_manager = BulletManager()

def update_bullets():
    bullet_manager.update()

def draw_bullets():
    bullet_manager.draw()

