bl_info = {
    "name": "Z-Tools",
    "author": "Nima Heydarzadeh",
    "version": (1, 0, 0),
    "blender": (3, 3, 0),
    "location": "View3D > Sidebar > Z-Tools",
    "description": "Collection and material management tools",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}

import bpy # type: ignore
import sys
import os

# تعریف نام‌های ماژول‌ها
modulesNames = [
    'AdvancedVertexMerge',
    'collection_scaler',    
    'Blender_rename',
    'dissolvesFaces',
    'StandaloneElements',
    'material_tools',
    'transform_manager',
]

# ساخت دیکشنری نام‌های کامل ماژول‌ها
modulesFullNames = {}
for currentModuleName in modulesNames:
    modulesFullNames[currentModuleName] = (f'{__name__}.{currentModuleName}')

# وارد کردن ماژول‌ها
import importlib
for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)

class ZToolsModuleSelector(bpy.types.PropertyGroup):
    active_module: bpy.props.EnumProperty(
        items=[
            ('AdvancedVertexMerge', 'Advanced Vertex Merge', 'Advanced vertex merging'),
            ('collection_scaler', 'Collection Scaler', 'Scale collections'),
            ('Blender_rename', 'Rename Tools', 'Rename objects'),
            ('dissolvesFaces', 'Dissolve Faces', 'Dissolve faces tools'),
            ('StandaloneElements', 'Elements Remover', 'Remove standalone elements'),
            ('material_tools', 'Material Tools', 'Material management tools'),
            ('transform_manager', 'Transform Manager', 'Transform management tools'),
        ],
        name="Module"
    ) # type: ignore

class ZToolsPanel(bpy.types.Panel):
    bl_label = "Z-Tools"
    bl_idname = "VIEW3D_PT_z_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Z-Tools'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # منوی آبشاری برای انتخاب ماژول
        layout.prop(scene.z_tools, "active_module")
        
        # نمایش پنل ماژول انتخاب شده
        active_module = scene.z_tools.active_module
        module_name = f"{__name__}.{active_module}"
        if module_name in sys.modules:
            module = sys.modules[module_name]
            if hasattr(module, 'draw_panel'):
                module.draw_panel(context, layout)

classes = (
    ZToolsModuleSelector,
    ZToolsPanel,
)

def register():
    # ثبت کلاس‌های اصلی
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # ثبت متغیر در صحنه
    bpy.types.Scene.z_tools = bpy.props.PointerProperty(type=ZToolsModuleSelector)
    
    # ثبت ماژول‌ها
    for currentModuleFullName in modulesFullNames.values():
        if currentModuleFullName in sys.modules:
            module = sys.modules[currentModuleFullName]
            if hasattr(module, 'register'):
                module.register()

def unregister():
    # حذف ثبت ماژول‌ها
    for currentModuleFullName in reversed(list(modulesFullNames.values())):
        if currentModuleFullName in sys.modules:
            module = sys.modules[currentModuleFullName]
            if hasattr(module, 'unregister'):
                module.unregister()
    
    # حذف متغیر از صحنه
    del bpy.types.Scene.z_tools
    
    # حذف ثبت کلاس‌های اصلی
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
