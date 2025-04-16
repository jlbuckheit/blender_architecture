
import bpy
import math
import mathutils
import bmesh


def apply_boolean_cut(base_object, cutting_object, operation='DIFFERENCE', delete=True):
    """
    Applies a Boolean operation (cut) between two objects.

    :param base_object: The object to apply the cut to (e.g., the cube).
    :param cutting_object: The object that performs the cut (e.g., the cylinder).
    :param operation: The type of Boolean operation ('DIFFERENCE', 'UNION', or 'INTERSECT').
    """
    # Set the base object as the active object
    bpy.context.view_layer.objects.active = base_object

    # Add a Boolean modifier to the base object
    boolean_modifier = base_object.modifiers.new(name="BooleanCut", type='BOOLEAN')

    # Set the operation for the Boolean modifier
    boolean_modifier.operation = operation

    # Set the cutting object
    boolean_modifier.object = cutting_object

    # Apply the modifier to finalize the operation
    bpy.ops.object.modifier_apply(modifier=boolean_modifier.name)

    # Optional: Delete the cutting object after the operation is applied
    bpy.data.objects[cutting_object.name].select_set(True)
    if delete:
        bpy.ops.object.delete()




def apply_array_modifier(
    base_object, 
    count=1, 
    axis=None, 
    spacing=1
):
    """
    Applies an Array Modifier to a single dimension.

    Args:
        base_object: The object to duplicate.
        count: The number of duplicates along the specified axis.
        axis: The axis along which to apply the array ('X', 'Y', or 'Z').
        spacing: The spacing between duplicates.
    """
    if count < 2:
        return  # No need to apply an array modifier if count is less than 2

    # Add an Array Modifier
    array_modifier = base_object.modifiers.new(name=f"Array_{axis}", type='ARRAY')
    array_modifier.count = count
    array_modifier.use_relative_offset = False
    array_modifier.use_constant_offset = True

    # Reset offsets to zero for all axes
    array_modifier.constant_offset_displace = [0, 0, 0]

    
    # Set spacing for the specified axis
    if axis.upper() == "X":
        array_modifier.constant_offset_displace[0] = spacing
    elif axis.upper() == "Y":
        array_modifier.constant_offset_displace[1] = spacing
    elif axis.upper() == "Z":
        array_modifier.constant_offset_displace[2] = spacing
    else:
        print(f'Invalid dimension {axis}, returning.')

def apply_array_modifiers(
    base_object, 
    counts=(1,1,1), 
    axes=('X', 'Y', 'Z'), 
    spacings=(1,1,1)
):
    for i in range(len(axes)):
        apply_array_modifier(
            base_object=base_object, 
            count=counts[i], 
            axis=axes[i], 
            spacing=spacings[i]
        )


def join_objects(objs, keep_ind=0):
    # Deselect all first
    bpy.ops.object.select_all(action='DESELECT')

    for obj in objs:
        # Select the object
        obj.select_set(True)

        # Make it the active object temporarily to apply modifiers
        bpy.context.view_layer.objects.active = obj

        # Apply any Array modifiers before joining
        for mod in obj.modifiers:
            if mod.type == 'ARRAY':
                bpy.ops.object.modifier_apply(modifier=mod.name)

    # Set the actual final active object (the one to keep after join)
    bpy.context.view_layer.objects.active = objs[keep_ind]

    # Join selected objects
    bpy.ops.object.join()

def rotate_around_point(obj, point=(0,0,0), axis='Z', angle_deg=90):
    """
    Rotate an object around a specific point in space.

    Parameters:
    - obj: The Blender object to rotate
    - point: A tuple (x, y, z) representing the pivot point
    - axis: 'X', 'Y', or 'Z' for the rotation axis
    - angle_deg: The angle in degrees to rotate
    """
    # Convert angle to radians
    angle_rad = math.radians(angle_deg)

    # Create the rotation matrix around the point
    rotation_axis = axis.upper()
    rot_matrix = mathutils.Matrix.Translation(point) @ \
                 mathutils.Matrix.Rotation(angle_rad, 4, rotation_axis) @ \
                 mathutils.Matrix.Translation(-mathutils.Vector(point))

    # Apply the rotation to the object's matrix
    obj.matrix_world = rot_matrix @ obj.matrix_world

def duplicate_object(obj, offset=(0, 0, 0)):
    """
    Duplicates an object along with its mesh data.

    Parameters:
    - obj: The Blender object to duplicate
    - offset: A (x, y, z) tuple to move the duplicate after creation

    Returns:
    - The new duplicated object
    """
    # Copy the object and its mesh data
    new_obj = obj.copy()
    new_obj.data = obj.data.copy()
    #new_obj.name = obj.name + "_Copy"

    # Apply offset to location
    new_obj.location = (
        obj.location.x + offset[0],
        obj.location.y + offset[1],
        obj.location.z + offset[2]
    )

    # Link new object to the current collection
    bpy.context.collection.objects.link(new_obj)

    print(f"Duplicated '{obj.name}' -> '{new_obj.name}' at offset {offset}")
    return new_obj

def add_sun(
    loc = (0.0, 0.0, 512.0), 
    direction = (0.0, 0.0, -120.0)
):

    # Create a new sun lamp data block
    sun_data = bpy.data.lights.new(name="Sun", type='SUN')
    
    # Create a new object with the lamp data
    sun_object = bpy.data.objects.new(name="Sun", object_data=sun_data)
    
    # Link the lamp object to the current collection
    bpy.context.collection.objects.link(sun_object)
    
    # Set the location of the sun lamp (optional)
    sun_object.location = loc
    
    sun_object.rotation_euler = (math.radians(60), 0, math.radians(45))

    return

def set_render_engine():

    # Set render engine to Cycles
    bpy.context.scene.render.engine = 'CYCLES'
    
    # Set device to GPU
    bpy.context.scene.cycles.device = 'GPU'
    
    # Optional: make sure GPU compute is enabled in preferences (needed in some setups)
    # This part affects user preferences, not just the current scene
    bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'  # or 'OPTIX' or 'HIP' or 'METAL'
    
    # Enable all available devices
    bpy.context.preferences.addons['cycles'].preferences.get_devices()
    for device in bpy.context.preferences.addons['cycles'].preferences.devices:
        device.use = True

def delete_materials_except_base(base_name="Material"):
    for mat in bpy.data.materials:
        #if mat.users == 0 and mat.name != base_name:
            bpy.data.materials.remove(mat)
            print(f"Material deleted: {mat}")

def object_exists(object_name):
    for obj in bpy.context.scene.objects:
        if obj.name == object_name:
            return True
    return False

def delete_all_except(exceptions):
    bpy.ops.object.select_all(action='SELECT')
    for obj in bpy.context.scene.objects:
        if obj.name in exceptions:
            bpy.data.objects[obj.name].select_set(False)
    bpy.ops.object.delete()
    return