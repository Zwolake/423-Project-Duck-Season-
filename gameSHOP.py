from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time

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
