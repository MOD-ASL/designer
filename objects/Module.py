class Module:
    def __init__(self,modelname, position, jointangle, path, quapos = False):
        self.ModelName = modelname
        try:
            self.Position = position
        except ValueError:
            pass
        try:
            self.JointAngle = jointangle
        except ValueError:
          pass
        self.nodes = {0:False, 1:False, 2:False, 3:False}
        self.Path = path
        self.Quaternion = quapos

    def connect(self, node):
        self.nodes[node] = True

    def disconnect(self, node):
        self.nodes[node] = False
