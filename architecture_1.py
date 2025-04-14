
import bpy
from utils import tools, face_utils
import math


def make_arch(
    #arch_size = 2,
    #arch_location = (0, 0, 0),
    #arch_scale = (.5, 1, .5),
    #arch_cut_vertices = 36,
    #legs_dist = 1.0,
    arch_config
):
    
    arch_cut_size = arch_config['size']/2
    arch_cut_location = (
        arch_config['location'][0],
        arch_config['location'][1],
        arch_config['location'][2] - arch_config['size']/4
    )

    arch_cut_rotation = (0, math.pi / 2, 0)

    bpy.ops.mesh.primitive_cube_add(
        size=arch_config['size'], 
        location=arch_config['location'],
        scale=arch_config['scale']
    )
    cube = bpy.context.object
    cube.name = 'arch'
    bpy.ops.mesh.primitive_cylinder_add(
        radius=arch_cut_size/2, 
        depth=arch_config['size'], 
        location=arch_cut_location,
        vertices=arch_config['cut_vertices'],
        rotation=arch_cut_rotation,
    )
    cylinder = bpy.context.object
    cylinder.name = 'arch_cut'
    
    if arch_config['vault']:
        tools.apply_boolean_cut(cube, cylinder, delete = False)
        tools.rotate_around_point(cylinder, point=arch_cut_location)
        tools.apply_boolean_cut(cube, cylinder)
    else:
        tools.apply_boolean_cut(cube, cylinder)

    face_utils.extrude_bottom_faces(cube, distance=arch_config['legs_dist'])

    return cube
    
def add_columns_to_arch(
    arch_config,
    #array_counts,
    radius,
    #depth,
    #location,
    vertices = 36,
    rotation = (0,0,0),
):

    location = (
        arch_config['location'][0] + arch_config['size']/2*arch_config['scale'][0],
        arch_config['location'][1] - arch_config['size']/2*arch_config['scale'][1],
        (2*arch_config['location'][2] - arch_config['legs_dist'])/2
    )
    depth = arch_config['size']*arch_config['scale'][2] + arch_config['legs_dist']
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=depth,
        location=location,
        vertices=vertices,
        rotation=rotation,
    )
    columns = bpy.context.object
    columns.name = 'columns'

    tools.apply_array_modifiers(
        base_object=columns, 
        counts=(arch_config['counts'][0]+1,arch_config['counts'][1]+1,arch_config['counts'][2]), 
        axes=('X', 'Y', 'Z'), 
        spacings=(
            -arch_config['size']*arch_config['scale'][0],
            arch_config['size']*arch_config['scale'][1],
            1,
        )
    )
    
    return columns

def add_capital(
    arch_config,
):    
    location = (
        arch_config['location'][0],
        arch_config['location'][1] - arch_config['size']/2*arch_config['scale'][1],
        #(2*arch_config['location'][2] - arch_config['legs_dist'])/2
        arch_config['location'][2] - arch_config['size']*arch_config['scale'][2]*5/8,
    )
    bpy.ops.mesh.primitive_cube_add(
        size=arch_config['size']/2, 
        location=location,
        scale=(arch_config['scale'][0]*2.2,
               arch_config['scale'][1]*0.8,
               arch_config['scale'][2]*0.5,
              )
    )
    cube = bpy.context.object
    cube.name = 'capital'

    face_utils.bevel_top_bottom_faces(
        cube, 
        bevel_width=arch_config['size']/40, 
        segments=3
    )

    tools.apply_array_modifiers(
        base_object=cube, 
        counts=(arch_config['counts'][0], 
                arch_config['counts'][1] + 1, 
                arch_config['counts'][2], 
               ),
        axes=('X', 'Y', 'Z'), 
        spacings=(
            -arch_config['size']*arch_config['scale'][0],
            arch_config['size']*arch_config['scale'][1],
            1,
        )
    )
    
    return cube

    
def add_keystone_arch(
    arch_config,
    cut_vertices = None
):
    if not cut_vertices:
        cut_vertices = arch_config['cut_vertices']
    arch_cut_size = arch_config['size']/2
    arch_cut_location = (
        arch_config['location'][0] + arch_config['size']/2*arch_config['scale'][0],
        arch_config['location'][1],
        arch_config['location'][2] - arch_config['size']/4
    )

    arch_cut_rotation = (
        math.pi / 2, 
        math.pi / cut_vertices, 
        math.pi / 2
    )

    bpy.ops.mesh.primitive_cylinder_add(
        radius=arch_cut_size/2, 
        depth=arch_config['size']*0.04, 
        location=arch_cut_location,
        vertices=cut_vertices,
        rotation=arch_cut_rotation,
        end_fill_type='NOTHING',
    )
    cylinder = bpy.context.object
    cylinder.name = 'keystone_arch'

    face_utils.delete_faces_with_negative_z_normal(cylinder)
    face_utils.extrude_faces_along_normals(cylinder, distance=arch_config['size']*0.02)
    face_utils.extrude_downward_faces_excluding_keystone(cylinder, distance=arch_config['size']*0.05)
    face_utils.inset_all_faces(cylinder, thickness=0.01, depth=-0.01, use_individual=True)
    
    tools.apply_array_modifiers(
        base_object=cylinder, 
        counts=(arch_config['counts'][0]+1,arch_config['counts'][1],arch_config['counts'][2]), 
        axes=('X', 'Y', 'Z'), 
        spacings=(
            -arch_config['size']*arch_config['scale'][0],
            arch_config['size']*arch_config['scale'][1],
            1,
        )
    )
    
    return cylinder


    