"""
[Blender and Python] Shader Utils library for Stickers Antaruxa
Juan R Nouche - October 2024
Email: juan.nouche@antaruxa.com
A Blender python functions library to create create and organize 
the stiker shadernodes
Antaruxa Stickers - Blender python shaders utils library
Copyright (c) 2024 Antaruxa
--------
"""


import bpy

# ==== CREATING AND REMOVE NODES (AUX)


def create_sticker_material_nodes(main_material=None, node_tree = None, 
                                  sticker_name = "sticker", obj_to_attach = "", 
                                  img_file = None, input_conn = "Base Color",
                                  is_seq = False, is_control_anim=False, img_offset = None, img_firstframe = None):
    """Creates and conects all the nodes we will need for the sticker shader
    node_tree      -- the main node tree
    sticker_name   -- the name of the sticker
    obj_to_attach  -- the name of the object to attach to the Texture Coordinate node
    img_file       -- pointer for the image to use in the image node
    input_conn     -- name of the input_connection on the base_material
    is_seq         -- true if an image sequence is selected
    img_offset     -- the number of images in de sequence if it is set
    img_firstframe -- the number of the first image
    
    
    returns:
    None at the moment
    """      


    """ Getting and moving the node connected tho object material's 
    Base Color
    """

    main_node = node_tree.nodes[0]
    
    base_coord = [0,0]

    #getting the node connected to Base Color input
    connected_node, conneted_socket = get_node_and_socket_connected_to_input(main_node, input_conn)
    

    # main_node.location.y -= 300
    #get the current position of the connected node
    base_coord[0] = main_node.location.x
    base_coord[1] = main_node.location.y
    #move left and right to make space for the group
        # connected_node.location.x += -200
    # connected_node.location.y += 300
    
    moving_all_nodes_connected(main_node, -600, 450)

    """ Creating and positioning the mixer to transparency
    """
    
    mix_node = node_tree.nodes.new( type = "ShaderNodeMix")
    mix_node.name = f"{sticker_name}_mix_node"
    base_coord[0] -= 350
    mix_node.location.x = base_coord[0]
    mix_node.location.y = base_coord[1]
    
    mix_node.data_type = 'RGBA'
    mix_node.clamp_factor = True
    mix_node.inputs["Factor"].default_value = 0.0
    
    # adding driver
    obj_who_drives = f"{sticker_name}_base_node"
    control_driver = bpy.data.objects[obj_who_drives]
    control_driver["transparency"] = 0.0
    set_driven_key_for_transparency(mix_node, control_driver)

     
    """ Creating and positioning de magical sticker group 
    """
    sticker_node_group_name = "Sticker Group Node"
    # first check if it exists yet
    if not sticker_node_group_name in bpy.data.node_groups:
        # if it doesn't we are defining a new kind of group node
        sticker_group_def = create_sticker_shader_group(sticker_node_group_name)
    
    ## add a new group to the material node tree
    sticker_group = node_tree.nodes.new('ShaderNodeGroup')
    sticker_group.name = f"{sticker_name}_group"
    ## adding our defined node tree to the new group   
    sticker_group.node_tree = bpy.data.node_groups[sticker_node_group_name]
    sticker_group.width = 220
    # We are going to use the original base_coords
    base_coord[0] -= 300
    # base_coord[1] -= 300
    sticker_group.location.x = base_coord[0]
    sticker_group.location.y = base_coord[1]


    
    """ Once the sticker group node is created 
    we are going to create the other nodes needed
    """

    # #añadir un nodo de MixRGB
    # mix_node = node_tree.nodes.new(type = "ShaderNodeMixRGB")
    # mix_node.location.x = 200

    # adding a TexImage Node for the sticker and set coords
    img_node = node_tree.nodes.new( type = "ShaderNodeTexImage")
    img_node.name = f"{sticker_name}_image"
    base_coord[0] -= 350
    img_node.location.x = base_coord[0]
    img_node.location.y = base_coord[1]
    # set the repeat to clip 

    img_node.extension = 'CLIP'
    img_node.image = img_file
    
    if is_seq or is_control_anim:
        img_node.image.source = 'SEQUENCE'

        # Sequence Properties
        img_node.image_user.use_auto_refresh = True
        img_node.image_user.use_cyclic = True
        img_node.image_user.frame_duration = img_offset
        img_node.image_user.frame_start = img_firstframe
        img_node.image_user.frame_offset = img_firstframe - 1
        
        if is_control_anim:
            obj_who_drives = f"{sticker_name}_base_node"
            control_driver = bpy.data.objects[obj_who_drives]
            img_node.image_user.frame_start = 1
            control_driver["frame_count"] = img_offset
            control_driver["active_frame"] = 1
            control_driver["initial_frame"] = img_firstframe
            set_driven_key_for_animated_sequence(img_node, control_driver, img_firstframe)


    # add the mapping node
    map_node = node_tree.nodes.new(type = "ShaderNodeMapping")
    map_node.name = f"{sticker_name}_mapping"
    base_coord[0] -= 200
    map_node.location.x = base_coord[0]
    map_node.location.y = base_coord[1]
    # set parameters of the mapping node
    map_node.inputs["Location"].default_value[0] = 0.5
    map_node.inputs["Location"].default_value[1] = 0.5
    map_node.inputs[3].default_value[1] = -1
    #
    obj_who_drives = f"{sticker_name}_base_node"
    map_driver = bpy.data.objects[obj_who_drives]
    add_driver_to_material(map_node, 
                           map_driver, 
                           "rotation_euler.z", "rotz", "-(rotz) + 0.0", 
                           "Rotation", ndx = 2, 
                           transf_type = 'ROT_Z', 
                           space = 'TRANSFORM_SPACE')


    # add the texture coordinate
    coord_node = node_tree.nodes.new(type = "ShaderNodeTexCoord")
    coord_node.name = f"{sticker_name}_obj_coords"
    base_coord[0] -= 200
    coord_node.location.x = base_coord[0]
    coord_node.location.y = base_coord[1]
    # conecting the object to use by the coord node
    coord_node.object = bpy.data.objects[obj_to_attach]
    
    # add the combine XYZ node coordinate
    xyz_node = node_tree.nodes.new(type = "ShaderNodeCombineXYZ")
    xyz_node.name = f"{sticker_name}_combine_XYZ"
    base_coord[1] -= 300
    xyz_node.location.x = base_coord[0]
    xyz_node.location.y = base_coord[1]
    # conecting the xyz node to driver object an create drivers
    obj_who_drives = f"{sticker_name}_normal_node"
    xyz_driver = bpy.data.objects[obj_who_drives]
    add_driver_to_material(xyz_node, 
                           xyz_driver, 
                           "location.x", "loc_x", "(loc_x) + 0.0", 
                           0, ndx = -1, 
                           transf_type = 'LOC_X', 
                           space = 'WORLD_SPACE')
    add_driver_to_material(xyz_node, 
                           xyz_driver, 
                           "location.y", "loc_y", "(loc_y) + 0.0", 
                           1, ndx = -1, 
                           transf_type = 'LOC_Y', 
                           space = 'WORLD_SPACE')
    add_driver_to_material(xyz_node, 
                           xyz_driver, 
                           "location.z", "loc_z", "(loc_z) + 0.0", 
                           2, ndx = -1, 
                           transf_type = 'LOC_Z', 
                           space = 'WORLD_SPACE')
    
    # add_driver_to_material( xyz_node, xyz_driver, 'location.x', 'X', 0)
    # add_driver_to_material( xyz_node, xyz_driver, 'location.y', 'Y', 1)
    # add_driver_to_material( xyz_node, xyz_driver, 'location.z', 'Z', 2)
    

    # fcurve = bpy.data.materials["Property Dump"].node_tree.nodes["Mix"].inputs[0].driver_add("default_value")

    """ Now we are going to make the conections
    """

    #conectar la salida del mix_node a la entrada del main material
    node_tree.links.new(mix_node.outputs["Result"], main_node.inputs[input_conn])

    #conectar la salida del group a la entrada B del mix_node 
    node_tree.links.new(sticker_group.outputs["Color"], mix_node.inputs["A"])

    #conectar la entrada del main material a la entrada 0 del group Base Color y a la entrada A del mix_color
    node_tree.links.new(connected_node.outputs[conneted_socket], sticker_group.inputs["Base Color"])
    node_tree.links.new(connected_node.outputs[conneted_socket], mix_node.inputs["B"])

    #conectar la salida del image tex a la entrada 1 del group Sticker Color
    node_tree.links.new(img_node.outputs["Color"], sticker_group.inputs["Sticker Color"]) 

    #conectar la salida del xyz a la entrada 3 del group Empty Location
    node_tree.links.new(xyz_node.outputs["Vector"], sticker_group.inputs["Empty Location"]) 

    #conectar la salida vector del map node a la entrada vector del img node
    node_tree.links.new(map_node.outputs["Vector"], img_node.inputs["Vector"])

    #conectar la salida alpha de la image a la entrada 2  del sticker_group
    node_tree.links.new(img_node.outputs["Alpha"], sticker_group.inputs["Alpha"])

    #conectar la salida object del coord node al map node
    node_tree.links.new(coord_node.outputs["Object"], map_node.inputs["Vector"])


def create_sticker_shader_group(group_name):
    """Creates the sticker shader group that is doing the magic
    group_name    -- the name for this kind of group
    returns:
    sticker_group -- the new shader group created
    """     

    """ Creating the group and her inputs and outputs
    """
    # Creting the group
    sticker_group = bpy.data.node_groups.new(group_name, 'ShaderNodeTree')
    
    # Creating and set location of the input node
    group_in = sticker_group.nodes.new('NodeGroupInput')
    group_in.location = (-800,0)
    
    # Adding customized inputs
    sticker_group.interface.new_socket(name = "Base Color", in_out = 'INPUT', socket_type = 'NodeSocketColor')
    sticker_group.interface.new_socket(name = "Sticker Color", in_out = 'INPUT', socket_type = 'NodeSocketColor')
    sticker_group.interface.new_socket(name = "Alpha", in_out = 'INPUT', socket_type = 'NodeSocketFloat')
    sticker_group.interface.new_socket(name = "Empty Location", in_out = 'INPUT', socket_type = 'NodeSocketVector')
 
    # Creating and set location for the output node
    group_out = sticker_group.nodes.new('NodeGroupOutput')
    group_out.location = (800,0)
    
    # Adding customized output
    sticker_group.interface.new_socket(name = "Color", in_out = 'OUTPUT', socket_type = 'NodeSocketColor')
    
    """ Creating and customizing the nodes for the group
    """

    # geo_node ShaderNodeNewGeometry - Geometry Position-normal (-800, -300)
    geo_node = sticker_group.nodes.new(type = 'ShaderNodeNewGeometry')
    geo_node.location = (-800,-300)
    
    # vinc_node ShaderNodeVectorMath - V incidendia (-550, -200) operation 'SUBSTRACT'
    vinc_node = sticker_group.nodes.new(type = 'ShaderNodeVectorMath')
    vinc_node.location = (-550,-200)
    vinc_node.operation = 'SUBTRACT'

    # norm_node ShaderNodeVectorMath - Normalize (-300, -200)  operation 'NORMALIZE'
    norm_node = sticker_group.nodes.new(type = 'ShaderNodeVectorMath')
    norm_node.location = (-300,-200)
    norm_node.operation = 'NORMALIZE'

    # ang_node ShaderNodeVectorMath - angulo v.N (-50, -300) operation 'DOT_PRODUCT'
    ang_node = sticker_group.nodes.new(type = 'ShaderNodeVectorMath')
    ang_node.location = (-50,-300)
    ang_node.operation = 'DOT_PRODUCT'

    # facing_node ShaderNodeMath - Facing Factor (200,-300) use_clamp True operation 'GREATER_THAN'
    facing_node = sticker_group.nodes.new(type = 'ShaderNodeMath')
    facing_node.location = (200,-300)
    facing_node.use_clamp = True
    facing_node.operation = 'GREATER_THAN'

    # filter_mix_node ShaderNodeMixRGB - Filter by Facing (400,100) 
    # data_type 'RGBA', blend_type 'MIX', clamp_result True, clamp_factor True
    filter_mix_node = sticker_group.nodes.new(type = 'ShaderNodeMix')
    filter_mix_node.location = (400, 100)
    filter_mix_node.data_type    = 'RGBA'
    filter_mix_node.blend_type   = 'MIX'
    filter_mix_node.clamp_result = True
    filter_mix_node.clamp_factor = True

    # mask_mix_node ShaderNodeMixRGB - Mix With Mask (600, -100)
    #data_type 'RGBA', blend_type 'MIX', clamp_result False, clamp_factor True
    mask_mix_node = sticker_group.nodes.new(type = 'ShaderNodeMix')
    mask_mix_node.location = (600, -100)
    mask_mix_node.data_type    = 'RGBA'
    mask_mix_node.blend_type   = 'MIX'
    mask_mix_node.clamp_result = False
    mask_mix_node.clamp_factor = True



    """ Making the links and connections
    """
    
    # Guardamos la operación new() para usar mas facil
    link = sticker_group.links.new
    
    # group_in - Empty Location , vinc_node [0]
    link(group_in.outputs["Empty Location"], vinc_node.inputs[0])

    # group_in - Alpha - mask_mix_node - Factor
    link(group_in.outputs["Alpha"], mask_mix_node.inputs["Factor"])
    
    # group_in - Sticker Color , filter_mix_node B
    link(group_in.outputs["Sticker Color"], filter_mix_node.inputs["B"])

    # group_in - Base Color, filter_mix_node A 
    link(group_in.outputs["Base Color"], filter_mix_node.inputs["A"])

    # group_in - Base Color, mask_mix_node A
    link(group_in.outputs["Base Color"], mask_mix_node.inputs["A"])

    # geo_node - Position, vinc_node [1]
    link(geo_node.outputs["Position"], vinc_node.inputs[1])

    # geo_node - Normal, ang_node [1]
    link(geo_node.outputs["Normal"], ang_node.inputs[0])

    # vinc_node - Vector, norm_node [0]
    link(vinc_node.outputs["Vector"], norm_node.inputs[0])

    # norm_node - Vector, ang_node [1]
    link(norm_node.outputs["Vector"], ang_node.inputs[1])

    # ang_node - Value, facing_node - Value
    link(ang_node.outputs["Value"], facing_node.inputs["Value"])

    # facing_node - Value, filter_mix_node - Factor
    link(facing_node.outputs["Value"], filter_mix_node.inputs["Factor"])

    # filter_mix_node - Result, mask_mix_node - B
    link(filter_mix_node.outputs["Result"], mask_mix_node.inputs["B"])

    # mask_mix_node - Result, group_out - Result
    link(mask_mix_node.outputs["Result"], group_out.inputs["Color"])

    return sticker_group


def remove_all_the_nodes_from_sticker(sticker_name, material, node_name_list):
    """Once disconnected remove all the shader nodes for this sticker
    sticker_name   -- the name of the sticker
    material       -- the base material where the sticker nodes are inserted (to get the node_tree)
    node_name_list -- a list containing the nodes which are going to be deleted
    returns:
    the nodes are disconected
    """   
    
    node_tree = material.node_tree
    
    for node_name in node_name_list:
        obj = node_tree.nodes[node_name]
        obj.select = True # to update node_tree
        node_tree.nodes.remove(obj)


# def create_material_for_sticker_plane(sticker_name, object_from, object_to, 
#                                       mat_name, img_file, input_conn = "Base Color", 
#                                       is_seq = False, img_offset = None):
#     """Creates the material shader for the sticker external plane
#     sticker_name  -- default name of the sticker
#     object_form   -- the main object of the sticker
#     object_to     -- the plane object
#     mat_name      -- name for the new material
#     img_file      -- the img_file for the sticker
#     is_seq         -- true if an image sequence is selected
#     img_offset     -- the number of images in de sequence if it is set
    

#     returns:
#     the material conected to the sticker plane
#     """     

#     """ Duplicating and naming the object from material 
#     """
#     nodelist=[]
    
#     obj = object_from
#     mat = obj.active_material
#     mat_copy = mat.copy()  # duplicamos el material principal
#     mat_copy.name = mat_name


#     """ Deleting not needed nodes
#     """
#     node_tree = mat_copy.node_tree
#     # Eliminamos todas las conexiones y nodos
#     node = node_tree.nodes[0]
    
#     node.name = f"{mat_name}_BSDRF"
#     select_all_nodes_connected(node, nodelist)
#     for nod in reversed(nodelist):
#         mat_copy.node_tree.nodes.remove(nod)

#     """ Assign the material to the plane
#     """
#     dup = object_to
#     dup.active_material = mat_copy
    
#     """ Creating a image texture and apply the sticker one
#     """
#     # adding a TexImage Node for the sticker and set coords
#     node = node_tree.nodes[0]
#     img_node = node_tree.nodes.new(type = "ShaderNodeTexImage")
#     img_node.name = f"{sticker_name} Image"
#     img_node.location.x = node.location.x - 300
#     img_node.location.y = node.location.y
#     # set the repeat to clip 
#     img_node.extension = 'CLIP'
#     img_node.image = img_file

#     if is_seq:
#         img_node.image.source = 'SEQUENCE'

#         # Sequence Properties
#         img_node.image_user.use_auto_refresh = True
#         img_node.image_user.use_cyclic = True
#         img_node.image_user.frame_duration = img_offset-1
#         img_node.image_user.frame_start = 1
#         img_node.image_user.frame_offset = 0


#     """ Connecting the created texture to the main input
#     """
#     node_tree.links.new(img_node.outputs["Color"], node.inputs[input_conn])
#     node_tree.links.new(img_node.outputs["Alpha"], node.inputs["Alpha"])


# ==== DRIVER CONTROL FUNCTIONS (AUX)

def set_driven_key_for_transparency(node = None, obj = None):
    
    ''' Add the driver to the mix Shader Color to control the sticker's transparency
        node        -- the source node "driven_node"
        obj  -- the target object "driver_obj"
    '''
    
    driver = node.inputs["Factor"].driver_add("default_value")
    
    transp = driver.driver.variables.new()
    transp.name = "transparency"
    transp.type = 'SINGLE_PROP'
    transp.targets[0].id_type = 'OBJECT'
    transp.targets[0].id = obj
    transp.targets[0].data_path = "transparency" 
    driver.driver.expression = "transparency"
    

def set_driven_key_for_animated_sequence(img = None, obj = None, img_firstframe = None): 

    ''' Add the driver expresion to control the offset in a controlled animated sequence
        img            -- the source node "driven_node" that contains the image_user object
        obj            -- the target object "driver_obj"
        img_firstframe -- the displacement to compute the image offset precisely
    '''

    #img = bpy.data.materials["caminando_plane_mat"].node_tree.nodes["caminando Image"].image_user
    image_user = img.image_user
    image_name = img.name
    
    scene = bpy.context.scene
 
    driver = image_user.driver_add("frame_offset")

    frame = driver.driver.variables.new()

    frame.name = "frame_current"
    frame.type = 'SINGLE_PROP'
    frame.targets[0].id_type = 'SCENE'
    frame.targets[0].id = scene
    frame.targets[0].data_path = "frame_current"

    duration = driver.driver.variables.new()
    duration.name = "duration"
    duration.type = 'SINGLE_PROP'
    duration.targets[0].id_type = 'OBJECT'
    duration.targets[0].id = obj
    duration.targets[0].data_path = 'frame_count'

    value = driver.driver.variables.new()
    value.name = "value"
    value.type = 'SINGLE_PROP'
    value.targets[0].id_type = 'OBJECT'
    value.targets[0].id = obj
    value.targets[0].data_path = "active_frame"

    value = driver.driver.variables.new()
    value.name = "desp"
    value.type = 'SINGLE_PROP'
    value.targets[0].id_type = 'OBJECT'
    value.targets[0].id = obj
    value.targets[0].data_path = "initial_frame"

    # driver.driver.expression = "-1*(((frame_current - 1) % duration) + 1) + (round(value) % duration)"
    # driver.driver.expression = "(-1*(((frame_current - 1) % duration) + 1) + (duration)) if value == duration else (-1*(((frame_current - 1) % duration) + 1) + (value % duration))"
    driver.driver.expression = "(-1*(((frame_current - 1) % duration) + 1) + (duration - 1) + desp) if value == duration else (-1*(((frame_current - 1) % duration) + 1) + ((value % duration)-1) + desp)"

def add_driver_to_material(driven_node, driver_obj, data_path, var_name, expr, input_ndx, ndx = -1, transf_type = 'LOC_X', space = 'WORLD_SPACE'):
    
    ''' Add driver_obj to a material node prop, driven_node by target dataPath
        driven_node -- the source node "driven_node"
        driver_obj  -- the target object "driver_obj"
        data_path   -- property or expresion in target that drives (rotation_euler.x, trasnslate.y)
        var_name    -- name of variable that should be created
        expr        -- expression to process with driver
        input_ndx   -- indice del input sockect o el nombre del socket
        ndx         -- -1 simple value >= 0 index for the default value
        trasnf_type -- type of transformation on the target (LOC_X, LOC_Y, LOC_Z, ROT_X, ROT_Y, ...)
        space       -- space where the transformation is applide (WORLD_SPACE, TRANSFORM_SPACE,...)
    '''
    if ndx >= 0:
        fcurve = driven_node.inputs[input_ndx].driver_add("default_value", ndx)
    else:
        fcurve = driven_node.inputs[input_ndx].driver_add("default_value")
        
    d = fcurve.driver
    d.type = 'SCRIPTED'
    d.expression = expr #0 added will be the same value
    
    var = d.variables.new()
    var.name = var_name
    var.type = 'TRANSFORMS'
    
    target = var.targets[0]
    target.id = driver_obj
    target.transform_space = space

    target.transform_type = transf_type
        
    target.data_path = data_path



# ==== IMAGE SEQUENCE FUNCTIONS (AUX)

def has_numbers(inputString):
    ''' Auxiliar function to check if there is at least a number in a string 
    returns:
    True or False
    '''
    import re
    return bool(re.search(r'\d', inputString))

def check_image_file_sequence(image_name):

    ''' Check if the selected image belongs to a sequence
        image_name  -- the path to one of the images in the sequence must have a number before extension
    returns:
        len(imagelist) -- the number of images in the sequence
        firstframe     -- the firstframe number of the images
    '''     
    if not has_numbers(image_name):
        return None, None, None
    imagelist = image_sequence_resolve_all(image_name)
    firstframe = image_sequence_get_first_frame(image_name)
    consecutive = check_if_images_in_sequence_are_consecutive(image_name)
    if not imagelist:
        return None, None, None
    else:
        return len(imagelist), firstframe, consecutive

def image_sequence_resolve_all(filepath):
    
    ''' Gets de list of images in a sequence
        filepath  -- the path to one of the images in the sequence must have a number before extension
    returns:
        the list of images in the sequence
    '''    
    import os

    basedir, filename = os.path.split(filepath)
    filename_noext, ext = os.path.splitext(filename)

    from string import digits
    if isinstance(filepath, bytes):
        digits = digits.encode()
    filename_nodigits = filename_noext.rstrip(digits)

    if len(filename_nodigits) == len(filename_noext):
        # input isn't from a sequence
        return []

    return [
        f.path
        for f in os.scandir(basedir)
        if f.is_file() and
           f.name.startswith(filename_nodigits) and
           f.name.endswith(ext) and
           f.name[len(filename_nodigits):-len(ext) if ext else -1].isdigit()
    ]
    
def image_sequence_get_first_frame(filepath):
    ''' Returns the first frame computing the numerical extensions in a file sequence
        filepath       -- the path to one of the images in the sequence must have a number before extension
    returns:
        the firstframe number 
    '''    
    import os

    basedir, filename = os.path.split(filepath)
    filename_noext, ext = os.path.splitext(filename)

    from string import digits
    if isinstance(filepath, bytes):
        digits = digits.encode()
    filename_nodigits = filename_noext.rstrip(digits)

    if len(filename_nodigits) == len(filename_noext):
        # input isn't from a sequence
        return -2
    
    contador = []
    for f in os.scandir(basedir):
        if f.is_file() and f.name.startswith(filename_nodigits) and f.name.endswith(ext):
            contador.append(int(''.join(filter(lambda i: i.isdigit(), f.name))))        
    if contador:
        return (min(contador))
    else:
        return -1

def check_if_images_in_sequence_are_consecutive(filepath):
    ''' check if the images are consecutive frames
        filepath  -- the path to one of the images in the sequence must have a number before extension
    returns:
        True if the images are consecutive
    '''    
    import os

    basedir, filename = os.path.split(filepath)
    filename_noext, ext = os.path.splitext(filename)

    from string import digits
    if isinstance(filepath, bytes):
        digits = digits.encode()
    filename_nodigits = filename_noext.rstrip(digits)

    if len(filename_nodigits) == len(filename_noext):
        # input isn't from a sequence
        return False
    
    contador = []
    for f in os.scandir(basedir):
        if f.is_file() and f.name.startswith(filename_nodigits) and f.name.endswith(ext):
            contador.append(int(''.join(filter(lambda i: i.isdigit(), f.name))))        
    if contador:
        return sorted(contador) == list(range(min(contador), max(contador)+1))
    else:
        return False


# ==== SHADERNODES FUNCTIONS (AUX) - GETTERS AND SETTERS

def get_main_material_node_tree(obj):

    """Gets the main shader node_tree linked to the object
    obj -- Name of the sticker

    returns:

    """      

    #obtener el material principal del objeto
    #main_material = obj.active_material
    main_material = obj.material_slots[0].material
    if not main_material.use_nodes:
        print ("no puedo seguir")

    #cargar el node tree
    return main_material.node_tree

def get_node_and_socket_connected_to_input(node = None, inputkey = "Base Color"):

    """Gets the node connected to the key and the socket connected to inputkey
    node      -- the main node we want to check the inputs
    inputkey  -- the key socket we are goin to check

    returns:
    from_node   -- the connected node
    from_socket -- the connected socket
    """      


    input = node.inputs[inputkey]
    if not input.is_linked:
        return None, None
    from_node = input.links[0].from_node  
    from_socket = input.links[0].from_socket.name
    return from_node, from_socket


def get_node_and_socket_connected_to_output(node = None, outputkey = "Base Color"):

    """Gets the node connected to the otuput key and the socket that is connected
    node       -- the main node we want to check the outputs
    outputkey  -- the key where the output node is connectec
                 must be a color vector.
    returns:
    to_node   -- the connected node
    to_socket -- the connected socket
    """      


    output = node.outputs[outputkey]
    to_nodes = []
    to_sockets = []
    for link in output.links:
        to_nodes.append(link.to_node)
        to_sockets.append(link.to_socket.name)
    #o_node = output.links[0].to_node  
    #o_socket = output.links[0].to_socket.name
    return to_nodes, to_sockets

def get_node_connected_to_input(node = None, inputkey = "Base Color"):

    """Gets the node connected to the outputkey
    node      -- the main node we wat to check
    inputkey  -- the key where the node network will be inserted
                 must be a color vector.
    returns:
    from_node -- the connected node
    """      


    input = node.inputs[inputkey]
    from_node = input.links[0].from_node  
    return from_node

def get_node_connected_to_output(node = None, outputkey = "Base Color"):

    """Gets the node connected to the input key
    node      -- the main node we wat to check
    inputkey  -- the key where the node network will be inserted
                 must be a color vector.
    returns:
    to_node -- the connected node
    """      


    output = node.outputs[outputkey]
    to_node = output.links[0].to_node  
    return to_node


def select_all_nodes_connected(node_in, nodelist):
    """Auxiliar to create_material_for_sticker_plane. Dectects inputs in a node 
    and add de nodes_form to node list recursively
    
    node_in  -- node to evaulate
    nodelist -- list to add the inputs nodes to delete

    returns:
    a list of nodes to delete in nodelist
    """     
   
    for n_inputs in node_in.inputs:
        for node_links in n_inputs.links:
            current_node = node_links.from_node
            print(f"going from {node_in.name} to {current_node.name}")
            if not (current_node in nodelist):            
                nodelist.append(current_node)
            else:
                print("It's repeated!!")
            select_all_nodes_connected(current_node, nodelist)


def get_all_shader_nodes_from_a_sticker(node_tree, sticker_name):

    """Gets all the shadernodes that belong tho the sticker
    node_tree    -- the node_tree where the sticker belong
    sticker_name -- the name of the sticker that we are going to check
    returns:
    True or False
    """   
    
    sticker_shader_nodes = [f"{sticker_name}_group", f"{sticker_name}_image", f"{sticker_name}_mapping",
                            f"{sticker_name}_obj_coords", f"{sticker_name}_combine_XYZ", f"{sticker_name}_mix_node", ]
    selected_stickers = []
    for stick in sticker_shader_nodes:
        node = node_tree.nodes[stick]
        node.select = True
        selected_stickers.append(node)
    return selected_stickers

def get_near_down_stickernode(material = None, sticker_name = ""):

    """Get the near down sticker node
    material     -- material where the sticker nodes are
    sticker_name -- the name of the sticker from we are going to look for
    returns:
    If success returns the near down node else None
    """   
    
    node_tree = material.node_tree
    
    # sticker_group = node_tree.nodes[f"{sticker_name}_group"] 
    mix_node = node_tree.nodes[f"{sticker_name}_mix_node"] #getting the final node
    
    node_in, socket_in = get_node_and_socket_connected_to_input(mix_node, "B")
    
    if "_mix_node" in node_in.name:
        return node_in
    return None

def get_near_up_stickernode(material = None, sticker_name = ""):
    
    """Get the near up sticker node
    material     -- material where the sticker nodes are
    sticker_name -- the name of the sticker from we are going to loock for
    returns:
    If success returns the near up node else None
    """   
    
    node_tree = material.node_tree
    
    # sticker_group = node_tree.nodes[f"{sticker_name}_group"] 
    mix_node = node_tree.nodes[f"{sticker_name}_mix_node"] #getting the final node
    
    node_out, socket_out = get_node_and_socket_connected_to_output(mix_node, "Result") 
    for node in node_out:
        if "_mix_node" in node.name:
            return node
    return None
            
# ==== SHADERNODES FUNCTIONS (AUX) - CHECKERS

def check_if_is_there_a_node_connected(node = None, inputkey = "Base Color"):
    """Checks if there is a node connected to the inputkey
    node      -- the main node we wat to check
    inputkey  -- the to check if a node is connected
                 
    returns:1
    from_node -- the connected node
    """      

    input = node.inputs[inputkey]
    if input:
        from_node = input.links[0].from_node
        
        if from_node:
            return 'IS_CONNECTED'
        else:
            return 'NOT_CONNECTED'
    else:
        return 'NOT_INPUTKEY'


def check_if_is_the_topmost(material = None, sticker_name = ""):
    """Check if the stickershader is the topmost
    material     -- the material where the sticker is connected
    sticker_name -- the name of the sticker that we are going to check
    returns:
    True or False
    """   
    
    node_tree = material.node_tree
    
    # sticker_group = node_tree.nodes[f"{sticker_name}_group"] 
    mix_node = node_tree.nodes[f"{sticker_name}_mix_node"] #getting the final node
    
    node_out, socket_out = get_node_and_socket_connected_to_output(mix_node, "Result") 
    if len(node_out) == 1:
        return True
    else:
        return False
    
    
def check_if_is_the_downmost(material = None, sticker_name = ""):
    """Check if the stickershader is the downmost
    material     -- the material where the sticker is connected
    sticker_name -- the name of the sticker that we are going to check
    returns:
    True or False
    """   
    
    node_tree = material.node_tree
    
    # sticker_group = node_tree.nodes[f"{sticker_name}_group"] 
    mix_node = node_tree.nodes[f"{sticker_name}_mix_node"] #getting the final node
    
    node_in, socket_in = get_node_and_socket_connected_to_input(mix_node, "B")
    if "_mix_node" in node_in.name:
        return False
    else:
        return True



# ==== SHADERNODES FUNCTIONS (AUX) - CONECTIONS AND MOVES
   

def disconnect_sticker_material(sticker_name, material):
    """Disconnect all the sticker nodes from and reconnect the outputs and inputs
    sticker_name -- the name of the sticker
    material     -- the base material where the sticker nodes are inserted (to get the node_tree)
    returns:
    the nodes are disconected
    """   
    
    node_tree = material.node_tree
    
    # sticker_group = node_tree.nodes[f"{sticker_name}_group"] 
    mix_node = node_tree.nodes[f"{sticker_name}_mix_node"] #getting the final node
    
    moving_all_nodes_connected(mix_node, 600, -450)
    
    #getting the socket out and the connected node (or nodes)
    node_out, socket_out = get_node_and_socket_connected_to_output(mix_node, "Result") 
    
    # getting the node in and the conected node
    node_in, socket_in = get_node_and_socket_connected_to_input(mix_node, "B")
    
    # making a connection between node_in.socket_in and node_out.socket_out remove the main connection
    if len(node_out) == 1:
        node_in.select = True 
        node_out[0].select = True
        node_tree.links.new(node_in.outputs[socket_in], node_out[0].inputs[socket_out[0]])
    else:
        node_in.select = True 
        node_out[0].select = True
        node_tree.links.new(node_in.outputs[socket_in], node_out[0].inputs[socket_out[0]])
        node_out[1].select = True
        node_tree.links.new(node_in.outputs[socket_in], node_out[1].inputs[socket_out[1]])
   
    # node_out.select = True ## test if it is selected
    # node_in.select = True 
    # node_tree.links.new(node_in.outputs[socket_in], node_out.inputs[socket_out])
    
    #https://blender.stackexchange.com/questions/141911/remove-node-links-by-python



def interchange_sticker_connections_and_positions(material = None, sticker_name = "", up=False):
    """Switchs positions between to stickers
    material     -- the material where the sticker is connected
    sticker_name -- the name of the sticker that we are going to reconnect up or down
    up           -- if True the sticker switch with the up sticker else with the down sticker
    returns:
    True or False
    """   
    
    
    node_tree = material.node_tree
    current_node = node_tree.nodes[f"{sticker_name}_mix_node"] #getting the final node
    current_node_group = node_tree.nodes[f"{sticker_name}_group"] #getting the final node
    if up:
        node_to = get_near_up_stickernode(material, sticker_name)
        
    else:
        node_to = get_near_down_stickernode(material, sticker_name)

    if node_to:
        stck_name = node_to.name
        stck_name = stck_name.replace("_mix_node","")
        node_group_to = node_tree.nodes[f"{stck_name}_group"]
    else:
        return False  

    if up: 
        #get output(s) from node to and connect current_node to it (them) 
        node_out, socket_out = get_node_and_socket_connected_to_output(node_to, "Result") 
        if len(node_out) == 1:
            node_tree.links.new(current_node.outputs["Result"], node_out[0].inputs[socket_out[0]])
        else:
            node_tree.links.new(current_node.outputs["Result"], node_out[0].inputs[socket_out[0]])
            node_tree.links.new(current_node.outputs["Result"], node_out[1].inputs[socket_out[1]])

        #get the nodes connected to the inputs from current_node and connect then to node_to inputs
        
        node_in1, socket_in1 = get_node_and_socket_connected_to_input(current_node, "B")        
        node_in2, socket_in2 = get_node_and_socket_connected_to_input(current_node_group, "Base Color")        
        print(node_in1.name, node_in2.name, socket_in1, socket_in2)
        print(node_to.name, node_group_to.name)
        
        node_tree.links.new(node_in1.outputs[socket_in1], node_to.inputs["B"])
        node_tree.links.new(node_in2.outputs[socket_in2], node_group_to.inputs["Base Color"])
        
        #connect node_to outputs to current_node inputs
        node_tree.links.new(node_to.outputs["Result"], current_node.inputs["B"])
        node_tree.links.new(node_to.outputs["Result"], current_node_group.inputs["Base Color"])        
    
    else:
        # get node_current output(s) and connect node_to tho them 
        node_out, socket_out = get_node_and_socket_connected_to_output(current_node, "Result") 
        if len(node_out) == 1:
            node_tree.links.new(node_to.outputs["Result"], node_out[0].inputs[socket_out[0]])
        else:
            node_tree.links.new(node_to.outputs["Result"], node_out[0].inputs[socket_out[0]])
            node_tree.links.new(node_to.outputs["Result"], node_out[1].inputs[socket_out[1]])


        #get the node_to inputs and connect current_node to them
        node_in1, socket_in1 = get_node_and_socket_connected_to_input(node_to, "B")        
        node_in2, socket_in2 = get_node_and_socket_connected_to_input(node_group_to, "Base Color")        
        
        node_tree.links.new(node_in1.outputs[socket_in1], current_node.inputs["B"])
        node_tree.links.new(node_in2.outputs[socket_in2], current_node_group.inputs["Base Color"])
 
        #connect current_node output to node_to inputs
        node_tree.links.new(current_node.outputs["Result"], node_to.inputs["B"])
        node_tree.links.new(current_node.outputs["Result"], node_group_to.inputs["Base Color"])        
        
    for node in node_tree.nodes: 
        node.select = False
    if up: #moving all current nodes up and all nodes_to down
        moving_all_nodes_from_a_sticker(node_tree, stck_name, -600, 450) #up node
        moving_all_nodes_from_a_sticker(node_tree, sticker_name, 600, -450) #up node
    else: #moving al current nodes down and all nodes_to up
        moving_all_nodes_from_a_sticker(node_tree, stck_name, 600, -450) #up node
        moving_all_nodes_from_a_sticker(node_tree, sticker_name, -600, 450) #up node
       
        
def moving_all_nodes_from_a_sticker(node_tree, sticker_name, offset_X, offset_Y):
    """ moving all the nodes conected to a node_in 
    node_tree  -- the node_tree where the nodes to mov are
    sticker_name -- the name of the sticker to move
    offset_X -- the offsetX to move (positive or negative)
    offset_Y -- the offsetY to move (positive or negative)
    result:
    the nodes are moved
    """

    nodelist = get_all_shader_nodes_from_a_sticker(node_tree, sticker_name)
    
    for nod in reversed(nodelist):
        final_X = nod.location.x + offset_X
        final_Y = nod.location.y + offset_Y
        nod.location.x = final_X
        nod.location.y = final_Y
        nod.select = True

 
def moving_all_nodes_connected(node_in, offset_X, offset_Y):
    """ moving all the nodes conected to a node_in 
    node_in  -- the node where the other nodes are connected in
    offset_X -- the offsetX to move (positive or negative)
    offset_Y -- the offsetY to move (positive or negative)
    result:
    the nodes are moved
    """

    # Eliminamos todas las conexiones y nodos
    node = node_in
    
    nodelist=[]
    
    select_all_nodes_connected(node, nodelist)
    for nod in reversed(nodelist):
        final_X = nod.location.x + offset_X
        final_Y = nod.location.y + offset_Y
        nod.location.x = final_X
        nod.location.y = final_Y
        nod.select = True  




