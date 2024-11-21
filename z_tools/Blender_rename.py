import bpy
from bpy.types import Operator, Panel, PropertyGroup

class ZTOOLS_PG_RenameSettings(PropertyGroup):
    """Property group for rename tool settings"""
    rename_mode: bpy.props.EnumProperty(
        name="Rename Mode",
        items=[
            ('FULL_RENAME', "Full Rename", "Rename all objects in collection or with specific name"),
            ('PREFIX_TYPE', "Add Object Type Prefix", "Add object type as prefix to object name")
        ],
        default='FULL_RENAME'
    )
    
    # For Full Rename Mode
    search_name: bpy.props.StringProperty(
        name="Search Name",
        description="Name to search for objects to rename"
    )
    
    rename_target: bpy.props.StringProperty(
        name="New Name",
        description="New name to apply to matching objects"
    )
    
    rename_scope: bpy.props.EnumProperty(
        name="Rename Scope",
        items=[
            ('OBJECT', "Single Object", "Rename a specific object"),
            ('COLLECTION', "Entire Collection", "Rename all objects in a collection")
        ],
        default='OBJECT'
    )
    
    selected_collection: bpy.props.PointerProperty(
        name="Selected Collection",
        type=bpy.types.Collection
    )
    
    selected_object: bpy.props.PointerProperty(
        name="Selected Object",
        type=bpy.types.Object
    )

class ZTOOLS_OT_RenameObjects(Operator):
    """Rename objects based on selected mode"""
    bl_idname = "ztools.rename_objects"
    bl_label = "Rename Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.ztools_rename_settings
        
        # Determine objects to rename based on scope
        objects_to_rename = []
        
        if settings.rename_mode == 'FULL_RENAME':
            if settings.rename_scope == 'OBJECT':
                if settings.selected_object:
                    objects_to_rename = [settings.selected_object]
            elif settings.rename_scope == 'COLLECTION':
                if settings.selected_collection:
                    objects_to_rename = [
                        obj for obj in settings.selected_collection.all_objects 
                        if settings.search_name in obj.name
                    ]
            
            # Rename objects
            renamed_count = 0
            for obj in objects_to_rename:
                if settings.search_name in obj.name:
                    obj.name = obj.name.replace(settings.search_name, settings.rename_target)
                    renamed_count += 1
            
            self.report({'INFO'}, f"Renamed {renamed_count} objects")
        
        elif settings.rename_mode == 'PREFIX_TYPE':
            # Determine objects to rename
            if settings.rename_scope == 'OBJECT':
                objects_to_rename = [settings.selected_object] if settings.selected_object else []
            elif settings.rename_scope == 'COLLECTION':
                objects_to_rename = settings.selected_collection.all_objects if settings.selected_collection else []
            
            # Add object type prefix
            renamed_count = 0
            for obj in objects_to_rename:
                # Skip if already prefixed
                if not obj.name.startswith(obj.type.lower() + '_'):
                    obj.name = f"{obj.type.lower()}_{obj.name}"
                    renamed_count += 1
            
            self.report({'INFO'}, f"Added type prefix to {renamed_count} objects")
        
        return {'FINISHED'}

class ZTOOLS_PT_RenamePanel(bpy.types.Panel):
    """Panel for object renaming tools"""
    bl_label = "Object Rename Tools"
    bl_idname = "ZTOOLS_PT_rename_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Z-Tools'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.ztools_rename_settings

        # Rename Mode Selection
        layout.prop(settings, "rename_mode", expand=True)

        # Scope Selection
        layout.prop(settings, "rename_scope", expand=True)

        # Object or Collection Selection
        if settings.rename_scope == 'OBJECT':
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

        # Mode-specific inputs
        if settings.rename_mode == 'FULL_RENAME':
            layout.prop(settings, "search_name", text="Search Name")
            layout.prop(settings, "rename_target", text="New Name")
        
        # Rename Button
        layout.operator("ztools.rename_objects", text="Rename Objects")

def register():
    # Register property group
    bpy.utils.register_class(ZTOOLS_PG_RenameSettings)
    
    # Register operators
    bpy.utils.register_class(ZTOOLS_OT_RenameObjects)
    
    # Register panel
    bpy.utils.register_class(ZTOOLS_PT_RenamePanel)
    
    # Add property to scene
    bpy.types.Scene.ztools_rename_settings = bpy.props.PointerProperty(type=ZTOOLS_PG_RenameSettings)

def unregister():
    # Remove scene property
    del bpy.types.Scene.ztools_rename_settings
    
    # Unregister classes
    bpy.utils.unregister_class(ZTOOLS_PT_RenamePanel)
    bpy.utils.unregister_class(ZTOOLS_OT_RenameObjects)
    bpy.utils.unregister_class(ZTOOLS_PG_RenameSettings)
