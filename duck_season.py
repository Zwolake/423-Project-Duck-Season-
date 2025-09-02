from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import *
import time

CAM_X = 0
CAM_Y = -100
CAM_Z = 100

LOOK_X = 200
LOOK_Y = 200
LOOK_Z = 25
LOOK_SPEED_X = 10
LOOK_SPEED_Z = 50
LOOK_DELTA_ANGLE = 0.1

PLAYER_X = -100
PLAYER_Y = -100
PLAYER_Z = 25
PLAYER_SPEED = 10

GROUND_LENGTH = 1000
GROUND_WIDTH = 1000

SKYBOX_HEIGHT = 1000

TREE_TRUNK_RADIUS = 10
TREE_TRUNK_HEIGHT = 50
TREE_LEAVES_RADIUS = 30
TREE_LEAVES_HEIGHT = 50

FOV_Y = 90

AIM_LEFT = False
AIM_RIGHT = False

#TODO - any other libraries


#TODO - GameObjects
#! Duck flying
#! Duck Falling
#! Duck Landed
# Dog(?)
# Wolves(?)
#! Rifle
#! Bullet
#* Tree
def draw_tree(x,y):
    glPushMatrix()  #? transform start

    glTranslatef(x, y, 0)

    #* tree leaves
    glPushMatrix()

    glTranslatef(0, 0, TREE_TRUNK_HEIGHT)  #? Move to the top of the trunk
    glColor3f(0.0, 0.5, 0.0)  #? Green color for leaves
    gluCylinder(gluNewQuadric(), TREE_LEAVES_RADIUS, 0, TREE_LEAVES_HEIGHT, 12, 1)  # parameters are: quadric, base radius, top radius, height, slices, stacks
    
    glPopMatrix()

    #*tree trunk
    glPushMatrix()

    glColor3f(0.5, 0.35, 0.05)  #? Brown color for trunk
    gluCylinder(gluNewQuadric(), TREE_TRUNK_RADIUS, TREE_TRUNK_RADIUS, TREE_TRUNK_HEIGHT, 12, 1)  # parameters are: quadric, base radius, top radius, height, slices, stacks
    
    glPopMatrix()
    
    glPopMatrix()   #? transform end
    
    # glVertex3f(-0.1, 0, 0)
    # glVertex3f(0.1, 0, 0)
    # glVertex3f(0.1, 0.5, 0)
    # glVertex3f(-0.1, 0.5, 0)
    # glEnd()
    # glColor3f(0.0, 0.5, 0.0)  # Green color for leaves
    # glBegin(GL_TRIANGLES)
    # glVertex3f(-0.5, 0.5, 0)
    # glVertex3f(0.5, 0.5, 0)
    # glVertex3f(0, 1, 0)
    # glEnd()

#! Shop


#TODO - Play Area
# Surface
def draw_surface():
    glBegin(GL_QUADS)
    glColor3f(0.0, 1, 0.0)  # Green color for grass
    glVertex3f(-GROUND_LENGTH, -GROUND_WIDTH, 0)
    glVertex3f(GROUND_LENGTH, -GROUND_WIDTH, 0)
    glVertex3f(GROUND_LENGTH, GROUND_WIDTH, 0)
    glVertex3f(-GROUND_LENGTH, GROUND_WIDTH, 0)
    glEnd()

#! Border
#! Shop


#TODO - UI
#! Ammo count
#! Money display
#! Shop UI - numbers corresponding to items
#! Crosshair


#TODO Implement game logic
#! Duck flying
#! Duck falling
#! Duck landed
#! Dog AI
#! Wolf AI
#! Rifle mechanics
#! Bullet mechanics
#! Border interactions
#! Shop interactions

#? saif kutta
#TODO Controls


#! Movement keys (WASD) + Shop menu (numbers)
def keyboardListener(key, _x, _y):
    #TODO assign movement
    global PLAYER_X, PLAYER_Y, PLAYER_Z
    global LOOK_X, LOOK_Y, LOOK_Z
    if key == b'w':
        PLAYER_Y += 1 * PLAYER_SPEED
    elif key == b's':
        PLAYER_Y -= 1 * PLAYER_SPEED
    elif key == b'a':
        PLAYER_X -= 1 * PLAYER_SPEED
    elif key == b'd':
        PLAYER_X += 1 * PLAYER_SPEED

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
def specialKeyListener(key, _x, _y):
    # assign look around
    # global LOOK_X, LOOK_Y, LOOK_Z
    # if key == GLUT_KEY_UP:
    #     LOOK_Z += 1 * LOOK_SPEED
    # elif key == GLUT_KEY_DOWN:
    #     LOOK_Z -= 1 * LOOK_SPEED        
    # elif key == GLUT_KEY_LEFT:
    #     LOOK_X -= 1 * LOOK_SPEED
    # elif key == GLUT_KEY_RIGHT:
    #     LOOK_X += 1 * LOOK_SPEED
    pass

# Shoot (mouse click)
def mouseListener(button, state, _x, _y):
    #TODO assign shooting
    global LOOK_X, LOOK_Y, LOOK_Z
    global AIM_LEFT, AIM_RIGHT
    if button == 0 and state == GLUT_DOWN:
        # *aim left
        AIM_LEFT = True
    if button == 0 and state == GLUT_UP:
        AIM_LEFT = False

    if button == 2 and state == GLUT_DOWN:
        # *aim right
        AIM_RIGHT = True
    if button == 2 and state == GLUT_UP:
        AIM_RIGHT = False

    if button == 3 and state == GLUT_DOWN:
        # aim up
        print("Aim Up")
        LOOK_Z = min(LOOK_Z + (1 * LOOK_SPEED_Z), SKYBOX_HEIGHT)
        pass

    if button == 4 and state == GLUT_DOWN:
        # aim down
        print("Aim Down")
        LOOK_Z = max(LOOK_Z - (1 * LOOK_SPEED_Z), -SKYBOX_HEIGHT)
        pass

#TODO Finishing touch

def devDebug():
    if not hasattr(devDebug, "last_print_time"):
        devDebug.last_print_time = time.time()

    current_time = time.time()
    if current_time - devDebug.last_print_time >= 100.0:
        x, y, z = PLAYER_X, PLAYER_Y, PLAYER_Z
        print(
            f"{glutGet(GLUT_ELAPSED_TIME)} : Player Currently At - X={x:.2f} Y={y:.2f} Z={z:.2f}"
        )

# camera
def setupCamera():
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    gluPerspective(FOV_Y, 16/9, 0.1, 2500) # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    #TODO camera position and orientation

    gluLookAt(PLAYER_X, PLAYER_Y, PLAYER_Z,  # Camera position
              PLAYER_X + LOOK_X , PLAYER_Y + LOOK_Y + 1, LOOK_Z,  # Look at point
              0, 0, 1)  # Up vector
    
# display
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, 0.9, 0.9, 0.5)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1280, 720)  # Set viewport size

    #TODO setupCamera()
    setupCamera()

    # Draw the surface and a tree so something is visible
    draw_surface()
    draw_tree(0, 0)
    glPushMatrix()
    glTranslatef(0, 0, 1000)
    glutSolidCube(10)
    glPopMatrix()

    # Display game info text at a fixed screen position
    # draw_text(10, 770, f"A Random Fixed Position Text")
    # draw_text(10, 740, f"See how the position and variable change?: {enemy_body_radius}")
    glutSwapBuffers()

# idle
def idle():
    global LOOK_X, LOOK_Y, LOOK_Z
    if AIM_LEFT:
        _x = LOOK_X * cos(-LOOK_DELTA_ANGLE) - LOOK_Y * sin(-LOOK_DELTA_ANGLE)
        _y = LOOK_X * sin(-LOOK_DELTA_ANGLE) + LOOK_Y * cos(-LOOK_DELTA_ANGLE)
        LOOK_X, LOOK_Y = _x, _y
        print(LOOK_X, LOOK_Y)
        print("Aim Left")

    if AIM_RIGHT:
        _x = LOOK_X * cos(LOOK_DELTA_ANGLE) - LOOK_Y * sin(LOOK_DELTA_ANGLE)
        _y = LOOK_X * sin(LOOK_DELTA_ANGLE) + LOOK_Y * cos(LOOK_DELTA_ANGLE)
        LOOK_X, LOOK_Y = _x, _y     
        print("Aim Right")

    #TODO update game state
    devDebug()

    glutPostRedisplay()  # Request a redraw

# main loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1280, 720)  # Window size
    glutInitWindowPosition(100, 100)  # Window position
    glutCreateWindow(b"Duck Season")  # Create the window

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # Register the idle function to move the bullet automatically

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()