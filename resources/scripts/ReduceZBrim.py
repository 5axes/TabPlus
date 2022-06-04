#------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessing Script
# Author:   5axes
# Date:     June 04, 2022
#
# Description:  ReduceZBrim
#
#------------------------------------------------------------------------------------------------------------------------------------
#
#   Version 1.0 04/06/2022 first prototype 
#
#------------------------------------------------------------------------------------------------------------------------------------

from ..Script import Script
from UM.Logger import Logger
from UM.Application import Application
import re #To perform the search
from enum import Enum
from collections import namedtuple
from typing import List, Tuple

__version__ = '1.0'

Point2D = namedtuple('Point2D', 'x y')

class Section(Enum):
    """Enum for section type."""

    NOTHING = 0
    SKIRT = 1
    BRIM = 2
    INNER_WALL = 3
    OUTER_WALL = 4
    INFILL = 5
    SKIN = 6
    SKIN2 = 7

def is_begin_layer_line(line: str) -> bool:
    """Check if current line is the start of a layer section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a layer section
    """
    return line.startswith(";LAYER:")

def is_begin_skirt_line(line: str) -> bool:
    """Check if current line is the start of a SKIRT section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a SKIRT section
    """
    return line.startswith(";TYPE:SKIRT")

def is_begin_type_line(line: str) -> bool:
    """Check if current line is the start of a type section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a type section
    """
    return line.startswith(";TYPE")

def is_begin_mesh_line(line: str) -> bool:
    """Check if current line is the start of a new MESH.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a new MESH
    """
    return line.startswith(";MESH:")

    
def is_z_line(line: str) -> bool:
    """Check if current line is a Z line

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a Z line segment
    """
    return "G0" in line and "Z" in line and not "E" in line

def is_z_G1_line(line: str) -> bool:
    """Check if current line is a G1 Z line

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a Z line segment
    """
    return "G1" in line and "Z" in line and not "E" in line
    
def is_e_line(line: str) -> bool:
    """Check if current line is a an Extruder line

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is an Extruder line segment
    """
    return "G1" in line  and "E" in line

def is_relative_extrusion_line(line: str) -> bool:
    """Check if current line is a relative extrusion line

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a relative extrusion line
    """
    return "M83" in line  

def is_absolute_extrusion_line(line: str) -> bool:
    """Check if current line is an absolute extrusion line

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is an absolute  extrusion line
    """
    return "M82" in line  
    
def is_only_extrusion_line(line: str) -> bool:
    """Check if current line is a pure extrusion command.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a pure extrusion command
    """
    return "G1" in line and not "X" in line and not "Y" in line and "E" in line
    
def getXY(currentLine: str) -> Point2D:
    """Create a ``Point2D`` object from a gcode line.

    Args:
        currentLine (str): gcode line

    Raises:
        SyntaxError: when the regular expressions cannot find the relevant coordinates in the gcode

    Returns:
        Point2D: the parsed coordinates
    """
    searchX = re.search(r"X(\d*\.?\d*)", currentLine)
    searchY = re.search(r"Y(\d*\.?\d*)", currentLine)
    if searchX and searchY:
        elementX = searchX.group(1)
        elementY = searchY.group(1)
    else:
        raise SyntaxError('Gcode file parsing error for line {currentLine}')

    return Point2D(float(elementX), float(elementY))
    
class ReduceZBrim(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "ReduceZBrim",
            "key": "ReduceZBrim",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "reduce":
                {
                    "label": "Skirt height reduction",
                    "description": "Skirt height reduction.",
                    "type": "float",
                    "unit": "mm",
                    "default_value": 0.08,
                    "minimum_value": 0.06,
                    "maximum_value_warning": 0.2,
                    "maximum_value": 0.3
                },
                "extruder_nb":
                {
                    "label": "Extruder Id",
                    "description": "Define extruder Id in case of multi extruders",
                    "unit": "",
                    "type": "int",
                    "default_value": 1
                },
                "lcdfeedback":
                {
                    "label": "Display details on LCD",
                    "description": "This setting will insert M117 gcode instructions, to display current modification in the G-Code is being used.",
                    "type": "bool",
                    "default_value": true
                }                  
            }
        }"""

    def execute(self, data):

        BrimReduce = float(self.getSettingValueByKey("reduce"))   
        Logger.log('d', 'BrimReduce : {}'.format(BrimReduce))            
        extruder_id  = self.getSettingValueByKey("extruder_nb")
        extruder_id = extruder_id -1
        UseLcd = self.getSettingValueByKey("lcdfeedback")
        
        
        idl=0
        currentlayer=0
        Zhop=False 

        # Deprecation function
        # extrud = list(Application.getInstance().getGlobalContainerStack().extruders.values())
        extrud = Application.getInstance().getGlobalContainerStack().extruderList
 
        layer_height_0 = extrud[extruder_id].getProperty("layer_height_0", "value")
        Logger.log('d', 'layer_height_0 : {}'.format(layer_height_0))
        NewZ = "Z{:.2f}".format(float(BrimReduce)) 
        
        layer_reduction = int((BrimReduce/layer_height_0)*100)
        Logger.log('d', 'layer_reduction : {}'.format(layer_reduction))


        #   machine_extruder_count
        extruder_count=Application.getInstance().getGlobalContainerStack().getProperty("machine_extruder_count", "value")
        extruder_count = extruder_count-1
        if extruder_id>extruder_count :
            extruder_id=extruder_count

            
        for layer in data:
            layer_index = data.index(layer)
            
            lines = layer.split("\n")
            for line in lines:
                    
                if line.startswith(";LAYER_COUNT:"):
                    # Logger.log("w", "found LAYER_COUNT %s", line[13:])
                    layercount=int(line[13:])                    
               
                # startswith ";LAYER"
                if is_begin_layer_line(line):
                    line_index = lines.index(line)    
                    # Logger.log('d', 'layer_lines : {}'.format(line))
                    currentlayer=int(line[7:])
                    # Logger.log('d', 'currentlayer : {:d}'.format(currentlayer))
                    if line.startswith(";LAYER:0"):
                        idl=1

                if idl == 2 and is_begin_type_line(line):
                    idl = 0
                    line_index = lines.index(line)   
                    lcd_gcode = "M117 End Reduce Z Brim Z{:.3f}".format(float(layer_height_0)) 
                    lines.insert(line_index , ";END_OF_MODIFICATION")
                    if UseLcd == True :               
                        lines.insert(line_index, lcd_gcode) 
                    lines.insert(line_index , "M221 S100")
                    if Zhop == False :
                        lines.insert(line_index , "G0 Z"+str(layer_height_0))
                    
                #---------------------------------------------------
                # Init modification of the BRIM extruding path
                #---------------------------------------------------
                # G0 F6000 X106.445 Y116.579 Z0.2   -> StartLine
                # ;TYPE:SKIRT
                # G1 F3000 E0                       -> ZHopLine/ELine
                # G1 F1200 X106.693 Y116.356 E0.011 -> SpeedLine
                
                # or
                
                # G0 F6000 X51.318 Y121.726 Z0.4    -> StartLine
                # ;TYPE:SKIRT
                # G1 F300 Z0.2                      -> ZHopLine
                # G1 F3000 E0                       -> ELine
                # G1 F1080 X51.568 Y121.624 E0.0089 -> SpeedLine
                
                # Relative mode 
 
                # G0 F6000 X109.982 Y102.608 Z0.2
                # ;TYPE:SKIRT
                # G1 F3000 E5
                # G1 F1080 X110.147 Y102.432 E0.00795
                if idl == 1 and is_begin_skirt_line(line):
                    idl=2
                  
                    line_index = lines.index(line)                 
 
                    #----------------------------
                    #    Begin of modification
                    #----------------------------   
                    lines.insert(line_index + 1, ";BEGIN_OF_MODIFICATION")                  
                    lines.insert(line_index + 2, "G0 Z" + str(BrimReduce) )
                    lines.insert(line_index + 3, "M221 S" + str(layer_reduction) )
                    if UseLcd == True :
                        lcd_gcode = "M117 Reduce Z Brim M221 S{:d}".format(int(layer_reduction))                     
                        lines.insert(line_index + 4, lcd_gcode)  
                        
                if  ( is_z_line(line) or is_z_G1_line(line) ) and idl>1 :
                    # Logger.log('d', 'is_z_line : {}'.format(line))
                    searchZ = re.search(r"Z(\d*\.?\d*)", line)
                    if searchZ:
                        currentz=float(searchZ.group(1))
                        if currentz == layer_height_0:
                            Zhop=False                        
                            line_index = lines.index(line) 
                            ZToReplace = "Z" + str(currentz)
                            lines[line_index]=line.replace(ZToReplace, NewZ)
                            Logger.log('d', 'is_z_line to replace : {}'.format(line))
                        else:
                            if currentz > layer_height_0:
                                Zhop=True 
                                Logger.log('d', 'is_z_line Zhop : {}'.format(line))
                
                
            result = "\n".join(lines)
            data[layer_index] = result

        return data
