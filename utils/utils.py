import xml.etree.ElementTree as ET
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def string2Tuple(input_string):
    """return a tuple from the input_string `x1 x2 ...`
    """
    list_from_string = [float(x) for x in input_string.split()]
    return tuple(list_from_string)

TOLERENCE = 10**-5
def roundup(input_num):
    if abs(input_num) < TOLERENCE:
        return 0.0
    else:
        return input_num
