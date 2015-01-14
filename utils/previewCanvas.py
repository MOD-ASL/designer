import wx
from wx.glcanvas import GLCanvas
from wx.glcanvas import WX_GL_DEPTH_SIZE
from wxPython.wx import *
from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from math import pi, sin, cos, sqrt, acos

#===================================================================================================
class PreviewCanvas(GLCanvas):
    def __init__(self, *args, **kwargs):
        attribs=[WX_GL_DEPTH_SIZE,16,0,0];
        GLCanvas.__init__(self, attribList=attribs,*args, **kwargs)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_MOTION, self.OnMouse)

        self.init = False
        self.width, self.height = self.GetSize()

        self.alpha = 0
        self.beta = 0
        self.distance = 5.0

        self.oldX = 0
        self.oldY = 0
        self.leftDown = False
        self.rightDown = False
        self.module_list = []
        self.module_scale = 20.0
    #-----------------------------------------------------------------------------------------------
    def OnDraw(self):
        dc = wx.PaintDC(self)
        self.SetCurrent()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        x = y = z = 0.0
        angle = ax = ay = az = 0.0
        for module_obj in self.module_list:
            glTranslate(-x, -y, -z)
            x, y = [round(i,2)*self.module_scale for i in module_obj.Position[0:2]]
            z = (module_obj.Position[2] - 0.05)*self.module_scale # z starts at 0.05
            glTranslate(x, y, z)
            #if len(module_obj.Position) == 7:
            #    [angle, ax, ay, az] = self.quaternion2AngleAxis(module_obj.Position[3:])
            self.drawCube(angle, ax, ay, az)

        #self.SwapBuffers() # not sure why this creates error

    def quaternion2AngleAxis(self,q):
        x, y, z, w = q
        scale = sqrt(x * x + y * y + z * z)
        axisX = x / scale
        axisY = y / scale
        axisZ = z / scale
        angle = acos(w) * 2.0

        return [angle, axisX, axisY, axisZ]

    def clear(self):
        self.module_list = []
        self.ChangeView()
        self.Refresh()

    def setData(self, module_list):
        self.module_list = module_list
        self.ChangeView()
        self.Refresh()

    #-----------------------------------------------------------------------------------------------
    def ChangeView(self):
        self.SetCurrent()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslate(0.0, 0.0, -self.distance)
        glRotate(-90, 0.0, 1.0, 0.0)
        glRotate(-90, 1.0, 0.0, 0.0)

        glRotate(self.alpha, 0.0, 0.0, 1.0)
        glRotate(self.beta, 0.0, 1.0, 0.0)

        self.OnDraw()

    #-----------------------------------------------------------------------------------------------
    def Resize(self):
        self.SetCurrent()
        ratio = float(self.width) / self.height;

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0, 0, self.width, self.height)
        gluPerspective(45, ratio, 1, 1000)

        self.ChangeView()

    #-----------------------------------------------------------------------------------------------
    def OnPaint(self, event):
        wx.PaintDC(self)
        self.SetCurrent()
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

    #-----------------------------------------------------------------------------------------------
    def OnLeftDown(self, event):
        self.oldX, self.oldY = event.GetPosition()
        self.leftDown = True

    def OnRightDown(self, event):
        self.oldX, self.oldY = event.GetPosition()
        self.rightDown = True

    def OnLeftUp(self, event):
        self.leftDown = False

    def OnRightUp(self, event):
        self.rightDown = False

    def OnMouse(self, event):
        if self.leftDown or self.rightDown:
            X, Y = event.GetPosition()
            if self.rightDown:
                self.distance += (Y - self.oldY) * 0.05

            if self.leftDown:
                self.alpha += (X - self.oldX) * 0.5
                self.beta += (Y - self.oldY) * 0.5

            self.ChangeView()
            self.oldX, self.oldY = X, Y

    #-----------------------------------------------------------------------------------------------
    def OnResize(self, e):
        self.width, self.height = e.GetSize()
        self.Resize()

    #-----------------------------------------------------------------------------------------------
    def ShowAxes(self):
        glDisable(GL_LIGHTING)

        glColor3f(1.0, 1.0, 0.0)
        glRasterPos3f(1.2, 0.0, 0.0)
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord('x'))
        glRasterPos3f(0.0, 1.2, 0.0)
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord('y'))
        glRasterPos3f(0.0, 0.0, 1.2)
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord('z'))

        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)
        glVertex3f(1, 0, 0)
        glVertex3f(1, 1, 0)
        glVertex3f(0, 1, 0)
        glEnd()
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 1)
        glVertex3f(0, 1, 1)
        glVertex3f(0, 1, 0)
        glEnd()
        glColor3f(0.0, 0.0, 1.0)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)
        glVertex3f(1, 0, 0)
        glVertex3f(1, 0, 1)
        glVertex3f(0, 0, 1)
        glEnd()

        glEnable(GL_LIGHTING)

    #-----------------------------------------------------------------------------------------------
    def InitGL(self):
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  (0.8, 0.8, 0.8, 1.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT,  (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_POSITION, (1.0, 1.0, 1.0, 0.0))
        glEnable(GL_LIGHT0)

#        glShadeModel(GL_SMOOTH)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)

        self.Resize()


    #-----------------------------------------------------------------------------------------------
    def drawCube(self, angle, ax, ay, az):
        glDisable(GL_LIGHTING)
        #glRotate(angle, ax, ay, az)
        # Draw Cube (multiple quads)
        min_cube = 0.0
        max_cube = 1-min_cube
        glBegin(GL_QUADS)

        glColor3f(min_cube,min_cube,max_cube)
        glVertex3f( max_cube, max_cube,-max_cube)
        glVertex3f(-max_cube, max_cube,-max_cube)
        glVertex3f(-max_cube, max_cube, max_cube)
        glVertex3f( max_cube, max_cube, max_cube)

        glColor3f(min_cube,min_cube,max_cube)
        glVertex3f( max_cube,-max_cube, max_cube)
        glVertex3f(-max_cube,-max_cube, max_cube)
        glVertex3f(-max_cube,-max_cube,-max_cube)
        glVertex3f( max_cube,-max_cube,-max_cube)

        glColor3f(min_cube,min_cube,max_cube)
        glVertex3f( max_cube, max_cube, max_cube)
        glVertex3f(-max_cube, max_cube, max_cube)
        glVertex3f(-max_cube,-max_cube, max_cube)
        glVertex3f( max_cube,-max_cube, max_cube)

        glColor3f(min_cube,min_cube,max_cube)
        glVertex3f( max_cube,-max_cube,-max_cube)
        glVertex3f(-max_cube,-max_cube,-max_cube)
        glVertex3f(-max_cube, max_cube,-max_cube)
        glVertex3f( max_cube, max_cube,-max_cube)

        glColor3f(min_cube,min_cube,max_cube)
        glVertex3f(-max_cube, max_cube, max_cube)
        glVertex3f(-max_cube, max_cube,-max_cube)
        glVertex3f(-max_cube,-max_cube,-max_cube)
        glVertex3f(-max_cube,-max_cube, max_cube)

        glColor3f(min_cube,min_cube,max_cube)
        glVertex3f( max_cube, max_cube,-max_cube)
        glVertex3f( max_cube, max_cube, max_cube)
        glVertex3f( max_cube,-max_cube, max_cube)
        glVertex3f( max_cube,-max_cube,-max_cube)

        glEnd()

        glBegin(GL_LINES)

        glColor3f(1,0,0)
        glVertex3f( max_cube, max_cube,-max_cube)
        glVertex3f(-max_cube, max_cube,-max_cube)
        glVertex3f(-max_cube, max_cube, max_cube)
        glVertex3f( max_cube, max_cube, max_cube)

        glColor3f(1,0,0)
        glVertex3f( max_cube,-max_cube, max_cube)
        glVertex3f(-max_cube,-max_cube, max_cube)
        glVertex3f(-max_cube,-max_cube,-max_cube)
        glVertex3f( max_cube,-max_cube,-max_cube)

        glColor3f(1,0,0)
        glVertex3f( max_cube, max_cube, max_cube)
        glVertex3f(-max_cube, max_cube, max_cube)
        glVertex3f(-max_cube,-max_cube, max_cube)
        glVertex3f( max_cube,-max_cube, max_cube)

        glColor3f(1,0,0)
        glVertex3f( max_cube,-max_cube,-max_cube)
        glVertex3f(-max_cube,-max_cube,-max_cube)
        glVertex3f(-max_cube, max_cube,-max_cube)
        glVertex3f( max_cube, max_cube,-max_cube)

        glColor3f(1,0,0)
        glVertex3f(-max_cube, max_cube, max_cube)
        glVertex3f(-max_cube, max_cube,-max_cube)
        glVertex3f(-max_cube,-max_cube,-max_cube)
        glVertex3f(-max_cube,-max_cube, max_cube)

        glColor3f(1,0,0)
        glVertex3f( max_cube, max_cube,-max_cube)
        glVertex3f( max_cube, max_cube, max_cube)
        glVertex3f( max_cube,-max_cube, max_cube)
        glVertex3f( max_cube,-max_cube,-max_cube)

        glEnd()

        posx, posy = 0,0
        sides = 32
        radius = 1
        """
        # front wheel
        glBegin(GL_POLYGON)
        for i in range(100):
            cosine= radius * cos(i*2*pi/sides) + posx
            sine  = radius * sin(i*2*pi/sides) + posy
            glColor3f(1.0,1.0,0.0)
            glVertex3f(cosine,-1.01,sine)
        glEnd()

        # left wheel
        glBegin(GL_POLYGON)
        for i in range(100):
            cosine= radius * cos(i*2*pi/sides) + posx
            sine  = radius * sin(i*2*pi/sides) + posy
            glColor3f(1.0,1.0,0.0)
            glVertex3f(1.01,cosine,sine)
        glEnd()

        # right wheel
        glBegin(GL_POLYGON)
        for i in range(100):
            cosine= radius * cos(i*2*pi/sides) + posx
            sine  = radius * sin(i*2*pi/sides) + posy
            glColor3f(1.0,1.0,0.0)
            glVertex3f(-1.01,cosine,sine)
        glEnd()
        """

        glEnable(GL_LIGHTING)
