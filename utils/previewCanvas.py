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
        self.Bind(wx.EVT_MIDDLE_DOWN, self.OnMiddleDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_MIDDLE_UP, self.OnMiddleUp)
        self.Bind(wx.EVT_MOTION, self.OnMouse)

        self.init = False
        self.width, self.height = self.GetSize()

        self.alpha = 0
        self.beta = 0
        self.distanceX = 0.0
        self.distanceY = 0.0
        self.distance = 5.0

        self.oldX = 0
        self.oldY = 0
        self.leftDown = False
        self.rightDown = False
        self.middleDown = False
        self.module_list = []
        self.module_scale = 20.0
        self.module_name = ""
        self.node_name = ""
    #-----------------------------------------------------------------------------------------------
    def OnDraw(self):

        dc = wx.PaintDC(self)
        self.SetCurrent()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for module_obj in self.module_list:
            high_light = False
            high_light_node = ""
            central_bend = round(module_obj.JointAngle[3]/pi*180)
            if self.module_name == module_obj.ModelName:
                high_light = True
                high_light_node = self.node_name
            x, y = [round(i,2)*self.module_scale for i in module_obj.Position[0:2]]
            z = (module_obj.Position[2] - 0.05)*self.module_scale # z starts at 0.05
            glTranslate(x, y, z)
            if len(module_obj.Position) == 7:
                [angle, ax, ay, az] = self.quaternion2AngleAxis(module_obj.Position[3:])
                glRotate(angle, ax, ay, az)
                self.drawCube(central_bend, high_light, high_light_node)
                glRotate(-angle, ax, ay, az)
            elif len(module_obj.Position) == 6:
                glRotate(module_obj.Position[3]/pi*180, 1.0, 0.0, 0.0)
                glRotate(module_obj.Position[4]/pi*180, 0.0, 1.0, 0.0)
                glRotate(module_obj.Position[5]/pi*180, 0.0, 0.0, 1.0)
                self.drawCube(central_bend, high_light, high_light_node)
                glRotate(-module_obj.Position[5]/pi*180, 0.0, 0.0, 1.0)
                glRotate(-module_obj.Position[4]/pi*180, 0.0, 1.0, 0.0)
                glRotate(-module_obj.Position[3]/pi*180, 1.0, 0.0, 0.0)
            glTranslate(-x, -y, -z)

        #self.SwapBuffers() # not sure why this creates error

    def quaternion2AngleAxis(self,q):
        w, x, y, z = q
        scale = sqrt(x * x + y * y + z * z)
        if scale == 0.0:
            return [0.0, 0.0, 0.0, 0.0]
        axisX = x / scale
        axisY = y / scale
        axisZ = z / scale
        angle = acos(w) * 2.0/pi*180

        return [angle, axisX, axisY, axisZ]

    def clear(self):
        self.module_list = []
        self.module_name = ""
        self.node_name = ""
        self.ChangeView()
        self.Refresh()

    def setData(self, module_list):
        self.module_list = module_list
        self.ChangeView()
        self.Refresh()

    def setHighlightModule(self, module_name = ""):
        self.module_name = module_name
        self.ChangeView()
        self.Refresh()
    def setHighlightNode(self, node_name = ""):
        self.node_name = node_name
        self.ChangeView()
        self.Refresh()

    #-----------------------------------------------------------------------------------------------
    def ChangeView(self):
        self.SetCurrent()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslate(self.distanceX, self.distanceY, -self.distance)
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

    def OnMiddleDown(self, event):
        self.oldX, self.oldY = event.GetPosition()
        self.middleDown = True

    def OnLeftUp(self, event):
        self.leftDown = False

    def OnRightUp(self, event):
        self.rightDown = False

    def OnMiddleUp(self, event):
        self.middleDown = False

    def OnMouse(self, event):
        if self.leftDown or self.rightDown or self.middleDown:
            X, Y = event.GetPosition()
            if self.rightDown:
                self.distance += (Y - self.oldY) * 0.05

            if self.middleDown:
                self.distanceX += (X - self.oldX) * 0.05
                self.distanceY -= (Y - self.oldY) * 0.05

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
    def drawCube(self, central_bend = 0.0, high_light = False, high_light_node = ""):
        glDisable(GL_LIGHTING)
        # Draw Cube (multiple quads)
        max_cube = 1.0
        glBegin(GL_QUADS)

        # back frame
        if central_bend == 0.0:
            if high_light_node == "b":
                glColor3f(0.0, 1.0, 0.0)
            else:
                glColor3f(1.0, 1.0, 0.0)
        else:
            glColor3f(0.5, 0.5, 0.5)
        glVertex3f( max_cube, max_cube,-max_cube)
        glVertex3f(-max_cube, max_cube,-max_cube)
        glVertex3f(-max_cube, max_cube, max_cube)
        glVertex3f( max_cube, max_cube, max_cube)

        # front wheel frame
        glColor3f(0.5, 0.5, 0.5)
        glVertex3f( max_cube,-max_cube, max_cube)
        glVertex3f(-max_cube,-max_cube, max_cube)
        glVertex3f(-max_cube,-max_cube,-max_cube)
        glVertex3f( max_cube,-max_cube,-max_cube)

        # back frame when central bend is 90
        if central_bend == 90.0:
            if high_light_node == "b":
                glColor3f(0.0, 1.0, 0.0)
            else:
                glColor3f(1.0, 1.0, 0.0)
        else:
            glColor3f(0.5, 0.5, 0.5)
        glVertex3f( max_cube, max_cube, max_cube)
        glVertex3f(-max_cube, max_cube, max_cube)
        glVertex3f(-max_cube,-max_cube, max_cube)
        glVertex3f( max_cube,-max_cube, max_cube)

        # back frame when central bend is -90
        if central_bend == -90.0:
            if high_light_node == "b":
                glColor3f(0.0, 1.0, 0.0)
            else:
                glColor3f(1.0, 1.0, 0.0)
        else:
            glColor3f(0.5, 0.5, 0.5)
        glVertex3f( max_cube,-max_cube,-max_cube)
        glVertex3f(-max_cube,-max_cube,-max_cube)
        glVertex3f(-max_cube, max_cube,-max_cube)
        glVertex3f( max_cube, max_cube,-max_cube)

        # right wheel frame
        glColor3f(0.5, 0.5, 0.5)
        glVertex3f(-max_cube, max_cube, max_cube)
        glVertex3f(-max_cube, max_cube,-max_cube)
        glVertex3f(-max_cube,-max_cube,-max_cube)
        glVertex3f(-max_cube,-max_cube, max_cube)

        # left wheel frame
        glColor3f(0.5, 0.5, 0.5)
        glVertex3f( max_cube, max_cube,-max_cube)
        glVertex3f( max_cube, max_cube, max_cube)
        glVertex3f( max_cube,-max_cube, max_cube)
        glVertex3f( max_cube,-max_cube,-max_cube)
        glEnd()

        if high_light:
            glLineWidth(5.0)
            glBegin(GL_LINES)
            glColor3f(1,0,0)
            glVertex3f( max_cube, max_cube, max_cube)
            glVertex3f( max_cube, max_cube,-max_cube)

            glVertex3f( max_cube, max_cube,-max_cube)
            glVertex3f(-max_cube, max_cube,-max_cube)

            glVertex3f(-max_cube, max_cube,-max_cube)
            glVertex3f(-max_cube, max_cube, max_cube)

            glVertex3f(-max_cube, max_cube, max_cube)
            glVertex3f( max_cube, max_cube, max_cube)

            glVertex3f( max_cube, max_cube, max_cube)
            glVertex3f( max_cube,-max_cube, max_cube)

            glVertex3f( max_cube,-max_cube, max_cube)
            glVertex3f(-max_cube,-max_cube, max_cube)

            glVertex3f(-max_cube,-max_cube, max_cube)
            glVertex3f(-max_cube,-max_cube,-max_cube)

            glVertex3f(-max_cube,-max_cube,-max_cube)
            glVertex3f( max_cube,-max_cube,-max_cube)

            glVertex3f( max_cube,-max_cube,-max_cube)
            glVertex3f( max_cube,-max_cube, max_cube)
            glEnd()
            glBegin(GL_LINES)
            glColor3f(1,0,0)
            glVertex3f( max_cube,-max_cube,-max_cube)
            glVertex3f( max_cube, max_cube,-max_cube)
            glEnd()
            glBegin(GL_LINES)
            glColor3f(1,0,0)
            glVertex3f(-max_cube,-max_cube,-max_cube)
            glVertex3f(-max_cube, max_cube,-max_cube)
            glEnd()
            glBegin(GL_LINES)
            glColor3f(1,0,0)
            glVertex3f(-max_cube,-max_cube, max_cube)
            glVertex3f(-max_cube, max_cube, max_cube)
            glEnd()

        posx, posy = 0,0
        sides = 32
        radius = 1
        # front wheel
        glBegin(GL_POLYGON)
        for i in range(100):
            cosine= radius * cos(i*2*pi/sides) + posx
            sine  = radius * sin(i*2*pi/sides) + posy
            if high_light_node == "f":
                glColor3f(0.0,1.0,0.0)
            else:
                glColor3f(1.0,1.0,0.0)
            glVertex3f(cosine,-1.01,sine)
        glEnd()

        # left wheel
        glBegin(GL_POLYGON)
        for i in range(100):
            cosine= radius * cos(i*2*pi/sides) + posx
            sine  = radius * sin(i*2*pi/sides) + posy
            if high_light_node == "l":
                glColor3f(0.0,1.0,0.0)
            else:
                glColor3f(1.0,1.0,0.0)
            glVertex3f(1.01,cosine,sine)
        glEnd()

        # right wheel
        glBegin(GL_POLYGON)
        for i in range(100):
            cosine= radius * cos(i*2*pi/sides) + posx
            sine  = radius * sin(i*2*pi/sides) + posy
            if high_light_node == "r":
                glColor3f(0.0,1.0,0.0)
            else:
                glColor3f(1.0,1.0,0.0)
            glVertex3f(-1.01,cosine,sine)
        glEnd()

        glEnable(GL_LIGHTING)
