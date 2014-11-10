#! /usr/bin/env python

import xml.etree.ElementTree as ET
import os

from objects.Link import Link
from utils.utils import prettify

class StructureBuilder(object):
    def __init__(self):
        self.component_dict = {} # {component_id: ET_element}
        self.link_dict = {} # {link_id: link_object}

    def addComponent(self, component_id, conf_file_path):
        if component_id in self.component_dict:
            raise ValueError("Component {!r} already exists!".format(component_id))
        else:
            if os.path.isfile(conf_file_path):
                component = ET.Element("Component")
                c_id = ET.SubElement(component, "component_id")
                c_id.text = component_id
                c_path = ET.SubElement(component, "file_path")
                c_path.text = conf_file_path
                self.component_dict[component_id] = component
            else:
                raise IOError("Conf file {!r} does not exist.".format(conf_file_path))

    def addLink(self, link_id, component1_id, component2_id,
                               component1_module, component2_module,
                               component1_node, component2_node,
                               distance, angle):

        if link_id in self.link_dict:
            raise ValueError("Link {!r} already exists!")
        if component1_id not in self.component_dict:
            raise ValueError("Component {!r} is not defined yet.".format(component1_id))
        if component2_id not in self.component_dict:
            raise ValueError("Component {!r} is not defined yet.".format(component2_id))

        for l_id, link_obj in self.link_dict.iteritems():
            for i in xrange(1,3):
                if link_obj.getComponentID(i) == component1_id:
                    if link_obj.getModuleName(i) == component1_module:
                        if link_obj.getNodeName(i) == str(component1_node):
                            raise ValueError(\
                                    "Node {!r} of module {!r} in component {!r} is already occupied."\
                                    .format(str(component1_node), component1_module, component1_id))
                if link_obj.getComponentID(i) == component1_id:
                    if link_obj.getModuleName(i) == component1_module:
                        if link_obj.getNodeName(i) == str(component1_node):
                            raise ValueError(\
                                    "Node {!r} of module {!r} in component {!r} is already occupied."\
                                    .format(str(component2_node), component2_module, component2_id))

        component1_info = {"ET_element": self.component_dict[component1_id],
                           "module_name": component1_module,
                           "node": str(component1_node)}
        component2_info = {"ET_element": self.component_dict[component2_id],
                           "module_name": component2_module,
                           "node": str(component2_node)}
        other_info = {"distance": str(distance), "angle": str(angle)}

        link = Link()
        link.link_id = str(link_id)
        link.link_info = {"component1_info": component1_info,
                          "component2_info": component2_info,
                          "other_info": other_info}

        self.link_dict[link_id] = link


    def build(self, file_path):
        root = ET.Element("Structure")
        components = ET.SubElement(root, "Components")
        links = ET.SubElement(root, "Links")

        for component_id, component in self.component_dict.iteritems():
            components.append(component)
        for link_id, link in self.link_dict.iteritems():
            links.append(link.toET())

        with open(file_path, "w") as f:
            f.write(prettify(root))

if __name__ == "__main__":
    SB = StructureBuilder()

    leg_conf_file = "/home/asl/SMORES/gaits_and_configs/simple/leg.conf"
    body_conf_file = "/home/asl/SMORES/gaits_and_configs/simple/body.conf"

    SB.addComponent("body", body_conf_file)
    SB.addComponent("frontLeftLeg", leg_conf_file)
    SB.addComponent("frontRightLeg", leg_conf_file)
    SB.addComponent("backLeftLeg", leg_conf_file)
    SB.addComponent("backRightLeg", leg_conf_file)


    SB.addLink("body2fl", "body", "frontLeftLeg", "Module_0", "Module_0", 1, 0, 0, 0)
    SB.addLink("body2fr", "body", "frontRightLeg", "Module_0", "Module_0", 2, 0, 0, 0)
    SB.addLink("body2bl", "body", "backLeftLeg", "Module_2", "Module_0", 1, 0, 0, 0)
    SB.addLink("body2br", "body", "backRightLeg", "Module_2", "Module_0", 2, 0, 0, 0)


    SB.build("/home/asl/SMORES/designer/data_files/walkbot/walkbot.struct")
