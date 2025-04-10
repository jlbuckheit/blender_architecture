
import bpy


import sys
sys.path.append("C:/Users/jlbuc/Documents/blender/python_procedural")

import importlib
import tools
import architecture_1
importlib.reload(architecture_1)
importlib.reload(tools)

### debug
# Delete all existing objects to start fresh
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()


### hyp
structure_center = (0,0,0)
arch_hyp = {
    'size': 4,
    'location': (6.5, -3.0, 4.0),
    'scale': (.5, .75, .5),
    'cut_vertices': 36,
    'legs_dist': 3,
}



arch_east = architecture_1.make_arch(
    arch_size = arch_hyp['size'],
    arch_location = arch_hyp['location'],
    arch_scale = arch_hyp['scale'],
    arch_cut_vertices = arch_hyp['cut_vertices'],
    legs_dist = arch_hyp['legs_dist'],
)

tools.apply_array_modifiers(
    base_object=arch_east, 
    counts=(1,3,1), 
    axes=('X', 'Y', 'Z'), 
    spacings=(1,1,1)
)

columns = architecture_1.add_columns_to_arch(
    arch_hyp,
    array_counts = (2,4,1),
)

tools.join_objects([arch_east, columns])

arch_east = tools.duplicate_object(arch_east)
tools.rotate_around_point(arch_east, angle_deg=90)
arch_north = tools.duplicate_object(arch_east)
tools.rotate_around_point(arch_east, angle_deg=180)
arch_west = tools.duplicate_object(arch_east)
tools.rotate_around_point(arch_east, angle_deg=270)

