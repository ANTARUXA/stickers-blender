"""
[Blender and Python] Main configuration file for Stickers Antaruxa
Juan R Nouche - October 2024
Email: juan.nouche@antaruxa.com
A Blender python functions library to create create and organize 
the stiker shadernodes
Antaruxa Stickers - Blender python main configuration file
Copyright (c) 2024 Antaruxa
--------
"""


import os

import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import AddonPreferences

from stickers_blender.addons.stickers_blender.config import __addon_name__


class StickerPreferences(AddonPreferences):

    bl_idname = __addon_name__


    sticker_name: StringProperty(
        # NAME OF THE STICKER
        name="Sticker Name",
        default="sticker",
        description="String which contains the name of the sticker",
        maxlen=1024,
        )

    img_filename: StringProperty(
        # IMAGE FILENAME
        name="Image Filename",
        default="//",
        subtype='FILE_PATH',
        description="String which contains the name of the sticker",
        maxlen=1024,
        )
 
    is_image_sequence: BoolProperty(
        name="Is Image Sequence",
        description="Bool to select image seq import",
        default = False
        )

    is_anim_select: BoolProperty(
        name="Is Multi-Pose",
        description="Bool to select keyable sequence",
        default = False
    )



    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.label(text="Add-on Preferences View")
        layout.prop(self, "sticker_name")
        layout.prop(self, "img_filename")
        layout.prop(self, "is_image_sequence")
        layout.prop(self, "is_anim_select")

