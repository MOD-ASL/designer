class Connection:
	def __init__(self,model1,model2,node1,node2,distance=0,angle=0):
        # Name string of module 1
		self.Module1 = model1
        # Name string of module 2
		self.Module2 = model2
        # Node index of the connected face of module 1
		self.Node1 = node1
        # Node index of the connected face of module 2
		self.Node2 = node2
        # Distance offset
		self.Distance = distance
        # Angle offset
		self.Angle = angle
	def __len__(self):
		return 1
