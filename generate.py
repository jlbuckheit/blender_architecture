
import bpy
import importlib
import os

from utils import tools, face_utils, blender_io
import architecture_1
import textures
#import landscape
#from terrain import river_network
from terrain import general
importlib.reload(tools)
importlib.reload(face_utils)
importlib.reload(blender_io)
importlib.reload(architecture_1)
importlib.reload(textures)
#importlib.reload(landscape)
#importlib.reload(river_network)
importlib.reload(general)

### TODO:
# - add brick texture
# - figure out how to make keystone z_thresh a function of vertices (stones)
# - dome/folia generator
# - landscape logic:
### - function to get edge intersection of land/water
### - function to randomly select some subset
### - place structures along subset
### - function to randomly select landscape vertex above water
### - make pedestal/stairs, the bottom face of which is below landscape
# - refactor


def generate():

    obj_exceptions = ['landscape']
    water_offset = -84
    
    # Delete all existing objects to start fresh
    tools.delete_all_except(obj_exceptions)
    tools.delete_materials_except_base()

    tools.set_render_engine()
    tools.add_sun()

    if 'landscape' not in obj_exceptions:
        landscape = general.get_landscape(water_offset)
    water = general.get_ocean()

    ### hyp
    structure_center = (0,0,0)
    arch_config = {
        'size': 4,
        'location': (12.0, -9.0, 4.0), #(6.5, -3.0, 4.0)
        'scale': (0.5, 0.75, 0.5),
        'cut_vertices': 72,
        'legs_dist': 3,
        'counts': (1,7,1),
        'vault': False,
    }



    arch_east = architecture_1.make_arch(arch_config)
    
    #acs = 6
    #ac_xs = 0.75
    #acly = abs(acs - (arch_config['size']*ac_xs) + ac_xs) + abs(arch_config['location'][1])
    #acly = abs(0.5*acs + 0.5*arch_config['size'] + 2*ac_xs -2) + abs(arch_config['location'][1])
    arch_corner_config = {
        'size': 6,
        'location': (12.0, -12.75, 6.0), #(6.5, -6.75, 6.0)
        'scale': (0.75, 0.75, 0.5),
        'cut_vertices': 72,
        'legs_dist': 4.5,
        'counts': (1,1,1),
        'vault': True,
    }
    arch_corner = architecture_1.make_arch(arch_corner_config)
    bpy.ops.mesh.primitive_cube_add(
        size=arch_corner_config['size']*0.5, 
        location=(
            arch_corner_config['location'][0],
            arch_corner_config['location'][1],
            arch_corner_config['location'][2] - arch_corner_config['size']*0.25,
        ),
        scale=(1,1,1)
    )
    corner_tower = bpy.context.object
    face_utils.extrude_bottom_faces(corner_tower, distance=arch_corner_config['legs_dist'] - arch_corner_config['size']*0.25)
    tools.join_objects([arch_corner, corner_tower])

    tools.apply_array_modifiers(
        base_object=arch_east, 
        counts=arch_config['counts'],
        axes=('X', 'Y', 'Z'), 
        spacings=(0,arch_config['size']*arch_config['scale'][1],0)
    )

    keystones = architecture_1.add_keystone_arch(arch_config, cut_vertices=25)

    tools.join_objects([arch_east, keystones])
    
    #columns = architecture_1.add_columns_to_arch(
    #    arch_config,
    #    #array_counts = (2,4,1),
    #    radius=0.25,
    #    vertices = 36,
    #)
    #tools.join_objects([arch_east, columns])

    capitals = architecture_1.add_capital(
        arch_config,
    )
    tools.join_objects([arch_east, capitals])
    tools.join_objects([arch_east, arch_corner])

    arch_east = tools.duplicate_object(arch_east)
    tools.rotate_around_point(arch_east, angle_deg=90)
    arch_north = tools.duplicate_object(arch_east)
    tools.rotate_around_point(arch_east, angle_deg=180)
    arch_west = tools.duplicate_object(arch_east)
    tools.rotate_around_point(arch_east, angle_deg=270)

