# * libraries

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import *
import random
import time
import sys

# * Game Configuration & Constants

# Window
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Camera & Player
PLAYER_Z = 0.01
PLAYER_SPEED = 1.5
PLAYER_R_INITIAL = -90
LOOK_SPEED_Z = 15
LOOK_DELTA_ANGLE = 1.5
FOV_Y = 70

# World
GROUND_HALF_LENGTH = 1000
SKYBOX_HEIGHT = 1000
GRAVITY = 0.5

# Tree
TREE_TRUNK_RADIUS = 10
TREE_TRUNK_HEIGHT = 50
TREE_LEAVES_RADIUS = 30
TREE_LEAVES_HEIGHT = 50
TREE_COUNT = 50

# Duck
DUCK_COUNT = 20
GROUND_DUCK_COUNT = 10
DUCK_FLYING_Z_MIN = 300
DUCK_FLYING_Z_MAX = 600
DUCK_SPEED = 1.0
DUCK_HITBOX_RADIUS = 135.0  # Decreased hitbox

# Bullet
BULLET_SPEED = 10.0
BULLET_LIFESPAN = 5.0 # in seconds

# --- Color Variables ---

# Duck
duck_color_schemes = [
    {"light": (0.7, 0.7, 0.7), "med": (0.6, 0.6, 0.6), "medium": (0.5, 0.5, 0.5), "dark": (0.3, 0.3, 0.3)},
    {"light": (0.8, 0.6, 0.4), "med": (0.7, 0.5, 0.3), "medium": (0.6, 0.4, 0.2), "dark": (0.4, 0.2, 0.1)},
    {"light": (0.6, 0.8, 0.6), "med": (0.5, 0.7, 0.5), "medium": (0.4, 0.6, 0.4), "dark": (0.2, 0.4, 0.2)},
    {"light": (0.8, 0.8, 0.6), "med": (0.7, 0.7, 0.5), "medium": (0.6, 0.6, 0.4), "dark": (0.4, 0.4, 0.2)},
    {"light": (0.9, 0.7, 0.9), "med": (0.8, 0.6, 0.8), "medium": (0.7, 0.5, 0.7), "dark": (0.5, 0.3, 0.5)},
]
eye_black = (0.0, 0.0, 0.0)

# Gun
gun_brown = (0.35, 0.15, 0.0)
gun_dark_brown = (0.2, 0.1, 0.0)
gun_black = (0.1, 0.1, 0.1)


# * Game Objects
class Duck:
    def __init__(self, x, y, z):
        self.position = [x, y, z]
        self.initial_pos = [x, y, z]
        self.direction = [random.choice([-1, 1]), random.choice([-1, 1]), 0]
        self.state = 'flying'  # flying, falling, dead
        self.wing_angle = 0.0
        self.fall_speed = 0.0
        self.color_scheme = random.choice(duck_color_schemes)

    def update(self, speed_multiplier=1.0, game=None):
        if self.state == 'flying':
            self.wing_angle += 10.0
            # Simple movement logic
            self.position[0] += self.direction[0] * DUCK_SPEED * speed_multiplier
            self.position[1] += self.direction[1] * DUCK_SPEED * speed_multiplier

            # Check collision with trees
            if game and game.is_point_in_tree(self.position[0], self.position[1], self.position[2]):
                self.direction[0] = -self.direction[0]
                self.direction[1] = -self.direction[1]
                self.position[0] += self.direction[0] * DUCK_SPEED * speed_multiplier
                self.position[1] += self.direction[1] * DUCK_SPEED * speed_multiplier

            # If duck flies too far, reset its position
            if abs(self.position[0]) > GROUND_HALF_LENGTH or abs(self.position[1]) > GROUND_HALF_LENGTH:
                self.position = self.initial_pos[:]
                self.direction = [random.choice([-1, 1]), random.choice([-1, 1]), 0]

        elif self.state == 'falling':
            self.fall_speed += GRAVITY
            self.position[2] -= self.fall_speed
            if self.position[2] <= 0:
                self.position[2] = 0
                self.dead_duck()

    def draw(self, night_mode=False, night_vision=False):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])

        # Rotate duck to face its flying direction
        if self.state == 'flying':
            angle = degrees(atan2(self.direction[1], self.direction[0]))
            glRotatef(angle, 0, 0, 1)

        if self.state == 'dead':
            glRotatef(180, 1, 0, 0)
        elif self.state == 'falling':
            glRotatef(90, 1, 0, 0)

        # Camouflage in night mode unless night vision is on
        if night_mode and not night_vision:
            # Darker colors for camouflage
            camo_scheme = {"light": (0.1, 0.1, 0.1), "med": (0.05, 0.05, 0.05), "medium": (0.02, 0.02, 0.02), "dark": (0.01, 0.01, 0.01)}
        else:
            camo_scheme = self.color_scheme

        # Body - increased scales by 6x (3x * 2x)
        glPushMatrix()
        glColor3f(*camo_scheme["light"])
        glScalef(9.0, 6.0, 15.0)  # 4.5 * 2, 3.0 * 2, 7.5 * 2
        glutSolidCube(1.5)
        glPopMatrix()

        # Neck - increased scales by 6x
        glPushMatrix()
        glColor3f(*camo_scheme["dark"])
        glScalef(4.2, 3.0, 4.2)  # 2.1 * 2, 1.5 * 2, 2.1 * 2
        glTranslatef(0, 1.8, 9.0)  # 0.9 * 2, 4.5 * 2
        glutSolidCube(1.0)
        glPopMatrix()

        # Head - increased scales by 6x
        glPushMatrix()
        glColor3f(*camo_scheme["med"])
        glScalef(6.6, 6.0, 6.0)  # 3.3 * 2, 3.0 * 2, 3.0 * 2
        glTranslatef(0, 1.2, 8.4)  # 0.6 * 2, 4.2 * 2
        glutSolidCube(1.0)
        glPopMatrix()

        # Beak - increased scales by 6x
        glPushMatrix()
        glColor3f(*camo_scheme["dark"])
        glScalef(3.6, 1.2, 3.0)  # 1.8 * 2, 0.6 * 2, 1.5 * 2
        glTranslatef(0, 1.8, 20.1)  # 0.9 * 2, 10.05 * 2
        glutSolidCube(1)
        glPopMatrix()

        # Eyes - increased scales by 6x
        for i in [-1, 1]:
            glPushMatrix()
            glColor3f(*eye_black)
            glScalef(1.2, 1.2, 1.2)  # 0.6 * 2, 0.6 * 2, 0.6 * 2
            glTranslatef(i * 7.5, 10.8, 45.0)  # 3.75 * 2, 5.4 * 2, 22.5 * 2
            glutSolidCube(1.0)
            glPopMatrix()

        # Wings - increased scales by 6x
        wing_delta = 25 * sin(radians(self.wing_angle))
        for i in [-1, 1]:
            glPushMatrix()
            glColor3f(*camo_scheme["medium"])
            glTranslatef(i * 4.8, 1.2, 0.0)  # 2.4 * 2, 0.6 * 2, 0.0
            if self.state == 'flying':
                glRotatef(i * (-wing_delta + 30), 0, 0, 1)
            glScalef(11.4, 1.2, 6.0)  # 5.7 * 2, 0.6 * 2, 3.0 * 2
            glutSolidCube(1.5)
            glPopMatrix()

        # Legs - increased scales by 6x
        for i in [-1, 1]:
            glPushMatrix()
            glColor3f(*camo_scheme["dark"])
            glScalef(1.8, 6.0, 1.8)  # 0.9 * 2, 3.0 * 2, 0.9 * 2
            glTranslatef(i * 6.0, -3.6, -3.0)  # 3.0 * 2, -1.8 * 2, -1.5 * 2
            glutSolidCube(1.0)
            glPopMatrix()

        # Tail - increased scales by 6x
        glPushMatrix()
        glColor3f(*camo_scheme["dark"])
        glTranslatef(0, -0.6, -6.0)  # -0.3 * 2, -3.0 * 2
        glRotatef(20, 1, 0, 0)
        glScalef(10.8, 1.8, 14.4)  # 5.4 * 2, 0.9 * 2, 7.2 * 2
        glutSolidCube(1.0)
        glPopMatrix()

        glPopMatrix()

    def drop_duck(self):
        if self.state == 'flying':
            self.state = 'falling'
            self.wing_angle = 0.0
            self.fall_speed = 0.0
            return True
        return False

    def dead_duck(self):
        self.state = 'dead'
        self.wing_angle = 0.0


class GroundDuck(Duck):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.state = 'walking'  # walking, dead
        self.walk_speed = DUCK_SPEED * 0.5
        self.walk_direction = random.choice([-1, 1])
        self.walk_timer = 0.0
        self.walk_duration = random.uniform(2.0, 5.0)

    def update(self, speed_multiplier=1.0, game=None):
        if self.state == 'walking':
            self.walk_timer += 0.016  # Assuming 60 FPS
            if self.walk_timer >= self.walk_duration:
                self.walk_direction = -self.walk_direction
                self.walk_timer = 0.0
                self.walk_duration = random.uniform(2.0, 5.0)
            self.position[0] += self.walk_direction * self.walk_speed * speed_multiplier
            # Keep on ground
            self.position[2] = 0

            # Check collision with trees
            if game and game.is_point_in_tree(self.position[0], self.position[1], self.position[2]):
                self.walk_direction = -self.walk_direction
                self.position[0] += self.walk_direction * self.walk_speed * speed_multiplier

            # If walk too far, reset
            if abs(self.position[0]) > GROUND_HALF_LENGTH:
                self.position[0] = self.initial_pos[0]
                self.walk_direction = random.choice([-1, 1])

    def draw(self, night_mode=False, night_vision=False):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])

        # Rotate to face walking direction
        if self.state == 'walking':
            angle = 90 if self.walk_direction > 0 else -90
            glRotatef(angle, 0, 0, 1)

        if self.state == 'dead':
            glRotatef(180, 1, 0, 0)

        # Camouflage in night mode unless night vision is on
        if night_mode and not night_vision:
            camo_scheme = {"light": (0.1, 0.1, 0.1), "med": (0.05, 0.05, 0.05), "medium": (0.02, 0.02, 0.02), "dark": (0.01, 0.01, 0.01)}
        else:
            camo_scheme = self.color_scheme

        # Body - increased scales by 6x (3x * 2x)
        glPushMatrix()
        glColor3f(*camo_scheme["light"])
        glScalef(9.0, 6.0, 15.0)  # 4.5 * 2, 3.0 * 2, 7.5 * 2
        glutSolidCube(1.5)
        glPopMatrix()

        # Neck - increased scales by 6x
        glPushMatrix()
        glColor3f(*camo_scheme["dark"])
        glScalef(4.2, 3.0, 4.2)  # 2.1 * 2, 1.5 * 2, 2.1 * 2
        glTranslatef(0, 1.8, 9.0)  # 0.9 * 2, 4.5 * 2
        glutSolidCube(1.0)
        glPopMatrix()

        # Head - increased scales by 6x
        glPushMatrix()
        glColor3f(*camo_scheme["med"])
        glScalef(6.6, 6.0, 6.0)  # 3.3 * 2, 3.0 * 2, 3.0 * 2
        glTranslatef(0, 1.2, 8.4)  # 0.6 * 2, 4.2 * 2
        glutSolidCube(1.0)
        glPopMatrix()

        # Beak - increased scales by 6x
        glPushMatrix()
        glColor3f(*camo_scheme["dark"])
        glScalef(3.6, 1.2, 3.0)  # 1.8 * 2, 0.6 * 2, 1.5 * 2
        glTranslatef(0, 1.8, 20.1)  # 0.9 * 2, 10.05 * 2
        glutSolidCube(1)
        glPopMatrix()

        # Eyes - increased scales by 6x
        for i in [-1, 1]:
            glPushMatrix()
            glColor3f(*eye_black)
            glScalef(1.2, 1.2, 1.2)  # 0.6 * 2, 0.6 * 2, 0.6 * 2
            glTranslatef(i * 7.5, 10.8, 45.0)  # 3.75 * 2, 5.4 * 2, 22.5 * 2
            glutSolidCube(1.0)
            glPopMatrix()

        # Wings - increased scales by 6x
        wing_delta = 25 * sin(radians(self.wing_angle))
        for i in [-1, 1]:
            glPushMatrix()
            glColor3f(*camo_scheme["medium"])
            glTranslatef(i * 4.8, 1.2, 0.0)  # 2.4 * 2, 0.6 * 2, 0.0
            if self.state == 'flying':
                glRotatef(i * (-wing_delta + 30), 0, 0, 1)
            glScalef(11.4, 1.2, 6.0)  # 5.7 * 2, 0.6 * 2, 3.0 * 2
            glutSolidCube(1.5)
            glPopMatrix()

        # Legs - increased scales by 6x
        for i in [-1, 1]:
            glPushMatrix()
            glColor3f(*camo_scheme["dark"])
            glScalef(1.8, 6.0, 1.8)  # 0.9 * 2, 3.0 * 2, 0.9 * 2
            glTranslatef(i * 6.0, -3.6, -3.0)  # 3.0 * 2, -1.8 * 2, -1.5 * 2
            glutSolidCube(1.0)
            glPopMatrix()

        # Tail - increased scales by 6x
        glPushMatrix()
        glColor3f(*camo_scheme["dark"])
        glTranslatef(0, -0.6, -6.0)  # -0.3 * 2, -3.0 * 2
        glRotatef(20, 1, 0, 0)
        glScalef(10.8, 1.8, 14.4)  # 5.4 * 2, 0.9 * 2, 7.2 * 2
        glutSolidCube(1.0)
        glPopMatrix()

        glPopMatrix()

    def drop_duck(self):
        if self.state == 'walking':
            self.state = 'dead'
            return True
        return False


class Bullet:
    def __init__(self, start_pos, direction):
        self.position = list(start_pos)
        self.direction = direction
        self.creation_time = time.time()

    def update(self):
        self.position[0] += self.direction[0] * BULLET_SPEED
        self.position[1] += self.direction[1] * BULLET_SPEED
        self.position[2] += self.direction[2] * BULLET_SPEED

    def draw(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glColor3f(1.0, 1.0, 0.0) # Yellow
        glutSolidSphere(2, 8, 8)
        glPopMatrix()


class HUD:
    def __init__(self):
        self.score = 0
        self.ammo = 10
        self.magazine_size = 10
        self.health = 100
        self.messages = []
        self.night_vision = False
        self.weapons = ["Shotgun"]
        self.reticle_good = True
        self.crosshair_size = 10
        self.last_shot_time = 0.0
        self.auto_fire_active = False

    def draw_text(self, x, y, text, font=GLUT_BITMAP_HELVETICA_18):
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))

    def add_score(self, value):
        self.score += value
        self.messages.append((f"+{value} pts", time.time()))

    def shoot(self):
        now = time.time()
        cooldown = 0.1 if hasattr(self, 'auto_fire_active') and self.auto_fire_active else 0.5
        if now - self.last_shot_time < cooldown:
            return False
        if self.ammo > 0:
            self.ammo -= 1
            self.last_shot_time = now
            return True
        else:
            self.messages.append(("Out of Ammo! Press R to Reload", time.time()))
            return False

    def reload(self):
        self.ammo = self.magazine_size
        self.messages.append(("Reloaded!", time.time()))

    def render(self, window_w, window_h, paused, night_mode=False, auto_fire_active=False, cooldown_remaining=0):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_w, 0, window_h)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # UI state: no lighting, no depth, enable blending
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Draw Score, Ammo
        glColor3f(1, 1, 1)
        self.draw_text(20, window_h - 30, f"Score: {self.score}")
        self.draw_text(20, window_h - 55, f"Ammo: {self.ammo}/{self.magazine_size}")
        if night_mode:
            self.draw_text(20, window_h - 80, "Night Mode")
        if self.night_vision:
            self.draw_text(20, window_h - 105, "Night Vision Active")
        if auto_fire_active:
            glColor3f(0, 1, 0)
            self.draw_text(20, window_h - 130, "Auto Fire Active")
        elif cooldown_remaining > 0:
            glColor3f(1, 0, 0)
            self.draw_text(20, window_h - 130, f"Auto Fire Cooldown: {int(cooldown_remaining)}s")

        # Draw Paused Message
        if paused:
            glColor3f(1, 0, 0)
            self.draw_text(window_w / 2 - 50, window_h / 2, "PAUSED")

        # Draw Crosshair
        cx, cy = window_w // 2, window_h // 2
        size = self.crosshair_size
        glColor3f(0.1, 1.0, 0.1)
        glBegin(GL_LINES)
        glVertex2f(cx - size, cy); glVertex2f(cx + size, cy)
        glVertex2f(cx, cy - size); glVertex2f(cx, cy + size)
        glEnd()

        # Draw Floating Messages
        now = time.time()
        active_messages = []
        y_offset = 0
        for msg, t in self.messages:
            if now - t < 2.0:
                glColor3f(1, 1, 0)
                self.draw_text(window_w / 2 - 100, window_h / 2 + 60 + y_offset, msg)
                y_offset += 20
                active_messages.append((msg, t))
        self.messages = active_messages

        # Restore state
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()


class Shop:
    def __init__(self, hud, game):
        self.active = False
        self.hud = hud
        self.game = game
        self.currency = 0
        self.items = [
            {"name": "Bigger Magazine", "key": "G", "description": "+5 bullets per reload", "cost": 100},
            {"name": "Night Vision", "key": "N", "description": "See ducks in night mode", "cost": 50},
            {"name": "Auto Fire Mode", "key": "A", "description": "Auto-lock on ducks, increase fire rate for 10s", "cost": 200},
        ]
        self.last_message = ""
        self.last_message_time = 0
        self.active_effects = {}
        self.cooldown_end_time = 0

    def toggle(self):
        self.active = not self.active

    def purchase(self, key):
        if not self.active: return
        key = key.decode("utf-8").upper()
        for item in self.items:
            if item["key"] == key:
                if item["name"] == "Night Vision" and not self.game.night_mode:
                    self.last_message = "Can only buy at night!"
                    self.last_message_time = time.time()
                    return True
                if item["name"] == "Auto Fire Mode" and time.time() < self.cooldown_end_time:
                    self.last_message = "Auto Fire on cooldown!"
                    self.last_message_time = time.time()
                    return True
                if self.currency >= item["cost"]:
                    self.currency -= item["cost"]
                    self.apply_effect(item)
                    self.last_message = f"Purchased {item['name']}!"
                else:
                    self.last_message = "Not enough points!"
                self.last_message_time = time.time()
                return True
        return False

    def apply_effect(self, item):
        name = item["name"]
        if name == "Bigger Magazine":
            self.hud.magazine_size += 5
            self.hud.reload()
            self.hud.messages.append(("Magazine +5", time.time()))
        elif name == "Night Vision":
            self.hud.night_vision = True
            self.hud.messages.append(("Night Vision Equipped", time.time()))
        elif name == "Auto Fire Mode":
            self.game.auto_fire_active = True
            self.game.auto_fire_end_time = time.time() + 10
            self.game.last_auto_shot = time.time()
            self.hud.messages.append(("Auto Fire Activated for 10s", time.time()))

    def draw_text(self, x, y, text, font=GLUT_BITMAP_HELVETICA_18):
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))

    def render(self, window_w, window_h):
        if not self.active: return

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_w, 0, window_h)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # UI state: no lighting, no depth, enable blending
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Semi-transparent backdrop
        glColor4f(0.0, 0.0, 0.0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(window_w, 0)
        glVertex2f(window_w, window_h); glVertex2f(0, window_h)
        glEnd()

        # Text + items
        cx, cy = window_w // 2, window_h // 2
        glColor3f(1, 1, 0); self.draw_text(cx - 60, cy + 130, "=== SHOP ===")
        glColor3f(1, 1, 1); self.draw_text(cx - 120, cy + 100, f"Points Available: {self.currency}")
        y_offset = 0
        for item in self.items:
            color = (0.5, 1, 0.5) if self.currency >= item["cost"] else (1, 0.3, 0.3)
            if item["name"] == "Auto Fire Mode" and time.time() < self.cooldown_end_time:
                color = (1, 0.3, 0.3)
            glColor3f(*color)
            self.draw_text(cx - 250, cy + 60 - y_offset,
                                f"[{item['key']}] {item['name']} ({item['cost']} pts) - {item['description']}")
            y_offset += 25

        glColor3f(0.8, 0.8, 0.8)
        self.draw_text(cx - 160, cy - 120, "Press item key to buy • Press B to exit")

        if time.time() - self.last_message_time < 2:
            glColor3f(0, 1, 0)
            self.draw_text(cx - 100, cy - 150, self.last_message)

        # Restore state
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()


# * Main Game Class
class Game:
    def __init__(self):
        # Player and Camera
        self.player_pos = [-100, -100, PLAYER_Z]
        self.player_r = PLAYER_R_INITIAL
        self.player_pitch = 0  # Added for vertical look
        self.look_at = [0, 200, PLAYER_Z] # Relative to player

        # Game State
        self.key_states = {b'w': False, b's': False, b'a': False, b'd': False}
        self.active_ducks = []
        self.bullets = []
        self.tree_positions = []
        self.hud = HUD()
        self.shop = Shop(self.hud, self)
        self.paused = False

        # Difficulty
        self.speed_multiplier = 1.0
        self.night_mode = False

        # Auto Fire
        self.auto_fire_active = False
        self.auto_fire_end_time = 0
        self.last_auto_shot = 0

        # Duck Spawning
        self.last_spawn_time = time.time()
        self.spawn_interval = random.uniform(2.0, 5.0)

        # Fallback teapot rotation (for shop overlay)
        self.teapot_angle = 0.0

        self.initialize_game()

    def update_cursor_visibility(self):
        if self.paused:
            glutSetCursor(GLUT_CURSOR_LEFT_ARROW)  # Show cursor when paused
        elif self.shop.active:
            glutSetCursor(GLUT_CURSOR_NONE)  # Hide cursor when shop is active
        else:
            glutSetCursor(GLUT_CURSOR_NONE)  # Hide cursor when playing

    def initialize_game(self):
        self.spawn_ducks()
        self.generate_trees()
        self.setup_lighting()
        
    def setup_lighting(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        light_pos = [0, 0, 500, 1]
        light_ambient = [0.4, 0.4, 0.4, 1.0]
        light_diffuse = [0.8, 0.8, 0.8, 1.0]
        
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        
    def spawn_ducks(self):
        flying_ducks = [
            Duck(random.uniform(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH),
                 random.uniform(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH),
                 random.uniform(DUCK_FLYING_Z_MIN, DUCK_FLYING_Z_MAX))
            for _ in range(DUCK_COUNT)
        ]
        ground_ducks = [
            GroundDuck(random.uniform(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH),
                       random.uniform(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH),
                       0)
            for _ in range(GROUND_DUCK_COUNT)
        ]
        self.active_ducks = flying_ducks + ground_ducks

    def generate_trees(self):
        for _ in range(TREE_COUNT):
            x = random.uniform(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH)
            y = random.uniform(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH)
            self.tree_positions.append((x, y))

    def is_point_in_tree(self, px, py, pz):
        for tx, ty in self.tree_positions:
            # Trunk
            if (tx - TREE_TRUNK_RADIUS <= px <= tx + TREE_TRUNK_RADIUS and
                ty - TREE_TRUNK_RADIUS <= py <= ty + TREE_TRUNK_RADIUS and
                1 <= pz <= TREE_TRUNK_HEIGHT):
                return True
            # Leaves
            if (tx - TREE_LEAVES_RADIUS <= px <= tx + TREE_LEAVES_RADIUS and
                ty - TREE_LEAVES_RADIUS <= py <= ty + TREE_LEAVES_RADIUS and
                TREE_TRUNK_HEIGHT <= pz <= TREE_TRUNK_HEIGHT + TREE_LEAVES_HEIGHT):
                return True
        return False

    def update_player(self):
        if self.shop.active:
            return

        # Calculate new position
        new_pos = self.player_pos[:]

        # Forward/Backward
        move_vec_x = -cos(radians(self.player_r))
        move_vec_y = -sin(radians(self.player_r))
        if self.key_states[b'w']:
            new_pos[0] += move_vec_x * PLAYER_SPEED
            new_pos[1] += move_vec_y * PLAYER_SPEED
        if self.key_states[b's']:
            new_pos[0] -= move_vec_x * PLAYER_SPEED
            new_pos[1] -= move_vec_y * PLAYER_SPEED

        # Strafe Left/Right
        strafe_vec_x = -cos(radians(self.player_r + 90))
        strafe_vec_y = -sin(radians(self.player_r + 90))
        if self.key_states[b'a']:
            new_pos[0] += strafe_vec_x * PLAYER_SPEED
            new_pos[1] += strafe_vec_y * PLAYER_SPEED
        if self.key_states[b'd']:
            new_pos[0] -= strafe_vec_x * PLAYER_SPEED
            new_pos[1] -= strafe_vec_y * PLAYER_SPEED

        # Check collision with trees
        if not self.is_point_in_tree(new_pos[0], new_pos[1], PLAYER_Z):
            self.player_pos = new_pos

        # Boundary checks
        self.player_pos[0] = max(-GROUND_HALF_LENGTH, min(GROUND_HALF_LENGTH, self.player_pos[0]))
        self.player_pos[1] = max(-GROUND_HALF_LENGTH, min(GROUND_HALF_LENGTH, self.player_pos[1]))

    def passive_mouse(self, x, y):
        if self.paused:
            return
        # Mouse look for both horizontal and vertical
        center_x = WINDOW_WIDTH / 2
        center_y = WINDOW_HEIGHT / 2
        delta_x = x - center_x
        delta_y = y - center_y

        self.player_r += delta_x * 0.05
        self.player_pitch += delta_y * 0.05
        self.player_pitch = max(-90, min(90, self.player_pitch))  # Limit pitch

        # Recenter mouse to
        if abs(delta_x) > 2 or abs(delta_y) > 2:  # Deadzone
            glutWarpPointer(int(center_x), int(center_y))

    def keyboard_down(self, key, x, y):
        if key in self.key_states:
            self.key_states[key] = True
        elif key.lower() == b'r':
            self.hud.reload()
        elif key.lower() == b'b':
            self.shop.toggle()
            self.update_cursor_visibility()
        elif key.lower() == b'p':
            self.paused = not self.paused
            self.update_cursor_visibility()
        elif key == b'\t':
            self.night_mode = not self.night_mode
        elif key.lower() == b'q':
            glutLeaveMainLoop()
            sys.exit()
        elif key == b'\x1b': # Escape key
            glutLeaveMainLoop()
            sys.exit()

        # Pass purchases to shop if it is active
        if self.shop.active:
            self.shop.purchase(key)

    def keyboard_up(self, key, x, y):
        if key in self.key_states:
            self.key_states[key] = False

    def mouse_listener(self, button, state, x, y):
        if self.shop.active or self.paused:
            return
        # Shoot on left click press
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            self.shoot()

        # Aim up/down with scroll wheel (alternative to mouse look)
        if button == 3 and state == GLUT_DOWN: # Scroll up
             self.player_pitch = min(self.player_pitch + LOOK_DELTA_ANGLE, 90)
        if button == 4 and state == GLUT_DOWN: # Scroll down
             self.player_pitch = max(self.player_pitch - LOOK_DELTA_ANGLE, -90)

    def shoot(self):
        if self.hud.shoot():
            # Calculate bullet direction vector using pitch
            cam_pos = self.player_pos
            look_point = [
                self.player_pos[0] - 200 * cos(radians(self.player_r)) * cos(radians(self.player_pitch)),
                self.player_pos[1] - 200 * sin(radians(self.player_r)) * cos(radians(self.player_pitch)),
                self.player_pos[2] + 200 * sin(radians(self.player_pitch)) - 0.01
            ]

            direction = [
                look_point[0] - cam_pos[0],
                look_point[1] - cam_pos[1],
                look_point[2] - cam_pos[2],
            ]

            # Normalize the vector
            mag = sqrt(sum(d**2 for d in direction))
            if mag > 0:
                norm_direction = [d / mag for d in direction]
                self.bullets.append(Bullet(cam_pos, norm_direction))

    def animate(self):
        if self.paused:
            glutPostRedisplay()
            return

        self.update_cursor_visibility()

        # Update difficulty based on score
        if self.night_mode:
            self.speed_multiplier = 2.0
        elif self.hud.score >= 50:
            self.speed_multiplier = 1.5
        else:
            self.speed_multiplier = 1.0

        # Update player & world only when shop is closed
        self.update_player()

        # Update ducks
        for duck in self.active_ducks:
            duck.update(self.speed_multiplier, self)

        # Remove dead ducks
        self.active_ducks = [d for d in self.active_ducks if d.state != 'dead']

        # Spawn new ducks if needed
        now = time.time()
        if now - self.last_spawn_time > self.spawn_interval:
            flying = [d for d in self.active_ducks if not isinstance(d, GroundDuck)]
            ground = [d for d in self.active_ducks if isinstance(d, GroundDuck)]
            if len(flying) < DUCK_COUNT:
                self.active_ducks.append(Duck(random.uniform(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH),
                                               random.uniform(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH),
                                               random.uniform(DUCK_FLYING_Z_MIN, DUCK_FLYING_Z_MAX)))
            if len(ground) < GROUND_DUCK_COUNT:
                self.active_ducks.append(GroundDuck(random.uniform(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH),
                                                    random.uniform(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH),
                                                    0))
            self.last_spawn_time = now
            self.spawn_interval = random.uniform(2.0, 5.0)

        # Update bullets and check lifespan
        self.bullets = [b for b in self.bullets if now - b.creation_time < BULLET_LIFESPAN]
        for bullet in self.bullets:
            bullet.update()

        # Remove bullets that hit trees or go below ground
        self.bullets = [b for b in self.bullets if not (self.is_point_in_tree(b.position[0], b.position[1], b.position[2]) or b.position[2] < 0)]

        # Auto Fire Logic
        if self.auto_fire_active:
            if now > self.auto_fire_end_time:
                self.auto_fire_active = False
                self.shop.cooldown_end_time = now + 60
                self.hud.messages.append(("Auto Fire Deactivated", now))
            elif now - self.last_auto_shot > 0.2:
                self.last_auto_shot = now
                # Find nearest duck
                nearest_duck = None
                min_dist = float('inf')
                for duck in self.active_ducks:
                    if duck.state in ['flying', 'walking']:
                        dist = sqrt(sum((p1 - p2)**2 for p1, p2 in zip(self.player_pos, duck.position)))
                        if dist < min_dist:
                            min_dist = dist
                            nearest_duck = duck
                if nearest_duck:
                    # Calculate direction to duck
                    direction = [
                        nearest_duck.position[0] - self.player_pos[0],
                        nearest_duck.position[1] - self.player_pos[1],
                        nearest_duck.position[2] - self.player_pos[2],
                    ]
                    mag = sqrt(sum(d**2 for d in direction))
                    if mag > 0:
                        norm_direction = [d / mag for d in direction]
                        self.bullets.append(Bullet(self.player_pos, norm_direction))
                        if not self.hud.auto_fire_active:
                            self.hud.ammo -= 1

        # Collision detection
        bullets_to_remove = []
        for i, bullet in enumerate(self.bullets):
            for duck in self.active_ducks:
                if duck.state in ['flying', 'walking']:
                    dist_sq = sum((p1 - p2)**2 for p1, p2 in zip(bullet.position, duck.position))
                    if dist_sq < DUCK_HITBOX_RADIUS**2:
                        if duck.drop_duck():
                            # Double points in night mode
                            points = 20 if self.night_mode else 10
                            self.hud.add_score(points)
                            self.shop.currency += points
                            bullets_to_remove.append(i)
                            break
            if i in bullets_to_remove:
                continue

        glutPostRedisplay()

    def draw_environment(self):
        # Draw ground
        glPushMatrix()
        glColor3f(0.2, 0.8, 0.2)  # Green ground
        glBegin(GL_QUADS)
        glVertex3f(-GROUND_HALF_LENGTH, -GROUND_HALF_LENGTH, 0)
        glVertex3f(GROUND_HALF_LENGTH, -GROUND_HALF_LENGTH, 0)
        glVertex3f(GROUND_HALF_LENGTH, GROUND_HALF_LENGTH, 0)
        glVertex3f(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH, 0)
        glEnd()
        glPopMatrix()

        # Draw skybox
        glPushMatrix()
        if self.night_mode:
            glColor3f(0.0, 0.0, 0.0)  # Black sky for night
        else:
            glColor3f(0.5, 0.7, 1.0)  # Blue sky
        glBegin(GL_QUADS)
        # Back
        glVertex3f(-GROUND_HALF_LENGTH, -GROUND_HALF_LENGTH, SKYBOX_HEIGHT)
        glVertex3f(GROUND_HALF_LENGTH, -GROUND_HALF_LENGTH, SKYBOX_HEIGHT)
        glVertex3f(GROUND_HALF_LENGTH, -GROUND_HALF_LENGTH, 0)
        glVertex3f(-GROUND_HALF_LENGTH, -GROUND_HALF_LENGTH, 0)
        # Front
        glVertex3f(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH, SKYBOX_HEIGHT)
        glVertex3f(GROUND_HALF_LENGTH, GROUND_HALF_LENGTH, SKYBOX_HEIGHT)
        glVertex3f(GROUND_HALF_LENGTH, GROUND_HALF_LENGTH, 0)
        glVertex3f(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH, 0)
        # Left
        glVertex3f(-GROUND_HALF_LENGTH, -GROUND_HALF_LENGTH, SKYBOX_HEIGHT)
        glVertex3f(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH, SKYBOX_HEIGHT)
        glVertex3f(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH, 0)
        glVertex3f(-GROUND_HALF_LENGTH, -GROUND_HALF_LENGTH, 0)
        # Right
        glVertex3f(GROUND_HALF_LENGTH, -GROUND_HALF_LENGTH, SKYBOX_HEIGHT)
        glVertex3f(GROUND_HALF_LENGTH, GROUND_HALF_LENGTH, SKYBOX_HEIGHT)
        glVertex3f(GROUND_HALF_LENGTH, GROUND_HALF_LENGTH, 0)
        glVertex3f(GROUND_HALF_LENGTH, -GROUND_HALF_LENGTH, 0)
        # Top
        glVertex3f(-GROUND_HALF_LENGTH, -GROUND_HALF_LENGTH, SKYBOX_HEIGHT)
        glVertex3f(GROUND_HALF_LENGTH, -GROUND_HALF_LENGTH, SKYBOX_HEIGHT)
        glVertex3f(GROUND_HALF_LENGTH, GROUND_HALF_LENGTH, SKYBOX_HEIGHT)
        glVertex3f(-GROUND_HALF_LENGTH, GROUND_HALF_LENGTH, SKYBOX_HEIGHT)
        glEnd()
        glPopMatrix()

    def draw_world(self):
        # Draw trees
        for x, y in self.tree_positions:
            glPushMatrix()
            glTranslatef(x, y, 0)
            # Trunk
            glColor3f(0.4, 0.2, 0.0)
            glPushMatrix()
            glTranslatef(0, 0, TREE_TRUNK_HEIGHT / 2)
            glScalef(TREE_TRUNK_RADIUS, TREE_TRUNK_RADIUS, TREE_TRUNK_HEIGHT)
            glutSolidCube(1)
            glPopMatrix()
            # Leaves
            glColor3f(0.0, 0.5, 0.0)
            glPushMatrix()
            glTranslatef(0, 0, TREE_TRUNK_HEIGHT + TREE_LEAVES_HEIGHT / 2)
            glScalef(TREE_LEAVES_RADIUS, TREE_LEAVES_RADIUS, TREE_LEAVES_HEIGHT)
            glutSolidCube(1)
            glPopMatrix()
            glPopMatrix()

        # Draw ducks
        for duck in self.active_ducks:
            duck.draw(self.night_mode, self.hud.night_vision)

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw()

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Set up camera
        cam_pos = self.player_pos
        look_point = [
            self.player_pos[0] - 200 * cos(radians(self.player_r)) * cos(radians(self.player_pitch)),
            self.player_pos[1] - 200 * sin(radians(self.player_r)) * cos(radians(self.player_pitch)),
            self.player_pos[2] + 200 * sin(radians(self.player_pitch))
        ]
        gluLookAt(cam_pos[0], cam_pos[1], cam_pos[2],
                  look_point[0], look_point[1], look_point[2],
                  0, 0, 1)

        # Draw environment and world
        self.draw_environment()
        self.draw_world()

        # Draw HUD
        cooldown_remaining = max(0, self.shop.cooldown_end_time - time.time())
        self.hud.render(WINDOW_WIDTH, WINDOW_HEIGHT, self.paused, self.night_mode, self.auto_fire_active, cooldown_remaining)

        # Draw shop if active
        self.shop.render(WINDOW_WIDTH, WINDOW_HEIGHT)

        glutSwapBuffers()

    def reshape(self, width, height):
        if height == 0:
            height = 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FOV_Y, width / height, 0.01, 10000.0)
        glMatrixMode(GL_MODELVIEW)


# * Main Function
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"Duck Hunter")

    game = Game()

    glutDisplayFunc(game.display)
    glutReshapeFunc(game.reshape)
    glutKeyboardFunc(game.keyboard_down)
    glutKeyboardUpFunc(game.keyboard_up)
    glutMouseFunc(game.mouse_listener)
    glutPassiveMotionFunc(game.passive_mouse)
    glutIdleFunc(game.animate)

    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

    glutMainLoop()


if __name__ == "__main__":
    main()
