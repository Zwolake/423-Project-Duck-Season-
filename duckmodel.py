import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Global variable for animation
rotation_angle = 0.0
wing_flapping_angle = 0.0

def draw_duck():

    # Colors
    duck_light_gray = (0.7, 0.7, 0.7)
    duck_med_gray = (0.6, 0.6, 0.6)
    duck_medium_gray = (0.5, 0.5, 0.5)
    duck_dark_gray = (0.3, 0.3, 0.3)
    eye_black = (0.0, 0.0, 0.0)

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

    # --- Draw the Wings (rotated cubes for flapping animation) ---
    global wing_flapping_angle
    wing_flapping_rotation = 25 * math.sin(math.radians(wing_flapping_angle))

    # Left wing
    glPushMatrix()
    glColor3f(*duck_medium_gray)
    glTranslatef(-1.5, 0.4, 0.0)
    glRotatef(wing_flapping_rotation - 30, 0, 0, 1)
    glScalef(1.9, 0.2, 1.0)
    glutSolidCube(1.5)
    glPopMatrix()

    # Right wing
    glPushMatrix()
    glColor3f(*duck_medium_gray)
    glTranslatef(1.7, 0.4, 0.0)
    glRotatef(-wing_flapping_rotation + 30, 0, 0, 1)
    glScalef(1.9, 0.2, 1.0)
    glutSolidCube(1.5)
    glPopMatrix()

    # --- Draw the Legs (cubes) ---
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


def display_scene():
    """
    Main display function.
    """
    global rotation_angle
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Set up the camera position and orientation
    gluLookAt(
        0, 5, 10,
        0, 0, 0,
        0, 1, 0
    )

    # Apply continuous rotation to the entire duck
    glRotatef(rotation_angle, 0, 1, 0)
    
    # Draw the duck model
    draw_duck()

    glutSwapBuffers()

def idle():
    global rotation_angle, wing_flapping_angle
    rotation_angle += 0.5
    wing_flapping_angle += 5.0
    if rotation_angle > 360:
        rotation_angle -= 360
    glutPostRedisplay()

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

    glutMainLoop()

if __name__ == "__main__":
    main()
