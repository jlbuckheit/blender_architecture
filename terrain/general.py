
import bpy
import os
import importlib

#import sys
#current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the parent directory (assuming your package is there)
#package_dir = os.path.join(current_dir, '..')
#sys.path.append(package_dir)
#print(package_dir)

import river_network
importlib.reload(river_network)


#sys.path.append("C:/Users/jlbuc/my_python/repos/blender_architecture/utils")
from utils import tools, face_utils, blender_io
importlib.reload(tools)
importlib.reload(face_utils)
importlib.reload(blender_io)


dim = 1024
scale_xy = 8
scale_z = 512

def get_landscape(water_offset):
    
    terrain_config = {
        ### io args
        'npz_path': './river_network_42_1024.npz', # './river_network_42_2048.npz',
        'name': 'landscape',
        'generate_terrain': False,
        ### loading args
        'scale_xy': scale_xy, # 8.0,
        'scale_z': scale_z, # 512.0,
        'displace_strength': 1.0,
        ### generate args
        'dim': dim, # 128,
        'disc_radius': 1.0,
        'max_delta': 0.05,
        'river_downcutting_constant': 1.3,
        'directional_inertia': 0.4,
        'default_water_level': 10.0,
        'evaporation_rate': 0.2,
        'remove_lakes_arg': True,
        'seed': 42,
    }

    if not os.path.exists(terrain_config['npz_path']):
        print(f'No file found at {npz_path}. Generating new terrain... ')
        terrain_config['generate_terrain'] = True
    if terrain_config['generate_terrain']:
        river_network.main(
            ### = terrain_config[''],
            dim = terrain_config['dim'],
            output_path = terrain_config['npz_path'],
            seed = terrain_config['seed'],
            default_water_level = terrain_config['default_water_level'],
        )
    landscape = blender_io.load_npz_terrain_with_river_displace(
        terrain_config['npz_path'], 
        name=terrain_config['name'], 
        scale_xy=terrain_config['scale_xy'], 
        scale_z=terrain_config['scale_z'],
        displace_strength=terrain_config['displace_strength'],
        #chunk_range = [0,0,256,256],### TODO: this does not work
        #npy_path = './river_network_42_1024_npy'
    )
    landscape.location = (-dim*scale_xy/2, dim*scale_xy/2, water_offset)
    return landscape

def get_ocean():
    bpy.ops.mesh.primitive_plane_add(size=dim*scale_xy, location=(0,0,0))
    water = bpy.context.active_object
    water.name = 'water'
    return water

#bpy.ops.mesh.primitive_plane_add(size=1.0, location=(dim*scale_xy/2, -dim*scale_xy/2, 44))
#water = bpy.context.active_object
#ocean_modifier = water.modifiers.new(name="Ocean", type='OCEAN')
##ocean_modifier.geometry_mode = 'DISPLACE'
#ocean_modifier.size = dim*scale_xy
#ocean_modifier.geometry_mode = 'GENERATE'
##ocean_modifier.repeat_x = 2
##ocean_modifier.repeat_y = 2
    
#npz_path = 'C:/Users/jlbuc/my_python/repos/blender_architecture/terrain/river_network.npz'
#landscape = blender_io.import_npz_mesh(npz_path, object_name="landscape")
#landscape = blender_io.load_npz_terrain(npz_path, name="landscape", scale_xy=1.0, scale_z=25.0, smooth=True)
#landscape = blender_io.load_npz_terrain_with_river_displace(npz_path, name="landscape", scale_xy=0.1, scale_z=2.5, displace_strength=100.0, smooth=True)
#landscape = blender_io.load_npz_terrain_with_river_displace(npz_path, name="landscape", scale_xy=0.1, scale_z=2.5, displace_strength=100.0)