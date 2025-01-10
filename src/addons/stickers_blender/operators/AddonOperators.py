"""
[Blender and Python] Operators code for Stickers Antaruxa
Juan R Nouche - January 2024
Email: juan.nouche@antaruxa.com
A Blender python functions library to create create and organize 
the stiker shadernodes
Antaruxa Stickers - Blender python operators code
Copyright (c) 2024 Antaruxa
--------
"""


import os

import bpy
import bmesh
import mathutils
from mathutils import (Vector)


from stickers_blender.addons.stickers_blender.config import __addon_name__
from stickers_blender.addons.stickers_blender.preference.AddonPreferences import StickerPreferences

from stickers_blender.common.version1_0_1.sticker_class import (
    Sticker,
    NO_VERTEX_SELECTED,
    NO_MESH_SELECTED,
    NO_EDITMODE,
    MORE_THAN_1_VTX_SELECTED,
    MORE_THAN_1_OBJ_SELECTED,
    SEL_SHOULD_BE_A_MESH,
    ALL_DONE,
)

from stickers_blender.common.version1_0_1.sticker_funcs import (
    is_valid_image_extension,
    is_valid_image_imghdr,
    check_if_sticker_name_exists,
)
from stickers_blender.common.version1_0_1.material_funcs import (
    check_image_file_sequence,
    disconnect_sticker_material,
    remove_all_the_nodes_from_sticker, 
    check_if_is_the_downmost,
    check_if_is_the_topmost,
    interchange_sticker_connections_and_positions,
    get_all_shader_nodes_from_a_sticker,
    
)


class AddNewSticker(bpy.types.Operator):
    """Operator class to add a new sticker
    """    
    
    bl_idname = 'opr.sticker_add'
    bl_label = 'Add Sticker'
    bl_options = {'REGISTER','UNDO'}

    
    def __init__(self):
        self.sticker = Sticker('CREATE')
        if not self.sticker:
            self.report({'ERROR'}, "The selected object must be a mesh.")  
            return {'CANCELLED'}
    
    def execute(self, context):

        addon_prefs = bpy.context.preferences.addons[__addon_name__].preferences
        assert isinstance(addon_prefs, StickerPreferences)        
        
        stickername = addon_prefs.sticker_name 
        img_filename = bpy.path.abspath(addon_prefs.img_filename)
        is_seq = addon_prefs.is_image_sequence
        is_control_anim = addon_prefs.is_anim_select
        img_offset = None
        img_firstframe = None
        
    
        if  not os.path.exists(img_filename):
            self.report({'ERROR'}, f"The filename {img_filename} does not exist. Check the filename.")
            return{'CANCELLED'}

        if not is_valid_image_extension(img_filename):
            self.report({'ERROR'}, "Selected image must have this extension: .png.")
            return{'CANCELLED'}

        if not is_valid_image_imghdr(img_filename):
            self.report({'ERROR'}, "The selected file is not an image or is corrupted.")
            return{'CANCELLED'}
        
        if is_seq and is_control_anim:
            self.report({'ERROR'}, "You can't select only one of these: Image Sequence or Controlled Anim.")
            return{'CANCELLED'}
        
        if is_seq or is_control_anim:
            img_offset, img_firstframe, consecutive = check_image_file_sequence(img_filename)
            if not img_offset:
                self.report({'ERROR'}, "Can't detect an Image Sequence. Check the File Name.")
                return{'CANCELLED'}
            if not consecutive:
                self.report({'ERROR'}, "The images in the sequence must have consecutive numbers. Check image numbers.")
                return{'CANCELLED'}
                
            
        
        if check_if_sticker_name_exists(stickername):
            self.report({'ERROR'}, "There is a sticker with this name yet. Write other name")
            return{'CANCELLED'}            
        
        result=self.sticker.create_sticker(stickername, img_filename, is_seq, is_control_anim, img_offset, img_firstframe)
        
        if result == MORE_THAN_1_OBJ_SELECTED: 
            self.report({'ERROR'}, "More than one object selected, you need to select only one.")  
            return {'CANCELLED'}
        elif result == NO_MESH_SELECTED: 
            self.report({'ERROR'}, "No MESH selected, you need to select one, switch to edit mode and select only one vertex.")  
            return {'CANCELLED'}
        elif result == NO_EDITMODE:
            self.report({'ERROR'}, "You need to switch to Edit Mode and select one vertex.")  
            return {'CANCELLED'}
        elif result == NO_VERTEX_SELECTED:
            self.report({'ERROR'}, "Must select one vertex.")  
            return {'CANCELLED'}
        elif result == MORE_THAN_1_VTX_SELECTED:
            self.report({'ERROR'}, "Must select a vertex. Just one.")  
            return {'CANCELLED'}
        else:
            self.report({'INFO'}, "Now you have a new sticker. Congratulations!!!")         
            return {'FINISHED'}


class RemoveSticker(bpy.types.Operator):
    """Operator class to remove a sticker
    """    
    
    bl_idname = 'opr.sticker_remove'
    bl_label = 'Remove Sticker'
    bl_options = {'REGISTER','UNDO'}

   
    def execute(self, context):
        
        addon_prefs = bpy.context.preferences.addons[__addon_name__].preferences
        assert isinstance(addon_prefs, StickerPreferences)     


        stickername = addon_prefs.sticker_name 
       
 
        if not check_if_sticker_name_exists(stickername):
            self.report({'ERROR'}, "Can't find the sticker in scene. Check the sticker name.")
            return{'CANCELLED'}            

        sticker_objs = [
            f"{stickername}_base_node",
            f"{stickername}_normal_node",
            f"{stickername}_projection_node",        
            #for the plane deactivated in this version
            #f"{stickername}_aux_plane",
        ] 
        
        main_obj = bpy.data.objects[sticker_objs[0]].parent
        main_material = main_obj.active_material
        
        sticker_shader_nodes = [
            f"{stickername}_group",
            f"{stickername}_image",
            f"{stickername}_mapping",
            f"{stickername}_obj_coords",
            f"{stickername}_combine_XYZ",
            f"{stickername}_mix_node",
        ]

        objs = bpy.data.objects

        for obj_name in sticker_objs:
            objs.remove(objs[obj_name], do_unlink=True)
        
        disconnect_sticker_material(stickername, main_material)
        remove_all_the_nodes_from_sticker(stickername, main_material, sticker_shader_nodes, False)
        for node in main_material.node_tree.nodes:
            node.select = False
            
        bpy.ops.outliner.orphans_purge()        

        self.report({'INFO'}, f"The sticker {stickername} has been removed successfully !!!")         
        return {'FINISHED'}


class StickerMatSelect(bpy.types.Operator):
    """Operator class to select the sticker materials
    in the node_tree
    """    
    
    bl_idname = 'opr.sticker_mat_select'
    bl_label = 'Select'
    bl_options = {'REGISTER','UNDO'}

   
    def execute(self, context):
        
        addon_prefs = bpy.context.preferences.addons[__addon_name__].preferences
        assert isinstance(addon_prefs, StickerPreferences)

        stickername = addon_prefs.sticker_name 
        is_selected = addon_prefs.is_mat_selected
        
        
 
        if not check_if_sticker_name_exists(stickername):
            addon_prefs.is_mat_selected = False
            self.report({'ERROR'}, "Can't find the sticker in scene. Check the sticker name.")
            return{'CANCELLED'} 
                   

        sticker_objs = [
            f"{stickername}_base_node",
            f"{stickername}_normal_node",
            f"{stickername}_projection_node",
            #for the plane deactivated in this version
            #f"{stickername}_aux_plane",
        ] 
        
        main_obj = bpy.data.objects[sticker_objs[0]].parent
        main_obj.select_set(True)
        main_material = main_obj.active_material
        node_tree = main_material.node_tree
 
        for node in node_tree.nodes:
            node.select = False
         
        if is_selected:
            get_all_shader_nodes_from_a_sticker(node_tree, stickername, select = False)  
            addon_prefs.is_mat_selected = False
            self.report({'INFO'}, f"The sticker {stickername} materials have been deselected !!!") 
        else: 
            get_all_shader_nodes_from_a_sticker(node_tree, stickername, select = True)  
            addon_prefs.is_mat_selected = True
            self.report({'INFO'}, f"The sticker {stickername} materials have been selected !!!") 
            
        [a.tag_redraw() for a in context.screen.areas]                   
        return {'FINISHED'}



class StickerMatUp(bpy.types.Operator):
    """Operator class to move 'up' the sticker shadernodes
    in the node_tree
    """    
    
    bl_idname = 'opr.sticker_up'
    bl_label = 'Move up'
    bl_options = {'REGISTER','UNDO'}

   
    def execute(self, context):
        
        addon_prefs = bpy.context.preferences.addons[__addon_name__].preferences
        assert isinstance(addon_prefs, StickerPreferences)

        stickername = addon_prefs.sticker_name 
        is_selected = addon_prefs.is_mat_selected
 
        if not is_selected:
            self.report({'ERROR'}, "You need to select the sticker materials first.")
            return{'CANCELLED'}            

        if not check_if_sticker_name_exists(stickername):
            addon_prefs.is_mat_selected = False
            self.report({'ERROR'}, "Can't find the sticker in scene. Check the sticker name.")
            return{'CANCELLED'} 


        sticker_objs = [
            f"{stickername}_base_node",
            f"{stickername}_normal_node",
            f"{stickername}_projection_node",
            #for the plane deactivated in this version
            #f"{stickername}_aux_plane",
        ] 
        
        main_obj = bpy.data.objects[sticker_objs[0]].parent
        main_obj.select_set(True)
        main_material = main_obj.active_material
        
        if check_if_is_the_topmost(main_material, stickername):
            self.report({'ERROR'}, "The sticker is the topmost yet. Can't move up.")
            return{'CANCELLED'}            
        
        interchange_sticker_connections_and_positions(main_material, stickername, up=True)
        
        self.report({'INFO'}, f"The sticker {stickername} has been moved up !!!")         
        return {'FINISHED'}

        
class StickerMatDown(bpy.types.Operator):
    """Operator class to move 'down' the sticker shadernodes
    in the node_tree
    """    
    
    bl_idname = 'opr.sticker_down'
    bl_label = 'Move down'
    bl_options = {'REGISTER','UNDO'}

   
    def execute(self, context):
        
        addon_prefs = bpy.context.preferences.addons[__addon_name__].preferences
        assert isinstance(addon_prefs, StickerPreferences)

        stickername = addon_prefs.sticker_name 
        is_selected = addon_prefs.is_mat_selected
 
        if not is_selected:
            self.report({'ERROR'}, "You need to select the sticker materials first.")
            return{'CANCELLED'}            

        if not check_if_sticker_name_exists(stickername):
            addon_prefs.is_mat_selected = False
            self.report({'ERROR'}, "Can't find the sticker in scene. Check the sticker name.")
            return{'CANCELLED'} 


        sticker_objs = [
            f"{stickername}_base_node",
            f"{stickername}_normal_node",
            f"{stickername}_projection_node",
            #for the plane deactivated in this version
            #f"{stickername}_aux_plane",
        ] 
        
        main_obj = bpy.data.objects[sticker_objs[0]].parent
        main_obj.select_set(True)
        main_material = main_obj.active_material
        
        if check_if_is_the_downmost(main_material, stickername):
            self.report({'ERROR'}, "The sticker is the downmost yet. Can't move down.")
            return{'CANCELLED'}            

        interchange_sticker_connections_and_positions(main_material, stickername, up=False)
        
        self.report({'INFO'}, f"The sticker {stickername} has been moved down !!!")         
        return {'FINISHED'}


