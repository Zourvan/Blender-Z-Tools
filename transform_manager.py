import bpy
import bmesh
from bpy.types import Operator, Panel, PropertyGroup , AddonPreferences , UIList
from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty, CollectionProperty, IntProperty, PointerProperty


# کلاس برای نگهداری اطلاعات هر مش در لیست
class MeshListItem(PropertyGroup):
    name: StringProperty(
        name="Name",
        description="Mesh name",
        default=""
    )
    is_selected: BoolProperty(
        name="Selected",
        description="Whether this mesh is selected",
        default=False
    )

# کلاس برای نمایش لیست مش‌ها
class MESH_UL_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, "is_selected", text="")
            row.label(text=item.name)

# Operator برای به‌روزرسانی لیست مش‌ها
class OBJECT_OT_update_mesh_list(Operator):
    bl_idname = "object.update_mesh_list"
    bl_label = "Update Mesh List"
    bl_description = "Update the list of meshes in the selected collection"

    def execute(self, context):
        props = context.scene.transform_manager_props
        collection = props.selected_collection

        # پاک کردن لیست قبلی
        props.mesh_list.clear()

        if collection:
            # اضافه کردن تمام مش‌های موجود در کالکشن به لیست
            for obj in collection.objects:
                if obj.type == 'MESH':
                    item = props.mesh_list.add()
                    item.name = obj.name
                    item.is_selected = False

        return {'FINISHED'}

# Operator برای Select All
class MESH_OT_select_all_meshes(Operator):
    bl_idname = "mesh.select_all_meshes"
    bl_label = "Select All"
    bl_description = "Select all meshes in the list"
    
    def execute(self, context):
        props = context.scene.transform_manager_props
        for item in props.mesh_list:
            item.is_selected = True
        return {'FINISHED'}

# Operator برای Select None
class MESH_OT_select_none_meshes(Operator):
    bl_idname = "mesh.select_none_meshes"
    bl_label = "Select None"
    bl_description = "Deselect all meshes in the list"
    
    def execute(self, context):
        props = context.scene.transform_manager_props
        for item in props.mesh_list:
            item.is_selected = False
        return {'FINISHED'}

# Operator برای اعمال ترنسفورم
class OBJECT_OT_apply_transforms(Operator):
    bl_idname = "object.apply_transforms"
    bl_label = "Apply Transform"
    bl_description = "Apply the selected transform to selected meshes"

    def execute(self, context):
        props = context.scene.transform_manager_props
        collection = props.selected_collection

        if collection:
            # ذخیره آبجکت فعال فعلی
            original_active = context.view_layer.objects.active
            
            # لیست آبجکت‌های انتخاب شده
            selected_objects = []
            
            # انتخاب تمام آبجکت‌های مورد نظر
            for item in props.mesh_list:
                if item.is_selected:
                    obj = bpy.data.objects.get(item.name)
                    if obj and obj.type == 'MESH':
                        obj.select_set(True)
                        selected_objects.append(obj)
                    else:
                        obj.select_set(False)
            
            if selected_objects:
                # تنظیم اولین آبجکت به عنوان آبجکت فعال
                context.view_layer.objects.active = selected_objects[0]
                
                # اعمال ترنسفورم به همه آبجکت‌های انتخاب شده
                if props.transform_type == 'LOCATION':
                    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
                elif props.transform_type == 'ROTATION':
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                elif props.transform_type == 'SCALE':
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                elif props.transform_type == 'ALL':
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                
                # برگرداندن وضعیت انتخاب به حالت اول
                for obj in selected_objects:
                    obj.select_set(False)
                
                # برگرداندن آبجکت فعال به حالت اول
                context.view_layer.objects.active = original_active

        return {'FINISHED'}


# PropertyGroup اصلی
class TransformManagerProperties(PropertyGroup):
    selected_collection: PointerProperty(
        name="Collection",
        type=bpy.types.Collection,
        description="Select a collection to manage transforms"
    )
    
    transform_type: EnumProperty(
        name="Transform Type",
        items=[
            ('LOCATION', "Location", "Apply location transform"),
            ('ROTATION', "Rotation", "Apply rotation transform"),
            ('SCALE', "Scale", "Apply scale transform"),
            ('ALL', "All Transforms", "Apply all transforms")
        ],
        default='ALL'
    )
    
    mesh_list: CollectionProperty(type=MeshListItem)
    active_mesh_index: IntProperty()

# پنل اصلی
def draw_panel(context, layout): 
    props = context.scene.transform_manager_props

    # محاسبه ارتفاع پنجره و تعیین تعداد ردیف‌ها
    region_height = context.region.height
    list_height = max(region_height * 0.2, 200)  # حداقل 200 پیکسل، 20 درصد ارتفاع پنجره
    row_height = 25  # ارتفاع هر ردیف (پیش‌فرض بلندر)
    num_rows = int(list_height / row_height)

    col = layout.column()
    col.prop(props, "selected_collection")

    if props.selected_collection:
        col.operator("object.update_mesh_list", text="Refresh Mesh List")
        col.prop(props, "transform_type")
        
        # دکمه‌های Select All و Select None
        row = col.row(align=True)
        row.operator("mesh.select_all_meshes", text="Select All")
        row.operator("mesh.select_none_meshes", text="Select None")
        
        box = layout.box()
        row = box.row()
        row.template_list(
            "MESH_UL_list", 
            "mesh_list",
            props, 
            "mesh_list",
            props, 
            "active_mesh_index",
            rows=num_rows
        )
        
        layout.operator("object.apply_transforms", text="Apply Transform")

# ثبت کلاس‌ها
classes = (
    MeshListItem,
    MESH_UL_list,
    OBJECT_OT_update_mesh_list,
    MESH_OT_select_all_meshes,
    MESH_OT_select_none_meshes,
    OBJECT_OT_apply_transforms,
    TransformManagerProperties,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.transform_manager_props = PointerProperty(type=TransformManagerProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.transform_manager_props

if __name__ == "__main__":
    register()
