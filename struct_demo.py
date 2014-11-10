#! /usr/bin/env python
from builders.structure_builder import StructureBuilder

# initialize StructureBuilder
SB = StructureBuilder()

# define some basic configuration files
leg_conf_file = "/home/asl/SMORES/gaits_and_configs/simple/leg.conf"
body_conf_file = "/home/asl/SMORES/gaits_and_configs/simple/bigbody.conf"

# add componenets
SB.addComponent("body", body_conf_file)
SB.addComponent("finger1", leg_conf_file)
SB.addComponent("finger2", leg_conf_file)
SB.addComponent("finger3", leg_conf_file)

# add links between componenets
SB.addLink("body2f1", "body", "finger1", "Module_1", "Module_0", 1, 0, 0, 0)
SB.addLink("body2f2", "body", "finger2", "Module_3", "Module_0", 1, 0, 0, 0)
SB.addLink("body2f3", "body", "finger3", "Module_1", "Module_0", 2, 0, 0, 0)

# save to stucture file
SB.build("/home/asl/SMORES/designer/data_files/grabbot/grabbot.struct")
