#! /usr/bin/env python

import xml.etree.ElementTree as ET
import os
import sys
import re
from collections import OrderedDict

from tableMaker.TableMaker import series, parallel
from tableMaker.CommandBlock import CommandBlock

SIM_TIME = 100

class GaitBuilder(object):
    """
    A builder that makes complex gait tables from a .control file
    """
    def __init__(self):
        self.GFL = GaitFileLoader()
        self.CB = CommandBlock()
        self.output_str = ""

    def loadControl(self, control_file_path):
        """
        Load .control file and make a gait file
        """
        ET_tree = ET.parse(control_file_path)
        root = ET_tree.getroot()
        block = root.find("Block")

        final_relative_block = self.processBlock(block)
        self.CB.stitch(final_relative_block)
        self.output_str = self.CB.make_table()

    def saveNewGait(self, file_name):
        """
        Save the gait file
        """
        with open(file_name, "w") as f:
            f.write(self.output_str)

    def processBlock(self, block):
        """
        Utilize table maker to build gait structure
        """
        if block.get("type") == "gait":
            gait = self.GFL.loadGaitFile(block.find("gait_file").text)
            return gait.toRelativeBlock(block.find("component_id").text)
        elif block.get("type") == "p_block":
            print "Converting a parallel block."
            return parallel(map(self.processBlock, list(block)))
        elif block.get("type") == "s_block":
            print "Converting a series block."
            return series(map(self.processBlock, list(block)))

class GaitCollisionChecker(object):
    """
    Class to check collision of modules when executing a gait
    """
    def __init__(self):
        self.GFL = GaitFileLoader()
        self.gait = None

    def loadGait(self, gait_data):
        gait = self.GFL.loadGaitData(gait_data)
        self.gait = gait
        return gait

    def runGait(self, CB_instance):
        processed_commands = set()
        current_commands = set(self.gait.command_dict_key_condition["START"])

        while len(current_commands) > 0:
            self.executeCommand(current_commands, CB_instance)

            processed_commands = processed_commands.union(current_commands)
            temp_set = set()
            for cmd in current_commands:
                set1 = set(self.gait.command_dict_key_label[cmd.label])
                if set1.issubset(processed_commands):
                    if cmd.label == "END":
                        set2 = set()
                    else:
                        set2 = set(self.gait.command_dict_key_condition[cmd.label])
                    temp_set = temp_set.union(set2)

            current_commands = temp_set

    def executeCommand(self, commands, CB_instance):
        command_dict = {} # {module_name: command_list_per_iter}
        for cmd in commands:
            cmd_str = cmd.cmd_str
            cmd_list  = map(float, cmd_str.replace("p","").split(" "))
            module_obj = CB_instance.findModuleObject(cmd.module_name)
            command_dict[cmd.module_name] = [(y-x)/SIM_TIME for x,y in zip(module_obj.JointAngle, cmd_list)]

        for t in xrange(SIM_TIME):
            for cmd in commands:
                module_obj = CB_instance.findModuleObject(cmd.module_name)
                cmd_list_per_iter = command_dict[cmd.module_name]
                module_obj.JointAngle = tuple([x+y for x,y in zip(module_obj.JointAngle, cmd_list_per_iter)])
        try:
            CB_instance.rebuildConfiguration()
        except ValueError as e:
            print
            print e
            print "at command {0.cmd_str} for module {0.module_name}.".format(cmd)


class GaitFileLoader(object):
    """
    Loader for gait file
    """
    def __init__(self):
        self.file_cache_dict = {} # {file_path: Gait_obj}
        self.RE_line_parser = re.compile("^(?P<m_name>[:\w]+)\s(?P<position>(p[0-9\.-]+\s){4})({(?P<label>[-\w]+)}\s)?(\((?P<condition>[-\w]+)\)\s)?;")

    def loadGaitFile(self, gait_file_name):
        """
        Load gait file to gait object
        """
        if gait_file_name not in self.file_cache_dict:

            with open(gait_file_name, "r") as f:
                gait = self.loadGaitData(f.readlines())

            self.file_cache_dict[gait_file_name] = gait
        else:
            gait = self.file_cache_dict[gait_file_name]

        return gait

    def loadGaitData(self, gait_data):
        """
        Load gait data to gait object
        """
        gait = Gait()

        for line in gait_data:
            if len(line) == 0:
                continue
            m = self.RE_line_parser.match(line)
            if m:
                if m.group("label") not in gait.command_dict_key_label:
                    gait.command_dict_key_label[m.group("label")] = []
                if m.group("condition") not in gait.command_dict_key_condition:
                    gait.command_dict_key_condition[m.group("condition")] = []

                module_name = m.group("m_name")
                cmd_str = m.group("position").strip()
                cmd_obj = Command(module_name, cmd_str, m.group("label"), m.group("condition"))
                gait.command_dict_key_label[m.group("label")].append(cmd_obj)
                gait.command_dict_key_condition[m.group("condition")].append(cmd_obj)
            else:
                raise IOError("Cannot parse gait file line \n{}".format(line))

        return gait


class Gait(object):
    """
    Gait object
    """
    def __init__(self):
        self.command_dict_key_label = OrderedDict() # {label: [Command_obj, ...]}
        self.command_dict_key_condition = OrderedDict() # {condition: [Command_obj, ...]}

    def toRelativeBlock(self, component_id = ""):
        series_list = []
        for label, cmd_obj_list in self.command_dict_key_label.iteritems():
           series_list.append(parallel([cmd_obj.toString(component_id) for cmd_obj in cmd_obj_list]))

        return series(series_list)


class Command(object):
    """
    Command object
    """
    def __init__(self, module_name, cmd_str, label="", condition=""):
        self.module_name = module_name
        self.cmd_str = cmd_str
        self.label = label
        self.condition = condition

    def toString(self, component_id):
        if component_id != "":
            name = "{}:{}".format(component_id, self.module_name)
        else:
            name = self.module_name
        return name + " " + self.cmd_str


if __name__ == "__main__":
    GB = GaitBuilder()
    GB.loadControl(sys.argv[1])
