
import bpy
import math
import mathutils
import bmesh

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

    # Select downward-facing faces, excluding keystone region
    selected_faces = []
    for f in bm.faces:
        world_center = obj.matrix_world @ f.calc_center_median()
        if f.normal.z > z_thresh and world_center.z < keystone_z_limit:
            f.select = True
            selected_faces.append(f)
    # Dissolve the selected faces
    if selected_faces:
        bmesh.ops.dissolve_faces(bm, faces=selected_faces, use_verts=True)
        bmesh.update_edit_mesh(obj.data)

    bpy.ops.mesh.select_all(action='DESELECT')
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


def inset_all_faces(obj, thickness=0.1, depth=0.0, use_individual=False):
    """
    Insets all faces of a mesh object.

    :param obj: The Blender object to modify (must be a mesh)
    :param thickness: The inset thickness
    :param depth: Extrusion depth along normals after inset
    :param use_individual: Whether to inset faces individually
    """
    if obj.type != 'MESH':
        print(f"Object {obj.name} is not a mesh.")
        return

    # Set object as active and go to edit mode
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')

    # Work with BMesh
    bm = bmesh.from_edit_mesh(obj.data)
    bm.faces.ensure_lookup_table()

    # Select all faces
    for face in bm.faces:
        face.select = True

    bmesh.update_edit_mesh(obj.data)

    # Inset faces
    bpy.ops.mesh.inset(
        thickness=thickness,
        depth=depth,
        use_individual=use_individual
    )

    # Update mesh and return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

