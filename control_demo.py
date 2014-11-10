#! /usr/bin/env python
from builders.control_builder import ControlBuilder

# initialize ControlBuilder
CB = ControlBuilder()

# define some basic gait files
pick = "/home/asl/SMORES/gaits_and_configs/simple/pick.gait"
roll = "/home/asl/SMORES/gaits_and_configs/simple/roll.gait"

# build basic gait block
f1 = CB.createGaitBlockET("finger1", pick)
f2 = CB.createGaitBlockET("finger2", pick)
f3 = CB.createGaitBlockET("finger3", pick)
bodyroll = CB.createGaitBlockET("body", roll)

# put basic blocks in parallel or series
blockET = CB.createParallelBlockET([f1, f2])
blockET = CB.createSeriesBlockET([blockET, f3, bodyroll])

# save to control file
CB.build(blockET, "/home/asl/SMORES/designer/data_files/grabbot/grabbot.control")
