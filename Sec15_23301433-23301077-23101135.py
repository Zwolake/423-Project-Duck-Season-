#* libraries
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from OpenGL.GLU import *
from math import *
import random
import time

''' x=width (left-right)
    y=depth (forward-backward)
    z=height (up-down) '''

#* Game variables
PLAYER_X = 0    #? player position
PLAYER_Y = 0
PLAYER_Z = 25
PLAYER_R = -90    #? Player rotation
PLAYER_SPEED = 2.5

LOOK_X = 0      #? focus point (changes with player)
LOOK_Y = 200
LOOK_Z = 25
LOOK_SPEED_Z = 20   #? change of vertical focus point
LOOK_DELTA_ANGLE = 2.5  #? degree change of horizontal focus point

GROUND_X = 1000    #? half of ground length
GROUND_Y = 1000     #? half of ground width

SKYBOX_HEIGHT = 1500

TREE_RADIUS = 10
TREE_HEIGHT = 50

FOV_Y = 90

BUTTONS = {'w':False, 's':False, 'a':False, 'd':False}  #? flags for smooth buttons

MOVE_FORWARD = False    #? flags for smooth buttons(2)
MOVE_BACKWARD = False
MOVE_LEFT = False
MOVE_RIGHT = False

AIM_LEFT = False    #? flags for smooth movement(3)
AIM_RIGHT = False

DUCK_COUNT = 20 #? no of ducks in the map
DUCK_FLYING_Z = 500 #? duck flight height
DUCK_WING_SPEED = 10    #? duck flapping speed
DUCK_SPEED = 5  #? duck moving speed
DUCK_SPEED_DELTA = 0.05 #? duck move speed change
DUCK_FALLING_SPEED = 2.5    #? falling duck speed
DUCKS = []  #? duck list
DUCK_HITBOX = 50    #? duck hitbox width

BULLETS = []    #? bullet list
BULLET_SPEED = 100  #? bullet speed

SCORE = 0   #? score + currency

AMMO_COUNT = 8  #? ammo

TREE_COUNT = 1000 #? environment tree count
rand_x = [random.uniform(-GROUND_X, GROUND_X) for _ in range(TREE_COUNT)]
rand_y = [random.uniform(GROUND_Y, -GROUND_Y) for _ in range(TREE_COUNT)]

# Color Variables
duck_light_gray = (0.7, 0.7, 0.7)
duck_med_gray = (0.6, 0.6, 0.6)
duck_medium_gray = (0.5, 0.5, 0.5)
duck_dark_gray = (0.3, 0.3, 0.3)
eye_black = (0.0, 0.0, 0.0)

'''Change these to scale the duck and gun'''
duck_scale = 2.0
gun_scale = 1.0



# Gun Color Variables
gun_brown = (0.35, 0.15, 0.0) 
gun_dark_brown = (0.2, 0.1, 0.0)
gun_black = (0.1, 0.1, 0.1)

# ---------- VIEW HELPERS ----------
def get_view_angles():
    """
    Returns (yaw_deg, pitch_deg) for current camera look vector.
    World up is +Z, forward is +Y.
    yaw: rotation around Z so that +Y is 0°
    pitch: rotation around X (nose up negative to match typical view)
    """
    vx = LOOK_X
    vy = LOOK_Y + 1   # you add +1 in gluLookAt
    vz = LOOK_Z - PLAYER_Z

    xy_len = max(1e-6, (vx*vx + vy*vy)**0.5)

    yaw_deg = -degrees(atan2(vx, vy))         # 0° faces +Y, +90° faces +X
    pitch_deg = -degrees(atan2(vz, xy_len))  # nose up => negative

    return yaw_deg, pitch_deg
# ----------------------------------------

#* ----- Duck ----- #
class Duck: #? duck
    def __init__(self, x, y, z, r):
        self.position = [x, y, z]
        self.rotation = r
        self.state = 'flying'
        self.wing_angle = 0.0
        self.dim = 6


    def draw_duck(self):
        global duck_dark_gray, duck_light_gray, duck_med_gray, duck_medium_gray, eye_black

        glPushMatrix()
        glTranslate(*self.position)
        glScalef(self.dim, self.dim, self.dim)
        glRotate(90, 1, 0, 0)
        glRotate(self.rotation, 0, 1, 0)

        if self.state == 'falling':
            self.dim = 4
            glRotatef(90, 1, 0, 0)
            if self.position[2] > 0:
                self.position[2] -= DUCK_FALLING_SPEED
            else:
                self.position[2] = 1
                self.state='dead'

        if self.state == 'dead':
            self.dim = 2
            glRotatef(180, 1, 0, 0)
        
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

    def drop_duck(self):    #? duck status falling

        '''If bullet hits the duck, the state changes into falling.
        So at collision of bullet and duck, call this function.'''

        self.state = 'falling'
        self.wing_angle = 0.0

    def dead_duck(self):    #? duck status dead        
        
        '''If falling duck hits ground state changes to dead.
        So when at collision with ground, call this function.'''

        self.state = 'dead'
        self.wing_angle = 0.0

#! Dog(?)
#! Wolves(?)

#TODO Rifle

#* ----- Bullet ----- #
class Bullet:   #? bullet 
    def __init__(self, start_pos, direction):
        self.position = list(start_pos)
        self.direction = direction
        # self.creation_time = time.time()

    def update(self):   #? updates bullet position
        self.position[0] += self.direction[0] / 1000 * BULLET_SPEED
        self.position[1] += self.direction[1] / 1000 * BULLET_SPEED
        self.position[2] += self.direction[2] / 1000 * BULLET_SPEED

        if self.position[2] > SKYBOX_HEIGHT:
            print("Bullet removed")
            BULLETS.remove(self)
            return


    def draw(self): #? draws bullet
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glColor3f(1.0, 1.0, 0.0) # Yellow
        glutSolidSphere(2, 8, 8)
        glPopMatrix()

#* ----- Tree ----- #
class Tree: #? tree
    def __init__(self, x, y, height=TREE_HEIGHT, radius=TREE_RADIUS):
        self.x = x
        self.y = y
        self.height = random.uniform(height-10,height+10)
        self.radius = random.uniform(radius-5, radius+5)

    def draw_tree(self):    #? draws tree
        glPushMatrix()  #? transform start

        glTranslatef(self.x, self.y, 0)

        #* tree leaves
        glPushMatrix()

        glTranslatef(0, 0, TREE_HEIGHT)  #? Move to the top of the trunk
        glColor3f(0.0, 0.5, 0.0)  #? Green color for leaves
        gluCylinder(gluNewQuadric(), TREE_RADIUS+20, 0, TREE_HEIGHT, 12, 1)  # parameters are: quadric, base radius, top radius, height, slices, stacks
        
        glPopMatrix()

        #*tree trunk
        glPushMatrix()

        glColor3f(0.5, 0.35, 0.05)  #? Brown color for trunk
        gluCylinder(gluNewQuadric(), TREE_RADIUS, TREE_RADIUS, TREE_HEIGHT, 12, 1)  # parameters are: quadric, base radius, top radius, height, slices, stacks
        
        glPopMatrix()
        
        glPopMatrix()   #? transform end

#TODO Shop

#* ----- play area ----- #
def draw_surface():
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.5, 0.0)  # Green color for grass
    glVertex3f(-GROUND_X, -GROUND_Y, 0)
    glVertex3f(GROUND_X, -GROUND_Y, 0)
    glVertex3f(GROUND_X, GROUND_Y, 0)
    glVertex3f(-GROUND_X, GROUND_Y, 0)


    glColor3f(0, 0.85, 0.85)
    glVertex3f(-GROUND_X, -GROUND_Y, 0)
    glVertex3f(GROUND_X, -GROUND_Y, 0)
    glVertex3f(GROUND_X, -GROUND_Y, DUCK_FLYING_Z + 10)
    glVertex3f(-GROUND_X, -GROUND_Y, DUCK_FLYING_Z + 10)

    glVertex3f(GROUND_X, -GROUND_Y, 0)
    glVertex3f(GROUND_X, GROUND_Y, 0)
    glVertex3f(GROUND_X, GROUND_Y, DUCK_FLYING_Z + 10)
    glVertex3f(GROUND_X, -GROUND_Y, DUCK_FLYING_Z + 10)

    glVertex3f(GROUND_X, GROUND_Y, 0)
    glVertex3f(-GROUND_X, GROUND_Y, 0)
    glVertex3f(-GROUND_X, GROUND_Y, DUCK_FLYING_Z + 10)
    glVertex3f(GROUND_X, GROUND_Y, DUCK_FLYING_Z + 10)

    glVertex3f(-GROUND_X, GROUND_Y, 0)
    glVertex3f(-GROUND_X, -GROUND_Y, 0)
    glVertex3f(-GROUND_X, -GROUND_Y, DUCK_FLYING_Z + 10)
    glVertex3f(-GROUND_X, GROUND_Y, DUCK_FLYING_Z + 10)

    glEnd()
        

#! Border


#TODO - UI
#! Ammo count
#! Money display
#! Shop UI - numbers corresponding to items
#! Crosshair

#TODO Implement game logic
#! Shop interactions

#* ----- Controls ----- #
def move_forward():
    global PLAYER_X, PLAYER_Y, PLAYER_Z
    move_x = PLAYER_X - (PLAYER_SPEED * cos(radians(PLAYER_R)))
    move_y = PLAYER_Y - (PLAYER_SPEED * sin(radians(PLAYER_R)))
    if -GROUND_X <= abs(move_x) <= GROUND_X:
        PLAYER_X = move_x
    if -GROUND_Y <= abs(move_y) <= GROUND_Y:
        PLAYER_Y = move_y
        # print("move forward")
        # print(PLAYER_X, PLAYER_Y)

def move_backward():
    global PLAYER_X, PLAYER_Y, PLAYER_Z
    move_x = PLAYER_X + (PLAYER_SPEED * cos(radians(PLAYER_R)))
    move_y = PLAYER_Y + (PLAYER_SPEED * sin(radians(PLAYER_R)))
    if -GROUND_X <= abs(move_x) <= GROUND_X:
        PLAYER_X = move_x
    if -GROUND_Y <= abs(move_y) <= GROUND_Y:
        PLAYER_Y = move_y
        # print("move backward")
        # print(PLAYER_X, PLAYER_Y)

def move_left():
    global PLAYER_X, PLAYER_Y, PLAYER_Z
    move_x = PLAYER_X - (PLAYER_SPEED * cos(radians(PLAYER_R + 90)))
    move_y = PLAYER_Y - (PLAYER_SPEED * sin(radians(PLAYER_R + 90)))
    if -GROUND_X <= abs(move_x) <= GROUND_X:
        PLAYER_X = move_x
    if -GROUND_Y <= abs(move_y) <= GROUND_Y:
        PLAYER_Y = move_y
        # print("move left")
        # print(PLAYER_X, PLAYER_Y)

def move_right():
    global PLAYER_X, PLAYER_Y, PLAYER_Z
    move_x = PLAYER_X + (PLAYER_SPEED * cos(radians(PLAYER_R + 90)))
    move_y = PLAYER_Y + (PLAYER_SPEED * sin(radians(PLAYER_R + 90)))
    if -GROUND_X <= abs(move_x) <= GROUND_X:
        PLAYER_X = move_x
    if -GROUND_Y <= abs(move_y) <= GROUND_Y:
        PLAYER_Y = move_y
        # print("move right")
        # print(PLAYER_X, PLAYER_Y)

def aim_left():
    global LOOK_X, LOOK_Y, LOOK_Z
    global PLAYER_X, PLAYER_Y, PLAYER_Z, PLAYER_R, PLAYER_SPEED

    aim_x = LOOK_X * cos(radians(LOOK_DELTA_ANGLE)) - LOOK_Y * sin(radians(LOOK_DELTA_ANGLE))
    aim_y = LOOK_X * sin(radians(LOOK_DELTA_ANGLE)) + LOOK_Y * cos(radians(LOOK_DELTA_ANGLE))
    LOOK_X, LOOK_Y = aim_x, aim_y
    PLAYER_R += LOOK_DELTA_ANGLE    #? Update player rotation

def aim_right():
    global LOOK_X, LOOK_Y, LOOK_Z
    global PLAYER_X, PLAYER_Y, PLAYER_Z, PLAYER_R, PLAYER_SPEED

    aim_x = LOOK_X * cos(radians(-LOOK_DELTA_ANGLE)) - LOOK_Y * sin(radians(-LOOK_DELTA_ANGLE))
    aim_y = LOOK_X * sin(radians(-LOOK_DELTA_ANGLE)) + LOOK_Y * cos(radians(-LOOK_DELTA_ANGLE))
    LOOK_X, LOOK_Y = aim_x, aim_y
    PLAYER_R -= LOOK_DELTA_ANGLE    #? Update player rotation

def shoot():
    global BULLETS, AMMO_COUNT

    if AMMO_COUNT > 0:
        _x, _y, _z = PLAYER_X+5, PLAYER_Y, PLAYER_Z

        dx = (PLAYER_X + LOOK_X) - _x
        dy = (PLAYER_Y + LOOK_Y + 1) - _y
        dz = LOOK_Z - _z

        BULLETS.append(Bullet((_x,_y,_z),(dx,dy,dz)))
        hud.shoot()
        AMMO_COUNT -= 1

#* ----- Keyboard ----- #
def keyboardListener(key, _x, _y):
    #TODO assign movement
    global PLAYER_X, PLAYER_Y, PLAYER_Z
    global LOOK_X, LOOK_Y, LOOK_Z
    global MOVE_FORWARD, MOVE_BACKWARD, MOVE_LEFT, MOVE_RIGHT
    global BUTTONS

    if key == b'w':
        BUTTONS['w']=True
    if key == b's':
        BUTTONS['s']=True
    if key == b'a':
        BUTTONS['a']=True
    if key == b'd':
        BUTTONS['d']=True

    if key == b' ':
        # Shoot
        shoot()
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

def keyboardUpListener(key, _x, _y):
    global shop, hud
    if key == b'w':
        BUTTONS['w']=False
    if key == b's':
        BUTTONS['s']=False
    if key == b'a':
        BUTTONS['a']=False
    if key == b'd':
        BUTTONS['d']=False

    if key in [b'b', b'B']:
        shop.toggle()
        return

    if shop.active:
        # allow purchase of G, A, or numbers 1,2
        if key in [b'1', b'2']:
            global AMMO_COUNT
            if shop.purchase(key) == 1:
                hud.magazine_size += 2
                hud.ammo += 2
                AMMO_COUNT += 2
            elif shop.purchase(key) == 2:
                hud.ammo = hud.magazine_size
                AMMO_COUNT = hud.magazine_size

def specialKeyListener(key, _x, _y):
    pass

#* ----- Mouse ----- #
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
        # print("Aim Up")
        LOOK_Z = min(LOOK_Z + (1 * LOOK_SPEED_Z), SKYBOX_HEIGHT)
        pass

    if button == 4 and state == GLUT_DOWN:
        #* aim down
        # print("Aim Down")
        LOOK_Z = max(LOOK_Z - (1 * LOOK_SPEED_Z), -SKYBOX_HEIGHT)
        pass

#TODO Finishing touch

# ----- DEBUG ----- #
def devDebug():
    if not hasattr(devDebug, "last_print_time"):
        devDebug.last_print_time = time.time()

    current_time = time.time()
    if current_time - devDebug.last_print_time >= 100.0:
        x, y, z = PLAYER_X, PLAYER_Y, PLAYER_Z
        print(
            f"{glutGet(GLUT_ELAPSED_TIME)} : Player Currently At - X={x:.2f} Y={y:.2f} Z={z:.2f}"
        )

#* ----- Camera ----- #
def setupCamera():
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    gluPerspective(FOV_Y, 16/9, 0.1, 2000) # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    #TODO camera position and orientation

    gluLookAt(PLAYER_X, PLAYER_Y, PLAYER_Z,  # Camera position
              PLAYER_X + LOOK_X , PLAYER_Y + LOOK_Y + 1, LOOK_Z,  # Look at point
              0, 0, 1)  # Up vector
    
#* display function -> draw
#render shop 
def display():
    global hud, shop
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # draw 3D world (ducks, environment, gun, etc.)

    # draw HUD
    hud.render(window_width, window_height)

    # draw Shop overlay (if active)
    shop.render(window_width, window_height)

    glutSwapBuffers()

    glPushMatrix()
    glTranslatef(PLAYER_X + LOOK_X , PLAYER_Y + LOOK_Y + 1, LOOK_Z)
    glutSolidSphere(1, 10, 10)
    glPopMatrix()
    
#* ----- Draw ----- #
def showScreen():
    glEnable(GL_DEPTH_TEST)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, 0.9, 0.9, 0.5)  # skyblue
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1280, 720)  # Set viewport size

    #TODO setupCamera()
    setupCamera()

    glDisable(GL_DEPTH_TEST)
    draw_surface()
    glEnable(GL_DEPTH_TEST)


    for i in range(TREE_COUNT):
        Tree(rand_x[i], rand_y[i]).draw_tree()

    if len(DUCKS) < DUCK_COUNT: #? spawns DUCK_COUNT amount of ducks
        DUCKS.append(Duck(  random.uniform(-GROUND_X, GROUND_X),
                            random.uniform(-GROUND_Y, GROUND_Y), 
                            random.uniform( DUCK_FLYING_Z + DUCK_FLYING_Z/4, 
                                            DUCK_FLYING_Z - DUCK_FLYING_Z/4),
                            random.uniform(0, 359)))
        
    for duck in DUCKS:
        duck.draw_duck()
        state = "flying"
        #draw_duck(x, y, z, state)

    for bullet in BULLETS:
        bullet.draw()

    hud.render(window_width, window_height)

    # draw Shop overlay (if active)
    shop.render(window_width, window_height)

    #TODO UI elements

    #* ---- Crosshair ---- #
    # Initialize
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(-640, 640, -480, 480, 0, 1)  # 640 x 480 Crosshair, Center -- (0,0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    
    # Crosshair
    glLineWidth(2)
    glColor3f(1, 1, 1)
    glBegin(GL_LINES)
    glVertex2f(0, -10)
    glVertex2f(0, 10)
    glVertex2f(-10, 0)
    glVertex2f(10, 0)
    glEnd()

    glEnable(GL_DEPTH_TEST)

    # De-Initialize
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glutSwapBuffers()

# FPS = 60  # Target frames per second
# FRAME_TIME_MS = int(1000 / FPS)

#* ----- Idle ----- #
def idle():
    global LOOK_X, LOOK_Y, LOOK_Z
    global PLAYER_X, PLAYER_Y, PLAYER_Z, PLAYER_R, PLAYER_SPEED
    global BULLETS
    global SCORE
    global shop, hud
# ---------------------------------- #
    #* Player movement
    if BUTTONS['w']:
        move_forward()
    if BUTTONS['s']:
        move_backward()
    if BUTTONS['a']:
        move_left()
    if BUTTONS['d']:
        move_right()
    
    #* Player aiming
    if AIM_LEFT:
        aim_left()
        # print(PLAYER_R)
        # print("Aim Left")

    if AIM_RIGHT:
        aim_right()
        # print(PLAYER_R)
        # print("Aim Right")


    #* ---- Duck animation ---- #
    for duck in DUCKS:
        if duck.state == 'flying':
            duck.wing_angle += DUCK_WING_SPEED
            _x = duck.position[0] - (DUCK_SPEED * cos(radians(duck.rotation+90)))   #? position change in x
            _y = duck.position[1] - (DUCK_SPEED * sin(radians(duck.rotation+90)))   #? position change in y
            if abs(_x) > GROUND_X + 10:  #? bound and flip teleport to other x_axis bound
                # print('a')
                _x *= -1
            if abs(_y) > GROUND_Y + 10:  #? same for y_axis
                # print('b')
                _y *= -1
            duck.position[0], duck.position[1] = _x, _y #? update position
            # print(duck.position[0], duck.position[1])

            for bullet in BULLETS:
                x = bullet.position[0] - duck.position[0]
                y = bullet.position[1] - duck.position[1]
                z = bullet.position[2] - duck.position[2]

                if abs(x) <= DUCK_HITBOX and abs(y) <= DUCK_HITBOX and abs(z) <= DUCK_HITBOX:
                    duck.state = 'falling'
                    BULLETS.remove(bullet)
                    print('hit')
            
    #* ---- Bullet animation ---- #
    for bullet in BULLETS:
        bullet.update()
    #* ---- Duck hitbox ---- #
    for duck in DUCKS:
        _x, _y, _z = duck.position
        dx = abs(_x - PLAYER_X)
        dy = abs(_y - PLAYER_Y)
        # dz = abs(_z - PLAYER_Z)

        if dx <= DUCK_HITBOX/2 and dy <= DUCK_HITBOX/2:
            if 1 < _z <= PLAYER_Z:
                shop.currency += 25
                SCORE = shop.currency
                hud.score = shop.currency
                hud.currency = shop.currency
                DUCKS.remove(duck)
                print(f"score: {SCORE}")
            elif _z == 1:
                shop.currency += 10
                SCORE = shop.currency
                hud.score = shop.currency
                hud.currency = shop.currency
                DUCKS.remove(duck)
                print(f"score: {SCORE}")

    # devDebug()

    glutPostRedisplay()  # Request a redraw
    # Schedule next frame
    # glutTimerFunc(FRAME_TIME_MS, idle, 0)

#KAFI : 

#hud->
class HUD:
    def __init__(self):
        self.score, self.c, self.magazine_size = 0, AMMO_COUNT, 8
        self.currency = 0
        self.health, self.crosshair_size = 100, 10
        self.messages, self.last_shot_time = [], 0.0
        self.night_vision, self.auto_fire_active = False, False

    def draw_text(self,x,y,text,font=GLUT_BITMAP_HELVETICA_18):
        glRasterPos2f(x,y)
        for ch in text: glutBitmapCharacter(font, ord(ch))

    def shoot(self):
        now, cooldown = time.time(), (0.1 if self.auto_fire_active else 0.5)
        if now - self.last_shot_time < cooldown: return False
        if self.ammo>0:
            self.ammo -= 1; self.last_shot_time = now; return True
        self.messages.append(("Out of Ammo!",time.time())); return False
    

    def reload(self):
        self.ammo=self.magazine_size
        self.messages.append(("Reloaded!",time.time()))

    def render(self,w,h):
        self.score = SCORE
        self.ammo = AMMO_COUNT

        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0,w,0,h)
        glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
        glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST); glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)

        glColor3f(1,1,1); self.draw_text(20,h-30,f"Score: {self.score}")

        self.draw_text(20,h-55,f"Ammo: {AMMO_COUNT}/{self.magazine_size}")
        self.draw_text(20,h-80,f"Currency: {self.currency}")
        cx, cy, size = w//2, h//2, self.crosshair_size

        glColor3f(0.1,1.0,0.1)
        glBegin(GL_LINES)
        glVertex2f(cx-size,cy); glVertex2f(cx+size,cy)
        glVertex2f(cx,cy-size); glVertex2f(cx,cy+size)
        glEnd()
        now=time.time(); msgs=[]; y_off=0

        for msg,t in self.messages:
            if now-t<2.0:
                glColor3f(1,1,0); self.draw_text(w//2-40,h//2+60+y_off,msg)
                y_off+=20; msgs.append((msg,t))
        self.messages=msgs

        glDisable(GL_BLEND); glEnable(GL_DEPTH_TEST); #glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW); glPopMatrix()


#shop ->
class Shop:
    def __init__(self, hud):
        self.active = False
        self.hud = hud
        self.currency = 0
        self.items = [
            {"id": 1, "name": "Bigger Magazine", "key": "G", "cost": 100},
            {"id": 2, "name": "Refill Magazine", "key": "A", "cost": 50}
        ]
        self.last_message = ""
        self.last_message_time = 0

    def toggle(self):
        self.active = not self.active
        glutSetCursor(GLUT_CURSOR_LEFT_ARROW if self.active else GLUT_CURSOR_NONE)

    def purchase(self, key):
        key = key.decode("utf-8").upper()
        for item in self.items:
            if item["key"] == key or str(item["id"]) == key:
                if self.currency >= item["cost"]:
                    self.currency -= item["cost"]
                    self.last_message = f"Purchased {item['name']}!"
                    return item["id"]
                else:
                    self.last_message = "Not enough points!"
                self.last_message_time = time.time()
        return 0

    def render(self, w, h):
        if not self.active:
            return
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, w, 0, h)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glColor4f(0, 0, 0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(w, 0)
        glVertex2f(w, h)
        glVertex2f(0, h)
        glEnd()

        cx, cy = w // 2, h // 2
        glColor3f(1, 1, 0)
        self.draw_text(cx - 60, cy + 130, "=== SHOP ===")

        glColor3f(1, 1, 1)
        self.draw_text(cx - 120, cy + 100, f"Points: {self.currency}")

        y_off = 0
        for item in self.items:
            glColor3f(0.5, 1, 0.5 if self.currency >= item["cost"] else 0.3)
            self.draw_text(
                cx - 250,
                cy + 60 - y_off,
                f"[{item['id']}] [{item['key']}] {item['name']} ({item['cost']} pts)"
            )
            y_off += 25

        if time.time() - self.last_message_time < 2:
            glColor3f(0, 1, 0)
            self.draw_text(cx - 100, cy - 150, self.last_message)

        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        # glEnable(GL_LIGHTING)

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def draw_text(self, x, y, text, font=GLUT_BITMAP_HELVETICA_18):
        glRasterPos2f(x, y)
        [glutBitmapCharacter(font, ord(ch)) for ch in text]
#end

# Instantiate global objects
hud = HUD()
shop = Shop(hud)

# Global window dimensions
window_width = 1280
window_height = 720

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1280, 720)  # Window size
    glutInitWindowPosition(100, 100)  # Window position
    glutCreateWindow(b"Duck Season")  # Create the window

    global hud, shop
    hud = HUD()
    shop = Shop(hud)

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutKeyboardUpFunc(keyboardUpListener)  # Register keyboard up listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    # glutPassiveMotionFunc(passiveMouseListener)
    glutIdleFunc(idle)  # FPS limiting uses timer instead
    # idle()  # Start the timer-based loop

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()
