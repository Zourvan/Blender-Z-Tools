import bpy
from bpy.types import Operator, Panel
from bpy.props import FloatVectorProperty, EnumProperty

def update_collection_list(self, context):
    """Dynamically update collection list"""
    collections = [
        (col.name, col.name, "") 
        for col in bpy.data.collections
    ]
    return collections

class ZTOOLS_OT_CollectionScaler(Operator):
    """Scale collections based on input values"""
    bl_idname = "ztools.collection_scaler"
    bl_label = "Scale Collections"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get the selected collection
        selected_collection = context.scene.ztools_collections

        try:
            # Find the collection
            collection = bpy.data.collections.get(selected_collection)
            
            if collection:
                # Scale all objects in the collection
                scale_x = context.scene.ztools_scale_x
                scale_y = context.scene.ztools_scale_y
                scale_z = context.scene.ztools_scale_z
                
                for obj in collection.all_objects:
                    obj.scale = (scale_x, scale_y, scale_z)
                    obj.update_tag()
                
                # Update the scene
                bpy.context.view_layer.update()
                
                self.report({'INFO'}, f"Scaled collection: {selected_collection}")
            else:
                self.report({'ERROR'}, f"Collection not found: {selected_collection}")
        
        except Exception as e:
            self.report({'ERROR'}, str(e))
        
        return {'FINISHED'}

class ZTOOLS_PT_CollectionPanel(Panel):
    """Panel for Collection Tools"""
    bl_label = "Collection Tools"
    bl_idname = "ZTOOLS_PT_collection_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Z-Tools'

    def draw(self, context):
        layout = self.layout
        
        # Collection dropdown
        layout.prop(context.scene, "ztools_collections", text="Collection")
        
        # Scale input fields
        row = layout.row()
        row.prop(context.scene, "ztools_scale_x", text="X")
        row.prop(context.scene, "ztools_scale_y", text="Y")
        row.prop(context.scene, "ztools_scale_z", text="Z")
        
        # Do Scale Button
        layout.operator("ztools.collection_scaler", text="Scale them!!")

def register():
    # Register properties
    bpy.types.Scene.ztools_collections = bpy.props.EnumProperty(
        name="Collections",
        description="Select a collection to scale",
        items=update_collection_list
    )
    bpy.types.Scene.ztools_scale_x = bpy.props.FloatProperty(
        name="Scale X", 
        default=1.0, 
        min=0.01, 
        max=100
    )
    bpy.types.Scene.ztools_scale_y = bpy.props.FloatProperty(
        name="Scale Y", 
        default=1.0, 
        min=0.01, 
        max=100
    )
    bpy.types.Scene.ztools_scale_z = bpy.props.FloatProperty(
        name="Scale Z", 
        default=1.0, 
        min=0.01, 
        max=100
    )

    # Register classes
    bpy.utils.register_class(ZTOOLS_OT_CollectionScaler)
    bpy.utils.register_class(ZTOOLS_PT_CollectionPanel)

def unregister():
    # Unregister properties
    del bpy.types.Scene.ztools_collections
    del bpy.types.Scene.ztools_scale_x
    del bpy.types.Scene.ztools_scale_y
    del bpy.types.Scene.ztools_scale_z

    # Unregister classes
    bpy.utils.unregister_class(ZTOOLS_OT_CollectionScaler)
    bpy.utils.unregister_class(ZTOOLS_PT_CollectionPanel)
