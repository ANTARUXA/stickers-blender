"""
[Blender and Python] Cretion Class for Stickers
Juan R Nouche - October 2024
Email: juan.nouche@antaruxa.com
The main class used to create stickers
Antaruxa Stickers - Blender python main creation Sticker Class
Copyright (c) 2024 Antaruxa
--------
"""


import os

import bpy
import bmesh
import mathutils
from mathutils import (Vector)


from stickers_blender.common.sticker_funcs import (
    create_a_plane_with_segments,
    create_empty,
    create_circle,
    create_constraint_to_object,
    parent_object_to_vertex_in_mesh,
    is_valid_image_imghdr,
    is_valid_image_extension,
    is_there_file_on_path,
    create_custom_properties_for_sticker,
    check_if_sticker_name_exists,
    add_driver_to_object,
)

from stickers_blender.common.material_funcs import (
    create_sticker_shader_group,
    add_driver_to_material,
    create_sticker_material_nodes,
    get_node_connected_to_input,
    get_main_material_node_tree,
    # for plane deactivate in this version
    # create_material_for_sticker_plane,
    disconnect_sticker_material,
    remove_all_the_nodes_from_sticker,
    check_image_file_sequence,  
)



# == GLOBAL VARIABLES

# return values
NO_VERTEX_SELECTED       = -1
NO_MESH_SELECTED         = -2
NO_EDITMODE              = -3
MORE_THAN_1_VTX_SELECTED = -4
MORE_THAN_1_OBJ_SELECTED = -5
SEL_SHOULD_BE_A_MESH     = -6
ALL_DONE                 = 0



class Sticker(object):
    

    def __init__(self, mode = 'CREATE'):
        
        if mode == 'CREATE':  # modo create inicializamos variables
            self.current_obj = bpy.context.active_object
            object_type = getattr(self.current_obj, 'type', '')
            if object_type != 'MESH':
                print("NO MESH SELECTED")
                return None
            
            self.collection         = self.current_obj.users_collection[0]

            self.sticker_name       = ""
            self.current_mesh       = None

            self.anchor_vertex      = None
            self.anchor_empty       = None
            self.base_node          = None
            self.calcnormal_node    = None
            self.aux_plane          = None
            
            self.material_node_tree = None
            self.sticker_image      = None
            self.is_seq             = False
            self.input_conn         = "Base Color"
    
    def create_sticker(self, name = "sticker-default", img_filename = "//", is_seq = False, is_control_anim = False, img_offset = None, img_firstframe = None):
        """Create a complete sticker structure
        """    
        

        selected_objs        = bpy.context.selected_objects
        self.sticker_name    = name
        self.is_seq          = is_seq
        self.is_control_anim = is_control_anim
        self.img_offset      = img_offset
        self.img_firstframe  = img_firstframe
        
        if len(selected_objs) > 1:
            return MORE_THAN_1_OBJ_SELECTED
        
        elif self.current_obj == None or self.current_obj.type != 'MESH':
            return NO_MESH_SELECTED     
       
        elif self.current_obj.mode != 'EDIT':
            return NO_EDITMODE

        else:
           

            self.current_mesh = mesh = bmesh.from_edit_mesh(self.current_obj.data)
            selected_verts = list(filter(lambda v: v.select, mesh.verts))
            numvertex = len(selected_verts)

            if numvertex <= 0:
                return NO_VERTEX_SELECTED            

            else:
                if numvertex > 1:
                    return MORE_THAN_1_VTX_SELECTED

                else:
                    
                    self.anchor_vertex = selected_verts[0]
                    self.create_anchor_empty_and_parent(self.sticker_name)
                    self.anchor_empty.lock_location = (True, True, True) 
                    self.create_and_parent_base_sticker_node(self.sticker_name)
                    self.create_and_parent_calcnormal_node(self.sticker_name)


                    head, tail = os.path.split(img_filename)
                    #reusing a single image if it exists
                    if tail in bpy.data.images and not (is_seq or is_control_anim):
                        self.sticker_image=bpy.data.images[tail]
                    else:
                        self.sticker_image = bpy.data.images.load(filepath = img_filename)
                        self.sticker_image.pack()
                        
                    self.material_node_tree = get_main_material_node_tree(self.current_obj)
                    main_material = self.current_obj.material_slots[0].material
                   
                    create_sticker_material_nodes( main_material,
                                                  self.material_node_tree, 
                                                  self.sticker_name, 
                                                  self.base_node.name, 
                                                  self.sticker_image, 
                                                  self.input_conn,
                                                  self.is_seq,
                                                  self.is_control_anim,
                                                  self.img_offset,
                                                  self.img_firstframe,
                                                  )
                    #creates the plane deactivated in this version
                    #self.create_and_parent_the_aux_plane(self.sticker_name) 

                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False) #dejamos en modo objeto
                                       
                    
                    return ALL_DONE
                
    def create_anchor_empty_and_parent(self, name="sticker"):
        """Creates an empty which will be used to anchoring the sticker
        name       -- Name of the sticker

        returns:

        """      

        self.anchor_empty = create_empty(f"{name}_anchor_vertex", self.collection, 'SPHERE')
        parent_object_to_vertex_in_mesh(self.anchor_empty, self.current_obj, self.anchor_vertex.index)
        self.anchor_empty.hide_viewport = True

    def create_and_parent_base_sticker_node(self, name="sticker"):
        """Creates an empty which will be used as base node for the sticker
        name       -- Name of the sticker

        returns:

        """      

        self.base_node = create_empty(f"{name}_base_node", self.collection,'CIRCLE')
        #deactivated in this version
        #self.base_node = create_circle(f"{name}_base_node", self.collection, radius = 1.0)
        self.base_node.parent = self.anchor_empty
        create_constraint_to_object(self.base_node, self.current_obj, 'SHRINKWRAP', "sticker_anchor_shrinkwrap")
        create_constraint_to_object(self.base_node, self.current_obj, 'TRACK_TO', "sticker_anchor_track_to")
        self.base_node['sticker_name'] = name
        #deactivated in this version
        #self.base_node['hide_plane'] = False
        self.base_node['flip_horiz'] = False
        self.base_node['flip_vert'] = False
        self.base_node.lock_rotation[0] = True #Locking RotateX
        self.base_node.lock_rotation[1] = True #Locking RotateY


        

    def create_and_parent_calcnormal_node(self, name="sticker"):
        """Creates an empty which will be used as main node for the sticker
        name       -- Name of the sticker

        returns:

        """      

        self.calcnormal_node = create_empty(f"{name}_normal_node", self.collection,'PLAIN_AXES')
        self.calcnormal_node.parent = self.base_node
        self.calcnormal_node.location = Vector((0.0, 0.0, -1.0))
        self.calcnormal_node.hide_viewport = True        
    
    #realated with plane creation deactivated in this version

    # def create_and_parent_the_aux_plane(self, name):
    #     """Creates an auxiliar plane to use when the sticker is not affixed to the object
    #     name       -- Name of the sticker
    #         self.current_mesh = None

    #     returns:

    #     """      
        #self.aux_plane = create_a_plane_with_segments(10, 10, 0.5, f"{name}_aux_plane", self.collection)
        #self.aux_plane.parent = self.base_node
        # create_constraint_to_object(self.aux_plane, self.current_obj, 'SHRINKWRAP', "aux_plane_shrinkwrap")
        # create_constraint_to_object(self.aux_plane, self.current_obj, 'TRACK_TO', "aux_plane_track_to")
       
        # add_driver_to_object(self.aux_plane, self.base_node, 
        #                      "rotation_euler", "rotation_euler.z", 
        #                      "rot_x", "rot_x + 0.0", ndx = 2, 
        #                      transf_type = 'ROT_Z', space = 'TRANSFORM_SPACE')

        # create_material_for_sticker_plane(name, self.current_obj, self.aux_plane, 
        #                                   f"{name}_plane_mat", self.sticker_image,
        #                                   self.input_conn, self.is_seq, self.img_offset, self.img_firstframe)
        

