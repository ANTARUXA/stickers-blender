"""
[Blender and Python] Utils library for blender Stickers
Juan R Nouche - October 2024
Email: juan.nouche@antaruxa.com
Antaruxa Stickers - Blender python functions library
Copyright (c) 2024 Antaruxa
--------
"""

import os, imghdr

import bpy
import bmesh
import mathutils
from mathutils import (Vector)

# ==== INTERNAL FUNCTIONS (AUX)

def interpolate_range(value, from_min, from_max, to_min, to_max):
    """Interpolates a value from a numerical source range into a numerical target range
    value    -- the value to interpolate
    from_min -- min value from the source range
    from_max -- max value from the source range
    to_min   -- min value to target range
    to_max   -- max value to target range
    returns:
    the value interpolated in the target range
    """
    # Figure out how 'wide' each range is
    range_from = from_max - from_min
    range_to = to_max - to_min

    # Convert the left range into a 0-1 range (float)
    scaled_value = float(value - from_min) / float(range_from)

    # Convert the 0-1 range into a value in the right range.
    return to_min + (scaled_value * range_to)


def create_a_plane_mesh_with_uvs(x_segments, y_segments, size):
    """Creates a bmesh grid primitive
    x_segments -- integer number of segments in the x axis
    y_segments -- integer number of segments in the y axis 
    size       -- float width (or height) in blender units
    returns:
    bm         -- the bmesh created
    """
    
    bm=bmesh.new() 
    bmesh.ops.create_grid(bm, x_segments = x_segments, y_segments = y_segments, size = size, matrix=mathutils.Matrix.Identity(4), calc_uvs=True)

    ## get max and min vertex x and y to calculate the uvs
    xvert = []
    yvert = []
    for vtx in bm.verts:
        xvert.append (vtx.co.x)
        yvert.append (vtx.co.y)
    maxx = max(xvert)
    minx = min(xvert)
    maxy = max(yvert)
    miny = min(yvert)

    # compute uv
    uv_layer = bm.loops.layers.uv.verify()

    for face in bm.faces:
        for loop in face.loops:
            loop_uv = loop[uv_layer]
            # use interpolates xy vertex coordinate range [minx, maxx] and [miny, maxy] on range uv [0.0, 1.0] 
            loop_uv.uv = interpolate_range(loop.vert.co.x, minx, maxx, 0.0, 1.0), interpolate_range(loop.vert.co.y, miny, maxy, 0.0, 1.0)
            
            # print(f"\tloop index: {loop.index}; UV Coords: {loop[uv_layer].uv}")

            
    return bm

# ==== EXTERNAL FUNCTIONS CHEKINGS

def is_valid_image_imghdr(file_name):
    """Check if the file in file_name path is a valid image
    file_name -- str path containing the file name
    returns:
    bool      -- True or False
    """
    with open(file_name, 'rb') as f:
        header = f.read(32)  # Read the first 32 bytes
        return imghdr.what(None, header) is not None

def is_valid_image_extension(file_name):
    """Check if the file in file_name path has a valid 
    extensions at the moment only .png is a valid extension
    file_name -- str path containing the file name
    returns:
    bool      -- True or False
    """
    #valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    valid_extensions = {'.png'}
    return any(file_name.lower().endswith(ext) for ext in valid_extensions)

def is_there_file_on_path(file_name):
    """Check whether there is a file on this path
    file_name -- str path containing the file name
    returns:
    bool      -- True or False
    """
    return os.path.isfile(file_name)

def check_if_sticker_name_exists(name=""):
    """Check whether the sticker name is already used
    name -- the name of the sticker. We will check if anchor_vertex exists
    returns:
    bool      -- True or False
    """
     
    # finding the objects that may be a sticker
        
    for obj in bpy.data.objects:
        # check if the obj has the sticker_name property
        if "sticker_name" in obj: 
            if obj.sticker_name == name:
                return True
    return False


# ==== EXTERNAL FUNCTIONS GEOMETRY

def create_a_plane_with_segments(x_segments, y_segments, size, name = "sticker", coll = None):
    """Creates a plane object usin a bmesh grid primitive
    x_segments -- integer number of segments in the x axis
    y_segments -- integer number of segments in the y axis 
    size       -- float width (or height) in blender units
    name       -- the name for the plane
    coll       -- the collection where the object will be linked
    returns:
    obje       -- the plane created
    """
   
    bm = create_a_plane_mesh_with_uvs(x_segments, y_segments, size)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    mesh.update()
    bm.free()
    obj = bpy.data.objects.new(name, mesh)

    coll.objects.link(obj)
    
    return obj
    #obj.show_name=True
    
    

def create_empty(name='vertex-parent',coll=None, type='PLAIN_AXES'):
    """Create a empty object to parent with vertex
    name -- the name for the empty 
    coll -- collection where the new empty will be linked
    returns:
    empty -- the empty obj
    """    
    bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
    bpy.context.scene.cursor.rotation_euler = Vector((0.0, 0.0, 0.0))
    #Movemos el cursor al centro y ya no tenemos que frizear

    empty = bpy.data.objects.new(
        f"{name}",
        None,
        )
    empty.empty_display_type = type
    display_size = 1
    if type == 'SPHERE' or type == 'CIRCLE':
        display_size = 0.5
    
    empty.empty_display_size = display_size
    coll.objects.link(empty) #añadimos a la collection
    #print(coll.name)
    return empty

def create_circle(name = 'vertex-parent', coll=None, radius = 1.0):

    bpy.ops.curve.primitive_bezier_circle_add(radius = radius, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    ob = bpy.context.active_object
    ob.name = name
    return ob
    
    




def parent_object_to_vertex_in_mesh(obj, parent_obj, index):
    """Parenting an object to a selected vertex in a mexh
    obj        -- the object to parent
    parent_obj -- the object to parent to
    index      -- the index of the vertex to parent t
    """    
    obj.parent = parent_obj
    obj.parent_type = 'VERTEX'
    obj.parent_vertices = [index] * 3 
    
def create_constraint_to_object(obj=None, target_obj=None, kind='TRACK_TO', name='default_constraint'):
    """Create a empty object to parent with vertex
    obj        -- the object where the constraint will be
    target_obj -- if any
    kind       -- kind of constraint
    name       -- the name that the constraint will have
    
    returns:
    constraint -- the constraint obj
    
    kind of constraints list link
    https://upbge.org/docs/latest/api/bpy_types_enum_items/constraint_type_items.html
    """      
    constraint = obj.constraints.new(kind)

    constraint.name = name
    if target_obj:
        constraint.target = target_obj
    if kind == 'SHRINKWRAP':
        constraint.use_track_normal = True
        constraint.track_axis = 'TRACK_Z'
        constraint.shrinkwrap_type = 'TARGET_PROJECT'
        constraint.wrap_mode = 'ON_SURFACE'
    else:
        constraint.target_space='LOCAL'
        constraint.track_axis = 'TRACK_Y'
        constraint.up_axis = 'UP_Y'
        
    return constraint

def add_driver_to_object(driven_obj, driver_obj, prop, data_path, var_name, expr, ndx = -1, transf_type = 'LOC_X', space = 'WORLD_SPACE'):
    
    ''' Add driver_obj to a material node prop, driven_obj by target dataPath
        driven_obj -- the source object "driven_obj"
        driver_obj  -- the target object "driver_obj"
        prop        -- the name of the property to be drived like rotation_euler, translation, etc.
        data_path   -- property or expresion in target that drives (rotation_euler.x, trasnslate.y)
        var_name    -- name of variable that should be created
        expr        -- expression to process with driver
        ndx         -- -1 simple value >= 0 index for the default value
        trasnf_type -- type of transformation on the target (LOC_X, LOC_Y, LOC_Z, ROT_X, ROT_Y, ...)
        space       -- space where the transformation is applide (WORLD_SPACE, TRANSFORM_SPACE,...)
    '''
    if ndx >= 0:
        fcurve = driven_obj.driver_add(prop, ndx)
    else:
        fcurve = driven_obj.driver_add(prop)
        
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



# ==== INTERNAL FUNCTIONS PROPERTIES

def create_custom_property(object = None, 
          name="", 
          subtype='FLOAT', 
          default = None, 
          value = None):
    """Create a a custom property to an object
    object     -- the object that will have the property 
    name       -- the name in interface
    subtype    -- type of property can be 'BOOLEAN' (default), 'INT', 'FLOAT', 'STRING', 'ENUM', 'POINTER', 'COLLECTION'
    default    -- default value for the propertie
    
    returns:
    the property setted
    
    use of custom properties id_properties_ui
    https://blender.stackexchange.com/questions/302333/how-can-i-add-a-custom-property-with-a-dynamically-defined-name-to-an-object
    types and subtypes
    https://docs.blender.org/api/current/bpy.types.Property.html#bpy.types.Property
    """      
    
    obj = object
    obj[name] = value
    ui_prop = obj.id_properties_ui(name)
    ui_prop.update(
        subtype = subtype,
        default = default,
        )
    obj.select_set(state = True) #to update interface

def delete_custom_property(object = None, name=""):
    
    """Delete a custom property from an object
    object     -- the object which have the property 
    name       -- the name in interface
    
    returns:
    the property is deleted
    
    use of custom properties id_properties_ui
    https://blender.stackexchange.com/questions/302333/how-can-i-add-a-custom-property-with-a-dynamically-defined-name-to-an-object
    types and subtypes
    https://docs.blender.org/api/current/bpy.types.Property.html#bpy.types.Property
    """      

    obj = object
    del obj[name]
    obj.select_set(state = True) #to update interface

# ==== INTERNAL FUNCTIONS PROPERTIES

def create_custom_properties_for_sticker(obj = None, sticker_name = ""):
    """Create the custom properties needed by the sticker
    obj        -- the object which will have the property 
    name       -- the name of the sticker 
    
    returns:
    the properties will be setted
    
    """      
    # == first sticker name

    property_name = 'sticker_name'
    subtype = 'BYTE_STRING'
    default = ""
    value = sticker_name
   
    create_custom_property(obj, property_name, subtype, default, value)
    
    # == show hide plane
    
