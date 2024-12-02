"""
[Blender and Python] Property getter-setter library for Stickers Antaruxa
Juan R Nouche - October 2024
Email: juan.nouche@antaruxa.com
A Blender python functions library to create create and organize 
the stiker shadernodes
Antaruxa Stickers - Blender python property getter-setter library
Copyright (c) 2024 Antaruxa
--------
"""


import bpy

'''Getter sticker_name only getter (read only)
'''
def get_sticker_name(self):
    return self["sticker_name"]

# used for plane deactivated in this version
# '''Getter-Setter hide_plane Boolean
# '''
# def get_hide_plane(self):
#     return self["hide_plane"]
# def set_hide_plane(self,value):
#     self["hide_plane"]=value
#     obj = self.id_data
#     if "_base_node" in obj.name:
#         for child in obj.children:
#             if "_plane" in child.name:
#                 child.hide_viewport = value
#                 child.hide_render = value

'''Getter-Setter flip_X Boolean
'''
def get_flip_X(self):
    return self["flip_X"]
def set_flip_X(self,value):
    self["flip_X"]=value
    obj = self.id_data
    if "_base_node" in obj.name:
        sticker_name = obj.sticker_name
        anchor = obj.parent
        main_obj = anchor.parent
        main_material = main_obj.active_material
        for child in obj.children:
            if "_plane" in child.name:
                child.scale[0]=-child.scale[0]
        actualvalue = main_material.node_tree.nodes[f"{sticker_name}_mapping"].inputs[3].default_value[0]
        main_material.node_tree.nodes[f"{sticker_name}_mapping"].inputs[3].default_value[0] = -actualvalue

'''Getter-Setter flip_Y Boolean
'''
def get_flip_Y(self):
    return self["flip_Y"]
def set_flip_Y(self,value):
    self["flip_Y"]=value
    obj = self.id_data
    if "_base_node" in obj.name:
        sticker_name = obj.sticker_name
        anchor = obj.parent
        main_obj = anchor.parent
        main_material = main_obj.active_material
        for child in obj.children:
            if "_plane" in child.name:
                child.scale[1]=-child.scale[1]
        actualvalue = main_material.node_tree.nodes[f"{sticker_name}_mapping"].inputs[3].default_value[1]
        main_material.node_tree.nodes[f"{sticker_name}_mapping"].inputs[3].default_value[1] = -actualvalue

'''Getter frame_count only getter (read only)
'''
def get_frame_count(self):
    return self["frame_count"]

'''Getter initial_frame only getter (read only)
'''
def get_initial_frame(self):
    return self["initial_frame"]


'''Getter-Setter active_frame int
'''
def get_active_frame(self):
    return self["active_frame"]

def set_active_frame(self,value):
    obj = self.id_data
    max = obj.frame_count 
    if 1 <= value <= max: 
        self["active_frame"]=value


'''Getter-Setter transparency float
'''
def get_transparency(self):
    return self["transparency"]

def set_transparency(self,value):
    #obj = self.id_data
    max = 1.0
    if 0 <= value <= max: 
        self["transparency"]=value


      
def obj_has_property(btype, propname):
    """Check if an Object has a property (API defined)
    btype    -- bpy.types.Object
    propname -- name of the property
    return:
    True if the property exists
    """    
    for prop in btype.bl_rna.properties:
        if prop.identifier == propname:
            return True
    return False



