
import bpy
import importlib
import os

from utils import tools, face_utils, blender_io
import architecture_1
import textures
#import landscape
from terrain import river_network
importlib.reload(tools)
importlib.reload(face_utils)
importlib.reload(blender_io)
importlib.reload(architecture_1)
importlib.reload(textures)
#importlib.reload(landscape)
importlib.reload(river_network)

### TODO:
# - add brick texture
# - figure out how to make keystone z_thresh a function of vertices (stones)
# - dome/folia generator
# - landscape generator crashes in blender at small scales. 
### - keep function but with warning, default to loading files generated outside blender
### - or is this just because I set 'disc_radius': 0.1,, test this first, it is nice to generate in blender
# - refactor


def generate():
    # Delete all existing objects to start fresh
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    tools.delete_materials_except_base()

    tools.set_render_engine()
    tools.add_sun()
    
    #npz_path = 'C:/Users/jlbuc/my_python/repos/blender_architecture/terrain/river_network.npz'
    #landscape = blender_io.import_npz_mesh(npz_path, object_name="landscape")
    #landscape = blender_io.load_npz_terrain(npz_path, name="landscape", scale_xy=1.0, scale_z=25.0, smooth=True)
    #landscape = blender_io.load_npz_terrain_with_river_displace(npz_path, name="landscape", scale_xy=0.1, scale_z=2.5, displace_strength=100.0, smooth=True)
    #landscape = blender_io.load_npz_terrain_with_river_displace(npz_path, name="landscape", scale_xy=0.1, scale_z=2.5, displace_strength=100.0)

    
    terrain_config = {
        ### io args
        'npz_path': './river_network.npz',
        'name': 'landscape',
        'generate_terrain': False,
        ### loading args
        'scale_xy': 0.1,
        'scale_z': 2.5,
        'displace_strength': 100.0,
        ### generate args
        'dim': 256,
        'disc_radius': 0.1,
        'max_delta': 0.05,
        'river_downcutting_constant': 1.3,
        'directional_inertia': 0.4,
        'default_water_level': 1.0,
        'evaporation_rate': 0.2,
        'remove_lakes_arg': True,
    }
    
    if not os.path.exists(terrain_config['npz_path']):
        print(f'No file found at {npz_path}. Generating new terrain... ')
        terrain_config['generate_terrain'] = True
    if terrain_config['generate_terrain']:
        river_network.main(
            ### = terrain_config[''],
            dim = terrain_config['dim'],
            disc_radius = terrain_config['disc_radius'],
            output_path = terrain_config['npz_path'],
        )
    landscape = blender_io.load_npz_terrain_with_river_displace(
        terrain_config['npz_path'], 
        name=terrain_config['name'], 
        scale_xy=terrain_config['scale_xy'], 
        scale_z=terrain_config['scale_z'],
        displace_strength=terrain_config['displace_strength'],
    )
    
    return
    
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

