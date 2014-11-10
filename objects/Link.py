import xml.etree.ElementTree as ET
import Connection

class Link(object):
    def __init__(self):
        self.link_id = ""
        self.link_info = {}

    def loadLink(self, link):
        """
        link - ET_element
        """
        component1_info = {"ET_element":link.find("component1").find("Component"),
                           "module_name":link.find("module1").text,
                           "node":link.find("node1").text}
        component2_info = {"ET_element":link.find("component2").find("Component"),
                           "module_name":link.find("module2").text,
                           "node":link.find("node2").text}
        other_info = {"distance":link.find("distance").text, "angle":link.find("angle").text}

        self.link_id = link.find("link_id").text
        self.link_info = {"component1_info": component1_info,
                          "component2_info": component2_info,
                          "other_info": other_info}

    def getLinkID(self):
        return self.link_id

    def getModuleName(self, component):
        """
        component - 1 or 2
        """
        key = "component{}_info".format(component)
        return self.link_info[key]["module_name"]

    def getNodeName(self, component):
        """
        component - 1 or 2
        """
        key = "component{}_info".format(component)
        return self.link_info[key]["node"]

    def getComponentFilePath(self, component):
        """
        component - 1 or 2
        """
        key = "component{}_info".format(component)
        return self.link_info[key]["ET_element"].find("file_path").text

    def getComponentID(self, component):
        """
        component - 1 or 2
        """
        key = "component{}_info".format(component)
        return self.link_info[key]["ET_element"].find("component_id").text

    def getDistance(self):
        return self.link_info["other_info"]["distance"]

    def getAngle(self):
        return self.link_info["other_info"]["angle"]

    def toConnection(self):
        module1_name = "{}:{}".format(self.getComponentID(1), self.getModuleName(1))
        node1_id = self.getNodeName(1)
        module2_name = "{}:{}".format(self.getComponentID(2), self.getModuleName(2))
        node2_id = self.getNodeName(2)

        distance = self.getDistance()
        angle = self.getAngle()
        return Connection.Connection(module1_name, module2_name, node1_id, node2_id, distance, angle)

    def toET(self):

        link = ET.Element("Link")
        link_id = ET.SubElement(link, "link_id")
        link_id.text = self.link_id

        component1 = ET.SubElement(link, "component1")
        component1.append(self.link_info["component1_info"]["ET_element"])
        component2 = ET.SubElement(link, "component2")
        component2.append(self.link_info["component2_info"]["ET_element"])

        module1 = ET.SubElement(link, "module1")
        module1.text = self.getModuleName(1)
        module2 = ET.SubElement(link, "module2")
        module2.text = self.getModuleName(2)

        node1 = ET.SubElement(link, "node1")
        node1.text = self.getNodeName(1)
        node2 = ET.SubElement(link, "node2")
        node2.text = self.getNodeName(2)

        distance = ET.SubElement(link, "distance")
        distance.text = self.getDistance()
        angle = ET.SubElement(link, "angle")
        angle.text = self.getAngle()

        return link
