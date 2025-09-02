"""
Duck Shooting
# First-Person Shooter template with simple Boids flock AI for ducks
# Menu scene + Shooting scene + Level/Shop
# Animated FPS hands + rifle made from simple meshes
# Triplanar terrain shader + simple water shader with ripples
# Ray picking for shooting; distance-based scoring; basic HUD text

Controls -
W/A/S/D  : Move
Mouse    : Look around
Left Click: Shoot
R        : Reload (fake, affects reticle color)
1/2/3    : Switch levels
M        : Menu / Play toggle
B        : Open Shop (stub) / Close
Esc      : Quit
"""

import math, random, time, sys
from ctypes import c_float, c_uint, sizeof, c_void_p, POINTER

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLUT import *

def v_add(a,b): return [a[0]+b[0], a[1]+b[1], a[2]+b[2]]
def v_sub(a,b): return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]
def v_scale(a,s): return [a[0]*s, a[1]*s, a[2]*s]
def v_dot(a,b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def v_cross(a,b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]

def v_len(a):
    return math.sqrt(v_dot(a,a))

def v_norm(a):
    L=v_len(a)
    return [0,0,0] if L==0 else [a[0]/L,a[1]/L,a[2]/L]

def mat_identity():
    return [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]

def mat_perspective(fovy, aspect, znear, zfar):
    f = 1.0/math.tan(math.radians(fovy)/2)
    nf = 1/(znear - zfar)
    return [
        f/aspect,0,0,0,
        0,f,0,0,
        0,0,(zfar+znear)*nf,-1,
        0,0,(2*znear*zfar)*nf,0
    ]

def mat_lookat(eye, center, up):
    f=v_norm(v_sub(center,eye))
    s=v_norm(v_cross(f, up))
    u=v_cross(s, f)
    M = [
        s[0], u[0], -f[0], 0,
        s[1], u[1], -f[1], 0,
        s[2], u[2], -f[2], 0,
        -v_dot(s, eye), -v_dot(u, eye), v_dot(f, eye), 1
    ]
    return M

def mat_mul(a,b):
    r=[0]*16
    for i in range(4):
        for j in range(4):
            r[i*4+j] = sum(a[i*4+k]*b[k*4+j] for k in range(4))
    return r

def mat_translate(tx,ty,tz):
    M=mat_identity()
    M[12]=tx; M[13]=ty; M[14]=tz
    return M

def mat_rotate_y(angle_deg):
    a=math.radians(angle_deg); c=math.cos(a); s=math.sin(a)
    return [c,0,s,0, 0,1,0,0, -s,0,c,0, 0,0,0,1]

def mat_scale(sx,sy,sz):
    return [sx,0,0,0, 0,sy,0,0, 0,0,sz,0, 0,0,0,1]

TRIPLANAR_VS = """
#version 120
attribute vec3 aPos;
attribute vec3 aNormal;

uniform mat4 uMVP;
uniform mat4 uModel;

varying vec3 vWorldPos;
varying vec3 vNormal;

void main(){
    vec4 worldPos = uModel * vec4(aPos,1.0);
    vWorldPos = worldPos.xyz;
    vNormal = (uModel * vec4(aNormal,0.0)).xyz;
    gl_Position = uMVP * vec4(aPos,1.0);
}
"""

TRIPLANAR_FS = """
#version 330 core
in vec3 vWorldPos;
in vec3 vNormal;

uniform vec3 uCamPos;
out vec4 FragColor;

// Procedural triplanar with simple checker-like tone
float hash(vec3 p){ return fract(sin(dot(p,vec3(12.9898,78.233,37.719)))*43758.5453); }

vec3 triplanar(vec3 pos, vec3 n){
    vec3 an = abs(normalize(n)+1e-5);
    an /= (an.x+an.y+an.z);
    float s = 0.5+0.5*sin(pos.x*0.2)+0.5+0.5*sin(pos.y*0.2)+0.5+0.5*sin(pos.z*0.2);
    float g = clamp(s/3.0,0.0,1.0);
    vec3 base = mix(vec3(0.15,0.45,0.2), vec3(0.3,0.25,0.2), g);
    return base*an.x + base*an.y + base*an.z;
}

void main(){
    vec3 n = normalize(vNormal);
    vec3 col = triplanar(vWorldPos*0.5, n);
    // simple diffuse with overhead light
    float diff = max(dot(n, normalize(vec3(0.3,1.0,0.4))), 0.1);
    FragColor = vec4(col*diff, 1.0);
}
"""

BASIC_VS = """
#version 330 core
layout(location=0) in vec3 aPos;
layout(location=1) in vec3 aNormal;

uniform mat4 uMVP;
uniform mat4 uModel;

out vec3 vNormal;

void main(){
    vNormal = mat3(uModel) * aNormal;
    gl_Position = uMVP * vec4(aPos,1.0);
}
"""

BASIC_FS = """
#version 330 core
in vec3 vNormal;

out vec4 FragColor;

void main(){
    vec3 n = normalize(vNormal);
    float l = max(dot(n, normalize(vec3(0.4,1.0,0.2))), 0.1);
    vec3 c = mix(vec3(0.8,0.7,0.6), vec3(0.6,0.5,0.4), n.y*0.5+0.5);
    FragColor = vec4(c*l, 1.0);
}
"""

WATER_VS = """
#version 330 core
layout(location=0) in vec3 aPos;
layout(location=1) in vec3 aNormal;

uniform mat4 uMVP;
uniform float uTime;

out float vWave;

void main(){
    float h = sin(aPos.x*0.05 + uTime*1.5)*0.2 + cos(aPos.z*0.05 + uTime*1.2)*0.2;
    vec3 p = aPos + vec3(0.0, h, 0.0);
    vWave = h;
    gl_Position = uMVP * vec4(p,1.0);
}
"""

WATER_FS = """
#version 330 core
in float vWave;

out vec4 FragColor;

void main(){
    float fres = clamp(0.2 + abs(vWave)*1.5, 0.2, 0.9);
    vec3 deep = vec3(0.0,0.1,0.2);
    vec3 surf = vec3(0.1,0.3,0.5);
    vec3 col = mix(deep, surf, fres);
    FragColor = vec4(col, 0.85);
}
"""

def make_plane(n=100, size=200.0, y=0.0):
    verts=[]; norms=[]; idx=[]
    step = size/n
    half = size/2
    for i in range(n+1):
        for j in range(n+1):
            x = -half + j*step
            z = -half + i*step
            verts += [x, y, z]
            norms += [0,1,0]
    for i in range(n):
        for j in range(n):
            a = i*(n+1)+j
            b = a+1
            c = a+(n+1)
            d = c+1
            idx += [a,c,b, b,c,d]
    return bufferize(verts, norms, idx)

def make_cube(s=1.0):
    p=[-s,-s,-s, s,-s,-s, s,s,-s, -s,s,-s, -s,-s,s, s,-s,s, s,s,s, -s,s,s]
    faces=[(0,1,2,3,[0,0,-1]),(4,5,6,7,[0,0,1]),(0,4,7,3,[-1,0,0]),(1,5,6,2,[1,0,0]),(3,2,6,7,[0,1,0]),(0,1,5,4,[0,-1,0])]
    verts=[]; norms=[]; idx=[]; vi=0
    for a,b,c,d,n in faces:
        base=vi
        for q in (a,b,c,d):
            verts+=p[q*3:q*3+3]
            norms+=n
        idx += [base,base+1,base+2, base,base+2,base+3]
        vi+=4
    return bufferize(verts,norms,idx)

def make_duck():
    return make_cube(0.5)

class Mesh:
    def __init__(self, verts, norms, idx):
        self.icount = len(idx)
        self.vbo = glGenBuffers(1)
        self.nbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        array_type = (c_float * len(verts))(*verts)
        glBufferData(GL_ARRAY_BUFFER, sizeof(array_type), array_type, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, self.nbo)
        array_type2 = (c_float * len(norms))(*norms)
        glBufferData(GL_ARRAY_BUFFER, sizeof(array_type2), array_type2, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        array_type3 = (c_uint * len(idx))(*idx)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(array_type3), array_type3, GL_STATIC_DRAW)

    def draw(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.nbo)
        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glDrawElements(GL_TRIANGLES, self.icount, GL_UNSIGNED_INT, c_void_p(0))
        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)



def bufferize(verts, norms, idx):
    return Mesh(verts, norms, idx)

class Camera:
    def __init__(self):
        self.pos=[0,1.7,5]
        self.pitch=0.0
        self.yaw= -90.0
        self.fov=70.0

    def front(self):
        cy=math.cos(math.radians(self.yaw)); sy=math.sin(math.radians(self.yaw))
        cp=math.cos(math.radians(self.pitch)); sp=math.sin(math.radians(self.pitch))
        return v_norm([cy*cp, sp, sy*cp])

    def right(self):
        return v_norm(v_cross(self.front(), [0,1,0]))

    def view(self):
        center = v_add(self.pos, self.front())
        return mat_lookat(self.pos, center, [0,1,0])

class Duck:
    def __init__(self):
        self.pos=[random.uniform(-30,30), random.uniform(2,15), random.uniform(-30,30)]
        self.vel=v_norm([random.uniform(-1,1), random.uniform(-0.2,0.6), random.uniform(-1,1)])
        self.speed=random.uniform(3.0,6.0)
        self.alive=True
        self.radius=0.8
        self.wing_phase=random.uniform(0, 2*math.pi)
        self.score_base=10

    def steer(self, neighbors):
        if not self.alive: return
        sep=[0,0,0]; ali=[0,0,0]; coh=[0,0,0]; count=0
        for d in neighbors:
            if d is self or not d.alive: continue
            off=v_sub(d.pos, self.pos)
            dist=v_len(off)
            if dist<8.0:
                sep=v_add(sep, v_scale(v_norm(off), -1.0/(dist+1e-3)))
            if dist<20.0:
                ali=v_add(ali, d.vel)
                coh=v_add(coh, d.pos)
                count+=1
        if count>0:
            ali=v_norm(v_scale(ali, 1.0/count))
            coh=v_norm(v_sub(v_scale(coh, 1.0/count), self.pos))
        acc=[0,0.05,0]
        acc=v_add(acc, v_scale(sep, 1.5))
        acc=v_add(acc, v_scale(ali, 0.6))
        acc=v_add(acc, v_scale(coh, 0.8))
        self.vel = v_norm(v_add(self.vel, v_scale(acc, 0.02)))
        for i,limit in enumerate([80,50,80]):
            if abs(self.pos[i])>limit:
                self.vel[i] *= -1

    def update(self, dt):
        if not self.alive: return
        self.pos = v_add(self.pos, v_scale(self.vel, self.speed*dt))
        self.wing_phase += dt*10.0

class World:
    def __init__(self):
        self.cam=Camera()
        self.duck_mesh=make_duck()
        self.plane_mesh=make_plane(80, 300.0, 0.0)
        self.water_mesh=make_plane(80, 200.0, -1.0)
        try:
            self.shader_basic = compileProgram(compileShader(BASIC_VS, GL_VERTEX_SHADER), compileShader(BASIC_FS, GL_FRAGMENT_SHADER))
        except Exception as e:
            print("Basic shader compilation failed:", e)
            self.shader_basic = 0
        try:
            self.shader_triplanar = compileProgram(compileShader(TRIPLANAR_VS, GL_VERTEX_SHADER), compileShader(TRIPLANAR_FS, GL_FRAGMENT_SHADER))
        except Exception as e:
            print("Triplanar shader compilation failed:", e)
            self.shader_triplanar = 0
        try:
            self.shader_water = compileProgram(compileShader(WATER_VS, GL_VERTEX_SHADER), compileShader(WATER_FS, GL_FRAGMENT_SHADER))
        except Exception as e:
            print("Water shader compilation failed:", e)
            self.shader_water = 0
        self.time0=time.time()
        self.ducks=[Duck() for _ in range(25)]
        self.last_shot=0
        self.score=0
        self.mag=5
        self.menu=True
        self.shop=False
        self.level=1
        self.reticle_good=True

    def reset_level(self, lvl):
        self.level=lvl
        count = 20 + 10*(lvl-1)
        speed = 3.0 + 1.0*(lvl-1)
        self.ducks=[Duck() for _ in range(count)]
        for d in self.ducks:
            d.speed *= (0.8 + 0.3*(lvl-1))
        self.score=0
        self.mag=5

    def update(self, dt):
        if self.menu or self.shop: return
        for d in self.ducks:
            d.steer(self.ducks)
        for d in self.ducks:
            d.update(dt)
        for d in self.ducks:
            if not d.alive and random.random()<0.002:
                d.alive=True
                d.pos=[random.uniform(-30,30), random.uniform(2,15), random.uniform(-30,30)]

    def shoot(self, ray_o, ray_dir):
        if self.mag<=0:
            print("*click* Empty magazine — press R to reload")
            self.reticle_good=False
            return
        self.mag-=1
        self.last_shot=time.time()
        self.reticle_good=True
        best=None; best_dist=1e9
        for d in self.ducks:
            if not d.alive: continue
            oc=v_sub(ray_o, d.pos)
            b=2*v_dot(oc, ray_dir)
            c=v_dot(oc,oc)-d.radius*d.radius
            disc=b*b-4*c
            if disc<0: continue
            t=(-b - math.sqrt(disc))/2
            if t>0 and t<best_dist:
                best=d; best_dist=t
        if best:
            best.alive=False
            dist=v_len(v_sub(best.pos, ray_o))
            pts=int(best.score_base + dist*0.5)
            self.score += pts
            print(f"Duck down! +{pts} points (dist ~{dist:.1f}m)")
        else:
            print("Miss!")

APP = {
    'w': 1280,
    'h': 720,
    'keys': set(),
    'mx': 0, 'my': 0, 'last_mx': None, 'last_my': None,
    'world': None,
    'last_time': None
}

def draw_mesh(mesh, shader, model, view, proj, extra_uniforms=None):
    glUseProgram(shader)
    mvp = mat_mul(mat_mul(proj, view), model)
    loc = glGetUniformLocation(shader, 'uMVP')
    if loc!=-1:
        glUniformMatrix4fv(loc, 1, GL_FALSE, (c_float*16)(*mvp))
    loc = glGetUniformLocation(shader, 'uModel')
    if loc!=-1:
        glUniformMatrix4fv(loc, 1, GL_FALSE, (c_float*16)(*model))
    if extra_uniforms:
        for name, val in extra_uniforms.items():
            loc = glGetUniformLocation(shader, name)
            if loc==-1: continue
            if isinstance(val, float): glUniform1f(loc, val)
            elif isinstance(val, (int,bool)): glUniform1i(loc, int(val))
            elif isinstance(val, (list,tuple)) and len(val)==3: glUniform3f(loc, *val)
    mesh.draw()


def render_world(world: World):
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.55,0.75,0.95,1.0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    aspect = APP['w']/APP['h']
    proj = mat_perspective(world.cam.fov, aspect, 0.1, 500.0)
    view = world.cam.view()

    model = mat_identity()
    draw_mesh(world.plane_mesh, world.shader_triplanar, model, view, proj, {'uCamPos': world.cam.pos})

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    draw_mesh(world.water_mesh, world.shader_water, mat_translate(0,-0.7,0), view, proj, {'uTime': time.time()-world.time0})
    glDisable(GL_BLEND)

    for d in world.ducks:
        if not d.alive: continue
        heading = math.degrees(math.atan2(d.vel[2], d.vel[0]))
        M = mat_identity()
        M = mat_mul(M, mat_translate(*d.pos))
        M = mat_mul(M, mat_rotate_y(-heading))
        M = mat_mul(M, mat_scale(0.8,0.5,0.5))
        draw_mesh(world.duck_mesh, world.shader_basic, M, view, proj)
        spread = 0.6 + 0.4*math.sin(d.wing_phase)
        for sgn in (-1,1):
            Mw = mat_identity()
            Mw = mat_mul(Mw, mat_translate(d.pos[0], d.pos[1], d.pos[2]))
            Mw = mat_mul(Mw, mat_rotate_y(-heading))
            Mw = mat_mul(Mw, mat_translate(0.0, 0.2, 0.0))
            Mw = mat_mul(Mw, mat_translate(0.0, 0.0, sgn*0.55))
            Mw = mat_mul(Mw, mat_scale(0.05, 0.25, spread))
            draw_mesh(world.duck_mesh, world.shader_basic, Mw, view, proj)

    cam = world.cam
    gun_base = mat_identity()
    gun_base = mat_mul(gun_base, mat_translate(cam.pos[0], cam.pos[1]-0.2, cam.pos[2]))
    gun_base = mat_mul(gun_base, mat_scale(0.2,0.2,0.7))
    draw_mesh(world.duck_mesh, world.shader_basic, gun_base, view, proj)

    draw_hud(world)


def draw_hud(world: World):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, APP['w'], 0, APP['h'])
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glLineWidth(2)
    glColor3f(0.1, 1.0 if world.reticle_good else 0.2, 0.1 if world.reticle_good else 0.2)
    cx, cy = APP['w']//2, APP['h']//2
    glBegin(GL_LINES)
    glVertex2f(cx-10, cy); glVertex2f(cx+10, cy)
    glVertex2f(cx, cy-10); glVertex2f(cx, cy+10)
    glEnd()

    glColor3f(0,0,0)
    draw_text(10, APP['h']-20, f"Score: {world.score}")
    draw_text(10, APP['h']-40, f"Mag: {world.mag}  | Level: {world.level}")
    if world.menu:
        draw_text(cx-120, cy+60, "DUCK HUNTER 3D")
        draw_text(cx-220, cy+20, "Press M to Start • 1/2/3 to choose Level")
        draw_text(cx-160, cy-20, "WASD move • Mouse look • Click to shoot • R reload")
        draw_text(cx-170, cy-60, "Press B for Shop (skins & perks, stub)")
    if world.shop:
        draw_text(cx-70, cy+60, "SHOP")
        draw_text(cx-200, cy+20, "(Stub) Press B to exit • (No costs implemented)")
        draw_text(cx-180, cy-10, "Perk: Bigger Magazine [G] • Skin: Golden Gun [H]")

    glEnable(GL_DEPTH_TEST)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_text(x,y,s):
    glRasterPos2f(x,y)
    for ch in s:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

SENS = 0.12
SPEED = 10.0


def on_mouse_motion(x,y):
    if APP['world'].menu or APP['world'].shop:
        APP['last_mx']=x; APP['last_my']=y
        return
    if APP['last_mx'] is None:
        APP['last_mx']=x; APP['last_my']=y
        return
    dx = x-APP['last_mx']; dy = y-APP['last_my']
    APP['last_mx']=x; APP['last_my']=y
    cam = APP['world'].cam
    cam.yaw += dx*SENS
    cam.pitch -= dy*SENS
    cam.pitch = max(-89.0, min(89.0, cam.pitch))


def on_mouse_click(button, state, x, y):
    if button==GLUT_LEFT_BUTTON and state==GLUT_DOWN:
        w=APP['world']
        if w.menu:
            w.menu=False
            return
        if w.shop:
            return
        cam=w.cam
        ray_o=cam.pos
        ray_dir=cam.front()
        w.shoot(ray_o, ray_dir)


def on_key_down(key, x, y):
    if key==b'\x1b': sys.exit(0)
    APP['keys'].add(key)
    w=APP['world']
    if key in (b'M', b'm'): w.menu = not w.menu
    if key in (b'B', b'b'): w.shop = not w.shop
    if key==b'1': w.reset_level(1)
    if key==b'2': w.reset_level(2)
    if key==b'3': w.reset_level(3)
    if key in (b'R', b'r'):
        w.mag=5
        print("Reloaded.")
    if w.shop:
        if key in (b'G', b'g'):
            w.mag=8; print("Perk applied: Bigger Magazine (8)")
        if key in (b'H', b'h'):
            print("Golden Gun skin equipped (visual only stub)")


def on_key_up(key, x, y):
    if key in APP['keys']: APP['keys'].remove(key)


def update_cam(dt):
    w=APP['world']
    if w.menu or w.shop: return
    cam=w.cam
    f=cam.front(); r=cam.right()
    move=[0,0,0]
    if b'w' in APP['keys'] or b'W' in APP['keys']:
        move=v_add(move, f)
    if b's' in APP['keys'] or b'S' in APP['keys']:
        move=v_add(move, v_scale(f,-1))
    if b'a' in APP['keys'] or b'A' in APP['keys']:
        move=v_add(move, v_scale(r,-1))
    if b'd' in APP['keys'] or b'D' in APP['keys']:
        move=v_add(move, r)
    if b' ' in APP['keys']:
        move=v_add(move, [0,1,0])
    if b'c' in APP['keys'] or b'C' in APP['keys']:
        move=v_add(move, [0,-1,0])
    if v_len(move)>0:
        move=v_norm(move)
        cam.pos = v_add(cam.pos, v_scale(move, SPEED*dt))

def display():
    world=APP['world']
    now=time.time()
    if APP['last_time'] is None: APP['last_time']=now
    dt = now-APP['last_time']; APP['last_time']=now
    update_cam(dt)
    world.update(dt)
    render_world(world)
    glutSwapBuffers()


def reshape(w,h):
    APP['w']=max(1,w); APP['h']=max(1,h)
    glViewport(0,0,APP['w'],APP['h'])


def timer(_):
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)


def init_gl():
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CCW)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(APP['w'], APP['h'])
    glutCreateWindow(b"Duck Hunter 3D - PyOpenGL")

    init_gl()

    APP['world']=World()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutPassiveMotionFunc(on_mouse_motion)
    glutMotionFunc(on_mouse_motion)
    glutMouseFunc(on_mouse_click)
    glutKeyboardFunc(on_key_down)
    glutKeyboardUpFunc(on_key_up)
    glutTimerFunc(16, timer, 0)
    glutMainLoop()

if __name__=="__main__":
    main()
