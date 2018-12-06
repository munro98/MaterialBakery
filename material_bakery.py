# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Material Bakery",
    "author": "Nigel Munro",
    "version": (0, 6, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Material > Material Bakery",
    "warning": "",
    "description": "Bake out PBR texture maps",
    "wiki_url": ""
                "Scripts/Material/MaterialBakery",
    "category": "Material",
}


# TODO Iterate materials, break down tasks into smaller functions, move out graph to props position

import bpy

from bpy.types import (
        Operator,
        Menu,
        Panel,
        PropertyGroup,
        AddonPreferences,
        )

from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        )

class MatBake_Panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Material Bakery"
    bl_idname = "MATBAKE_PT_main"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Hello world!", icon='WORLD_DATA')

        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        row = layout.row()
        row.prop(obj, "name")
        

        row = layout.row()
        row.prop(context.scene, "bakery_resolution")
        
        row = layout.row()
        col = row.column()
        col.prop(context.scene, "bakery_albedo")
        col = row.column()
        col.prop(context.scene, "bakery_albedo_alpha")


        row = layout.row()
        col = row.column()
        col.prop(context.scene, "bakery_roughness")
        col = row.column()
        col.prop(context.scene, "bakery_normals")
        
        row = layout.row()
        row.prop_search(context.scene, "bakery_out_uv", obj.data, "uv_layers")
        
        row = layout.row()
        row.prop(context.scene, "bakery_out_directory")
        
        
        #row = layout.row()
        #row.prop(context.scene, "uv_bake_alpha_color")
        
        op = layout.operator("material.mat_bake_create_maps", text="Create Maps")

        row = layout.row()
        row.prop(bpy.context.scene.cycles, "samples")

        row = layout.row()
        row.prop(context.scene, "bakery_margin")

        op = layout.operator("material.mat_bake_bake_maps", text="Bake Maps")
        
        #row.prop(self, "resolution")
        #row.props_enum(self, "resolution")
        #row.prop(obj, "location")

        #row = layout.row()
        #row.operator("mesh.primitive_cube_add")
        
        

class MatBake_CreateMaps(Operator):
    bl_idname = 'material.mat_bake_create_maps'
    bl_label = "Create Maps"
    bl_description = "Create texture maps"
    #bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob and ob.type == 'MESH' and bpy.context.scene.bakery_out_uv != '') # and context.mode == 'EDIT_MESH'

    def draw(self, context):
        layout = self.layout
        

        # cleaning up
        terminate(global_undo)

        return{'FINISHED'}
    
    def execute(self, context):
        # initialise
        
        print("Executing Create Maps")
        
        ob = bpy.context.active_object

        # Get material
        mat = ob.data.materials[0]

        mat.use_nodes=True

        nodes=mat.node_tree.nodes

        # create node
        node_uv_map = nodes.new(type='ShaderNodeUVMap')
        node_uv_map.uv_map = context.scene.bakery_out_uv

        w = context.scene.bakery_resolution
        h = context.scene.bakery_resolution

        img_col = bpy.data.images.new("Map_col", width=w, height=h)
        img_rgh = bpy.data.images.new("Map_rgh", width=w, height=h)
        img_nrm = bpy.data.images.new("Map_nrm", width=w, height=h)

        links = mat.node_tree.links


        col = nodes.new(type='ShaderNodeTexImage')
        col.image = img_col

        link = links.new(node_uv_map.outputs[0], col.inputs[0])

        rgh = nodes.new(type='ShaderNodeTexImage')
        rgh.image = img_rgh

        link = links.new(node_uv_map.outputs[0], rgh.inputs[0])

        nrm = nodes.new(type='ShaderNodeTexImage')
        nrm.image = img_nrm

        link = links.new(node_uv_map.outputs[0], nrm.inputs[0])
        
        
        return{'FINISHED'}


class MatBake_BakeMaps(Operator):
    bl_idname = 'material.mat_bake_bake_maps'
    bl_label = "Bake Maps(Cycles Only)"
    bl_description = "Bake out selected texture maps(Cycles Only)."


    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob and ob.type == 'MESH' and context.scene.render.engine == 'CYCLES') # and context.mode == 'EDIT_MESH'

    def draw(self, context):
        layout = self.layout
        
        # cleaning up
        terminate(global_undo)

        return{'FINISHED'}
    
    def execute(self, context):
        # initialise
        print("executing Bake")

        if context.scene.bakery_albedo:
            print("bake albedo")
        else:
            print("bake")
        

        ob = bpy.context.active_object

        # Get material
        mat_plane = ob.data.materials[0]

        links = mat_plane.node_tree.links

        mat_plane.use_nodes=True
        nodes=mat_plane.node_tree.nodes

        node_uv_map = None

        for node in nodes:
            print(node.type)
            if node_uv_map is None:
                if node.type == 'UVMAP' and node.uv_map == context.scene.bakery_out_uv:
                    node_uv_map = node
            else:
                if node.type == 'UVMAP' and node.uv_map == context.scene.bakery_out_uv:
                    print("already found!")


        col = None
        rgh = None
        nrm = None

        outCounter = 0
        outLinks = len(node_uv_map.outputs[0].links)

        if outCounter < outLinks:
            for link in node_uv_map.outputs[0].links:
                node = link.to_node
                if node.type == 'TEX_IMAGE' and node.image.name.endswith('_col'):
                    col = node
                    break
                
        outCounter = outCounter + 1

        if outCounter < outLinks:
            for link in node_uv_map.outputs[0].links:
                node = link.to_node
                if node.type == 'TEX_IMAGE' and node.image.name.endswith('_rgh'):
                    rgh = node
                    break

        outCounter = outCounter + 1

        if outCounter < outLinks:
            for link in node_uv_map.outputs[0].links:
                node = link.to_node
                if node.type == 'TEX_IMAGE' and node.image.name.endswith('_nrm'):
                    nrm = node
                    break


        nodes.active = None

        if col:
            nodes.active = col
            bpy.ops.object.bake(type='DIFFUSE')

        if rgh:
            nodes.active = rgh
            bpy.ops.object.bake(type='ROUGHNESS')


        bsdf_prin = None

        for n in nodes:
            if bsdf_prin == None:
                if n.type == 'BSDF_PRINCIPLED':
                    bsdf_prin = n
            else:
                if bsdf_prin != None and n.type == 'BSDF_PRINCIPLED':
                    self.report({'INFO'}, "Found multiple bsdf principled shaders in material graph")
                    #return {'CANCELLED'}


        in_base_col = None

        if len(bsdf_prin.inputs[0].links) > 0:
            in_base_col = bsdf_prin.inputs[0].links[0].from_node
        else:
            print("in color empty")
            


        in_nrm = None
        in_nrm_tex = None

        if len(bsdf_prin.inputs[17].links) > 0:
            in_nrm = bsdf_prin.inputs[17].links[0].from_node
            
            if in_nrm.type == 'NORMAL_MAP':
                if len(bsdf_prin.inputs[17].links) > 0:
                    n = bsdf_prin.inputs[17].links[0].from_node
                    
                    if len(n.inputs[1].links) > 0:
                        n2 = n.inputs[1].links[0].from_node
                        if n2.type:
                            in_nrm_tex = n2

            if in_nrm_tex is not None:
                link = links.new(in_nrm_tex.outputs[0], bsdf_prin.inputs[0])

                nodes.active = nrm
                bpy.ops.object.bake(type='DIFFUSE')
                #save

                if in_base_col is None:
                    links.remove(bsdf_prin.inputs[0].links[0])
                else:
                    link = links.new(in_base_col.outputs[0], bsdf_prin.inputs[0])
            else:
                print("Could not find BSDF Principled normal texture input2")
        else:
            print("Could not find BSDF Principled normal texture input")
        
        return{'FINISHED'}
        
    
classes = (
    MatBake_CreateMaps,
    MatBake_BakeMaps,
    MatBake_Panel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    #bpy.utils.register_class(HelloWorldPanel)
    
    
    bpy.types.Scene.bakery_resolution = IntProperty(
        name="Resolution",
        description="resolution",
        default=1024,
        min=32,
        max=8192,
        )
    
    bpy.types.Scene.bakery_alpha_color = FloatVectorProperty(
        name="Alpha Color",
        description="Color to be used for transparency",
        subtype='COLOR',
        min=0.0,
        max=1.0)
        
    bpy.types.Scene.bakery_out_directory = StringProperty(
        name="Output",
        description="Output Drectory for created map",
        subtype="DIR_PATH"
        )

    bpy.types.Scene.bakery_albedo = BoolProperty(
        name="Albedo",
        description="Bake Albedo",
        default=True
        )
        
    bpy.types.Scene.bakery_albedo_alpha = BoolProperty(
        name="Alpha Albedo",
        description="Add alpha channel to base color map",
        default=False
        )
    
    bpy.types.Scene.bakery_roughness = BoolProperty(
        name="Roughness",
        description="Bake Roughness",
        default=True
        )
    
    bpy.types.Scene.bakery_normals = BoolProperty(
        name="Normals",
        description="Bake Normals",
        default=True
        )
        
    bpy.types.Scene.bakery_out_uv = StringProperty(
        name="Output UV",
        description="Select the UV Map used to bake"
        )

    bpy.types.Scene.bakery_margin = IntProperty(
        name="Bake Margin",
        description="Bake Margin",
        default=16,
        min=0,
        max=8192,
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    #bpy.utils.unregister_class(HelloWorldPanel)
    
    del bpy.types.Scene.bakery_alpha_color
    del bpy.types.Scene.bakery_resolution
    del bpy.types.Scene.bakery_out_directory
    del bpy.types.Scene.bakery_albedo
    del bpy.types.Scene.bakery_albedo_alpha
    del bpy.types.Scene.bakery_roughness
    del bpy.types.Scene.bakery_normals
    del bpy.types.Scene.bakery_out_uv


if __name__ == "__main__":
    register()
