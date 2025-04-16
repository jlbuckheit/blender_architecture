import bpy
import bmesh
import random
import math
from mathutils import noise, Vector

def generate_landscape(name="PerlinTerrain", size=32, resolution=128, scale=1.0, river_count=2):

    # Create grid mesh
    bpy.ops.mesh.primitive_grid_add(
        size=size,
        x_subdivisions=resolution,
        y_subdivisions=resolution,
        enter_editmode=False,
        location=(0, 0, 0)
    )
    terrain = bpy.context.active_object
    terrain.name = name

    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    mesh = bmesh.from_edit_mesh(terrain.data)

    # Smooth Perlin-based mountains
    for v in mesh.verts:
        x, y = v.co.x / size * scale * 4, v.co.y / size * scale * 4  # scale controls frequency
        vec = Vector((x, y, 0.0))
        height = noise.noise(vec)  # This is Perlin by default
        v.co.z = height * 8  # Adjust amplitude

    # Add rivers
    for _ in range(river_count):
        river_path = generate_river_path(size, resolution)
        for v in mesh.verts:
            for rx, ry in river_path:
                dist = math.hypot(v.co.x - rx, v.co.y - ry)
                if dist < 4.0:
                    v.co.z -= (4.0 - dist) * 1.5  # Carve valleys gently

    bmesh.update_edit_mesh(terrain.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    return terrain


def generate_river_path(size, resolution):
    # Smoother meandering river from one edge to the other
    path = []
    step = size / resolution
    y = -size / 2
    curve_amplitude = size / 4
    curve_frequency = 2 * math.pi / size * 2  # Adjust for gentle sin wave

    for i in range(resolution):
        offset = random.uniform(-0.3, 0.3)
        x = math.sin(i * curve_frequency + offset) * curve_amplitude
        path.append((x, y))
        y += step

    return path
