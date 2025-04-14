
import bpy
import numpy as np
from PIL import Image
import os
import tempfile

def load_npz_terrain_with_river_displace(npz_path, name="Terrain", scale_xy=0.1, scale_z=1.0,
                                         displace_strength=100.0, use_uv=False):
    """
    Loads a .npz terrain file with 'height' and optionally 'river', creates a mesh in Blender,
    and applies a displace modifier based on river intensity.
    """
    # Load data
    data = np.load(npz_path)
    if "height" not in data:
        raise KeyError("The .npz file must contain a 'height' array.")

    height = data["height"]
    river = data.get("river")  # Optional

    n_rows, n_cols = height.shape
    verts = []
    faces = []

    # Create vertices
    for y in range(n_rows):
        for x in range(n_cols):
            z = height[y, x]
            verts.append((x, -y, z))  # Flip Y for Blender convention

    # Create quad faces
    for y in range(n_rows - 1):
        for x in range(n_cols - 1):
            v1 = y * n_cols + x
            v2 = v1 + 1
            v3 = v1 + n_cols + 1
            v4 = v1 + n_cols
            faces.append((v1, v2, v3, v4))

    # Create mesh and object
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    # Apply object scale
    obj.scale = (scale_xy, scale_xy, scale_z)

    # Smooth shading
    for p in mesh.polygons:
        p.use_smooth = True

    # Set object active and select it
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Displace modifier with river
    if river is not None:
        print("Applying river displace modifier...")

        # Normalize river to 0–255
        river_normalized = river - river.min()
        if river_normalized.max() > 0:
            river_normalized /= river_normalized.max()
        river_img = (river_normalized * 255).astype(np.uint8)

        # Save image to temp file
        tmp_path = os.path.join(tempfile.gettempdir(), f"{name}_river.png")
        Image.fromarray(river_img).save(tmp_path)

        # Load image as Blender texture
        if os.path.exists(tmp_path):
            image = bpy.data.images.load(tmp_path)
        else:
            raise FileNotFoundError(f"Image not saved at {tmp_path}")

        # Create texture datablock
        tex = bpy.data.textures.new(name + "_RiverTex", type='IMAGE')
        tex.image = image

        # Create and configure displace modifier
        disp_mod = obj.modifiers.new("RiverDisplace", type='DISPLACE')
        disp_mod.texture = tex
        disp_mod.strength = displace_strength
        disp_mod.mid_level = 0.0

        # Use LOCAL coordinates unless UV unwrap is requested
        if use_uv:
            # Create UV map via ops (only way in Blender)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project()
            bpy.ops.object.mode_set(mode='OBJECT')
            disp_mod.texture_coords = 'UV'
        else:
            disp_mod.texture_coords = 'LOCAL'

        print(f"Displace modifier applied with strength={displace_strength} and coords={disp_mod.texture_coords}")
    else:
        print("No 'river' array found in .npz file — skipping displace modifier.")

    return obj




import bpy
import numpy as np
from PIL import Image
import os
import tempfile

def load_npz_terrain_with_river_displace_1(npz_path, name="Terrain", scale_xy=0.1, scale_z=1.0,
                                         displace_strength=0.5, smooth=True):
    """
    Loads a .npz terrain file with 'height' and optionally 'river', creates a mesh in Blender,
    and applies a displace modifier based on river intensity.
    """
    # Load data
    data = np.load(npz_path)
    if "height" not in data:
        raise KeyError("The .npz file must contain a 'height' array.")

    height = data["height"]
    river = data.get("river")  # Optional

    n_rows, n_cols = height.shape
    verts = []
    faces = []

    # Create vertices
    for y in range(n_rows):
        for x in range(n_cols):
            z = height[y, x]
            verts.append((x, -y, z))  # Flip Y for Blender convention

    # Create quad faces
    for y in range(n_rows - 1):
        for x in range(n_cols - 1):
            v1 = y * n_cols + x
            v2 = v1 + 1
            v3 = v1 + n_cols + 1
            v4 = v1 + n_cols
            faces.append((v1, v2, v3, v4))

    # Create mesh and object
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    obj.scale = (scale_xy, scale_xy, scale_z)
    if smooth:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()

    # Add displace modifier using river data
    if river is not None:
        print("Applying river displace modifier...")

        # Normalize river array to 0-255
        river_normalized = river.copy()
        river_normalized -= river_normalized.min()
        if river_normalized.max() > 0:
            river_normalized /= river_normalized.max()
        river_img = (river_normalized * 255).astype(np.uint8)

        # Save temporary grayscale image
        tmp_dir = tempfile.gettempdir()
        img_path = os.path.join(tmp_dir, f"{name}_river.png")
        Image.fromarray(river_img).save(img_path)

        # Load image into Blender
        img = bpy.data.images.load(img_path)

        # Create texture
        tex = bpy.data.textures.new(name + "_RiverTex", type='IMAGE')
        tex.image = img

        # Ensure object is active and selected before applying any modifier
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Add displace modifier
        disp_mod = obj.modifiers.new("RiverDisplace", type='DISPLACE')
        disp_mod.texture = tex
        disp_mod.texture_coords = 'LOCAL'

        disp_mod.strength = displace_strength
        
        # Add UV map (if not present)
        if not obj.data.uv_layers:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project()
            bpy.ops.object.mode_set(mode='OBJECT')

        print(f"Displace modifier applied with texture: {img_path}")

    return obj



import bpy
import numpy as np

def load_npz_terrain(npz_path, name="Terrain", scale_xy=0.1, scale_z=1.0, smooth=True):
    """
    Loads a .npz terrain file with a 'height' array and creates a mesh in Blender.
    
    Parameters:
        npz_path (str): Path to the .npz file.
        name (str): Name of the Blender object.
        scale_xy (float): Uniform scale factor for X and Y axes.
        scale_z (float): Scale factor for height (Z-axis).
        smooth (bool): Whether to shade the mesh smooth.
    """
    # Load data
    data = np.load(npz_path)
    if "height" not in data:
        raise KeyError("The .npz file must contain a 'height' array.")
    
    height = data["height"]
    n_rows, n_cols = height.shape
    verts = []
    faces = []

    # Create vertices
    for y in range(n_rows):
        for x in range(n_cols):
            z = height[y, x]
            verts.append((x, -y, z))  # Invert Y for Blender-style orientation

    # Create quad faces
    for y in range(n_rows - 1):
        for x in range(n_cols - 1):
            v1 = y * n_cols + x
            v2 = v1 + 1
            v3 = v1 + n_cols + 1
            v4 = v1 + n_cols
            faces.append((v1, v2, v3, v4))

    # Create Blender mesh
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    # Scale and smooth
    obj.scale = (scale_xy, scale_xy, scale_z)
    if smooth:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()

    print(f"Loaded terrain mesh '{name}' with shape {height.shape}.")

    return obj