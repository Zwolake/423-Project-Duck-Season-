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
