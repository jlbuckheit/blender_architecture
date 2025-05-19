
import bpy
import numpy as np
from scipy.special import comb
import bmesh

from utils import tools

def make_boat():

    # Define control points
    num_points = 32
    control_points_x = [0, 4, 8, 12]
    control_points_y = [-1, -3, -1, 0]
    control_xy = np.column_stack((control_points_x, control_points_y))
    control_yz = np.column_stack((control_points_x, control_points_y))
    
    # Sample Bézier curves
    empty_dim = np.zeros((num_points, 1))
    gunwale_curve_pts = np.hstack((bezier_curve(control_xy, num_points), empty_dim))
    keel_curve_pts = np.hstack((bezier_curve(control_yz, num_points), empty_dim))
    keel_curve_pts[:, [1, 2]] = keel_curve_pts[:, [2, 1]]  # Swap Y and Z
    #keel_curve_pts[:, 2] = -keel_curve_pts[:, 2]
    
    # Create Blender curve objects
    gunwale_obj = create_curve_object("GunwaleCurve", gunwale_curve_pts)
    keel_obj = create_curve_object("KeelCurve", keel_curve_pts)
        
    # Build mesh bridge between them
    hull = create_strip_between_curves(gunwale_obj, keel_obj)
    #duplicate = hull.copy()
    #duplicate.data = hull.data.copy()
    duplicate = tools.duplicate_object(hull)
    # Mirror over Y axis (negate X scale or apply matrix)
    duplicate = tools.mirror_object_over_cursor(duplicate, mirror_x=False, mirror_y=True, mirror_z=False)
    #join_objects(hull, duplicate)
    tools.join_objects([hull,duplicate])

    tools.merge_duplicate_vertices(hull)
    ### add stern transom
    tools.select_edges_near_x(hull)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.edge_face_add()
    bpy.ops.mesh.select_all(action='DESELECT')

    ### add deck
    tools.select_edges_near_z(hull)
    bpy.ops.mesh.edge_face_add()
    bpy.ops.mesh.inset(thickness=0.1, depth=0.25, use_boundary=True)
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')
    return


# --- Bézier curve sampling ---
def bezier_curve(control_points, num_points=64):
    n = len(control_points) - 1

    def bernstein(i, n, t):
        return comb(n, i) * (t ** i) * ((1 - t) ** (n - i))

    t = np.linspace(0, 1, num_points)
    curve = np.zeros((num_points, 2))
    for i in range(n + 1):
        b = bernstein(i, n, t)[:, np.newaxis]
        curve += b * control_points[i]
    return curve

# --- Create a Blender curve object from 3D points ---
def create_curve_object(name, points):
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new(type='POLY')
    spline.points.add(len(points) - 1)
    
    for i, pt in enumerate(points):
        spline.points[i].co = (*pt, 1.0)

    curve_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(curve_obj)
    return curve_obj

# --- Get evaluated points from a curve object ---
def get_curve_points(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()
    verts = [v.co.copy() for v in mesh.vertices]
    obj_eval.to_mesh_clear()
    return verts

# --- Build a mesh strip between two curves ---
def create_strip_between_curves(curve1_obj, curve2_obj):
    points1 = get_curve_points(curve1_obj)
    points2 = get_curve_points(curve2_obj)

    if len(points1) != len(points2):
        print("The curves must have the same number of evaluated points.")
        return None

    mesh_data = bpy.data.meshes.new("HullMesh")
    obj = bpy.data.objects.new("Hull", mesh_data)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    verts = []

    for p1, p2 in zip(points1, points2):
        v1 = bm.verts.new(p1)
        v2 = bm.verts.new(p2)
        verts.append((v1, v2))

    bm.verts.ensure_lookup_table()

    for i in range(len(verts) - 1):
        v1a, v1b = verts[i]
        v2a, v2b = verts[i + 1]
        bm.faces.new([v1a, v2a, v2b, v1b])

    bm.to_mesh(mesh_data)
    bm.free()

    # Delete the Bézier curve objects after mesh creation
    bpy.data.objects.remove(curve1_obj)
    bpy.data.objects.remove(curve2_obj)

    return obj


