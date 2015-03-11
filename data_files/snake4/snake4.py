from TableMaker import *
from math import pi
class Snake4:

	def __init__(self):
		self.names = {'front':3,
					'mid-front':2,
					'mid-back':1,
					'back':0,
		}
		self.drive_angle = 0

	def lay_flat(self):
		''' Lays down flat, ready to drive'''
		return parallel( [self.sms(module, {'center':0, 'front':0})
						for module_name in self.names.keys] )

	def drive_absolute(self, angle):
		''' Drive the wheels forward to the specified angle '''
		self.drive_angle = angle
		return parallel( [self.sms(module_name, {'left':angle, 'right':angle})
						for module_name in self.names.keys] )

	def drive(self, relative_angle):
		''' Drive the wheels to the specified angle relative the current position '''
		return self.drive_absolute(self.drive_angle + relative_angle)

	def rear_up(self):
		''' Rears the snake up to climb a ledge '''
		return self.sms('mid-front', {'center': pi/2})

	def janky_pause(self, time):
		''' A janky implementation of pausing for the requested number of milliseconds. '''
		sms = lambda module_name, positions: self.sms(module_name, positions, self.grasper_names) 
		return sms('center', {'left':0, 'right':0}) + ' [' + str(time) + ']'	


#---------------------------------------------------
	def sms(self, module_name, positions, names = None):
	    ''' Sets module state. Positions is a dict or a list. '''
	    if names == None:
	    	names = self.names
	    if isinstance(positions, dict):
	        p = ['i', 'i', 'i', 'i']
	        for i,key in enumerate(['front', 'left', 'right', 'center']):
	            # map specified joints into table command; leave as 'i' (no change) if not used.
	            if positions.has_key(key):
	                p[i] = positions[key]
	            #p = [ positions['front'], positions['left'], positions['right'], positions['center'] ]
	    elif isinstance(positions, list):
	        # for conciseness, you can also specify as a list.
	        p = positions
	    else:
	        assert(False)
	    out = ''
	    out += 'Module_' + str(names[module_name])
	    for i in xrange(0,4):
	        if p[i] is 'i':
	            out += ' i'
	        else:
	            out += ' p' + str(p[i])
	    #out += ' p' + str(p[0]) + ' p' + str(p[1]) + ' p' + str(p[2]) + ' p' + str(p[3])
	    return out

if __name__=='__main__':
	s = Snake4()
	c = CommandBlock()
	r = series([ s.lay_flat(), s.janky_pause(1000), s.drive(pi), s.janky_pause(500), s.rear_up() ])	
	c.stitch(r)
	print c
	c.write('snake4-auto.gait')