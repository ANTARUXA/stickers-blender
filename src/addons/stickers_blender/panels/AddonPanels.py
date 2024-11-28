"""
[Blender and Python] Panels used to control the Stickers Antaruxa
Juan R Nouche - October 2024
Email: juan.nouche@antaruxa.com
A Blender python functions library to create create and organize 
the stiker shadernodes
Antaruxa Stickers - Blender python panels to control the stickers
Copyright (c) 2024 Antaruxa
--------
"""

import bpy

from stickers_blender.addons.stickers_blender.config import __addon_name__
from stickers_blender.addons.stickers_blender.operators.AddonOperators import AddNewSticker
from stickers_blender.addons.stickers_blender.operators.AddonOperators import RemoveSticker
from stickers_blender.common.i18n.i18n import i18n


class StickerObjectPanel(bpy.types.Panel):
    """Panel Class in 3d-view to create and remove sticker
    """    
    
    bl_idname = 'VIEW3D_PT_sticker_panel'
    bl_label = 'Sticker Utils'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Stickers'
    

    
    def draw(self, context: bpy.types.Context):

        addon_prefs = context.preferences.addons[__addon_name__].preferences

        layout = self.layout
       
    
        row = layout.row()
        row.label(text="You should put a name and select a png image or sequence")
        
        row = layout.row()
        stick = layout.prop(addon_prefs, "sticker_name")
        
        row = layout.row()
        layout.prop(addon_prefs, "img_filename")
        
        row = layout.row(align = True)
        layout.prop(addon_prefs, "is_image_sequence")
        layout.prop(addon_prefs, "is_anim_select")

        row = layout.row(align = True)
        row.operator(AddNewSticker.bl_idname, text=AddNewSticker.bl_label)
        row.operator(RemoveSticker.bl_idname, text=RemoveSticker.bl_label)
        
    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True


class StickerMaterialPanel(bpy.types.Panel):
    
    bl_label = "Stickers"
    bl_idname = "ADDON_PT_Panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Stickers"
    
    
    @classmethod
    def poll(self, context):
        return context.area.ui_type == "ShaderNodeTree"    

    def draw(self,context):

        addon_prefs = context.preferences.addons[__addon_name__].preferences

        layout = self.layout
        
        layout = self.layout
       
    
        row = layout.row()
        row.label(text="Put the name of sticker and move up and down")
        
        row = layout.row()
        stick = layout.prop(addon_prefs, "sticker_name")

        row = layout.row(align = True)
        row.operator("opr.sticker_down", text="Move Down")
        row.operator("opr.sticker_up", text="Move Up")
                
        

