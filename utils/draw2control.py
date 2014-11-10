#! /usr/bin/env python

import xml.etree.ElementTree as ET
import sys

from utils import prettify

class Draw2Control(object):
    def __init__(self):
        self.ET_tree = None
        self.connection_dict = {} # {id_in_xml: [list of id in xml]}
        pass

    def loadXML(self, file_path):
        self.ET_tree = ET.parse(file_path)
        for element in self.ET_tree.iterfind("root/mxCell[@source]"):
            s = element.get("source")
            t = element.get("target")
            if s not in self.connection_dict:
                self.connection_dict[s] = []
            self.connection_dict[s].append(t)

    def printConnections(self):
        for s, t in self.connection_dict.iteritems():
            print s," --- ",",".join(t)

    def getElementTypeWithID(self, element_id):
        for item in self.ET_tree.iterfind("root/mxCell[@id='{}']".format(element_id)):
            return item.get("value")

    def processConnection(self, current_id):
        element_type = self.getElementTypeWithID(current_id)
        if element_type == "p(":
            # start of parallel
            print "Creating a parallel control block."
            block = ET.Element("Block")
            block.set("type", "p_block")

            end_of_parallel_id = -1

            for next_id in self.connection_dict[current_id]:
                (next_next_id, next_block) = self.processConnection(next_id)
                block.append(next_block)

                if end_of_parallel_id != -1:
                    if end_of_parallel_id != next_next_id:
                        raise ValueError("Got next_next_id {}, expect {}".format( \
                                                            next_next_id, end_of_parallel_id))
                else:
                    element_type = self.getElementTypeWithID(next_next_id)
                    if element_type != ")p":
                        raise ValueError("Got next_next type {}, expect )p".format( \
                                                            element_type))
                    else:
                        end_of_parallel_id = next_next_id

            next_id = self.connection_dict[end_of_parallel_id][0]

            return (next_id, block)

        elif element_type == "s(":
            print "Creating a series control block."
            # start of series
            end_of_series = False
            list_of_block = []
            next_id = self.connection_dict[current_id][0]
            while not end_of_series:
                (next_id, next_block) = self.processConnection(next_id)
                list_of_block.append(next_block)
                element_type = self.getElementTypeWithID(next_id)
                if element_type == ")s":
                    end_of_series = True

            block = ET.Element("Block")
            block.set("type", "s_block")
            block.extend(list_of_block)

            next_id = self.connection_dict[next_id][0]

            return (next_id, block)

        elif element_type in [")p", ")s", None]:
            raise ValueError("Getting unexpected value {}".format(element_type))
        else:
            # this is a single gait element
            block = ET.Element("Block")
            block.set("type", "gait")
            component_id = ET.SubElement(block, "component_id")
            component_id.text = element_type.split("\n")[0]
            gait_file = ET.SubElement(block, "gait_file")
            gait_file.text = "/home/asl/SMORES/gaits_and_configs/simple/" + element_type.split("\n")[1] + ".gait"
            next_id = self.connection_dict[current_id][0]
            return (next_id, block)

    def buildControlET(self, file_name):
        root = ET.Element("Control")

        start_id = -1
        for item in self.ET_tree.iterfind("root/mxCell[@value='start']"):
            start_id = item.get("id")
            break

        for next_id in self.connection_dict[start_id]:
            (end_id, final_ET) = self.processConnection(next_id)
        element_type = self.getElementTypeWithID(end_id)
        if element_type != "end":
            raise ValueError("Did we actually finish? Ends at {}".format(end_id))

        root.append(final_ET)

        with open(file_name, "w") as f:
            f.write(prettify(root))



if __name__ == "__main__":
    D2C = Draw2Control()
    D2C.loadXML(sys.argv[1])
    D2C.printConnections()
    D2C.buildControlET(sys.argv[2])
