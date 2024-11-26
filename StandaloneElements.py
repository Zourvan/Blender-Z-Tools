import bpy
import bmesh
from bpy.props import EnumProperty, CollectionProperty, IntProperty, BoolProperty, StringProperty, FloatVectorProperty
from bpy.types import Operator, PropertyGroup, UIList

class StandaloneElementProperty(PropertyGroup):
    item_name: StringProperty(name="Item Name") # type: ignore
    item_index: IntProperty() # type: ignore
    select: BoolProperty(name="Select", default=False) # type: ignore
    coordinates: FloatVectorProperty(name="Coordinates", size=3) # type: ignore

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
    ) # type: ignore
    element_list: CollectionProperty(type=StandaloneElementProperty) # type: ignore
    element_list_index: IntProperty() # type: ignore

class LIST_OT_PopulateElements(Operator):
    bl_idname = "object.populate_elements"
    bl_label = "Populate Elements List"
    bl_description = "Find and list all standalone elements"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        props = context.scene.standalone_tool_props
        props.element_list.clear()

        # Switch to edit mode temporarily
        bpy.ops.object.mode_set(mode='EDIT')
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        if props.element_type == 'VERTEX':
            elements = [v for v in bm.verts if not v.link_edges]
            for i, v in enumerate(elements):
                item = props.element_list.add()
                item.item_name = f"Vertex {i}"
                item.item_index = i
                item.coordinates = v.co.copy()

        elif props.element_type == 'EDGE':
            elements = [e for e in bm.edges if not e.link_faces]
            for i, e in enumerate(elements):
                item = props.element_list.add()
                item.item_name = f"Edge {i}"
                item.item_index = i
                item.coordinates = e.verts[0].co.lerp(e.verts[1].co, 0.5)

        elif props.element_type == 'FACE':
            elements = [f for f in bm.faces if all(not e.link_faces for e in f.edges if e not in f.edges)]
            for i, f in enumerate(elements):
                item = props.element_list.add()
                item.item_name = f"Face {i}"
                item.item_index = i
                item.coordinates = f.calc_center_median()

        bpy.ops.object.mode_set(mode='OBJECT')
        
        self.report({'INFO'}, f"Found {len(props.element_list)} standalone {props.element_type.lower()}(s)")
        return {'FINISHED'}

class LIST_OT_ClearStandaloneElements(Operator):
    bl_idname = "object.clear_standalone_elements"
    bl_label = "Clear Selected Elements"
    bl_description = "Remove selected standalone elements"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        props = context.scene.standalone_tool_props
        selected_items = [item for item in props.element_list if item.select]
        
        if not selected_items:
            self.report({'WARNING'}, "No elements selected")
            return {'CANCELLED'}

        # Switch to edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        # Ensure all elements are deselected first
        for v in bm.verts:
            v.select = False
        for e in bm.edges:
            e.select = False
        for f in bm.faces:
            f.select = False

        if props.element_type == 'VERTEX':
            elements = [v for v in bm.verts if not v.link_edges]
            for item in selected_items:
                if item.item_index < len(elements):
                    elements[item.item_index].select = True

        elif props.element_type == 'EDGE':
            elements = [e for e in bm.edges if not e.link_faces]
            for item in selected_items:
                if item.item_index < len(elements):
                    elements[item.item_index].select = True

        elif props.element_type == 'FACE':
            elements = [f for f in bm.faces if all(not e.link_faces for e in f.edges if e not in f.edges)]
            for item in selected_items:
                if item.item_index < len(elements):
                    elements[item.item_index].select = True

        # Delete selected elements
        bpy.ops.mesh.delete()

        # Update the mesh
        bmesh.update_edit_mesh(me)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Clear the list
        props.element_list.clear()

        self.report({'INFO'}, f"Removed {len(selected_items)} {props.element_type.lower()}(s)")
        return {'FINISHED'}

class LIST_OT_SelectAll(Operator):
    bl_idname = "object.select_all_elements"
    bl_label = "Select All Elements"
    bl_description = "Select all elements in the list"

    def execute(self, context):
        props = context.scene.standalone_tool_props
        for item in props.element_list:
            item.select = True
        return {'FINISHED'}

class LIST_OT_SelectNone(Operator):
    bl_idname = "object.select_none_elements"
    bl_label = "Select None Elements"
    bl_description = "Deselect all elements in the list"

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

def draw_panel(context, layout):
    props = context.scene.standalone_tool_props

    layout.prop(props, "element_type", expand=True)
    layout.operator("object.populate_elements", text="Populate List")
    
    row = layout.row()
    row.template_list("UL_StandaloneElementList", "", props, "element_list", props, "element_list_index")

    total_items = len(props.element_list)
    selected_items = sum(1 for item in props.element_list if item.select)
    
    box = layout.box()
    row = box.row()
    row.label(text=f"Selected: {selected_items} / Total: {total_items}")
    
    row = layout.row(align=True)
    row.operator("object.select_all_elements", text="Select All")
    row.operator("object.select_none_elements", text="Select None")

    layout.operator("object.clear_standalone_elements", text="Clear Selected Elements")

classes = (
    StandaloneElementProperty,
    StandaloneToolsProperties,
    LIST_OT_PopulateElements,
    LIST_OT_ClearStandaloneElements,
    LIST_OT_SelectAll,
    LIST_OT_SelectNone,
    UL_StandaloneElementList,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.standalone_tool_props = bpy.props.PointerProperty(type=StandaloneToolsProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.standalone_tool_props

if __name__ == "__main__":
    register()
