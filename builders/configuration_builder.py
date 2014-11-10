#! /usr/bin/env python

import xml.etree.ElementTree as ET
import os
import sys
from collections import OrderedDict
from ast import literal_eval
import numpy

from objects import Module, Connection, Link
from utils import kinematics
from utils.utils import prettify, string2Tuple, roundup

TOLERANCE = 0.001

class Component(object):
    """
    A base class for a structure or a configuration
    """
    def __init__(self):
        self.name = ""
        self.ET_tree = None
        self.file_path = ""

    def loadXML(self, file_path, file_cache_dict={}):
        """
        Load given XML file and parse to a ET tree object
        """
        self.name = os.path.splitext(os.path.split(file_path)[1])[0]

        if file_path not in file_cache_dict:
            self.ET_tree = ET.parse(file_path)
            file_cache_dict[file_path] = self.ET_tree
        else:
            self.ET_tree = file_cache_dict[file_path]

        self.file_path = file_path

class Configuration(Component):
    """
    A configuration class
    """
    def __init__(self, *args, **kwds):
        super(Configuration, self).__init__(*args, **kwds)

class Structure(Component):
    """
    A structure class
    """
    def __init__(self, *args, **kwds):
        super(Structure, self).__init__(*args, **kwds)
        self.component_dict = {} # {component_id: Configuration object}
        self.file_cache_dict = {} # {file_path: ET_tree}
        self.link_dict = OrderedDict() # {link_id: {component1_info: dict,
                                       #            component2_info: dict,
                                       #            other_info: dict}}
                                       # The order of the link matters,
                                       # as the configuration position
                                       # depends on the previous link.

    def loadComponents(self):
        """
        Load all components in the given structure
        """
        root = self.ET_tree.getroot()
        components = root.find("Components")
        for component in components:
            file_path = component.find("file_path").text
            component_id = component.find("component_id").text

            conf = Configuration()
            conf.loadXML(file_path, self.file_cache_dict)
            self.component_dict[component_id] = conf

    def loadLinks(self):
        """
        Load all links in the given structure
        """
        root = self.ET_tree.getroot()
        links = root.find("Links")
        for link in links:
            link_id = link.find("link_id").text

            link_obj = Link.Link()
            link_obj.loadLink(link)
            self.link_dict[link_id] = link_obj

    def printLinks(self):
        """
        Print all loaded links
        """
        print "There are {} links.".format(len(self.link_dict))
        for link_id, link_obj in self.link_dict.iteritems():
            print "{} is connected with {}.".format(link_obj.getModuleName(1), link_obj.getModuleName(2))
        print

    def printSummary(self):
        """
        Print all loaded components and links
        """
        print "There are {} components.".format(len(self.component_dict))
        print ",".join(self.component_dict.keys())
        print
        self.printLinks()

    def getCachedFile(self, file_path):
        """
        Get the cached ET tree of a given file
        """
        return self.file_cache_dict[file_path]

class ConfigurationBuilder(object):
    """
    A builder class that builds complex configuration from a given structure file
    """
    def __init__(self):
        self.struct = None
        self.module_dict = OrderedDict() # {component_id: [module1, module2, ...]}
        self.updated_module_dict = {} # after position transformation {component_id: [module1, module2, ...]}
        self.connection_dict = {} # {component_id: [connection1, connection2, ...]}

    def loadStructure(self, structure_file_path):
        """
        Load structure file to a structure object
        """
        print "Converting structure file {} ...".format(structure_file_path)
        self.struct = Structure()
        self.struct.loadXML(structure_file_path)
        self.struct.loadComponents()
        self.struct.loadLinks()

    def buildNewConfiguration(self):
        """
        Build the final configuration
        """
        for link_id, link_obj in self.struct.link_dict.iteritems():
            # find the configuration file cache
            component1_file_path = link_obj.getComponentFilePath(1)
            ET_tree_c1 = self.struct.getCachedFile(component1_file_path)
            component1_id = link_obj.getComponentID(1)
            # load modules and connections
            if component1_id not in self.updated_module_dict:
                module_list_c1 = self.getModuleList(ET_tree_c1, component1_id)
                connection_list_c1 = self.getConnectionList(ET_tree_c1, component1_id)

                self.module_dict[component1_id] = module_list_c1
                self.updated_module_dict[component1_id] = module_list_c1
                self.connection_dict[component1_id] = connection_list_c1

            # find the configuration file cache
            component2_file_path = link_obj.getComponentFilePath(2)
            ET_tree_c2 = self.struct.getCachedFile(component2_file_path)
            component2_id = link_obj.getComponentID(2)
            # load modules and connections
            if component2_id not in self.updated_module_dict:
                module_list_c2 = self.getModuleList(ET_tree_c2, component2_id)
                connection_list_c2 = self.getConnectionList(ET_tree_c2, component2_id)

                self.module_dict[component2_id] = module_list_c2

                update_connection_list = [link_obj.toConnection()] + connection_list_c2

                self.updateModulePosition(update_connection_list)
                self.connection_dict[component2_id] = update_connection_list
            else:
                raise ValueError("Component {!r} has already been updated.".format(component2_id))

    def rebuildConfiguration(self):
        """
        Rebuild the configuration not from a stucture file
        """
        self.updated_module_dict = {}

        for link_id, link_obj in self.struct.link_dict.iteritems():
            # find the configuration file cache
            component1_id = link_obj.getComponentID(1)
            # load modules and connections
            if component1_id not in self.updated_module_dict:
                module_list_c1 = self.module_dict[component1_id]
                self.updated_module_dict[component1_id] = module_list_c1

            # find the configuration file cache
            component2_id = link_obj.getComponentID(2)
            # load modules and connections
            if component2_id not in self.updated_module_dict:
                module_list_c2 = self.module_dict[component2_id]
                connection_list_c2 = self.connection_dict[component2_id]

                self.updateModulePosition(connection_list_c2)
            else:
                raise ValueError("Component {!r} has already been rebuilt.".format(component2_id))

    def updateModulePosition(self, connection_list):
        """
        Transform the position of some SMORES robots based on the links between configurations
        """
        #TODO: Deal with situation where the connection module is in the middle of the connection chain
        for connection in connection_list:
            (parent_module_name, child_module_name) = self.findParentModule(connection.Module1, connection.Module2)
            parent_module_obj = self.findModuleObject(parent_module_name)
            child_module_obj = self.findModuleObject(child_module_name)
            if parent_module_name == connection.Module1:
                node1 = connection.Node1
                node2 = connection.Node2
            else:
                node1 = connection.Node2
                node2 = connection.Node1

            (module_position, rotation_matrix, quaternion) = \
                    kinematics.get_new_position(parent_module_obj, child_module_obj.JointAngle, \
                                                int(node1), int(node2))

            child_module_obj.Position = tuple(module_position[0:3]) + quaternion
            child_module_obj.rotation_matrix = rotation_matrix

            component_id = child_module_name.split(":")[0]
            self.checkCollision(child_module_obj)
            if component_id not in self.updated_module_dict:
                self.updated_module_dict[component_id] = [child_module_obj]
            else:
                self.updated_module_dict[component_id].append(child_module_obj)

    def checkCollision(self, module_obj):
        """
        Check if there is any self-collision between the given module and the list of exist modules
        """
        #TODO: Find better way that finding distance between two module to check collision
        module1_pos = numpy.array(module_obj.Position[:3])
        for component_id, module_obj_list in self.updated_module_dict.iteritems():
            for m in module_obj_list:
                module2_pos = numpy.array(m.Position[:3])
                if numpy.linalg.norm(module1_pos - module2_pos) - 0.1 < -TOLERANCE:
                    raise ValueError("There is a self-collision between {} and {}.".format(module_obj.ModelName, m.ModelName))

    def findParentModule(self, module1_name, module2_name):
        """
        Find the SMORES robot whose position is already updated
        """
        parent_module = ""
        child_module = ""

        component1_id = module1_name.split(":")[0]
        component2_id = module2_name.split(":")[0]

        check1 = False
        check2 = False
        for component_id, module_obj_list in self.updated_module_dict.iteritems():
            if component_id == component1_id:
                check1 = True
                if module1_name in [x.ModelName for x in module_obj_list]:
                    if parent_module == "":
                        parent_module = module1_name
                    else:
                        raise ValueError("Both modules {!r} and {!r} have been updated.".format(module1_name, module2_name))

            if component_id == component2_id:
                check2 = True
                if module2_name in [x.ModelName for x in module_obj_list]:
                    if parent_module == "":
                        parent_module = module2_name
                    else:
                        raise ValueError("Both modules {!r} and {!r} have been updated.".format(module1_name, module2_name))

            if check1 and check2:
                break

        if parent_module == module1_name:
            child_module = module2_name
        elif parent_module == module2_name:
            child_module = module1_name
        else:
            # randomly assign
            parent_module = module1_name
            child_module = module2_name

        return (parent_module, child_module)

    def saveNewConfiguration(self, file_name):
        """
        Save the final configuration
        """
        configuration = ET.Element("configuration")
        modules = ET.SubElement(configuration, "modules")
        connections = ET.SubElement(configuration, "connections")

        for component_id, module_list in self.module_dict.iteritems():
            for module_obj in module_list:
                module = self.moduleObject2ET(module_obj)
                modules.append(module)

            for connection_obj in self.connection_dict[component_id]:
                connection = self.connectionObject2ET(connection_obj)
                connections.append(connection)

        with open(file_name, "w") as f:
            f.write(self.replaceAllModuleName(prettify(configuration)))

    def replaceAllModuleName(self, xml_string):
        """
        Rename all SMORES robots with name "Module_Num" where "Num" starts from 0
        """
        counter = 0
        for component_id, module_list in self.module_dict.iteritems():
            for module_obj in module_list:
                new_name = "Module_{}".format(counter)
                xml_string = xml_string.replace(module_obj.ModelName, new_name)
                counter += 1
        return xml_string

    def connectionObject2ET(self, connection_obj):
        """
        Convert a connection object to an ET element object
        """

        connection = ET.Element("connection")

        module1 = ET.SubElement(connection, "module1")
        module1.text = connection_obj.Module1
        module2 = ET.SubElement(connection, "module2")
        module2.text = connection_obj.Module2

        node1 = ET.SubElement(connection, "node1")
        node1.text = str(connection_obj.Node1)
        node2 = ET.SubElement(connection, "node2")
        node2.text = str(connection_obj.Node2)

        distance = ET.SubElement(connection, "distance")
        distance.text = str(connection_obj.Distance)
        angle = ET.SubElement(connection, "angle")
        angle.text = str(connection_obj.Angle)

        return connection

    def moduleObject2ET(self, module_obj):
        """
        Convert a module object to an ET element object
        """
        module = ET.Element("module")
        name = ET.SubElement(module, "name")
        name.text = module_obj.ModelName
        position = ET.SubElement(module, "position")
        position.text = " ".join([str(roundup(x)) for x in module_obj.Position])
        joints = ET.SubElement(module, "joints")
        joints.text = " ".join([str(roundup(x)) for x in module_obj.JointAngle])
        path = ET.SubElement(module, "path")
        path.text = module_obj.Path

        return module

    def findModuleObject(self, module_name):
        """
        Find a module object from a with a given name
        """
        component_id = module_name.split(":")[0]
        for module_obj in self.module_dict[component_id]:
            if module_obj.ModelName == module_name:
                return module_obj
        raise ValueError("Cannot find module with name {!r}".format(module_name))

    def getModuleList(self, ET_tree, component_id):
        """
        Get a list of modules from the given ET_tree
        """
        module_list = []

        # load configuration information
        configuration = ET_tree.getroot()
        modules = configuration.find("modules")
        for module in modules.findall("module") :
            module_name = "{}:{}".format(component_id, module.find('name').text)
            position_str = module.find('position').text
            module_position = string2Tuple(position_str)
            joint_angle_str = module.find('joints').text
            module_joint_angle = string2Tuple(joint_angle_str)
            module_file_path = module.find('path').text

            if len(module_position) == 6:
                new_module = Module.Module(module_name, module_position, module_joint_angle, module_file_path)
                new_module.rotation_matrix = kinematics.rotz(module_position[5])* \
                                             kinematics.roty(module_position[4])* \
                                             kinematics.rotx(module_position[3])
            elif len(module_position) == 7:
                new_module = Module.Module(module_name, module_position, module_joint_angle ,module_file_path, True)
                new_module.rotation_matrix = kinematics.quatToRot(module_position[3:])

            module_list.append(new_module)
        return module_list

    def getConnectionList(self, ET_tree, component_id):
        """
        Get a list of connections from the given ET_tree
        """
        connection_list = []

        # load connection information
        configuration = ET_tree.getroot()
        connections = configuration.find("connections")
        for connection in connections.findall('connection') :
            module1_name = "{}:{}".format(component_id, connection.find('module1').text)
            module2_name = "{}:{}".format(component_id, connection.find('module2').text)
            new_connection = Connection.Connection(module1_name, module2_name,
                                        int(connection.find('node1').text), int(connection.find('node2').text),
                                        float(connection.find('distance').text), float(connection.find('angle').text))
            connection_list.append(new_connection)

        return connection_list


if __name__ == "__main__":
    CB = ConfigurationBuilder()
    CB.loadStructure(sys.argv[1])
    CB.struct.printSummary()
    CB.buildNewConfiguration()
    print "Saving new configuration to {}.".format(sys.argv[2])
    CB.saveNewConfiguration(sys.argv[2])
