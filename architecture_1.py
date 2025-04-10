
import bpy
import tools
import math


def make_arch(
    arch_size = 2,
    arch_location = (0, 0, 0),
    arch_scale = (.5, 1, .5),
    arch_cut_vertices = 36,
    legs_dist = 1.0,
):
    
    arch_cut_size = arch_size/2
    arch_cut_location = (
        arch_location[0],
        arch_location[1],
        arch_location[2] - arch_size/4
    )

    arch_cut_rotation = (0, math.pi / 2, 0)

    bpy.ops.mesh.primitive_cube_add(
        size=arch_size, 
        location=arch_location,
        scale=arch_scale
    )
    cube = bpy.context.object
    cube.name = 'arch'
    bpy.ops.mesh.primitive_cylinder_add(
        radius=arch_cut_size/2, 
        depth=arch_size, 
        location=arch_cut_location,
        vertices=arch_cut_vertices,
        rotation=arch_cut_rotation,
    )
    cylinder = bpy.context.object
    cylinder.name = 'arch_cut'
    
    tools.apply_boolean_cut(cube, cylinder)

    tools.extrude_bottom_faces(cube, distance=legs_dist)
    
    return cube

def add_columns_to_arch(
    arch_hyp,
    array_counts,
    #radius,
    #depth,
    #location,
    vertices = 36,
    rotation = (0,0,0),
):

    location = (
        arch_hyp['location'][0] + arch_hyp['size']/2*arch_hyp['scale'][0],
        arch_hyp['location'][1] - arch_hyp['size']/2*arch_hyp['scale'][1],
        (2*arch_hyp['location'][2] - arch_hyp['legs_dist'])/2
    )
    depth = arch_hyp['size']*arch_hyp['scale'][2] + arch_hyp['legs_dist']
    radius = .25
    
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
        counts=(2,4,1), 
        axes=('X', 'Y', 'Z'), 
        spacings=(
            -arch_hyp['size'],
            arch_hyp['size']*arch_hyp['scale'][1]*2,
            1,
        )
    )

    
    return columns