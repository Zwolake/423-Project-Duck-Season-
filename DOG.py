import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Global variable for animation
rotation_angle = 0.0
tail_wagging_angle = 0.0

def draw_dog():
    """
    Draws a 3D dog using only cubes with a wagging tail.
    """
    # Define colors for the dog
    dog_brown = (0.5, 0.4, 0.2)
    dog_light_brown = (0.6, 0.5, 0.3)
    dog_dark_brown = (0.3, 0.2, 0.1)
    eye_black = (0.0, 0.0, 0.0)

    


    # --- Draw the Body (a large cube) ---
    glPushMatrix()
    glRotate(90, 1, 0, 0)

    glPushMatrix()
    glColor3f(*dog_brown)
    glScalef(2.0, 1.5, 3)
    glTranslatef(0, 0, 0)
    glutSolidCube(1.0)
    glPopMatrix()

    # --- Draw the Neck (a cube) ---
    glPushMatrix()
    glColor3f(*dog_brown)
    glScalef(0.6, 0.6, 0.6)
    glTranslatef(0, 1.8, 2.0)
    glutSolidCube(1.2)
    glPopMatrix()

    # --- Draw the Head (a cube) ---
    glPushMatrix()
    glColor3f(*dog_brown)
    glScalef(1.0, 1.0, 1.0)
    glTranslatef(0, 1.5, 2)
    glutSolidCube(1.0)
    glPopMatrix()

    # --- Draw the Snout (a smaller cube) ---
    glPushMatrix()
    glColor3f(*dog_dark_brown)
    glScalef(0.4, 0.4, 0.3)
    glTranslatef(0, 3.0, 8.5)
    glutSolidCube(1)
    glPopMatrix()
    
    # --- Draw the Ears (small cubes) ---
    # Left ear
    glPushMatrix()
    glColor3f(*dog_light_brown)
    glScalef(0.2, 0.5, 0.3)
    glTranslatef(-3.0, 3.3, 6.0)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Right ear
    glPushMatrix()
    glColor3f(*dog_light_brown)
    glScalef(0.2, 0.5, 0.3)
    glTranslatef(3.0, 3.3, 6.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # --- Draw the Eyes (small black cubes) ---
    # Left eye
    glPushMatrix()
    glColor3f(*eye_black)
    glScalef(0.15, 0.15, 0.15)
    glTranslatef(-2.0, 11.5, 17.0)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Right eye
    glPushMatrix()
    glColor3f(*eye_black)
    glScalef(0.15, 0.15, 0.15)
    glTranslatef(2.0, 11.5, 17.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # --- Draw the Tail (a wagging cube) ---
    global tail_wagging_angle
    tail_wagging_rotation = 20 * math.sin(math.radians(tail_wagging_angle))
    
    glPushMatrix()
    glColor3f(*dog_light_brown)
    glTranslatef(0, 0.4, -1.8)
    glRotatef(tail_wagging_rotation, 0, 1, 0)
    glScalef(0.3, 0.3, 1.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # --- Draw the Legs (four cubes) ---
    # Front left leg
    glPushMatrix()
    glColor3f(*dog_dark_brown)
    glScalef(0.3, 0.8, 0.3)
    glTranslatef(-2.5, -1.1, 3.5)
    glutSolidCube(1.0)
    glPopMatrix()

    # Front right leg
    glPushMatrix()
    glColor3f(*dog_dark_brown)
    glScalef(0.3, 0.8, 0.3)
    glTranslatef(2.5, -1.1, 3.5)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Back left leg
    glPushMatrix()
    glColor3f(*dog_dark_brown)
    glScalef(0.3, 0.8, 0.3)
    glTranslatef(-2.5, -1.1, -3.5)
    glutSolidCube(1.0)
    glPopMatrix()

    # Back right leg
    glPushMatrix()
    glColor3f(*dog_dark_brown)
    glScalef(0.3, 0.8, 0.3)
    glTranslatef(2.5, -1.1, -3.5)
    glutSolidCube(1.0)
    glPopMatrix()
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

    # Apply continuous rotation to the entire dog
    glRotatef(rotation_angle, 0, 1, 0)
    
    # Draw the dog model
    draw_dog()

    glutSwapBuffers()

def idle():
    """
    Called when the program is idle to update the scene.
    """
    global rotation_angle, tail_wagging_angle
    rotation_angle += 0.5
    tail_wagging_angle += 5.0
    if rotation_angle > 360:
        rotation_angle -= 360
    glutPostRedisplay()

def reshape_window(w, h):
    """
    Handles window resizing.
    """
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / h, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def main():
    """
    Initializes GLUT and starts the main loop.
    """
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"3D Dog Model")

    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(display_scene)
    glutReshapeFunc(reshape_window)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()
