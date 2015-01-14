#! /usr/bin/env python
from builders.control_builder import ControlBuilder
import os, sys

if len(sys.argv) < 2:
    print "Usage: python control_demo.py path/to/control_file.control"
    sys.exit(0)

# initialize ControlBuilder
CB = ControlBuilder()

##############################################################
####### Change these path to the right directory #############
# define some basic gait files
front = "/home/asl/SMORES/gaits_and_configs/vleg/front.gait"
back = "/home/asl/SMORES/gaits_and_configs/vleg/back.gait"
normal = "/home/asl/SMORES/gaits_and_configs/vleg/normal.gait"
##############################################################

if not os.path.isfile(front):
    print "Please change the path of the gait files to the right directory."
    sys.exit(0)

# build basic gait block
f1 = CB.createGaitBlockET("Component_1", front)
b1 = CB.createGaitBlockET("Component_1", back)
n1 = CB.createGaitBlockET("Component_1", normal)

f2 = CB.createGaitBlockET("Component_2", front)
b2 = CB.createGaitBlockET("Component_2", back)
n2 = CB.createGaitBlockET("Component_2", normal)

f3 = CB.createGaitBlockET("Component_3", front)
b3 = CB.createGaitBlockET("Component_3", back)
n3 = CB.createGaitBlockET("Component_3", normal)

f4 = CB.createGaitBlockET("Component_4", front)
b4 = CB.createGaitBlockET("Component_4", back)
n4 = CB.createGaitBlockET("Component_4", normal)

# put basic blocks in parallel or series
b1 = CB.createParallelBlockET([f1, f4])
b2 = CB.createParallelBlockET([n1, b2, b3, n4])
b3 = CB.createParallelBlockET([n2, n3])
b4 = CB.createParallelBlockET([f2, f3])
b5 = CB.createParallelBlockET([b1, n2, n3, b4])
b6 = CB.createParallelBlockET([n1, n4])


blockET = CB.createSeriesBlockET([b1,b2,b3]*6)

# save to control file
CB.build(blockET, sys.argv[1])
