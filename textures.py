
import bpy

def apply_single_brick_texture(obj):
    # Create a new material
    mat = bpy.data.materials.new(name="BrickMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Add nodes
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    diffuse_node = nodes.new(type='ShaderNodeBsdfDiffuse')
    brick_node = nodes.new(type='ShaderNodeTexBrick')
    mapping_node = nodes.new(type='ShaderNodeMapping')
    texcoord_node = nodes.new(type='ShaderNodeTexCoord')

    # Arrange node positions
    output_node.location = (600, 0)
    diffuse_node.location = (400, 0)
    brick_node.location = (200, 0)
    mapping_node.location = (0, 0)
    texcoord_node.location = (-200, 0)

    # Configure Brick Texture to fit 1 brick per UV tile
    brick_node.offset = 0.0
    brick_node.offset_frequency = 1
    brick_node.squash = 0.0
    brick_node.squash_frequency = 1
    #print(dir(brick_node))
    
    #return
    #brick_node.inputs['Offset'].default_value = 0.0
    #brick_node.inputs['Frequency'].default_value = 1.0
    #brick_node.inputs['Squash'].default_value = 0.0
    brick_node.inputs['Scale'].default_value = 1.0  # 1 brick per UV tile
    brick_node.inputs['Mortar Size'].default_value = 0.02
    brick_node.inputs['Color1'].default_value = (0.8, 0.3, 0.3, 1)
    brick_node.inputs['Color2'].default_value = (0.7, 0.2, 0.2, 1)
    brick_node.inputs['Mortar'].default_value = (0.1, 0.1, 0.1, 1)

    # Set Mapping scale
    mapping_node.inputs['Scale'].default_value = (1, 1, 1)

    # Connect nodes
    links.new(texcoord_node.outputs['UV'], mapping_node.inputs['Vector'])
    links.new(mapping_node.outputs['Vector'], brick_node.inputs['Vector'])
    links.new(brick_node.outputs['Color'], diffuse_node.inputs['Color'])
    links.new(diffuse_node.outputs['BSDF'], output_node.inputs['Surface'])

    # Assign the material to the object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    # Auto-unwrap if no UVs exist
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')
    if not obj.data.uv_layers:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.smart_project()
        bpy.ops.object
