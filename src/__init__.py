"""
[Blender and Python] Main add-on file for Stickers Antaruxa
Juan R Nouche - January 2025
Email: juan.nouche@antaruxa.com
A Blender python functions library to create create and organize 
the stiker shadernodes
Antaruxa Stickers - Blender python main add-on file
Copyright (c) 2025 Antaruxa
--------
"""

import bpy

from stickers_blender.addons.stickers_blender.config import __addon_name__
from stickers_blender.common.class_loader import auto_load
from stickers_blender.common.class_loader.auto_load import add_properties, remove_properties

from stickers_blender.common.version1_0_1.get_set_pops import (
    # used by plane deactivated in this version
    # get_hide_plane,   
    # set_hide_plane,   
    get_sticker_name,
    get_flip_X,   
    set_flip_X,   
    get_flip_Y,
    set_flip_Y,
    get_frame_count, 
    get_active_frame, 
    set_active_frame,
    get_initial_frame,
    get_transparency, 
    set_transparency,
      
)


bl_info = {
    "name": "Sticker Antaruxa",
    "author": "Juan R Nouche",
    "blender": (4, 2, 0),
    "version": (1, 0, 2),
    "description": "To manage stickers over any materials",
    "category": "3D View",
    # optional
    # "tracker_url": "[contact email]",
    # "doc_url": "[documentation url]",
    # "support": "COMMUNITY",
}

_addon_properties = {
    bpy.types.Object: {
        "sticker_name": bpy.props.StringProperty(get=get_sticker_name), 
        # used for plane deactivated in this version
        # "hide_plane": bpy.props.BoolProperty(options={'ANIMATABLE'}, get = get_hide_plane, set = set_hide_plane),
        "flip_X": bpy.props.BoolProperty(options={'ANIMATABLE'}, get = get_flip_X, set = set_flip_X),
        "flip_Y": bpy.props.BoolProperty(options={'ANIMATABLE'}, get= get_flip_Y, set = set_flip_Y),
        "frame_count": bpy.props.IntProperty(name="Number of frames", default = 1, get = get_frame_count),
        "active_frame": bpy.props.IntProperty(name="Active Frame", options={'ANIMATABLE'}, get = get_active_frame, set = set_active_frame),
        "initial_frame": bpy.props.IntProperty(name="Initial frames", default = 1, get = get_initial_frame),
        "transparency": bpy.props.FloatProperty(options={'ANIMATABLE'}, default = 1.0, get = get_transparency, set = set_transparency),
        "ScaleX": bpy.props.FloatProperty(options = {"ANIMATABLE"}, default = 1.0),
        "ScaleY": bpy.props.FloatProperty(options = {"ANIMATABLE"}, default = 1.0),
        "Rotate": bpy.props.IntProperty(options = {"ANIMATABLE"}, default = 1),
        
    }   
}


def register():

    # Register classes
    auto_load.init()
    auto_load.register()
    add_properties(_addon_properties)

    print("{} addon is installed.".format(bl_info["name"]))


def unregister():

    # unRegister classes
    auto_load.unregister()
    remove_properties(_addon_properties)

    print("{} addon is uninstalled.".format(bl_info["name"]))
