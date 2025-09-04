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

TREE_COUNT = 30 #? environment tree count
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


    def draw_duck(self):    #? draws duck at given point
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
        glTranslate(*self.position)
        glRotate(90, 1, 0, 0)

        glPushMatrix()
        glColor3f(*duck_light_gray)
        glScalef(duck_scale * 1.5, duck_scale * 1, duck_scale * 2.5)
        glTranslatef(0, 0, 0)
        glutSolidCube(1.5)
        glPopMatrix()

        # Neck
        glPushMatrix()
        glColor3f(*duck_dark_gray)
        glScalef(duck_scale * 0.7, duck_scale * 0.5, duck_scale * 0.7)
        glTranslatef(0, 0.6, 3)
        glutSolidCube(1.0)
        glPopMatrix()

        # Head
        glPushMatrix()
        glColor3f(*duck_med_gray)
        glScalef(duck_scale * 1.1, duck_scale * 1.0, duck_scale * 1.0)
        glTranslatef(0, 0.4, 2.8)
        glutSolidCube(1.0)
        glPopMatrix()

        # Beak
        glPushMatrix()
        glColor3f(*duck_dark_gray)
        glScalef(duck_scale * 0.6, duck_scale * 0.2, duck_scale * 0.5)
        glTranslatef(0, 0.6, 6.7)
        glutSolidCube(1)
        glPopMatrix()

        # Left eye
        glPushMatrix()
        glColor3f(*eye_black)
        glScalef(duck_scale * 0.2, duck_scale * 0.2, duck_scale * 0.2)
        glTranslatef(-2.5, 3.6, 15.0)
        glutSolidCube(1.0)
        glPopMatrix()
        
        # Right eye
        glPushMatrix()
        glColor3f(*eye_black)
        glScalef(duck_scale * 0.2, duck_scale * 0.2, duck_scale * 0.2)
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
        glScalef(duck_scale * 1.9, duck_scale * 0.2, duck_scale * 1.0)
        glutSolidCube(1.5)
        glPopMatrix()

        # Right wing
        glPushMatrix()
        glColor3f(*duck_medium_gray)
        glTranslatef(1.7, 0.4, 0.0)
        if self.state == 'flying':
            glRotatef(-self.wing_delta + 30, 0, 0, 1)
        glScalef(duck_scale * 1.9, duck_scale * 0.2, duck_scale * 1.0)
        glutSolidCube(1.5)
        glPopMatrix()

        # Left leg
        glPushMatrix()
        glColor3f(*duck_dark_gray)
        glScalef(duck_scale * 0.3, duck_scale * 1.0, duck_scale * 0.3)
        glTranslatef(-2.0, -1.2, -1.0)
        glutSolidCube(1.0)
        glPopMatrix()

        # Right leg
        glPushMatrix()
        glColor3f(*duck_dark_gray)
        glScalef(duck_scale * 0.3, duck_scale * 1.0, duck_scale * 0.3)
        glTranslatef(2.0, -1.2, -1.0)
        glutSolidCube(1.0)
        glPopMatrix()

        # Tail
        glPushMatrix()
        glColor3f(*duck_dark_gray)
        glTranslatef(0, -0.2, -2.0)
        glRotatef(20, 1, 0, 0)
        glScalef(duck_scale * 1.8, duck_scale * 0.3, duck_scale * 2.4)
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

#! Shop - KAFI :
# from OpenGL.GL import *
# from OpenGL.GLUT import *
# from OpenGL.GLU import *
# import time


class Shop:
    def __init__(self, hud=None):
        #shop status
        self.active = False
        self.hud = hud

        #shop items
        self.items = [
            {"id": 1, "name": "Bigger Magazine", "key": "G", "description": "+5 bullets per reload", "cost": 100, "type": "perk", "effect": self.buy_magazine},
            {"id": 2, "name": "Golden Gun Skin", "key": "H", "description": "Shiny golden rifle", "cost": 200, "type": "cosmetic", "effect": self.buy_skin},
            {"id": 3, "name": "Health Boost", "key": "J", "description": "+20 HP instantly", "cost": 50, "type": "consumable", "effect": self.buy_health},
            {"id": 4, "name": "Double Points (30s)", "key": "K", "description": "2x points for 30s", "cost": 150, "type": "timed", "effect": self.buy_double_points},
            {"id": 5, "name": "Fast Reload (20s)", "key": "L", "description": "Reload speed x2 for 20s", "cost": 120, "type": "timed", "effect": self.buy_fast_reload},
            {"id": 6, "name": "Armor Vest", "key": "M", "description": "Reduces damage taken by 50%", "cost": 250, "type": "perk", "effect": self.buy_armor},
            {"id": 7, "name": "Night Vision", "key": "N", "description": "Better visibility at night", "cost": 180, "type": "perk", "effect": self.buy_night_vision},
            {"id": 8, "name": "Stamina Boost", "key": "O", "description": "+50 max stamina", "cost": 120, "type": "perk", "effect": self.buy_stamina},
            {"id": 9, "name": "New Weapon: SMG", "key": "P", "description": "Unlock SMG weapon", "cost": 400, "type": "weapon", "effect": self.buy_weapon},
        ]

        #currency
        self.currency = 0

        #feedback
        self.last_message = ""
        self.last_message_time = 0

        #timed effects
        self.active_effects = {}  

    def toggle(self):
        """Toggle shop screen on/off."""
        self.active = not self.active

    def purchase(self, key, hud):
        """Handle purchase attempt based on pressed key."""
        for item in self.items:
            if item["key"] == key.upper():
                if self.currency >= item["cost"]:
                    self.currency -= item["cost"]
                    self.apply_effect(item, hud)
                    self.last_message = f"Purchased {item['name']}!"
                else:
                    self.last_message = "Not enough points!"
                self.last_message_time = time.time()
                return True
        return False

    def purchase_by_id(self, item_id):
        """Handle purchase attempt based on item ID (from provided code)."""
        item = next((i for i in self.items if i["id"] == item_id), None)
        if not item:
            self.last_message = "Item not found!"
            return
        if self.currency >= item["cost"]:
            self.currency -= item["cost"]
            item["effect"]()
            self.last_message = f"Bought {item['name']}"
        else:
            self.last_message = "Not enough points!"

    def apply_effect(self, item, hud):
        """Apply purchased perk to the HUD/game state."""
        name = item["name"]

        if item["type"] == "perk":
            if name == "Bigger Magazine":
                hud.magazine_size += 5
                hud.ammo = hud.magazine_size
            elif name == "Armor Vest":
                hud.armor = True
            elif name == "Night Vision":
                hud.night_vision = True

        elif item["type"] == "cosmetic":
            if name == "Golden Gun Skin":
                hud.messages.append(("Golden Gun Equipped!", time.time()))
                hud.skin = "golden"

        elif item["type"] == "consumable":
            if name == "Health Boost":
                hud.health = min(100, hud.health + 20)

        elif item["type"] == "timed":
            duration = 30 if "Double Points" in name else 20
            expiry = time.time() + duration
            self.active_effects[name] = expiry
            hud.messages.append((f"{name} Activated!", time.time()))

    def update_effects(self, hud):
        """Check and expire timed effects."""
        now = time.time()
        expired = []
        for effect, expiry in self.active_effects.items():
            if now > expiry:
                expired.append(effect)

        #remove expired effects
        for effect in expired:
            hud.messages.append((f"{effect} expired!", time.time()))
            del self.active_effects[effect]

    def has_effect(self, effect_name):
        """Check if a timed effect is active."""
        return effect_name in self.active_effects

    #effect
    def buy_magazine(self):
        if self.hud:
            self.hud.magazine_size += 5
            self.hud.ammo = self.hud.magazine_size
            self.hud.messages.append(("Magazine +5", time.time()))

    def buy_reload(self):
        if self.hud:
            self.hud.messages.append(("Reload faster!", time.time()))

    def buy_armor(self):
        if self.hud:
            self.hud.armor = True
            self.hud.messages.append(("Armor Equipped", time.time()))

    def buy_stamina(self):
        if self.hud:
            self.hud.max_stamina += 50
            self.hud.stamina = self.hud.max_stamina
            self.hud.messages.append(("Stamina Boosted!", time.time()))

    def buy_night_vision(self):
        if self.hud:
            self.hud.night_vision = not self.hud.night_vision
            self.hud.messages.append(("Night Vision ON" if self.hud.night_vision else "Night Vision OFF", time.time()))

    def buy_skin(self):
        if self.hud:
            self.hud.skin = "golden"
            self.hud.messages.append(("Golden Skin Equipped!", time.time()))

    def buy_weapon(self):
        if self.hud:
            if "SMG" not in self.hud.weapons:
                self.hud.weapons.append("SMG")
                self.hud.messages.append(("Unlocked SMG!", time.time()))

    def buy_health(self):
        if self.hud:
            self.hud.health = min(100, self.hud.health + 20)
            self.hud.messages.append(("Health Boosted!", time.time()))

    def buy_double_points(self):
        if self.hud:
            duration = 30
            expiry = time.time() + duration
            self.active_effects["Double Points (30s)"] = expiry
            self.hud.messages.append(("Double Points Activated!", time.time()))

    def buy_fast_reload(self):
        if self.hud:
            duration = 20
            expiry = time.time() + duration
            self.active_effects["Fast Reload (20s)"] = expiry
            self.hud.messages.append(("Fast Reload Activated!", time.time()))

    def draw_text(self, x, y, text, font=GLUT_BITMAP_HELVETICA_18):
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))

    def render(self, window_w, window_h):
        """Render the shop screen overlay."""
        if not self.active:
            return

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_w, 0, window_h)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_LIGHTING)
        cx, cy = window_w // 2, window_h // 2

        #shop title
        glColor3f(1, 1, 0)
        self.draw_text(cx - 60, cy + 130, "=== SHOP ===")
        glColor3f(1, 1, 1)
        self.draw_text(cx - 120, cy + 100, f"Points Available: {self.currency}")

        #item list
        y_offset = 0
        for item in self.items:
            color = (0.5, 1, 0.5) if self.currency >= item["cost"] else (1, 0.3, 0.3)
            glColor3f(*color)
            self.draw_text(cx - 250, cy + 60 - y_offset,
                           f"[{item['key']}] {item['name']} ({item['cost']} pts) - {item['description']}")
            y_offset += 25

        #instructions
        glColor3f(0.8, 0.8, 0.8)
        self.draw_text(cx - 160, cy - 120, "Press item key to buy • Press B to exit")

        #last purchase message
        if time.time() - self.last_message_time < 2:
            glColor3f(0, 1, 0)
            self.draw_text(cx - 100, cy - 150, self.last_message)

        #restore
        glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()


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
    if key == b'w':
        BUTTONS['w']=False
    if key == b's':
        BUTTONS['s']=False
    if key == b'a':
        BUTTONS['a']=False
    if key == b'd':
        BUTTONS['d']=False

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
#kafi: 
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

    draw_surface()

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
                SCORE += 25
                DUCKS.remove(duck)
                print(f"score: {SCORE}")        
            elif _z == 1:
                SCORE += 10
                DUCKS.remove(duck)
                print(f"score: {SCORE}")        

    # devDebug()

    glutPostRedisplay()  # Request a redraw
    # Schedule next frame
    # glutTimerFunc(FRAME_TIME_MS, idle, 0)

#KAFI---bruh wasnt sure where to add so pasting it here (may have overdone stuff and maybe it wont work :v ) : 
#HUD ----------->
# from OpenGL.GL import *
# from OpenGL.GLUT import *
# from OpenGL.GLU import *
# import math, time, random

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
#kafi
hud = HUD()
shop = Shop(hud=hud) 

# main loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1280, 720)  # Window size
    glutInitWindowPosition(100, 100)  # Window position
    glutCreateWindow(b"Duck Season")  # Create the window

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
