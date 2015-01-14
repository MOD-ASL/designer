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
f1 = CB.createGaitBlockET("finger1", pick)
f2 = CB.createGaitBlockET("finger2", pick)
f3 = CB.createGaitBlockET("finger3", pick)
bodyroll = CB.createGaitBlockET("body", roll)

# put basic blocks in parallel or series
blockET = CB.createParallelBlockET([f1, f2])
blockET = CB.createSeriesBlockET([blockET, f3, bodyroll])

# save to control file
CB.build(blockET, sys.argv[1])
