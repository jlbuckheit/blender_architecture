
import bpy
import math
import mathutils
import bmesh
from mathutils.bvhtree import BVHTree
import random

import tqdm

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


def select_n_intersecting_edges(source_obj, target_obj, n=None):
    if source_obj.type != 'MESH' or target_obj.type != 'MESH':
        print("Both objects must be meshes.")
        return []

    depsgraph = bpy.context.evaluated_depsgraph_get()
    source_eval = source_obj.evaluated_get(depsgraph)
    target_eval = target_obj.evaluated_get(depsgraph)

    target_bvh = BVHTree.FromObject(target_eval, depsgraph)
    if not target_bvh:
        print("Could not build BVH tree from target object.")
        return []

    # Prepare source mesh for editing
    bpy.ops.object.mode_set(mode='OBJECT')
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    source_obj.select_set(True)
    bpy.context.view_layer.objects.active = source_obj
    bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(source_obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    source_matrix = source_obj.matrix_world

    # Find all intersecting edges and store their midpoints
    intersecting_edges = []
    edge_midpoints = {}

    for edge in bm.edges:
        v1_world = source_matrix @ edge.verts[0].co
        v2_world = source_matrix @ edge.verts[1].co
        direction = v2_world - v1_world
        length = direction.length
        if length == 0:
            continue
        direction.normalize()

        hit = target_bvh.ray_cast(v1_world, direction, length)
        if hit[0] is not None:
            intersecting_edges.append(edge)
            edge_midpoints[edge] = (v1_world + v2_world) / 2

    if not intersecting_edges:
        print("No intersecting edges found.")
        return []

    # If n is None or exceeds available, just select all
    if n is None or n >= len(intersecting_edges):
        selected = intersecting_edges
    else:
        # Start with a random edge
        selected = [random.choice(intersecting_edges)]
        remaining = set(intersecting_edges) - set(selected)

        while len(selected) < n and remaining:
            last_mid = edge_midpoints[selected[-1]]
            # Sort remaining by distance to last selected midpoint
            next_edge = min(remaining, key=lambda e: (edge_midpoints[e] - last_mid).length)
            selected.append(next_edge)
            remaining.remove(next_edge)

    # Deselect everything and highlight selected edges
    for e in bm.edges:
        e.select = False
    ### TODO: would have liked this to be a separate function
    #total_midpoint = mathutils.Vector((0, 0, 0))
    for e in selected:
        e.select = True
        #total_midpoint += edge_midpoints[e]
    #average_midpoint = total_midpoint / len(selected)
    
    bmesh.update_edit_mesh(source_obj.data, loop_triangles=False, destructive=False)
    
    edge_pairs = get_selected_edge_vertex_pairs(source_eval)
    
    return edge_pairs


def select_apply_scale_deselect(object_name):
    # Get the object by name
    obj = bpy.data.objects.get(object_name)
    
    if obj is None:
        print(f"Object '{object_name}' not found.")
        return
    
    # Select the object
    obj.select_set(True)
    
    # Make the object the active object
    bpy.context.view_layer.objects.active = obj
    
    # Apply the scale
    bpy.ops.object.transform_apply(scale=True)
    
    # Deselect the object
    obj.select_set(False)
    
    print(f"Applied scale to '{obj.name}' and deselected it.")

    
def deselect_all_and_object_mode():
    # Make sure you're in Object Mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

def get_selected_edge_vertex_pairs(obj):
    """Return selected edges from the given object as sorted vertex index pairs."""
    original_mode = obj.mode
    if original_mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(obj.data)
    edge_pairs = []

    for e in bm.edges:
        if e.select:
            v1, v2 = e.verts[0].index, e.verts[1].index
            edge_pairs.append(tuple(sorted((v1, v2))))

    # Restore mode if we changed it
    if original_mode != 'EDIT':
        bpy.ops.object.mode_set(mode=original_mode)

    return edge_pairs


def select_edges_by_vertex_pairs(obj, edge_pairs):
    """Select edges on the given object that match the sorted vertex index pairs."""
    original_mode = obj.mode
    if original_mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(obj.data)

    for e in bm.edges:
        e.select = False

    for e in bm.edges:
        v1, v2 = e.verts[0].index, e.verts[1].index
        if tuple(sorted((v1, v2))) in edge_pairs:
            e.select = True

    bmesh.update_edit_mesh(obj.data, False)

    # Restore mode if we changed it
    if original_mode != 'EDIT':
        bpy.ops.object.mode_set(mode=original_mode)

def vec_deg2rad(rotation_degrees):
    return tuple(math.radians(a) for a in rotation_degrees)

def mirror_object_over_cursor(obj, mirror_x=False, mirror_y=False, mirror_z=False):
    """
    Mirrors the given object across the 3D cursor position along specified axes.
    """
    # Get 3D cursor location
    cursor_loc = bpy.context.scene.cursor.location.copy()
    mirrored = obj
    
    # Create a duplicate
    #mirrored = obj.copy()
    #mirrored.data = obj.data.copy()
    #bpy.context.collection.objects.link(mirrored)

    # Translate to origin relative to cursor
    to_cursor = mathutils.Matrix.Translation(-cursor_loc)
    from_cursor = mathutils.Matrix.Translation(cursor_loc)

    # Create a mirror scale matrix
    scale = [ -1 if axis else 1 for axis in (mirror_x, mirror_y, mirror_z) ]
    mirror_matrix = mathutils.Matrix.Scale(scale[0], 4, (1, 0, 0)) @ \
                    mathutils.Matrix.Scale(scale[1], 4, (0, 1, 0)) @ \
                    mathutils.Matrix.Scale(scale[2], 4, (0, 0, 1))

    # Combine transformations: to cursor -> mirror -> back
    transform = from_cursor @ mirror_matrix @ to_cursor

    # Apply to duplicate
    mirrored.matrix_world = transform @ obj.matrix_world

    # Optional: rename
    mirrored.name = f"{obj.name}_Mirrored"

    return mirrored


def subdivide_mesh(obj, cuts=4):
    """
    Subdivides all edges of the mesh uniformly using BMesh.
    """
    if obj.type != 'MESH':
        raise TypeError("Object must be a mesh")

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    bm = bmesh.from_edit_mesh(obj.data)
    bm.verts.ensure_lookup_table()

    # Select all edges
    edges_to_subdivide = [e for e in bm.edges]

    # Subdivide them
    bmesh.ops.subdivide_edges(
        bm,
        edges=edges_to_subdivide,
        cuts=cuts,
        use_grid_fill=True,
        smooth=0.0
    )

    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')





def get_edges_with_smallest_x(obj, n=1):
    if obj.type != 'MESH':
        raise TypeError("Selected object must be a mesh.")

    # Enter object edit mode and get bmesh
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)

    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    # Get edges with average X value of their vertices
    edge_avg_x = [(e, (e.verts[0].co.x + e.verts[1].co.x) / 2.0) for e in bm.edges]
    edge_avg_x.sort(key=lambda pair: pair[1])  # Sort by average X

    # Select the top `n` edges with smallest X
    for e, _ in edge_avg_x[:n]:
        e.select = True

    # Deselect all other edges
    for e, _ in edge_avg_x[n:]:
        e.select = False

    bmesh.update_edit_mesh(obj.data, loop_triangles=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    return [e for e, _ in edge_avg_x[:n]]

def make_face_from_selected_edges(obj):
    if obj.type != 'MESH':
        raise TypeError("Selected object must be a mesh.")

    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)

    # Get selected edges
    selected_edges = [e for e in bm.edges if e.select]

    if not selected_edges:
        print("No edges selected.")
        return None

    # Collect unique vertices from selected edges
    verts_set = set()
    for edge in selected_edges:
        verts_set.update(edge.verts)

    verts = list(verts_set)

    if len(verts) < 3:
        print("Need at least 3 vertices to create a face.")
        return None

    try:
        face = bm.faces.new(verts)
        bmesh.update_edit_mesh(obj.data)
        print("Face created.")
        return face
    except ValueError:
        print("Face already exists or vertices not in correct order.")
        return None


def merge_duplicate_vertices(obj, distance=0.0001):
    """
    Merges duplicate vertices in a mesh object using bmesh (context-independent).
    """
    if obj.type != 'MESH':
        print(f"Object '{obj.name}' is not a mesh.")
        return

    # Ensure object is in OBJECT mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Get mesh data
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # Merge vertices within the given distance
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=distance)

    # Write back to mesh
    bm.to_mesh(mesh)
    bm.free()

    print(f"Merged vertices in '{obj.name}' with threshold: {distance}")

def select_edges_near_z(obj, tolerance=0.01):
    # Ensure we're in object mode to manipulate the selection
    bpy.ops.object.mode_set(mode='OBJECT')

    # Deselect all edges first
    obj.data.edges.foreach_set("select", [False] * len(obj.data.edges))

    # Iterate through all edges of the object
    for edge in obj.data.edges:
        # Check the z-values of the vertices in the edge
        v1 = obj.data.vertices[edge.vertices[0]].co
        v2 = obj.data.vertices[edge.vertices[1]].co
        
        # Check if both vertices are near z=0
        if abs(v1.z) < tolerance and abs(v2.z) < tolerance:
            edge.select = True

    # Switch back to edit mode to see the selection
    bpy.ops.object.mode_set(mode='EDIT')

def select_edges_near_x(obj, tolerance=0.01):
    # Ensure we're in object mode to manipulate the selection
    bpy.ops.object.mode_set(mode='OBJECT')

    # Deselect all edges first
    obj.data.edges.foreach_set("select", [False] * len(obj.data.edges))

    # Iterate through all edges of the object
    for edge in obj.data.edges:
        # Check the z-values of the vertices in the edge
        v1 = obj.data.vertices[edge.vertices[0]].co
        v2 = obj.data.vertices[edge.vertices[1]].co
        
        # Check if both vertices are near z=0
        if abs(v1.x) < tolerance and abs(v2.x) < tolerance:
            edge.select = True

    # Switch back to edit mode to see the selection
    bpy.ops.object.mode_set(mode='EDIT')