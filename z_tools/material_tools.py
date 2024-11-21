import bpy
from bpy.types import Operator, Panel, PropertyGroup
from typing import List, Optional

class ZTOOLS_MT_MaterialListItem(PropertyGroup):
    name: bpy.props.StringProperty(name="Material Name")
    index: bpy.props.IntProperty(name="Material Index")
    selected: bpy.props.BoolProperty(name="Selected", default=False)

class ZTOOLS_PG_MaterialToolSettings(PropertyGroup):
    """Property group for material tool settings"""
    selection_mode: bpy.props.EnumProperty(
        name="Selection Mode",
        items=[
            ('OBJECT', "Object", "Select materials from a specific object"),
            ('COLLECTION', "Collection", "Select materials from a collection")
        ],
        default='OBJECT',
        update=lambda self, context: self.update_material_list(context)
    )
    selected_collection: bpy.props.PointerProperty(
        name="Selected Collection",
        type=bpy.types.Collection,
        update=lambda self, context: self.update_material_list(context)
    )
    selected_object: bpy.props.PointerProperty(
        name="Selected Object",
        type=bpy.types.Object,
        update=lambda self, context: self.update_material_list(context)
    )
    search_term: bpy.props.StringProperty(
        name="Search Materials",
        description="Filter materials by name",
        update=lambda self, context: self.update_material_list(context)
    )

    def update_material_list(self, context):
        """
        Automatically update material list when object or collection is selected
        """
        # Clear previous materials list
        context.scene.ztools_material_list.clear()

        # Determine objects based on selection mode
        objects_to_check: List[bpy.types.Object] = []
        
        if self.selection_mode == 'OBJECT':
            obj = self.selected_object
            if obj and obj.type == 'MESH':
                objects_to_check = [obj]
        
        elif self.selection_mode == 'COLLECTION':
            collection = self.selected_collection
            if collection:
                objects_to_check = [
                    obj for obj in collection.all_objects 
                    if obj.type == 'MESH'
                ]

        # Collect unique materials
        unique_materials = set()
        for obj in objects_to_check:
            for idx, material in enumerate(obj.data.materials):
                if material and material not in unique_materials:
                    # Apply search filter
                    if not self.search_term or self.search_term.lower() in material.name.lower():
                        unique_materials.add(material)
                        item = context.scene.ztools_material_list.add()
                        item.name = material.name
                        item.index = idx
                        item.selected = False

class ZTOOLS_OT_MaterialClearer(Operator):
    """Clear selected materials from objects"""
    bl_idname = "ztools.material_clearer"
    bl_label = "Clear Selected Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.ztools_material_tool_settings

        # Determine objects based on selection mode
        objects_to_process: List[bpy.types.Object] = []
        
        if settings.selection_mode == 'OBJECT':
            obj = settings.selected_object
            if obj and obj.type == 'MESH':
                objects_to_process = [obj]
            else:
                self.report({'WARNING'}, "Select a valid mesh object")
                return {'CANCELLED'}
        
        elif settings.selection_mode == 'COLLECTION':
            collection = settings.selected_collection
            if collection:
                objects_to_process = [
                    obj for obj in collection.all_objects 
                    if obj.type == 'MESH'
                ]
            else:
                self.report({'WARNING'}, "Select a valid collection")
                return {'CANCELLED'}

        # Get materials to remove
        materials_to_remove = [
            item.name for item in context.scene.ztools_material_list 
            if item.selected
        ]

        if not materials_to_remove:
            self.report({'WARNING'}, "No materials selected to clear")
            return {'CANCELLED'}

        # Process materials for each object
        cleared_count = 0
        for obj in objects_to_process:
            # Check if object has materials
            if not obj.data.materials:
                continue

            # Remove selected materials
            for material_name in materials_to_remove:
                for idx, mat in enumerate(obj.data.materials):
                    if mat and mat.name == material_name:
                        obj.data.materials.pop(index=idx)
                        cleared_count += 1
                        break

        # Update material list automatically
        settings.update_material_list(context)
        
        self.report({'INFO'}, f"Cleared {cleared_count} materials")
        return {'FINISHED'}

class ZTOOLS_UL_MaterialList(bpy.types.UIList):
    """Custom UIList with shift-select support"""
    last_index: Optional[int] = None

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "selected", text="")
            layout.label(text=item.name, icon='MATERIAL')
        elif self.layout_type in {'GRID'}:
            layout.prop(item, "selected", text="")

    def invoke(self, context, event):
        list_length = len(context.scene.ztools_material_list)
        current_index = context.scene.ztools_material_list_index

        if event.shift and self.last_index is not None and 0 <= current_index < list_length:
            start_index = min(self.last_index, current_index)
            end_index = max(self.last_index, current_index)
            
            for i in range(start_index, end_index + 1):
                context.scene.ztools_material_list[i].selected = True

        self.last_index = current_index
        return super().invoke(context, event)

class ZTOOLS_OT_SelectAllMaterials(Operator):
    """Select all materials in the list"""
    bl_idname = "ztools.select_all_materials"
    bl_label = "Select All Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for item in context.scene.ztools_material_list:
            item.selected = True
        return {'FINISHED'}

class ZTOOLS_OT_SelectNoneMaterials(Operator):
    """Deselect all materials in the list"""
    bl_idname = "ztools.select_none_materials"
    bl_label = "Deselect All Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for item in context.scene.ztools_material_list:
            item.selected = False
        return {'FINISHED'}

class ZTOOLS_PT_MaterialPanel(Panel):
    """Panel for material management"""
    bl_label = "Material Tools"
    bl_idname = "ZTOOLS_PT_material_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Z-Tools'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.ztools_material_tool_settings

        # Search Field
        layout.prop(settings, "search_term", icon='VIEWZOOM')

        # Selection Mode
        layout.prop(settings, "selection_mode", expand=True)

        # Object or Collection Selection
        if settings.selection_mode == 'OBJECT':
            layout.prop_search(
                settings, "selected_object", 
                context.scene, "objects", 
                text="Object"
            )
        else:
            layout.prop_search(
                settings, "selected_collection", 
                bpy.data, "collections", 
                text="Collection"
            )
        
        # Material List
        layout.label(text="Materials:")
        row = layout.row()
        row.template_list(
            "ZTOOLS_UL_MaterialList", 
            "ztools_material_list", 
            context.scene, 
            "ztools_material_list", 
            context.scene, 
            "ztools_material_list_index", 
            rows=5
        )
        
        # Select All and Select None buttons
        row = layout.row()
        row.operator("ztools.select_all_materials", text="Select All")
        row.operator("ztools.select_none_materials", text="Select None")
        
        # Disable Clear button if no materials or no selections
        materials = context.scene.ztools_material_list
        has_selected = any(item.selected for item in materials)
        
        # Clear Materials Button
        op = layout.operator("ztools.material_clearer", text="Clear Selected Materials")
        op.enabled = bool(materials and has_selected)


def register():
    bpy.utils.register_class(ZTOOLS_MT_MaterialListItem)
    bpy.utils.register_class(ZTOOLS_PG_MaterialToolSettings)
    bpy.utils.register_class(ZTOOLS_OT_MaterialClearer)
    bpy.utils.register_class(ZTOOLS_UL_MaterialList)
    bpy.utils.register_class(ZTOOLS_PT_MaterialPanel)
    bpy.utils.register_class(ZTOOLS_OT_SelectAllMaterials)
    bpy.utils.register_class(ZTOOLS_OT_SelectNoneMaterials)

    # Register properties
    bpy.types.Scene.ztools_material_list = bpy.props.CollectionProperty(type=ZTOOLS_MT_MaterialListItem)
    bpy.types.Scene.ztools_material_list_index = bpy.props.IntProperty(name="Material List Index", default=0)
    bpy.types.Scene.ztools_material_tool_settings = bpy.props.PointerProperty(type=ZTOOLS_PG_MaterialToolSettings)

def unregister():
    # Unregister properties
    del bpy.types.Scene.ztools_material_list
    del bpy.types.Scene.ztools_material_list_index
    del bpy.types.Scene.ztools_material_tool_settings

    # Unregister classes
    bpy.utils.unregister_class(ZTOOLS_PT_MaterialPanel)
    bpy.utils.unregister_class(ZTOOLS_UL_MaterialList)
    bpy.utils.unregister_class(ZTOOLS_OT_MaterialClearer)
    bpy.utils.unregister_class(ZTOOLS_PG_MaterialToolSettings)
    bpy.utils.unregister_class(ZTOOLS_MT_MaterialListItem)
    bpy.utils.unregister_class(ZTOOLS_OT_SelectAllMaterials)
    bpy.utils.unregister_class(ZTOOLS_OT_SelectNoneMaterials)

# اجرای اسکریپت در بلندر
if __name__ == "__main__":
    register()
