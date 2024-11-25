import bpy
from bpy.props import EnumProperty, CollectionProperty, IntProperty, BoolProperty, StringProperty, FloatVectorProperty
from bpy.types import Operator, Panel, PropertyGroup, UIList

bl_info = {
    "name": "Standalone Elements Remover",
    "description": "Removes standalone vertices, edges, and faces in Blender",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (3, 3, 0),
    "location": "View3D > Sidebar > Z-Tools",
    "category": "3D View"
}

class StandaloneElementProperty(PropertyGroup):
    item_name: StringProperty(name="Item Name")
    item_index: IntProperty()
    select: BoolProperty(name="Select", default=False)
    coordinates: FloatVectorProperty(name="Coordinates", size=3)

class StandaloneToolsProperties(PropertyGroup):
    element_type: EnumProperty(
        name="Element Type",
        description="Choose the type of element to clean",
        items=[
            ('VERTEX', "Vertex", "Isolated vertex"),
            ('EDGE', "Edge", "Isolated edge"),
            ('FACE', "Face", "Isolated face"),
        ],
        default='VERTEX'
    )
    element_list: CollectionProperty(type=StandaloneElementProperty)
    element_list_index: IntProperty()

class LIST_OT_PopulateElements(Operator):
    bl_idname = "object.populate_elements"
    bl_label = "Populate Standalone Elements"
    bl_description = "Populate the list with standalone elements"

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "Active object is not a mesh")
            return {'CANCELLED'}

        mesh = obj.data
        props = context.scene.standalone_tool_props
        props.element_list.clear()
        
        if props.element_type == 'VERTEX':
            vertex_connections = {i: set() for i in range(len(mesh.vertices))}
            for edge in mesh.edges:
                v1, v2 = edge.vertices
                vertex_connections[v1].add(v2)
                vertex_connections[v2].add(v1)

            for idx, vertex in enumerate(mesh.vertices):
                if not vertex_connections[idx]:  # No connections
                    item = props.element_list.add()
                    item.item_name = f"Vertex {idx}"
                    item.item_index = idx
                    item.coordinates = vertex.co

        elif props.element_type == 'EDGE':
            for idx, edge in enumerate(mesh.edges):
                if edge.is_loose:
                    item = props.element_list.add()
                    item.item_name = f"Edge {idx}"
                    item.item_index = idx
        
        else:  # FACE
            bm = bmesh.new()
            bm.from_mesh(mesh)
            for f in bm.faces:
                connected_edges = [e for e in f.edges if len(e.link_faces) > 1]
                if not connected_edges:  # No shared edge with another face
                    item = props.element_list.add()
                    item.item_name = f"Face {f.index}"
                    item.item_index = f.index
            bm.free()

        return {'FINISHED'}

class LIST_OT_ClearStandaloneElements(Operator):
    bl_idname = "object.clear_standalone_elements"
    bl_label = "Clear Standalone Elements"
    bl_description = "Clear selected standalone elements"

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "Active object is not a mesh")
            return {'CANCELLED'}

        props = context.scene.standalone_tool_props

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        mesh = obj.data
        element_type = props.element_type

        for item in props.element_list:
            if item.select:
                if element_type == 'VERTEX':
                    mesh.vertices[item.item_index].select = True
                elif element_type == 'EDGE':
                    mesh.edges[item.item_index].select = True
                elif element_type == 'FACE':
                    mesh.polygons[item.item_index].select = True
        
        bpy.ops.object.mode_set(mode='EDIT')
        if element_type == 'VERTEX':
            bpy.ops.mesh.delete(type='VERT')
        elif element_type == 'EDGE':
            bpy.ops.mesh.delete(type='EDGE')
        elif element_type == 'FACE':
            bpy.ops.mesh.delete(type='FACE')
        
        bpy.ops.object.mode_set(mode='OBJECT')
        props.element_list.clear()

        return {'FINISHED'}

class LIST_OT_SelectAll(Operator):
    bl_idname = "object.select_all_elements"
    bl_label = "Select All Elements"

    def execute(self, context):
        props = context.scene.standalone_tool_props
        for item in props.element_list:
            item.select = True
        return {'FINISHED'}

class LIST_OT_SelectNone(Operator):
    bl_idname = "object.select_none_elements"
    bl_label = "Select None Elements"

    def execute(self, context):
        props = context.scene.standalone_tool_props
        for item in props.element_list:
            item.select = False
        return {'FINISHED'}

class UL_StandaloneElementList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'DOT'
        layout.prop(item, "select", text="")
        layout.label(text=item.item_name, icon=custom_icon)
        if data.element_type == 'VERTEX':
            layout.label(text=f"{item.coordinates[0]:.2f}, {item.coordinates[1]:.2f}, {item.coordinates[2]:.2f}")

class PANEL_PT_StandaloneElementsPanel(Panel):
    bl_label = "Standalone Elements"
    bl_idname = "PANEL_PT_standalone_elements"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Z-Tools'

    def draw(self, context):
        layout = self.layout
        props = context.scene.standalone_tool_props

        layout.prop(props, "element_type", expand=True)
        layout.operator("object.populate_elements", text="Populate List")
        
        row = layout.row()
        row.template_list("UL_StandaloneElementList", "", props, "element_list", props, "element_list_index")
        
        row = layout.row(align=True)
        row.operator("object.select_all_elements", text="Select All")
        row.operator("object.select_none_elements", text="Select None")

        layout.operator("object.clear_standalone_elements", text="Clear Selected Elements")

def register():
    bpy.utils.register_class(StandaloneElementProperty)
    bpy.utils.register_class(StandaloneToolsProperties)
    bpy.utils.register_class(LIST_OT_PopulateElements)
    bpy.utils.register_class(LIST_OT_ClearStandaloneElements)
    bpy.utils.register_class(LIST_OT_SelectAll)
    bpy.utils.register_class(LIST_OT_SelectNone)
    bpy.utils.register_class(UL_StandaloneElementList)
    bpy.utils.register_class(PANEL_PT_StandaloneElementsPanel)

    bpy.types.Scene.standalone_tool_props = bpy.props.PointerProperty(type=StandaloneToolsProperties)

def unregister():
    bpy.utils.unregister_class(StandaloneElementProperty)
    bpy.utils.unregister_class(StandaloneToolsProperties)
    bpy.utils.unregister_class(LIST_OT_PopulateElements)
    bpy.utils.unregister_class(LIST_OT_ClearStandaloneElements)
    bpy.utils.unregister_class(LIST_OT_SelectAll)
    bpy.utils.unregister_class(LIST_OT_SelectNone)
    bpy.utils.unregister_class(UL_StandaloneElementList)
    bpy.utils.unregister_class(PANEL_PT_StandaloneElementsPanel)

    del bpy.types.Scene.standalone_tool_props

if __name__ == "__main__":
    register()
