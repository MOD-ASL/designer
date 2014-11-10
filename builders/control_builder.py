#! /usr/bin/env python

import xml.etree.ElementTree as ET
import os
import sys

from utils.utils import prettify

class ControlBuilder(object):
    def __init__(self):
        pass

    def createParallelBlockET(self, list_of_blockET):
        blockET = ET.Element("Block")
        blockET.set("type", "p_block")

        for child_blockET in list_of_blockET:
            if child_blockET is None:
                continue
            if child_blockET.get("type") == "p_block":
                blockET.extend(list(child_blockET))
            else:
                blockET.append(child_blockET)

        return blockET

    def createSeriesBlockET(self, list_of_blockET):
        blockET = ET.Element("Block")
        blockET.set("type", "s_block")

        for child_blockET in list_of_blockET:
            if child_blockET is None:
                continue
            if child_blockET.get("type") == "s_block":
                blockET.extend(list(child_blockET))
            else:
                blockET.append(child_blockET)

        return blockET

    def build(self, blockET, file_name):
        root = ET.Element("Control")
        root.append(blockET)

        with open(file_name, "w") as f:
            f.write(prettify(root))

    def createGaitBlockET(self, component_id, gait_file_path):
        if not os.path.isfile(gait_file_path):
            raise IOError("Gait file {!r} does not exist.".format(gait_file_path))
        blockET = ET.Element("Block")
        blockET.set("type", "gait")
        c_id = ET.SubElement(blockET, "component_id")
        c_id.text = component_id
        file_name = ET.SubElement(blockET, "gait_file")
        file_name.text = gait_file_path

        return blockET

if __name__ == "__main__":
    CB = ControlBuilder()
    CB.loadStructure(sys.argv[1])
    CB.build()
