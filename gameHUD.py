from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, time

class HUD:
    def __init__(self):
        self.score = 0
        self.ammo = 10
        self.health = 100
        self.level = 1
        self.magazine_size = 10
        self.last_hit_time = 0
        self.crosshair_size = 10
        self.messages = []  #floating messages
        self.start_time = time.time()
        self.menu = False
        self.shop_active = False
        self.reticle_good = True

    def add_score(self, value, distance=1.0):
        # score increase
        gained = int(value * distance)
        self.score += gained
        self.messages.append((f"+{gained} pts", time.time()))

    def damage(self, value):
        self.health = max(0, self.health - value)
        self.last_hit_time = time.time()
        self.messages.append((f"-{value} HP", time.time()))

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

    def draw_text(self, x, y, text, font=GLUT_BITMAP_HELVETICA_18):
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))

    def render(self, window_w, window_h):
        #2D HUD
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_w, 0, window_h)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_LIGHTING)

        #score, ammo, health
        glColor3f(1,1,1)
        self.draw_text(20, window_h-30, f"Score: {self.score}")
        self.draw_text(20, window_h-55, f"Ammo: {self.ammo}/{self.magazine_size}")
        self.draw_text(20, window_h-80, f"Health: {self.health}")
        self.draw_text(20, window_h-105, f"Level: {self.level}")

        #crosshair
        cx, cy = window_w//2, window_h//2
        size = self.crosshair_size
        glColor3f(0.1, 1.0 if self.reticle_good else 0.2, 0.1 if self.reticle_good else 0.2)
        glBegin(GL_LINES)
        glVertex2f(cx - size, cy)
        glVertex2f(cx + size, cy)
        glVertex2f(cx, cy - size)
        glVertex2f(cx, cy + size)
        glEnd()

        #menu
        if self.menu:
            glColor3f(0, 0, 0)
            self.draw_text(cx - 120, cy + 60, "DUCK HUNTER 3D")
            self.draw_text(cx - 220, cy + 20, "Press M to Start • 1/2/3 to choose Level")
            self.draw_text(cx - 160, cy - 20, "WASD move • Mouse look • Click to shoot • R reload")
            self.draw_text(cx - 170, cy - 60, "Press B for Shop (skins & perks, stub)")

        #shop
        if self.shop_active:
            glColor3f(0, 0, 0)
            self.draw_text(cx - 70, cy + 60, "SHOP")
            self.draw_text(cx - 200, cy + 20, "(Stub) Press B to exit • (No costs implemented)")
            self.draw_text(cx - 180, cy - 10, "Perk: Bigger Magazine [G] • Skin: Golden Gun [H]")

        #floating messages (2s)
        now = time.time()
        active = []
        y_offset = 0
        for msg, t in self.messages:
            if now - t < 2.0:
                glColor3f(1,1,0)
                self.draw_text(window_w//2 - 40, window_h//2 + 60 + y_offset, msg)
                y_offset += 20
                active.append((msg,t))
        self.messages = active

        #red when damaged
        if now - self.last_hit_time < 0.5:
            alpha = 1 - ((now - self.last_hit_time)/0.5)
            glColor4f(1,0,0,alpha)
            glBegin(GL_QUADS)
            glVertex2f(0,0)
            glVertex2f(window_w,0)
            glVertex2f(window_w,window_h)
            glVertex2f(0,window_h)
            glEnd()

        #restore
        glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def get_elapsed_time(self):
        return int(time.time() - self.start_time)

    def reset(self):
        self.score = 0
        self.ammo = self.magazine_size
        self.health = 100
        self.level = 1
        self.start_time = time.time()
        self.messages = []
