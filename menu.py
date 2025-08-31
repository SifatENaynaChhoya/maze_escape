"""
Menu system for game start screen and instructions
Refactored with modern UI design patterns and improved visual aesthetics
"""
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from config import *
import game_state
from renderer import draw_text
import math
import time

# Modern color palette
class MenuColors:
    # Primary colors - Deep purple theme
    PRIMARY_DARK = (0.15, 0.12, 0.35)      # Deep purple background
    PRIMARY_LIGHT = (0.25, 0.20, 0.50)     # Lighter purple accent
    
    # Button colors - Vibrant gradients
    BUTTON_PRIMARY = (0.35, 0.65, 0.85)    # Modern cyan blue
    BUTTON_SUCCESS = (0.20, 0.80, 0.45)    # Vibrant green
    BUTTON_DANGER = (0.95, 0.35, 0.45)     # Modern red
    BUTTON_INFO = (0.65, 0.45, 0.85)       # Purple accent
    
    # Text colors
    TEXT_PRIMARY = (0.95, 0.95, 0.98)      # Near white
    TEXT_ACCENT = (0.85, 0.75, 0.95)       # Light purple
    TEXT_HIGHLIGHT = (0.95, 0.85, 0.35)    # Golden yellow
    
    # Background elements
    PANEL_BG = (0.08, 0.08, 0.20)          # Very dark blue
    BORDER_ACCENT = (0.45, 0.35, 0.75)     # Purple border

def setup_2d_projection():
    """Configure OpenGL for 2D menu rendering"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def draw_animated_background():
    """Draw an animated background with subtle effects"""
    # Animated gradient background
    current_time = time.time()
    wave_offset = math.sin(current_time * 0.5) * 0.05
    
    # Draw gradient background
    glBegin(GL_QUADS)
    # Top gradient (darker)
    glColor3f(*(MenuColors.PRIMARY_DARK[0] + wave_offset, 
               MenuColors.PRIMARY_DARK[1] + wave_offset, 
               MenuColors.PRIMARY_DARK[2] + wave_offset))
    glVertex2f(0, 800)
    glVertex2f(1000, 800)
    
    # Bottom gradient (lighter)
    glColor3f(*MenuColors.PANEL_BG)
    glVertex2f(1000, 0)
    glVertex2f(0, 0)
    glEnd()
    
    # Draw subtle animated circles for visual interest
    glColor4f(*MenuColors.BORDER_ACCENT, 0.1)
    for i in range(3):
        center_x = 200 + i * 300
        center_y = 400 + math.sin(current_time + i) * 50
        radius = 80 + math.cos(current_time * 0.7 + i) * 20
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(center_x, center_y)
        for angle in range(0, 361, 10):
            x = center_x + radius * math.cos(math.radians(angle))
            y = center_y + radius * math.sin(math.radians(angle))
            glVertex2f(x, y)
        glEnd()

def draw_modern_button(x, y, width, height, color, text, text_offset_x=None):
    """Draw a modern styled button with subtle shadow and border effects"""
    # Calculate text offset if not provided
    if text_offset_x is None:
        text_offset_x = width // 2 - len(text) * 6
    
    # Draw button shadow
    shadow_offset = 4
    glColor4f(0.0, 0.0, 0.0, 0.3)
    glBegin(GL_QUADS)
    glVertex2f(x + shadow_offset, y - shadow_offset)
    glVertex2f(x + width + shadow_offset, y - shadow_offset)
    glVertex2f(x + width + shadow_offset, y + height - shadow_offset)
    glVertex2f(x + shadow_offset, y + height - shadow_offset)
    glEnd()
    
    # Draw button border
    glColor3f(*MenuColors.BORDER_ACCENT)
    border_width = 2
    glBegin(GL_QUADS)
    glVertex2f(x - border_width, y - border_width)
    glVertex2f(x + width + border_width, y - border_width)
    glVertex2f(x + width + border_width, y + height + border_width)
    glVertex2f(x - border_width, y + height + border_width)
    glEnd()
    
    # Draw main button
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()
    
    # Draw button highlight
    glColor4f(1.0, 1.0, 1.0, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(x, y + height * 0.6)
    glVertex2f(x + width, y + height * 0.6)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()
    
    # Draw button text
    glColor3f(*MenuColors.TEXT_PRIMARY)
    draw_text(x + text_offset_x, y + 15, text, GLUT_BITMAP_HELVETICA_18)

def draw_title_with_effects():
    """Draw clean titles with same style as button text"""
    title_text = "Maze Escape"
    subtitle_text = "3D Adventure"
    
    # Position titles centered to align with START GAME button
    title_x = 440  # Centered around x=500 like the button
    title_y = 670
    subtitle_x = 455  # Centered around x=500 like the button
    
    # Draw main title "Maze Escape" with clean white text like buttons
    glColor3f(0.95, 0.95, 0.98)  # Same white color as button text
    draw_text(title_x, title_y, title_text, GLUT_BITMAP_HELVETICA_18)
    
    # Draw subtitle "3D Adventure" with clean white text like buttons
    glColor3f(0.95, 0.95, 0.98)  # Same white color as button text
    draw_text(subtitle_x, title_y - 35, subtitle_text, GLUT_BITMAP_HELVETICA_18)
    
    # Draw decorative border around title area - centered and adjusted
    current_time = time.time()
    border_pulse = 0.6 + 0.4 * math.sin(current_time * 2.5)
    glColor3f(MenuColors.BORDER_ACCENT[0] * border_pulse,
              MenuColors.BORDER_ACCENT[1] * border_pulse, 
              MenuColors.BORDER_ACCENT[2] * border_pulse)
    glLineWidth(3)
    glBegin(GL_LINE_LOOP)
    glVertex2f(280, 590)
    glVertex2f(720, 590)
    glVertex2f(720, 700)
    glVertex2f(280, 700)
    glEnd()
    glLineWidth(1)

def draw_main_menu_panel():
    """Draw the main menu with modern button layout"""
    # Draw main panel background
    panel_x, panel_y = 300, 150
    panel_width, panel_height = 400, 320
    
    glColor3f(*MenuColors.PANEL_BG)
    glBegin(GL_QUADS)
    glVertex2f(panel_x, panel_y)
    glVertex2f(panel_x + panel_width, panel_y)
    glVertex2f(panel_x + panel_width, panel_y + panel_height)
    glVertex2f(panel_x, panel_y + panel_height)
    glEnd()
    
    # Draw panel border with corner accents
    glColor3f(*MenuColors.BORDER_ACCENT)
    glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    glVertex2f(panel_x, panel_y)
    glVertex2f(panel_x + panel_width, panel_y)
    glVertex2f(panel_x + panel_width, panel_y + panel_height)
    glVertex2f(panel_x, panel_y + panel_height)
    glEnd()
    
    # Draw corner decorations
    corner_size = 15
    corners = [(panel_x, panel_y), (panel_x + panel_width, panel_y),
               (panel_x, panel_y + panel_height), (panel_x + panel_width, panel_y + panel_height)]
    
    glColor3f(*MenuColors.TEXT_HIGHLIGHT)
    for corner_x, corner_y in corners:
        glBegin(GL_TRIANGLES)
        if corner_x == panel_x:  # Left side
            if corner_y == panel_y:  # Bottom left
                glVertex2f(corner_x, corner_y)
                glVertex2f(corner_x + corner_size, corner_y)
                glVertex2f(corner_x, corner_y + corner_size)
            else:  # Top left
                glVertex2f(corner_x, corner_y)
                glVertex2f(corner_x + corner_size, corner_y)
                glVertex2f(corner_x, corner_y - corner_size)
        else:  # Right side
            if corner_y == panel_y:  # Bottom right
                glVertex2f(corner_x, corner_y)
                glVertex2f(corner_x - corner_size, corner_y)
                glVertex2f(corner_x, corner_y + corner_size)
            else:  # Top right
                glVertex2f(corner_x, corner_y)
                glVertex2f(corner_x - corner_size, corner_y)
                glVertex2f(corner_x, corner_y - corner_size)
        glEnd()
    
    glLineWidth(1)
    
    # Draw buttons with improved spacing and styling
    button_y_positions = [380, 310, 240]
    button_colors = [MenuColors.BUTTON_SUCCESS, MenuColors.BUTTON_PRIMARY, MenuColors.BUTTON_DANGER]
    button_texts = ["🎮 START GAME", "📖 INSTRUCTIONS", "❌ EXIT"]
    button_text_offsets = [45, 35, 70]
    
    for i, (y_pos, color, text, text_offset) in enumerate(zip(button_y_positions, button_colors, button_texts, button_text_offsets)):
        # Add subtle animation to buttons
        wave_offset = math.sin(time.time() * 2 + i * 0.5) * 2
        draw_modern_button(350 + wave_offset, y_pos, 300, 60, color, text, text_offset)

def draw_instructions_panel():
    """Draw the instructions screen with improved layout and visual hierarchy"""
    # Draw main instructions panel
    panel_margin = 80
    panel_x, panel_y = panel_margin, panel_margin
    panel_width = 1000 - (panel_margin * 2)
    panel_height = 800 - (panel_margin * 2)
    
    # Background with gradient effect
    glBegin(GL_QUADS)
    glColor3f(*MenuColors.PANEL_BG)
    glVertex2f(panel_x, panel_y)
    glVertex2f(panel_x + panel_width, panel_y)
    
    glColor3f(*MenuColors.PRIMARY_DARK)
    glVertex2f(panel_x + panel_width, panel_y + panel_height)
    glVertex2f(panel_x, panel_y + panel_height)
    glEnd()
    
    # Draw border with animated corners
    current_time = time.time()
    border_glow = 0.4 + 0.1 * math.sin(current_time * 3)
    glColor3f(MenuColors.BORDER_ACCENT[0] * border_glow,
              MenuColors.BORDER_ACCENT[1] * border_glow,
              MenuColors.BORDER_ACCENT[2] * border_glow)
    glLineWidth(3)
    glBegin(GL_LINE_LOOP)
    glVertex2f(panel_x, panel_y)
    glVertex2f(panel_x + panel_width, panel_y)
    glVertex2f(panel_x + panel_width, panel_y + panel_height)
    glVertex2f(panel_x, panel_y + panel_height)
    glEnd()
    glLineWidth(1)
    
    # Enhanced title
    glColor3f(*MenuColors.TEXT_HIGHLIGHT)
    draw_text(300, 620, "🎮 GAME CONTROLS GUIDE", GLUT_BITMAP_TIMES_ROMAN_24)
    
    # Draw instruction sections with better organization
    sections = [
        ("🎯 MOVEMENT & NAVIGATION", [
            "WASD Keys ............ Move Forward/Back/Strafe",
            "Mouse Movement ....... Look Around & Aim",
            "R Key ............... Reset Camera View"
        ]),
        ("⚔️ COMBAT & INTERACTION", [
            "Left Click .......... Fire Weapon",
            "Right Click ......... Toggle View Mode",
            "E Key ............... Interact/Collect Items",
            "Keys 5,6,7 .......... Select Equipment"
        ]),
        ("🛠️ GAME CONTROLS", [
            "Spacebar ............ Pause Game",
            "ESC Key ............. Return to Menu",
            "C Key ............... Toggle Cheat Mode",
            "V Key ............... Wall Phasing (Cheat)"
        ])
    ]
    
    start_y = 550
    section_spacing = 140
    
    for i, (section_title, controls) in enumerate(sections):
        section_y = start_y - (i * section_spacing)
        
        # Draw section header
        glColor3f(*MenuColors.TEXT_ACCENT)
        draw_text(150, section_y, section_title, GLUT_BITMAP_HELVETICA_18)
        
        # Draw section controls
        for j, control in enumerate(controls):
            control_y = section_y - 30 - (j * 25)
            glColor3f(*MenuColors.TEXT_PRIMARY)
            draw_text(170, control_y, control, GLUT_BITMAP_HELVETICA_12)
    
    # Draw enhanced back button
    back_button_x, back_button_y = 400, 80
    draw_modern_button(back_button_x, back_button_y, 200, 60, 
                      MenuColors.BUTTON_SUCCESS, "🔙 BACK TO MENU", 35)

def draw_menu():
    """Main menu drawing function with enhanced visual design"""
    setup_2d_projection()
    draw_animated_background()
    
    if not game_state.show_instructions:
        draw_title_with_effects()
        draw_main_menu_panel()
    else:
        draw_instructions_panel()
    
    glutSwapBuffers()
