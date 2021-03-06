from builders.configuration_builder import ConfigurationBuilder
from builders.gait_builder import GaitBuilder, GaitCollisionChecker
import sys

if len(sys.argv) < 2:
    print "Usage: python make_gait.py path/to/robot_folder/robot_name"
    sys.exit(0)
file_name = sys.argv[1]

CB = ConfigurationBuilder()
CB.loadStructure(file_name+".struct")
CB.buildNewConfiguration()
CB.saveNewConfiguration(file_name+".conf")

GB = GaitBuilder()
GB.loadControl(file_name+".control")

GCC = GaitCollisionChecker()
gait = GCC.loadGait(GB.output_str.split("\n"))
GCC.runGait(CB)

GB.output_str = CB.replaceAllModuleName(GB.output_str)
GB.saveNewGait(file_name+".gait")
