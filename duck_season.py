#* libraries
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import *
import random
import time

''' x=width (left-right)
    y=depth (forward-backward)
    z=height (up-down) '''

#* Game variables
CAM_X = 0
CAM_Y = -100
CAM_Z = 100

PLAYER_X = -100
PLAYER_Y = -100
PLAYER_Z = 25
PLAYER_R = -90    #? Player rotation
PLAYER_SPEED = 10

LOOK_X = 0
LOOK_Y = 200
LOOK_Z = 25
LOOK_SPEED_X = 10
LOOK_SPEED_Z = 50
LOOK_DELTA_ANGLE = 5

GROUND_X = 1000    #? half of ground length
GROUND_Y = 1000     #? half of ground width

SKYBOX_HEIGHT = 1000

TREE_TRUNK_RADIUS = 10
TREE_TRUNK_HEIGHT = 50
TREE_LEAVES_RADIUS = 30
TREE_LEAVES_HEIGHT = 50

FOV_Y = 90

MOVE_FORWARD = False
MOVE_BACKWARD = False
MOVE_LEFT = False
MOVE_RIGHT = False

AIM_LEFT = False
AIM_RIGHT = False

DUCK_COUNT = 20
DUCK_FLYING_Z = 500
DUCKS = [[random.uniform(-500, 500),
          random.uniform(-500, 500), 
          random.uniform(DUCK_FLYING_Z + DUCK_FLYING_Z/4, 
                         DUCK_FLYING_Z - DUCK_FLYING_Z/4)]
          for _ in range(DUCK_COUNT)]

# Color Variables
duck_light_gray = (0.7, 0.7, 0.7)
duck_med_gray = (0.6, 0.6, 0.6)
duck_medium_gray = (0.5, 0.5, 0.5)
duck_dark_gray = (0.3, 0.3, 0.3)
eye_black = (0.0, 0.0, 0.0)

# Gun Color Variables
gun_brown = (0.35, 0.15, 0.0) 
gun_dark_brown = (0.2, 0.1, 0.0)
gun_black = (0.1, 0.1, 0.1)




#TODO - GameObjects
class Duck:
    def __init__(self, x, y, z):
        self.position = (x, y, z)
        self.wing_flapping_angle = 0
        self.state = 'flying'
        self.wing_angle = 0.0


    def draw_duck(self):
        global duck_dark_gray, duck_light_gray, duck_med_gray, duck_medium_gray, eye_black

        glPushMatrix()
        if self.state == 'dead':
            glRotatef(180, 1, 0, 0)
        
        if self.state == 'falling':
            glRotatef(90, 1, 0, 0)

        # Body
        glPushMatrix()
        glColor3f(*duck_light_gray)
        glScalef(1.5, 1, 2.5)
        glTranslatef(0, 0, 0)
        glutSolidCube(1.5)
        glPopMatrix()

        # Neck
        glPushMatrix()
        glColor3f(*duck_dark_gray)
        glScalef(0.7, 0.5, 0.7)
        glTranslatef(0, 0.6, 3)
        glutSolidCube(1.0)
        glPopMatrix()

        # Head
        glPushMatrix()
        glColor3f(*duck_med_gray)
        glScalef(1.1, 1.0, 1.0)
        glTranslatef(0, 0.4, 2.8)
        glutSolidCube(1.0)
        glPopMatrix()

        # Beak
        glPushMatrix()
        glColor3f(*duck_dark_gray)
        glScalef(0.6, 0.2, 0.5)
        glTranslatef(0, 0.6, 6.7)
        glutSolidCube(1)
        glPopMatrix()

        # Left eye
        glPushMatrix()
        glColor3f(*eye_black)
        glScalef(0.2, 0.2, 0.2)
        glTranslatef(-2.5, 3.6, 15.0)
        glutSolidCube(1.0)
        glPopMatrix()
        
        # Right eye
        glPushMatrix()
        glColor3f(*eye_black)
        glScalef(0.2, 0.2, 0.2)
        glTranslatef(2.5, 3.6, 15.0)
        glutSolidCube(1.0)
        glPopMatrix()


        self.wing_delta = 25 * sin(radians(self.wing_angle))
        
        # Left wing
        glPushMatrix()
        glColor3f(*duck_medium_gray)
        glTranslatef(-1.5, 0.4, 0.0)
        if self.state == 'flying':
            glRotatef(self.wing_delta - 30, 0, 0, 1)
        glScalef(1.9, 0.2, 1.0)
        glutSolidCube(1.5)
        glPopMatrix()

        # Right wing
        glPushMatrix()
        glColor3f(*duck_medium_gray)
        glTranslatef(1.7, 0.4, 0.0)
        if self.state == 'flying':
            glRotatef(-self.wing_delta + 30, 0, 0, 1)
        glScalef(1.9, 0.2, 1.0)
        glutSolidCube(1.5)
        glPopMatrix()

        # Left leg
        glPushMatrix()
        glColor3f(*duck_dark_gray)
        glScalef(0.3, 1.0, 0.3)
        glTranslatef(-2.0, -1.2, -1.0)
        glutSolidCube(1.0)
        glPopMatrix()

        # Right leg
        glPushMatrix()
        glColor3f(*duck_dark_gray)
        glScalef(0.3, 1.0, 0.3)
        glTranslatef(2.0, -1.2, -1.0)
        glutSolidCube(1.0)
        glPopMatrix()

        # Tail
        glPushMatrix()
        glColor3f(*duck_dark_gray)
        glTranslatef(0, -0.2, -2.0)
        glRotatef(20, 1, 0, 0)
        glScalef(1.8, 0.3, 2.4)
        glutSolidCube(1.0)
        glPopMatrix()
        glPopMatrix()

    def drop_duck(self):

        '''If bullet hits the duck, the state changes into falling.
        So at collision of bullet and duck, call this function.'''

        self.state = 'falling'
        self.wing_angle = 0.0

    def dead_duck(self):               
        
        '''If falling duck hits ground state changes to dead.
        So when at collision with ground, call this function.'''

        self.state = 'dead'
        self.wing_angle = 0.0




#! Duck Falling
#! Duck Landed





#* draw_duck placeholder
def draw_duck(x, y, z, state):  #? x,y,z, (flying/falling/landed)
    glPushMatrix()
    glTranslatef(x, y, z)

    if state == "flying":
        # Draw the duck in a flying position
        glColor3f(1.0, 1.0, 0.0)  # Yellow color for the duck
        glPushMatrix()
        glRotate(random.uniform(radians(0), radians(359)), 0, 0, 1)
        glutSolidSphere(5, 10, 10)  # Draw the duck's body
        glPopMatrix()

    elif state == "falling":
        # Draw the duck in a falling position
        glColor3f(1.0, 0.0, 0.0)  # Red color for the duck
        glutSolidSphere(5, 10, 10)  # Draw the duck's body
    elif state == "landed":
        # Draw the duck in a landed position
        glColor3f(0.0, 0.0, 0.0)  # Black color for the duck
        glutSolidSphere(5, 10, 10)  # Draw the duck's body

    glPopMatrix()

# Dog(?)
# Wolves(?)

#! Rifle
def draw_shotgun_model():
    # Stock (main wooden part)
    glPushMatrix()
    glColor3f(*gun_brown)
    glTranslatef(0.3, -0.3, 1.9)
    glScalef(0.4, 0.8, 2.0)
    glRotate(20, 1, 0, 0)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Body (receiver)
    glPushMatrix()
    glColor3f(*gun_black)
    glTranslatef(0.3, -0.2, 0.7)
    glScalef(0.5, 0.8, 1.3)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Handle (trigger handle)
    glPushMatrix()
    glColor3f(*gun_black)
    glTranslatef(0.25, -0.48, 0.0)
    glScalef(0.5, 1.2, 0.5)
    glutSolidCube(1.0)
    glPopMatrix()

    # Trigger Guard (a thin part under the body)
    glPushMatrix()
    glColor3f(*gun_black)
    glTranslatef(0.3, -0.5, -0.5)
    glScalef(0.4, 0.4, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Pump (front sliding part)
    glPushMatrix()
    glColor3f(*gun_dark_brown)
    glTranslatef(0.25, -0.15, -1.0)
    glScalef(1.0, 0.5, 1.8)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Magazine Tube (under the barrel)
    glPushMatrix()
    glColor3f(*gun_black)
    glTranslatef(0.25, -0.3, -1.5)
    glScalef(0.4, 0.4, 3.0)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Barrel (the longest part)
    glPushMatrix()
    glColor3f(*gun_black)
    glTranslatef(0.25, 0.1, -2.5)
    glScalef(0.4, 0.4, 4.0)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Sights (small parts on top of the barrel)
    glPushMatrix()
    glColor3f(*gun_black)
    glTranslatef(0.25, 0.3, -4.3)
    glScalef(0.1, 0.2, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()



#! Bullet
#* Tree
def draw_tree(x,y):
    glPushMatrix()  #? transform start

    glTranslatef(x, y, 0)

    #* tree leaves
    glPushMatrix()

    glTranslatef(0, 0, TREE_TRUNK_HEIGHT)  #? Move to the top of the trunk
    glColor3f(0.0, 0.5, 0.0)  #? Green color for leaves
    gluCylinder(gluNewQuadric(), TREE_LEAVES_RADIUS, 0, TREE_LEAVES_HEIGHT, 12, 1)  # parameters are: quadric, base radius, top radius, height, slices, stacks
    
    glPopMatrix()

    #*tree trunk
    glPushMatrix()

    glColor3f(0.5, 0.35, 0.05)  #? Brown color for trunk
    gluCylinder(gluNewQuadric(), TREE_TRUNK_RADIUS, TREE_TRUNK_RADIUS, TREE_TRUNK_HEIGHT, 12, 1)  # parameters are: quadric, base radius, top radius, height, slices, stacks
    
    glPopMatrix()
    
    glPopMatrix()   #? transform end

#! Shop


#TODO - Play Area
# Surface
def draw_surface():
    glBegin(GL_QUADS)
    glColor3f(0.0, 1, 0.0)  # Green color for grass
    glVertex3f(-GROUND_X, -GROUND_Y, 0)
    glVertex3f(GROUND_X, -GROUND_Y, 0)
    glVertex3f(GROUND_X, GROUND_Y, 0)
    glVertex3f(-GROUND_X, GROUND_Y, 0)
    glEnd()

#! Border
#! Shop

#TODO - UI
#! Ammo count
#! Money display
#! Shop UI - numbers corresponding to items
#! Crosshair

#TODO Implement game logic
#! Duck flying
#! Duck falling
#! Duck landed
# Dog AI
# Wolf AI
#! Rifle mechanics
#! Bullet mechanics
#! Border interactions
#! Shop interactions

#? saif kutta
#TODO Controls
def move_forward(): 
    global PLAYER_X, PLAYER_Y, PLAYER_Z
    move_x = PLAYER_X - (PLAYER_SPEED * cos(radians(PLAYER_R)))
    move_y = PLAYER_Y - (PLAYER_SPEED * sin(radians(PLAYER_R)))
    if -GROUND_X <= abs(move_x) <= GROUND_X:
        PLAYER_X = move_x
    if -GROUND_Y <= abs(move_y) <= GROUND_Y:
        PLAYER_Y = move_y
        print("move forward")
        print(PLAYER_X, PLAYER_Y)

def move_backward():
    global PLAYER_X, PLAYER_Y, PLAYER_Z
    move_x = PLAYER_X + (PLAYER_SPEED * cos(radians(PLAYER_R)))
    move_y = PLAYER_Y + (PLAYER_SPEED * sin(radians(PLAYER_R)))
    if -GROUND_X <= abs(move_x) <= GROUND_X:
        PLAYER_X = move_x
    if -GROUND_Y <= abs(move_y) <= GROUND_Y:
        PLAYER_Y = move_y
        print("move backward")
        print(PLAYER_X, PLAYER_Y)

def move_left():
    global PLAYER_X, PLAYER_Y, PLAYER_Z
    move_x = PLAYER_X - (PLAYER_SPEED * cos(radians(PLAYER_R + 90)))
    move_y = PLAYER_Y - (PLAYER_SPEED * sin(radians(PLAYER_R + 90)))
    if -GROUND_X <= abs(move_x) <= GROUND_X:
        PLAYER_X = move_x
    if -GROUND_Y <= abs(move_y) <= GROUND_Y:
        PLAYER_Y = move_y
        print("move left")
        print(PLAYER_X, PLAYER_Y)

def move_right():
    global PLAYER_X, PLAYER_Y, PLAYER_Z
    move_x = PLAYER_X + (PLAYER_SPEED * cos(radians(PLAYER_R + 90)))
    move_y = PLAYER_Y + (PLAYER_SPEED * sin(radians(PLAYER_R + 90)))
    if -GROUND_X <= abs(move_x) <= GROUND_X:
        PLAYER_X = move_x
    if -GROUND_Y <= abs(move_y) <= GROUND_Y:
        PLAYER_Y = move_y
        print("move right")
        print(PLAYER_X, PLAYER_Y)

#! Movement keys (WASD) + Shop menu (numbers)
def keyboardListener(key, _x, _y):
    #TODO assign movement
    global PLAYER_X, PLAYER_Y, PLAYER_Z
    global LOOK_X, LOOK_Y, LOOK_Z
    global MOVE_FORWARD, MOVE_BACKWARD, MOVE_LEFT, MOVE_RIGHT

    if key == b'w':
        move_forward()
    if key == b's':
        move_backward()
    if key == b'a':
        move_left()
    if key == b'd':
        move_right()

    if key == b' ':
        # Shoot
        print("Shoot")

    #TODO assign shop menu

    if key == b'1':
        pass
    elif key == b'2':
        pass
    elif key == b'3':
        pass
    elif key == b'4':
        pass

# 
def specialKeyListener(key, _x, _y):
    # assign look around
    # global LOOK_X, LOOK_Y, LOOK_Z
    # if key == GLUT_KEY
    #     LOOK_Z += 1 * LOOK_SPEED
    # elif key == GLUT_KEY_DOWN:
    #     LOOK_Z -= 1 * LOOK_SPEED        
    # elif key == GLUT_KEY_LEFT:
    #     LOOK_X -= 1 * LOOK_SPEED
    # elif key == GLUT_KEY_RIGHT:
    #     LOOK_X += 1 * LOOK_SPEED
    pass

#* camera movement (mouse buttons)
def mouseListener(button, state, _x, _y):
    #TODO assign shooting
    global LOOK_X, LOOK_Y, LOOK_Z
    global AIM_LEFT, AIM_RIGHT

    if button == 0 and state == GLUT_DOWN:
        #* aim left
        AIM_LEFT = True
    if button == 0 and state == GLUT_UP:
        AIM_LEFT = False

    if button == 2 and state == GLUT_DOWN:
        #* aim right
        AIM_RIGHT = True
    if button == 2 and state == GLUT_UP:
        AIM_RIGHT = False

    if button == 3 and state == GLUT_DOWN:
        #* aim up
        print("Aim Up")
        LOOK_Z = min(LOOK_Z + (1 * LOOK_SPEED_Z), SKYBOX_HEIGHT)
        pass

    if button == 4 and state == GLUT_DOWN:
        #* aim down
        print("Aim Down")
        LOOK_Z = max(LOOK_Z - (1 * LOOK_SPEED_Z), -SKYBOX_HEIGHT)
        pass

#TODO Finishing touch

def devDebug():
    if not hasattr(devDebug, "last_print_time"):
        devDebug.last_print_time = time.time()

    current_time = time.time()
    if current_time - devDebug.last_print_time >= 100.0:
        x, y, z = PLAYER_X, PLAYER_Y, PLAYER_Z
        print(
            f"{glutGet(GLUT_ELAPSED_TIME)} : Player Currently At - X={x:.2f} Y={y:.2f} Z={z:.2f}"
        )

# camera
def setupCamera():
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    gluPerspective(FOV_Y, 16/9, 0.1, 2500) # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    #TODO camera position and orientation

    gluLookAt(PLAYER_X, PLAYER_Y, PLAYER_Z,  # Camera position
              PLAYER_X + LOOK_X , PLAYER_Y + LOOK_Y + 1, LOOK_Z,  # Look at point
              0, 0, 1)  # Up vector
    
#* display function -> draw
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, 0.9, 0.9, 0.5)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1280, 720)  # Set viewport size

    #TODO setupCamera()
    setupCamera()

    # Draw the surface and a tree so something is visible
    draw_surface()
    draw_tree(0, 0)

    for duck in DUCKS:
        x = duck[0]
        y = duck[1]
        z = duck[2]
        state = "flying"
        draw_duck(x, y, z, state)

    glPushMatrix()
    glTranslatef(0, 0, 1000)
    glutSolidCube(10)
    glPopMatrix()

    # Display game info text at a fixed screen position
    # draw_text(10, 770, f"A Random Fixed Position Text")
    # draw_text(10, 740, f"See how the position and variable change?: {enemy_body_radius}")
    glutSwapBuffers()

#* idle function -> animate
def idle():
    global LOOK_X, LOOK_Y, LOOK_Z
    global PLAYER_X, PLAYER_Y, PLAYER_Z, PLAYER_R, PLAYER_SPEED
    
    #* Player aiming
    if AIM_LEFT:
        aim_x = LOOK_X * cos(radians(LOOK_DELTA_ANGLE)) - LOOK_Y * sin(radians(LOOK_DELTA_ANGLE))
        aim_y = LOOK_X * sin(radians(LOOK_DELTA_ANGLE)) + LOOK_Y * cos(radians(LOOK_DELTA_ANGLE))
        LOOK_X, LOOK_Y = aim_x, aim_y
        PLAYER_R += LOOK_DELTA_ANGLE    #? Update player rotation
        print(PLAYER_R)
        print("Aim Left")

    if AIM_RIGHT:
        aim_x = LOOK_X * cos(radians(-LOOK_DELTA_ANGLE)) - LOOK_Y * sin(radians(-LOOK_DELTA_ANGLE))
        aim_y = LOOK_X * sin(radians(-LOOK_DELTA_ANGLE)) + LOOK_Y * cos(radians(-LOOK_DELTA_ANGLE))
        LOOK_X, LOOK_Y = aim_x, aim_y
        PLAYER_R -= LOOK_DELTA_ANGLE    #? Update player rotation
        print(PLAYER_R)
        print("Aim Right")


    # -------- Duck animation --------- #
    global ducks
    for d in ducks:
        if d.state == 'flying':
            d.wing_angle += 5.0
    # ---------------------------------- #

    #TODO update game state
    devDebug()

    glutPostRedisplay()  # Request a redraw

#bruh wasnt sure where to add so pasting it here (may have overdone stuff and maybe it wont work :v ) : 
#HUD ----------->
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, time, random


class HUD:
    def __init__(self):
        #stats
        self.score = 0
        self.ammo = 10
        self.health = 100
        self.level = 1
        self.magazine_size = 10
        self.last_hit_time = 0
        self.crosshair_size = 10
        self.messages = []  # floating text
        self.start_time = time.time()

        #UI
        self.menu = False
        self.shop_active = False
        self.reticle_good = True

        #features
        self.skin = "default"
        self.armor = False
        self.night_vision = False

        #advanced features
        self.stamina = 100
        self.max_stamina = 100
        self.is_sprinting = False

        self.xp = 0
        self.xp_to_next = 100

        self.weapons = ["Sniper", "Shotgun", "Pistol"]
        self.current_weapon = 0

        self.achievements = []
        self.active_achievements = []  

        #minimap objects
        self.player_pos = (0, 0)
        self.duck_positions = []  

    #basic mechanics
    def add_score(self, value, distance=1.0):
        gained = int(value * distance)
        self.score += gained
        self.messages.append((f"+{gained} pts", time.time()))
        self.gain_xp(gained)

    def damage(self, value):
        self.health = max(0, self.health - value)
        self.last_hit_time = time.time()
        self.messages.append((f"-{value} HP", time.time()))
        if self.health <= 0:
            self.unlock_achievement("Game Over Survivor")

    def reload(self):
        self.ammo = self.magazine_size
        self.messages.append(("Reloaded", time.time()))

    def shoot(self):
        if self.ammo > 0:
            self.ammo -= 1
            return True
        else:
            self.messages.append(("Out of Ammo!", time.time()))
            return False

    def next_level(self):
        self.level += 1
        self.messages.append((f"Level {self.level}", time.time()))
        self.xp = 0
        self.xp_to_next = int(self.xp_to_next * 1.2)

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_to_next:
            self.next_level()

    #achievements
    def unlock_achievement(self, name):
        if name not in self.achievements:
            self.achievements.append(name)
            self.active_achievements.append((name, time.time()))

    #drawing Helpers
    def draw_text(self, x, y, text, font=GLUT_BITMAP_HELVETICA_18):
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))

    def draw_bar(self, x, y, w, h, value, max_value, color=(0, 1, 0)):
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + (w * (value / max_value)), y)
        glVertex2f(x + (w * (value / max_value)), y + h)
        glVertex2f(x, y + h)
        glEnd()
        #outline
        glColor3f(1, 1, 1)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()

    #minimap
    def render_minimap(self, window_w, window_h):
        size = 120
        cx, cy = window_w - size - 20, window_h - size - 20
        #background
        glColor3f(0.1, 0.1, 0.1)
        glBegin(GL_QUADS)
        glVertex2f(cx, cy)
        glVertex2f(cx + size, cy)
        glVertex2f(cx + size, cy + size)
        glVertex2f(cx, cy + size)
        glEnd()
        #border
        glColor3f(1, 1, 1)
        glBegin(GL_LINE_LOOP)
        glVertex2f(cx, cy)
        glVertex2f(cx + size, cy)
        glVertex2f(cx + size, cy + size)
        glVertex2f(cx, cy + size)
        glEnd()

        #player dot
        px, py = self.player_pos
        glColor3f(0, 1, 0)
        glBegin(GL_POINTS)
        glVertex2f(cx + size / 2, cy + size / 2)
        glEnd()

        #ducks as red dots
        glColor3f(1, 0, 0)
        glBegin(GL_POINTS)
        for dx, dy in self.duck_positions:
            mx = cx + size / 2 + dx * 0.1
            my = cy + size / 2 + dy * 0.1
            glVertex2f(mx, my)
        glEnd()

    #render
    def render(self, window_w, window_h):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_w, 0, window_h)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_LIGHTING)
        now = time.time()

        #score, ammo, health
        glColor3f(1, 1, 1)
        self.draw_text(20, window_h - 30, f"Score: {self.score}")
        self.draw_text(20, window_h - 55, f"Ammo: {self.ammo}/{self.magazine_size}")
        self.draw_text(20, window_h - 80, f"Health: {self.health}")
        self.draw_text(20, window_h - 105, f"Level: {self.level}")

        #bars
        self.draw_bar(20, 40, 200, 15, self.stamina, self.max_stamina, (0, 0.7, 1))  # stamina
        self.draw_text(20, 60, "Stamina")

        self.draw_bar(20, 20, 200, 15, self.xp, self.xp_to_next, (1, 1, 0))  # XP
        self.draw_text(20, 5, "XP")

        #crosshair
        cx, cy = window_w // 2, window_h // 2
        size = self.crosshair_size
        glColor3f(0.1, 1.0 if self.reticle_good else 0.2, 0.1 if self.reticle_good else 0.2)
        glBegin(GL_LINES)
        glVertex2f(cx - size, cy)
        glVertex2f(cx + size, cy)
        glVertex2f(cx, cy - size)
        glVertex2f(cx, cy + size)
        glEnd()

        #minimap
        self.render_minimap(window_w, window_h)

        #floating messages
        active = []
        y_offset = 0
        for msg, t in self.messages:
            if now - t < 2.0:
                glColor3f(1, 1, 0)
                self.draw_text(window_w // 2 - 40, window_h // 2 + 60 + y_offset, msg)
                y_offset += 20
                active.append((msg, t))
        self.messages = active

        #achievements
        ach_active = []
        y = window_h - 150
        for name, t in self.active_achievements:
            if now - t < 3.0:
                alpha = 1 - ((now - t) / 3.0)
                glColor3f(0, 1, alpha)
                self.draw_text(window_w // 2 - 100, y, f"Achievement Unlocked: {name}")
                y -= 20
                ach_active.append((name, t))
        self.active_achievements = ach_active

        #damage
        if now - self.last_hit_time < 0.5:
            alpha = 1 - ((now - self.last_hit_time) / 0.5)
            glColor4f(1, 0, 0, alpha)
            glBegin(GL_QUADS)
            glVertex2f(0, 0)
            glVertex2f(window_w, 0)
            glVertex2f(window_w, window_h)
            glVertex2f(0, window_h)
            glEnd()

        #weapon icons
        x = window_w - 200
        for i, weapon in enumerate(self.weapons):
            glColor3f(1, 1, 1 if i == self.current_weapon else 0.3)
            glBegin(GL_QUADS)
            glVertex2f(x + i * 60, 40)
            glVertex2f(x + i * 60 + 50, 40)
            glVertex2f(x + i * 60 + 50, 90)
            glVertex2f(x + i * 60, 90)
            glEnd()
            glColor3f(0, 0, 0)
            self.draw_text(x + i * 60 + 10, 65, weapon[0])  # initial as icon

        #restore
        glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    #utilities
    def get_elapsed_time(self):
        return int(time.time() - self.start_time)

    def reset(self):
        self.score = 0
        self.ammo = self.magazine_size
        self.health = 100
        self.level = 1
        self.start_time = time.time()
        self.messages = []
        self.xp = 0
        self.achievements = []
        self.active_achievements = []
#HUD END

# main loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1280, 720)  # Window size
    glutInitWindowPosition(100, 100)  # Window position
    glutCreateWindow(b"Duck Season")  # Create the window

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # Register the idle function to move the bullet automatically

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()
