import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Color Variables
duck_light_gray = (0.7, 0.7, 0.7)
duck_med_gray = (0.6, 0.6, 0.6)
duck_medium_gray = (0.5, 0.5, 0.5)
duck_dark_gray = (0.3, 0.3, 0.3)
eye_black = (0.0, 0.0, 0.0)


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


        self.wing_delta = 25 * math.sin(math.radians(self.wing_angle))
        
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


    def dead_duck(self):
        self.state = 'dead'
        self.wing_angle = 0.0


    def drop_duck(self):
        self.state = 'falling'
        self.wing_angle = 0.0


ducks = []

def display_scene():
    global ducks
    global rotation_angle
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Set up the camera position and orientation
    gluLookAt(
        0, 5, 10,
        0, 0, 0,
        0, 1, 0
    )

    
    # Draw the duck model
    if not ducks:
        ducks.append(Duck(0,0,0))
    ducks[0].draw_duck()

    glutSwapBuffers()

def idle():
    # -------- Duck animation --------- #
    global ducks
    for d in ducks:
        if d.state == 'flying':
            d.wing_angle += 5.0
    # ---------------------------------- #
    glutPostRedisplay()


def keyboard(key, x, y):
    global ducks
    if key == b'd':
        ducks[0].dead_duck()
    elif key == b's':
        ducks[0].drop_duck()
    elif key == b'f':
        ducks[0].state = 'flying'

def reshape_window(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / h, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Improved 3D Duck Drawing")

    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(display_scene)
    glutReshapeFunc(reshape_window)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)

    glutMainLoop()

if __name__ == "__main__":
    main()
