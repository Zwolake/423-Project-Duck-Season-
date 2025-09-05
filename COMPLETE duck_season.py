#Game Description : 
# Features

# Core Libraries and Dependencies
# - OpenGL.GL, OpenGL.GLUT, OpenGL.GLU for 3D rendering
# - math for trigonometric calculations
# - random for procedural generation
# - time for timing and cooldowns
# - sys for system exit

# Game Configuration & Constants
# - Window Settings: 1280x720 resolution
# - Player & Camera:
#   - Movement speed: 1.5 units/frame
#   - Mouse look sensitivity
#   - Vertical pitch control
#   - FOV: 70 degrees (normal), 20 degrees (sniper)
# - World:
#   - Ground size: 2000x2000 units
#   - Skybox height: 1000 units
#   - Gravity: 0.5 units/frame²
# - Trees: 50 randomly placed trees as obstacles
# - Ducks:
#   - 20 flying ducks
#   - 20 ground ducks
#   - Flying height range: 300-600 units
#   - Speed: 1.0 units/frame
#   - Hitbox radius: 135 units
# - Bullets:
#   - Speed: 10.0 units/frame
#   - Lifespan: 5 seconds
# - Dog Companion:
#   - Cost: 100 points
#   - Deployment duration: 30 seconds
#   - Hunting window: 5-10 seconds
#   - Speed: 3.0 units/frame
#   - Catch radius: 60 units
# - Color Schemes: 5 different duck color variations

# Game Objects

# Duck Class
# - States: flying, falling, dead
# - Features:
#   - Wing flapping animation (angle increment: 10°/frame)
#   - 3D model with body, neck, head, beak, eyes, wings, legs, tail
#   - Random color schemes
#   - Collision with trees
#   - Boundary reset when flying too far
#   - Size scaling based on state

# GroundDuck Class (inherits from Duck)
# - States: walking, dead
# - Features:
#   - Ground-based movement with random direction changes
#   - Walking animation with leg swinging
#   - Wing flapping same as flying ducks
#   - Collision avoidance with trees
#   - Z-axis movement (up/down on ground)

# Bullet Class
# - Simple projectile with position, direction, and creation time
# - Yellow sphere representation
# - Automatic removal after lifespan

# Dog Class
# - Features:
#   - Cube-based 3D model (body, head, ears, legs, tail)
#   - Hunts ground ducks within range
#   - Time-limited deployment (30s total, 5-10s hunting)
#   - Scoring: +10 per duck caught
#   - Bonus: +50 if all initial ground ducks are caught
#   - Cooldown after deployment

# HUD Class
# - Displays:
#   - Score and total points
#   - Ammo count (10/10 default, upgradable)
#   - Night mode indicator
#   - Night vision status
#   - Auto fire status and cooldown
#   - Dog status (time remaining, ducks caught)
# - Features:
#   - Floating messages for events
#   - Crosshair
#   - Paused message

# Shop Class
# - Items:
#   - Bigger Magazine (+5 ammo, 100 pts)
#   - Night Vision (see in night mode, 50 pts)
#   - Auto Fire Mode (10s auto-lock, 200 pts)
#   - Dog Companion (30s deployment, 100 pts)
# - Features:
#   - Currency system
#   - Cooldowns for limited items
#   - Visual feedback for purchases

#  Main Game Class (Game)
# - Initialization:
#   - Duck spawning
#   - Tree generation
#   - Lighting setup (single light source)
# - Player Controls:
#   - WASD movement
#   - Mouse look (horizontal/vertical)
#   - Shooting (left click)
#   - Sniper mode (right click)
#   - Reload (R key)
#   - Shop toggle (B key)
#   - Pause (P key)
#   - Night mode (Tab)
#   - Quit (Q/Escape)
# - Game Mechanics:
#   - Collision detection (bullets vs ducks, player vs trees)
#   - Auto fire targeting nearest duck
#   - Difficulty scaling (speed increases with score/night mode)
#   - Duck respawning
#   - Bullet management
# - Rendering:
#   - 3D environment (ground, skybox)
#   - World objects (trees, ducks, bullets, dog)
#   - HUD overlay
#   - Shop interface
# - Game Loop:
#   - 60 FPS animation
#   - Real-time updates for all objects

#  Additional Features
# - Night Mode: Darker environment, camouflage for ducks, requires night vision
# - Auto Fire: Automatic targeting with increased fire rate
# - Dog Companion: AI helper for hunting ground ducks
# - Shop System: Upgradeable ammo, special abilities
# - Scoring System: Points for hits, bonuses for dog catches
# - Collision System: Trees block movement and bullets
# - Boundary System: Ducks reset position when flying too far
# - Animation: Wing flapping, leg swinging, dog movement

# Technical Features
# - OpenGL immediate mode rendering
# - GLUT event handling
# - Perspective projection with gluPerspective
# - Lighting with glLight
# - Texture-less 3D models using glutSolidCube and glutSolidSphere
# - Real-time 3D transformations (translate, rotate, scale)
# - Mouse capture and warping for look controls
# - Keyboard state tracking for smooth movement
# - Timer-based events and cooldowns


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
GROUND_DUCK_COUNT = 20
DUCK_FLYING_Z_MIN = 300
DUCK_FLYING_Z_MAX = 600
DUCK_SPEED = 1.0
DUCK_HITBOX_RADIUS = 135.0  # Decreased hitbox

# Bullet
BULLET_SPEED = 10.0
BULLET_LIFESPAN = 5.0 # in seconds

# Dog
DOG_COST = 100
DOG_DEPLOY_DURATION = 30.0           # seconds total on field
DOG_HUNT_MIN = 5.0                   # will hunt for 5–10 seconds (random)
DOG_HUNT_MAX = 10.0
DOG_SPEED = 3.0
DOG_CATCH_RADIUS = 60.0

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
        self.direction = [random.choice([-1, 1]), random.choice([-1, 1]), random.uniform(-0.5, 0.5)]
        self.state = 'flying'  # flying, falling, dead
        self.wing_angle = 0.0
        self.fall_speed = 0.0
        self.color_scheme = random.choice(duck_color_schemes)
        self.dim = 6  # Added to match new14.py

    def update(self, speed_multiplier=1.0, game=None):
        if self.state == 'flying':
            self.wing_angle += 10.0
            # Simple movement logic
            self.position[0] += self.direction[0] * DUCK_SPEED * speed_multiplier
            self.position[1] += self.direction[1] * DUCK_SPEED * speed_multiplier
            self.position[2] += self.direction[2] * DUCK_SPEED * speed_multiplier
            self.position[2] = max(DUCK_FLYING_Z_MIN, min(DUCK_FLYING_Z_MAX, self.position[2]))

            # Check collision with trees
            if game and game.is_point_in_tree(self.position[0], self.position[1], self.position[2]):
                self.direction[0] = -self.direction[0]
                self.direction[1] = -self.direction[1]
                self.position[0] += self.direction[0] * DUCK_SPEED * speed_multiplier
                self.position[1] += self.direction[1] * DUCK_SPEED * speed_multiplier

            # If duck flies too far, reset its position
            if abs(self.position[0]) > GROUND_HALF_LENGTH or abs(self.position[1]) > GROUND_HALF_LENGTH:
                self.position = self.initial_pos[:]
                self.direction = [random.choice([-1, 1]), random.choice([-1, 1]), random.uniform(-0.5, 0.5)]

        elif self.state == 'falling':
            self.fall_speed += GRAVITY
            self.position[2] -= self.fall_speed
            if self.position[2] <= 0:
                self.position[2] = 0
                self.dead_duck()

    def draw(self, night_mode=False, night_vision=False):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])

        # Rotate duck to face its direction
        if self.state == 'flying':
            angle = degrees(atan2(self.direction[1], self.direction[0]))
            glRotatef(angle, 0, 0, 1)
        elif self.state == 'walking' and hasattr(self, 'dir'):
            angle = degrees(atan2(self.dir[1], self.dir[0]))
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

        # Overall scale to match new14.py
        glScalef(self.dim, self.dim, self.dim)
        glRotatef(90, 1, 0, 0)  # Match new14.py rotation
        glRotatef(self.rotation if hasattr(self, 'rotation') else 0, 0, 1, 0)  # Assuming rotation is angle for simplicity

        # Body - updated to match new14.py
        glPushMatrix()
        glColor3f(*camo_scheme["light"])
        glScalef(1.5, 1, 2.5)
        glTranslatef(0, 0, 0)
        glutSolidCube(1.5)
        glPopMatrix()

        # Neck - updated
        glPushMatrix()
        glColor3f(*camo_scheme["dark"])
        glScalef(0.7, 0.5, 0.7)
        glTranslatef(0, 0.6, 3)
        glutSolidCube(1.0)
        glPopMatrix()

        # Head - updated
        glPushMatrix()
        glColor3f(*camo_scheme["med"])
        glScalef(1.1, 1.0, 1.0)
        glTranslatef(0, 0.4, 2.8)
        glutSolidCube(1.0)
        glPopMatrix()

        # Beak - updated
        glPushMatrix()
        glColor3f(*camo_scheme["dark"])
        glScalef(0.6, 0.2, 0.5)
        glTranslatef(0, 0.6, 6.7)
        glutSolidCube(1)
        glPopMatrix()

        # Eyes - updated
        for i in [-1, 1]:
            glPushMatrix()
            glColor3f(*eye_black)
            glScalef(0.2, 0.2, 0.2)
            glTranslatef(i * 2.5, 3.6, 15.0)
            glutSolidCube(1.0)
            glPopMatrix()

        # Wings - updated
        wing_delta = 25 * sin(radians(self.wing_angle))
        for i in [-1, 1]:
            glPushMatrix()
            glColor3f(*camo_scheme["medium"])
            glTranslatef(i * 1.5 if i == -1 else 1.7, 0.4, 0.0)
            glRotatef(i * (-wing_delta + 30), 0, 0, 1)
            glScalef(1.9, 0.2, 1.0)
            glutSolidCube(1.5)
            glPopMatrix()

        # Legs - updated
        for i in [-1, 1]:
            glPushMatrix()
            glColor3f(*camo_scheme["dark"])
            glScalef(0.3, 1.0, 0.3)
            glTranslatef(i * 2.0, -1.2, -1.0)
            if self.state == 'walking' and hasattr(self, 'walk_timer'):
                leg_angle = 30 * sin(radians(self.walk_timer * 180))
                glRotatef(leg_angle * (-1 if i == -1 else 1), 0, 0, 1)
            glutSolidCube(1.0)
            glPopMatrix()

        # Tail - updated
        glPushMatrix()
        glColor3f(*camo_scheme["dark"])
        glTranslatef(0, -0.2, -2.0)
        glRotatef(20, 1, 0, 0)
        glScalef(1.8, 0.3, 2.4)
        glutSolidCube(1.0)
        glPopMatrix()

        glPopMatrix()

    def drop_duck(self):
        if self.state == 'flying':
            self.state = 'falling'
            self.wing_angle = 0.0
            self.fall_speed = 0.0
            self.dim = 4  # Match new14.py
            return True
        return False

    def dead_duck(self):
        self.state = 'dead'
        self.wing_angle = 0.0
        self.dim = 2  # Match new14.py


class GroundDuck(Duck):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.state = 'walking'  # walking, dead
        self.walk_speed = DUCK_SPEED * 0.5
        self.dir = [random.uniform(-1, 1), random.uniform(-1, 1)]
        mag = sqrt(self.dir[0]**2 + self.dir[1]**2)
        if mag > 0:
            self.dir = [self.dir[0] / mag, self.dir[1] / mag]
        self.walk_timer = 0.0
        self.walk_duration = random.uniform(2.0, 5.0)
        self.position = [x, y, 10]
        self.initial_pos = [x, y, 10]
        self.dim = 3
        self.dir_z = random.uniform(-0.5, 0.5)

    def update(self, speed_multiplier=1.0, game=None):
        if self.state == 'walking':
            self.walk_timer += 0.016  # Assuming 60 FPS
            self.wing_angle += 10.0
            if self.walk_timer >= self.walk_duration:
                self.dir = [random.uniform(-1, 1), random.uniform(-1, 1)]
                mag = sqrt(self.dir[0]**2 + self.dir[1]**2)
                if mag > 0:
                    self.dir = [self.dir[0] / mag, self.dir[1] / mag]
                self.walk_timer = 0.0
                self.walk_duration = random.uniform(2.0, 5.0)
            self.position[0] += self.dir[0] * self.walk_speed * speed_multiplier
            self.position[1] += self.dir[1] * self.walk_speed * speed_multiplier
            self.position[2] += self.dir_z * self.walk_speed * speed_multiplier
            self.position[2] = max(0, min(20, self.position[2]))

            # Check collision with trees
            if game and game.is_point_in_tree(self.position[0], self.position[1], self.position[2]):
                self.dir[0] = -self.dir[0]
                self.dir[1] = -self.dir[1]
                self.position[0] += self.dir[0] * self.walk_speed * speed_multiplier
                self.position[1] += self.dir[1] * self.walk_speed * speed_multiplier

            # If walk too far, reset
            if abs(self.position[0]) > GROUND_HALF_LENGTH or abs(self.position[1]) > GROUND_HALF_LENGTH:
                self.position[0] = self.initial_pos[0]
                self.position[1] = self.initial_pos[1]
                self.position[2] = 10
                self.dir = [random.uniform(-1, 1), random.uniform(-1, 1)]
                mag = sqrt(self.dir[0]**2 + self.dir[1]**2)
                if mag > 0:
                    self.dir = [self.dir[0] / mag, self.dir[1] / mag]



    def drop_duck(self):
        if self.state == 'walking':
            self.state = 'dead'
            self.dim = 2  # Match
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


class Dog:
    """
    Simple cube-based OpenGL dog companion that hunts ground ducks.
    - Purchase in shop for 100 points (key D).
    - Stays deployed for 30s, but will only actively hunt for 5–10s from deploy time.
    - +10 points per duck caught by the dog.
    - If all target ground ducks are hunted before timer ends, +50 bonus.
    - While dog is deployed, flying ducks move faster (harder to shoot).
    """
    def __init__(self, game):
        self.game = game
        # Spawn next to player
        px, py, pz = self.game.player_pos
        self.position = [px + 20, py + 20, 0]
        self.dir = [1.0, 0.0]
        self.speed = DOG_SPEED
        self.deployed_at = time.time()
        self.expires_at = self.deployed_at + DOG_DEPLOY_DURATION
        self.hunt_duration = DOG_DEPLOY_DURATION
        self.hunt_ends_at = self.deployed_at + self.hunt_duration
        self.caught = 0
        self.target = None
        # Snapshot of ground ducks at deploy-time for the "all hunted" bonus.
        self.initial_targets = set(id(d) for d in self.get_alive_ground_ducks())
        self.bonus_awarded = False

    def active(self):
        return time.time() < self.expires_at

    def hunting_now(self):
        # Only hunts during first 5–10 seconds of deployment
        return time.time() < self.hunt_ends_at

    def get_alive_ground_ducks(self):
        return [d for d in self.game.active_ducks if isinstance(d, GroundDuck) and d.state == 'walking']

    def pick_target(self):
        ducks = self.get_alive_ground_ducks()
        if not ducks:
            self.target = None
            return
        # nearest ground duck
        px, py = self.position[0], self.position[1]
        self.target = min(ducks, key=lambda d: (d.position[0]-px)**2 + (d.position[1]-py)**2)

    def update(self):
        # If expired, do nothing
        if not self.active():
            return

        # Only move/hunt during the hunting window
        if self.hunting_now():
            # Acquire or validate target
            if self.target is None or self.target.state != 'walking':
                self.pick_target()

            if self.target:
                tx, ty, tz = self.target.position
                # move towards target on ground
                dx, dy = (tx - self.position[0]), (ty - self.position[1])
                dist = sqrt(dx*dx + dy*dy) + 1e-6
                vx, vy = dx/dist, dy/dist
                self.position[0] += vx * self.speed
                self.position[1] += vy * self.speed
                self.dir = [vx, vy]

                # Catch if close enough
                if dist < DOG_CATCH_RADIUS:
                    if self.target.drop_duck():
                        # Score + currency on dog catch
                        self.game.hud.add_score(10)
                        self.game.shop.currency += 10
                        self.game.total_points += 10
                        self.caught += 1
                        self.game.hud.messages.append(("Dog caught a duck! +10", time.time()))
                        self.target = None
            else:
                # wander if no targets
                angle = random.uniform(0, 2*pi)
                self.dir = [cos(angle), sin(angle)]
                self.position[0] += self.dir[0] * (self.speed * 0.5)
                self.position[1] += self.dir[1] * (self.speed * 0.5)

        # Clamp to world bounds
        self.position[0] = max(-GROUND_HALF_LENGTH, min(GROUND_HALF_LENGTH, self.position[0]))
        self.position[1] = max(-GROUND_HALF_LENGTH, min(GROUND_HALF_LENGTH, self.position[1]))

        # Check "all hunted" bonus once
        if not self.bonus_awarded and self.active():
            # From the initial snapshot, are any still alive?
            alive_ids = set(id(d) for d in self.get_alive_ground_ducks())
            remaining = self.initial_targets.intersection(alive_ids)
            if len(self.initial_targets) > 0 and len(remaining) == 0:
                # All ground ducks from deployment snapshot are hunted
                self.game.hud.add_score(50)
                self.game.shop.currency += 50
                self.game.total_points += 50
                self.game.hud.messages.append(("Dog cleared the ground! +50", time.time()))
                self.bonus_awarded = True

    def draw(self):
        if not self.active():
            return

        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], 0.0)

        # Face movement direction
        angle = degrees(atan2(self.dir[1], self.dir[0]))
        glRotatef(angle, 0, 0, 1)

        # Simple cube-based model
        # Body
        glPushMatrix()
        glColor3f(0.6, 0.5, 0.4)
        glScalef(30.0, 18.0, 12.0)
        glutSolidCube(1.0)
        glPopMatrix()

        # Head
        glPushMatrix()
        glTranslatef(18.0, 0.0, 6.0)
        glColor3f(0.55, 0.45, 0.35)
        glScalef(10.0, 10.0, 10.0)
        glutSolidCube(1.0)
        glPopMatrix()

        # Ears
        for ey in [-1, 1]:
            glPushMatrix()
            glTranslatef(23.0, ey*4.0, 12.0)
            glColor3f(0.4, 0.3, 0.2)
            glScalef(3.0, 3.0, 6.0)
            glutSolidCube(1.0)
            glPopMatrix()

        # Legs
        for lx, ly in [(-10, -7), (-10, 7), (10, -7), (10, 7)]:
            glPushMatrix()
            glTranslatef(lx, ly, -6.0)
            glColor3f(0.35, 0.25, 0.15)
            glScalef(4.0, 4.0, 10.0)
            glutSolidCube(1.0)
            glPopMatrix()

        # Tail
        glPushMatrix()
        glTranslatef(-18.0, 0.0, 6.0)
        glRotatef(30, 0, 1, 0)
        glColor3f(0.45, 0.35, 0.25)
        glScalef(8.0, 2.5, 2.5)
        glutSolidCube(1.0)
        glPopMatrix()

        glPopMatrix()

    def time_left(self):
        return max(0.0, self.expires_at - time.time())

    def hunt_time_left(self):
        return max(0.0, self.hunt_ends_at - time.time())


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

    def render(self, window_w, window_h, paused, night_mode=False, auto_fire_active=False, cooldown_remaining=0, dog=None, shop=None, total_points=0):
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
        self.draw_text(20, window_h - 80, f"Total Points: {total_points}")
        if night_mode:
            self.draw_text(20, window_h - 105, "Night Mode")
        if self.night_vision:
            self.draw_text(20, window_h - 130, "Night Vision Active")
        if auto_fire_active:
            glColor3f(0, 1, 0)
            self.draw_text(20, window_h - 155, "Auto Fire Active")
        elif cooldown_remaining > 0:
            glColor3f(1, 0, 0)
            self.draw_text(20, window_h - 155, f"Auto Fire Cooldown: {int(cooldown_remaining)}s")

        # Dog status
        if dog and dog.active():
            glColor3f(0.8, 0.9, 1.0)
            self.draw_text(20, window_h - 180, f"Dog: {int(dog.time_left())}s left, hunts {int(dog.hunt_time_left())}s")
            self.draw_text(20, window_h - 200, f"Ducks caught by dog: {dog.caught}")

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
            {"name": "Dog Companion", "key": "D", "description": "Deploy hunting dog for 30s", "cost": DOG_COST},
        ]
        self.last_message = ""
        self.last_message_time = 0
        self.active_effects = {}
        self.cooldown_end_time = 0
        self.dog_cooldown_end_time = 0

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
                if item["name"] == "Dog Companion" and self.game.dog and self.game.dog.active():
                    self.last_message = "Dog already active!"
                    self.last_message_time = time.time()
                    return True
                if item["name"] == "Dog Companion" and time.time() < self.dog_cooldown_end_time:
                    self.last_message = "Dog on cooldown!"
                    self.last_message_time = time.time()
                    return True
                if self.currency >= item["cost"]:
                    self.currency -= item["cost"]
                    self.apply_effect(item)
                    self.last_message = f"Purchased {item['name']}! Points left: {self.currency}"
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
        elif name == "Dog Companion":
            self.game.deploy_dog()
            self.dog_cooldown_end_time = time.time() + 60
            self.hud.messages.append(("Dog Deployed!", time.time()))

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
            if item["name"] == "Dog Companion" and time.time() < self.dog_cooldown_end_time:
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
        self.base_speed_multiplier = 1.0
        self.night_mode = False

        # Auto Fire
        self.auto_fire_active = False
        self.auto_fire_end_time = 0
        self.last_auto_shot = 0

        # Duck Spawning
        self.last_spawn_time = time.time()
        self.spawn_interval = random.uniform(2.0, 5.0)

        # Dog
        self.dog = None

        # Fallback teapot rotation (for shop overlay)
        self.teapot_angle = 0.0

        # Total points counter
        self.total_points = 0

        # Sniper Mode
        self.sniper_mode = False
        self.sniper_fov = 20
        self.normal_fov = FOV_Y
        self.sniper_sway = [0.0, 0.0]  # x, y sway offset
        self.sniper_sway_time = 0.0

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

        # Right mouse button for sniper mode toggle
        if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            self.sniper_mode = not self.sniper_mode
            if self.sniper_mode:
                self.hud.messages.append(("Sniper Mode Activated", time.time()))
            else:
                self.hud.messages.append(("Sniper Mode Deactivated", time.time()))

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

    def deploy_dog(self):
        self.dog = Dog(self)

    def animate(self):
        if self.paused:
            glutPostRedisplay()
            return

        self.update_cursor_visibility()

        # Base difficulty based on score and night mode
        if self.night_mode:
            self.base_speed_multiplier = 2.0
        elif self.hud.score >= 50:
            self.base_speed_multiplier = 1.5
        else:
            self.base_speed_multiplier = 1.0

        # Update player & world only when shop is closed
        self.update_player()

        # Update Dog
        if self.dog:
            # If dog expired, clear it
            if not self.dog.active():
                self.dog = None
            else:
                self.dog.update()

        # Determine flying duck speed (increased while dog is deployed)
        dog_speed_boost = 1.8 if (self.dog and self.dog.active()) else 1.0
        flying_speed_multiplier = self.base_speed_multiplier * dog_speed_boost

        # Update ducks (flying vs ground multiplier)
        for duck in self.active_ducks:
            if isinstance(duck, GroundDuck):
                duck.update(1.0, self)
            else:
                duck.update(flying_speed_multiplier, self)

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
        self.bullets = [b for b in self.bullets if not (self.is_point_in_tree(bullet.position[0], bullet.position[1], bullet.position[2]) or bullet.position[2] < 0)]

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

        # Collision detection (player bullets vs ducks)
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
                            self.total_points += points
                            bullets_to_remove.append(i)
                            break
            if i in bullets_to_remove:
                continue

        # Remove bullets that collided
        self.bullets = [b for idx, b in enumerate(self.bullets) if idx not in bullets_to_remove]

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

        # Draw dog
        if self.dog and self.dog.active():
            self.dog.draw()

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

        # Add sniper sway
        if self.sniper_mode:
            self.sniper_sway_time += 0.016  # Assuming 60 FPS
            sway_x = sin(self.sniper_sway_time * 2) * 0.5
            sway_y = cos(self.sniper_sway_time * 1.5) * 0.3
            look_point[0] += sway_x
            look_point[1] += sway_y

        gluLookAt(cam_pos[0], cam_pos[1], cam_pos[2],
                  look_point[0], look_point[1], look_point[2],
                  0, 0, 1)

        # Draw environment and world
        self.draw_environment()
        self.draw_world()

        # Draw HUD
        cooldown_remaining = max(0, self.shop.cooldown_end_time - time.time())
        self.hud.render(WINDOW_WIDTH, WINDOW_HEIGHT, self.paused, self.night_mode, self.auto_fire_active, cooldown_remaining, dog=self.dog, total_points=self.total_points)

        # Draw shop if active
        self.shop.render(WINDOW_WIDTH, WINDOW_HEIGHT)

        glutSwapBuffers()

    def reshape(self, width, height):
        if height == 0:
            height = 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        current_fov = self.sniper_fov if self.sniper_mode else self.normal_fov
        gluPerspective(current_fov, width / height, 0.01, 10000.0)
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
