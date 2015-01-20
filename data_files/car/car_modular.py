import sys
sys.path.append('/home/tarik/designer/tableMaker')
from TableMaker import *

# module name map:
#names = {'center':0,
#    'front-center':1,
#    'front-left':2,
#    'front-right':3,
#    'back-center':4,
#    'back-right':5,
#    'back-left':6
#}
names = {'front-center':0,
    'center':1,
    'back-center':2,
    'front-left':3,
    'front-right':4,
    'back-left':5,
    'back-right':6
}

names = {'drive1':0,
		 'steer3-front':0,
		 'steer3-mid':1,
         'steer3-back':2
        }


# define module groups:
wheel_group = ['front-center', 'front-left', 'front-right', 'back-center', 'back-left', 'back-right']

#ss = set_module_state # for convenience

def drive1_stand_up():
    return sms( 'drive1', [0, 0, 0, 0.7] )

def steer3_stand_up():
    return parallel([
        sms( 'steer3-front', [0, 0, 0, 0.5] ),
        sms( 'steer3-mid',   [0, 0, 0, -0.5] ),
        sms( 'steer3-back',  [0, 0, 0, 0.7] ),
    ])
def drive1_drive_forward(angle):
    return sms( 'drive1', {'left':angle, 'right':angle, 'front':0, 'center':0.7})
def steer3_drive_forward(angle):
    return parallel([
        sms( 'steer3-front', {'left':angle, 'right':angle, '} ),#ack!
        sms( 'steer3-back', {'left':angle, 'right':angle} ),
    ])
def steer3_turn(angle):
    return parallel([
        sms( 'steer3-back', {'front':angle} ),
        sms( 'steer3-mid', {'front':-angle} )
    ])

#def stand_up():
#    ''' Assume neutral standing position. '''
#    return parallel([
#        self.drive1_stand_up(),
#        self.steer3_stand_up()
#    ])
#
#def drive_forward(angle):
#    ''' Drives the wheels forward, to the specified angle. '''
#    return parallel([ self.
#
#def turn(angle):
#    ''' Makes the center joints turn by specified angle. '''
#    return parallel([ sms( 'back-center', {'front':angle} ),
#                      sms( 'center', {'front':-angle} ),
#     ])

def sms(module_name, positions):
    ''' Sets module state. Positions is a dict or a list. '''
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

c = CommandBlock()
#r = series([ stand_up(),
#        drive_forward(3),
#        turn(.3),
#        drive_forward(12),
#        turn(-0.3),
#        drive_forward(21),
#        turn(0),
#        drive_forward(30)
#    ])
c = CommandBlock()
c.stitch(drive1_stand_up())
c.write('d1_standup.gait')
c = CommandBlock()
c.stitch(steer3_stand_up())
c.write('s3_standup.gait')
for i in [3, 12, 21, 30]:
    c = CommandBlock()
    c.stitch(drive1_drive_forward(i))
    c.write('d1_drive_'+ str(i) + '.gait')
    c = CommandBlock()
    c.stitch(steer3_drive_forward(i))
    c.write('s3_drive_' + str(i) + '.gait')
c = CommandBlock()
c.stitch(steer3_turn(0.3))
c.write('s3_turn_right.gait')
c = CommandBlock()
c.stitch(steer3_turn(-0.3))
c.write('s3_turn_left.gait')

