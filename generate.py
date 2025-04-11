
import bpy
import importlib

import tools
import architecture_1
importlib.reload(tools)
importlib.reload(architecture_1)

### TODO:
# - add brick texture
# - add keystone arch
# - dome/folia generator
# - landscape generator
# - refactor

# Delete all existing objects to start fresh
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def generate():
    ### hyp
    structure_center = (0,0,0)
    arch_hyp = {
        'size': 4,
        'location': (6.5, -3.0, 4.0),
        'scale': (0.5, 0.75, 0.5),
        'cut_vertices': 36,
        'legs_dist': 3,
        'counts': (1,3,1),
    }

    tools.set_render_engine()
    tools.add_sun()
    
    arch_east = architecture_1.make_arch(
        arch_size = arch_hyp['size'],
        arch_location = arch_hyp['location'],
        arch_scale = arch_hyp['scale'],
        arch_cut_vertices = arch_hyp['cut_vertices'],
        legs_dist = arch_hyp['legs_dist'],
    )

    architecture_1.add_keystone_arch(arch_hyp)
    
    tools.apply_array_modifiers(
        base_object=arch_east, 
        counts=arch_hyp['counts'],
        axes=('X', 'Y', 'Z'), 
        spacings=(0,arch_hyp['size']*arch_hyp['scale'][1],0)
    )

    
    #columns = architecture_1.add_columns_to_arch(
    #    arch_hyp,
    #    array_counts = (2,4,1),
    #    radius=0.25,
    #)
    #tools.join_objects([arch_east, columns])

    capitals = architecture_1.add_capital(
        arch_hyp,
    )
    tools.join_objects([arch_east, capitals])
    
    arch_east = tools.duplicate_object(arch_east)
    tools.rotate_around_point(arch_east, angle_deg=90)
    arch_north = tools.duplicate_object(arch_east)
    tools.rotate_around_point(arch_east, angle_deg=180)
    arch_west = tools.duplicate_object(arch_east)
    tools.rotate_around_point(arch_east, angle_deg=270)

