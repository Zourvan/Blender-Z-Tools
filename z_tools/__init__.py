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

import bpy
import sys
import os

# Dynamic import of modules
modulesNames = [
    'collection_scaler',
    'material_tools',
    'Blender_rename',
    'dissolvesFaces',
    'AdvancedVertexMerge',
]

modulesFullNames = {}
for currentModuleName in modulesNames:
    modulesFullNames[currentModuleName] = (f'{__name__}.{currentModuleName}')

import importlib
for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        
def register():
    # Dynamic registration of modules
    for currentModuleFullName in modulesFullNames.values():
        if currentModuleFullName in sys.modules:
            module = sys.modules[currentModuleFullName]
            if hasattr(module, 'register'):
                module.register()

def unregister():
    # Dynamic unregistration of modules
    for currentModuleFullName in reversed(list(modulesFullNames.values())):
        if currentModuleFullName in sys.modules:
            module = sys.modules[currentModuleFullName]
            if hasattr(module, 'unregister'):
                module.unregister()

if __name__ == "__main__":
    register()
