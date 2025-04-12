
import bpy
import math
import mathutils
import bmesh


def apply_boolean_cut(base_object, cutting_object, operation='DIFFERENCE'):
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
    bpy.ops.object.delete()


def extrude_bottom_faces(object, distance=1.0):
    """
    Extrudes the bottom faces of a given object, based on their normal direction.

    :param object: The object whose bottom faces will be extruded.
    :param distance: The distance to extrude the faces.
    """
    # Switch to Edit Mode to work with the mesh
    bpy.context.view_layer.objects.active = object
    bpy.ops.object.mode_set(mode='EDIT')

    # Deselect all faces
    bpy.ops.mesh.select_all(action='DESELECT')

    # Switch to face selection mode
    bpy.ops.mesh.select_mode(type='FACE')

    # Get the mesh data of the object
    mesh = object.data

    # Switch to Object mode to access mesh data
    bpy.ops.object.mode_set(mode='OBJECT')

    # Loop through all faces and select the ones with a normal facing down (negative Z direction)
    for face in mesh.polygons:
        if face.normal.z == -1.0:  # Check if the Z component of the normal is negative (faces pointing down)
            face.select = True  # Select the face

    # Switch back to Edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Extrude the selected faces (move them along the Z axis)
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, -distance)})

    # Return to Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')

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
    loc = (0.0, 0.0, 120.0), 
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
    
    sun_object.rotation_euler = (math.radians(30), 0, math.radians(45))

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


def bevel_top_bottom_faces(
    obj, 
    bevel_width=0.1, 
    segments=3,
    profile=0.1,
):
    # Ensure we're in object mode and select the object
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Switch to edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Create a BMesh from the object
    bm = bmesh.from_edit_mesh(obj.data)
    bm.normal_update()

    # Deselect everything
    for f in bm.faces:
        f.select = False

    # Get bounding box Z values
    z_coords = [v.co.z for v in bm.verts]
    min_z = min(z_coords)
    max_z = max(z_coords)
    threshold = 1e-5

    # Select top and bottom faces
    top_faces = [f for f in bm.faces if all(abs(v.co.z - max_z) < threshold for v in f.verts)]
    bottom_faces = [f for f in bm.faces if all(abs(v.co.z - min_z) < threshold for v in f.verts)]

    # Collect edges from those faces
    bevel_edges = set()
    for f in top_faces + bottom_faces:
        bevel_edges.update(f.edges)

    # Deselect all edges first
    for e in bm.edges:
        e.select = False

    # Select only the desired edges
    for e in bevel_edges:
        e.select = True

    # Bevel the selected edges
    bmesh.ops.bevel(
        bm,
        geom=list(bevel_edges),
        offset=bevel_width,
        segments=segments,
        profile=profile,
        affect='EDGES'
    )

    # Update and exit edit mode
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')


def delete_faces_with_negative_z_normal(obj=None, threshold=0.0):
    """
    Deletes all faces from the given object that have a normal.z < threshold.
    
    Parameters:
    - obj: The mesh object to operate on. If None, uses the active object.
    - threshold: A float value to compare against the face normal's Z component.
    """
    if obj is None:
        obj = bpy.context.object

    if obj is None or obj.type != 'MESH':
        print("No valid mesh object found.")
        return

    # Enter Edit Mode
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(rotation=True)
    bpy.ops.object.mode_set(mode='EDIT')

    # Get BMesh and update normals
    bm = bmesh.from_edit_mesh(obj.data)
    bm.normal_update()

    # Find faces with Z-normal less than threshold
    faces_to_delete = [f for f in bm.faces if f.normal.z < threshold]

    # Delete those faces
    bmesh.ops.delete(bm, geom=faces_to_delete, context='FACES')

    # Update the mesh and return to Object Mode
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    #print(f"Deleted {len(faces_to_delete)} faces with normal.z < {threshold}")

def extrude_faces_along_normals(obj, distance=0.1, threshold=0.3):
    ### TODO: grabbing outer faces is janky and should be made into a tools function
    # Get the active object
    #obj = bpy.context.active_object
    if obj is None or obj.type != 'MESH':
        print("Active object is not a mesh")
        return

    # Ensure we're in object mode before switching to edit
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='EDIT')

    # Get bmesh from the object
    mesh = bmesh.from_edit_mesh(obj.data)
    mesh.faces.ensure_lookup_table()

    # Select all faces
    for face in mesh.faces:
        face.select = True

    bpy.ops.mesh.extrude_region_shrink_fatten(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, 
                                              TRANSFORM_OT_shrink_fatten={
                                                  "value":-distance, "use_even_offset":False, "mirror":False, 
                                                  "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', 
                                                  "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, 
                                                  "snap":False, "release_confirm":False, "use_accurate":False
                                              })
    
    ###
    ###
    select_outer_faces_facing_up()
                                 
    bpy.ops.mesh.extrude_region_shrink_fatten(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":True, "mirror":False}, 
                                              TRANSFORM_OT_shrink_fatten={
                                                  "value":-distance, "use_even_offset":False, "mirror":False, 
                                                  "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', 
                                                  "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, 
                                                  "snap":False, "release_confirm":False, "use_accurate":False
                                              })

    #print(f"Extruded all faces along normals by {distance} units")


def select_outer_faces_facing_up(z_thresh=0.01, flat_thresh=0.01, y_thresh=0.9999999999):
    obj = bpy.context.active_object
    if obj is None or obj.type != 'MESH':
        print("Select a mesh object.")
        return

    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    bm.faces.ensure_lookup_table()

    # Clear selection
    for face in bm.faces:
        face.select = False

    # Normal transformation: object space → world space
    normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()

    for face in bm.faces:
        world_normal = normal_matrix @ face.normal
        world_normal.normalize()

        # Select if the face is mostly facing upward (positive Z), but not perfectly vertical or flat
        if world_normal.z < z_thresh and abs(world_normal.z) > flat_thresh:
            face.select = True
        if abs(world_normal.y) > 0.9999999999:
            face.select = True

    bmesh.update_edit_mesh(obj.data, loop_triangles=True)
    print("Selection complete.")

def extrude_downward_faces_excluding_keystone(obj=None, z_thresh=0.9, keystone_ratio=0.5, distance=1.0):
    ### TODO: z_thresh should be a function of how many vertices (stones) in arch
    if obj is None:
        obj = bpy.context.object

    if not obj or obj.type != 'MESH':
        print("No valid mesh object selected.")
        return

    # Ensure Object Mode and apply rotation
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(rotation=True)

    # Calculate bounding box height
    z_coords = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
    min_z = min(v.z for v in z_coords)
    max_z = max(v.z for v in z_coords)
    height = max_z - min_z
    keystone_z_limit = max_z - (height * keystone_ratio)
    
    # Switch to Edit Mode and get BMesh
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    bm.faces.ensure_lookup_table()

    # Deselect everything first
    for f in bm.faces:
        f.select = False

    # Select faces that face downward, excluding those near the top
    for f in bm.faces:
        world_center = obj.matrix_world @ f.calc_center_median()
        if f.normal.z > z_thresh and world_center.z < keystone_z_limit:
            f.select = True

    # Update selection
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, -distance)})
    bpy.ops.object.mode_set(mode='OBJECT')

    print("Selected downward-facing faces, excluding keystone region.")