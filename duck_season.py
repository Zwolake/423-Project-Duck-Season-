import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import *

FOV_Y = 120


#TODO - any other libraries


#TODO - GameObjects
# Duck flying
# Duck Falling
# Duck Landed
# Dog(?)
# Wolves(?)
# Rifle
# Bullet
# Tree
def draw_tree(x,y):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glColor3f(0.5, 0.35, 0.05)  # Brown color for trunk
    glBegin(GL_QUADS)
    glVertex3f(-0.1, 0, 0)
    glVertex3f(0.1, 0, 0)
    glVertex3f(0.1, 0.5, 0)
    glVertex3f(-0.1, 0.5, 0)
    glEnd()
    glColor3f(0.0, 0.5, 0.0)  # Green color for leaves
    glBegin(GL_TRIANGLES)
    glVertex3f(-0.5, 0.5, 0)
    glVertex3f(0.5, 0.5, 0)
    glVertex3f(0, 1, 0)
    glEnd()
    glPopMatrix()

# Shop


#TODO - Play Area
# Surface
# Border
# Shop


#TODO - UI
# Ammo count
# Money display
# Shop UI - numbers corresponding to items
# Crosshair


#TODO Implement game logic
# Duck flying
# Duck falling
# Duck landed
# Dog AI
# Wolf AI
# Rifle mechanics
# Bullet mechanics
# Border interactions
# Shop interactions


#TODO Controls


# Movement keys (WASD) + Shop menu (numbers)
def keyboardListener(key, x, y):
    #TODO assign movement

    if key == b'w':
        pass
    elif key == b's':
        pass
    elif key == b'a':
        pass
    elif key == b'd':
        pass

    #TODO assign shop menu

    if key == b'1':
        pass
    elif key == b'2':
        pass
    elif key == b'3':
        pass
    elif key == b'4':
        pass

# Look around (arrow keys)
def specialKeyListener(key, x, y):
    #TODO assign look around

    if key == GLUT_KEY_UP:
        pass
    elif key == GLUT_KEY_DOWN:
        pass
    elif key == GLUT_KEY_LEFT:
        pass
    elif key == GLUT_KEY_RIGHT:
        pass

# Shoot (mouse click)
def mouseListener(button, state, x, y):
    #TODO assign shooting

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        pass


#TODO Finishing touch

# camera
def setupCamera():
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    gluPerspective(FOV_Y, 1.25, 0.1, 2500) # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    #TODO camera position and orientation

    gluLookAt(0, 100, 0,  # Camera position
              0, 0, 0,  # Look at point
              0, 0, 1)  # Up vector
    
# display
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size

    #TODO setupCamera()
    setupCamera()

    #TODO draw_shapes()
    draw_tree(0, 0)

    # Display game info text at a fixed screen position
    # draw_text(10, 770, f"A Random Fixed Position Text")
    # draw_text(10, 740, f"See how the position and variable change?: {enemy_body_radius}")

# idle
def idle():

    #TODO update game state

    glutPostRedisplay()  # Request a redraw

# main loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1280, 720)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    duckseason = glutCreateWindow(b"Duck Season")  # Create the window

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # Register the idle function to move the bullet automatically

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()