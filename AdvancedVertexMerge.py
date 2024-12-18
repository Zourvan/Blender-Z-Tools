import bpy # type: ignore
import bmesh # type: ignore
from mathutils import Vector # type: ignore
from bpy.types import Operator, PropertyGroup # type: ignore
from bpy.props import FloatProperty, BoolProperty, EnumProperty # type: ignore

class ZTOOLS_PG_VertexMergeSettings(PropertyGroup):
    """Property group for vertex merge tool settings"""
    merge_distance: FloatProperty(
        name="Merge Distance",
        description="Maximum distance between vertices to merge",
        default=0.01,
        min=0.0001,
        max=10.0,
        precision=4,
        step=0.1
    ) # type: ignore

    merge_mode: EnumProperty(
        name="Merge Mode",
        description="Select merging strategy",
        items=[
            ('CENTER', 'Center Point', 'Merge to average center point'),
            ('FIRST', 'First Selected', 'Merge to first selected vertex'),
            ('LAST', 'Last Selected', 'Merge to last selected vertex')
        ],
        default='CENTER'
    ) # type: ignore

    limit_to_selection: BoolProperty(
        name="Limit to Selection",
        description="Only merge vertices within current selection",
        default=False
    ) # type: ignore

class ZTOOLS_OT_AdvancedVertexMerge(Operator):
    """Advanced Vertex Merge Tool"""
    bl_idname = "ztools.advanced_vertex_merge"
    bl_label = "Advanced Vertex Merge"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and 
                context.active_object.type == 'MESH' and 
                context.active_object.mode == 'EDIT')

    def execute(self, context):
        settings = context.scene.ztools_vertex_merge_settings
        obj = context.active_object
        
        # Create a fresh bmesh each time
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.verts.index_update()

        # Track vertices to merge
        vertices_to_merge = []

        # Determine vertices to process
        if settings.limit_to_selection:
            vertices = [v for v in bm.verts if v.select and v.is_valid]
        else:
            vertices = [v for v in bm.verts if v.is_valid]

        # First pass: find vertices to merge
        for i, base_vert in enumerate(vertices):
            if not base_vert.is_valid:
                continue
            
            nearby_verts = [
                v for v in vertices[i+1:] 
                if v.is_valid and 
                v != base_vert and 
                (base_vert.co - v.co).length <= settings.merge_distance
            ]
            
            if nearby_verts:
                vertices_to_merge.append([base_vert] + nearby_verts)

        # Second pass: merge vertices
        merged_count = 0
        for merge_group in vertices_to_merge:
            # Filter out invalid vertices
            valid_group = [v for v in merge_group if v.is_valid]
            
            if not valid_group:
                continue

            if settings.merge_mode == 'CENTER':
                # Safely calculate center
                try:
                    target_co = sum((v.co for v in valid_group), Vector()) / len(valid_group)
                    valid_group[0].co = target_co
                except Exception as e:
                    print(f"Error calculating center: {e}")
                    continue

            elif settings.merge_mode == 'FIRST':
                target_co = valid_group[0].co
            elif settings.merge_mode == 'LAST':
                target_co = valid_group[-1].co
                valid_group[0].co = target_co

            # Remove duplicate vertices
            for v in valid_group[1:]:
                if v.is_valid:
                    try:
                        bm.verts.remove(v)
                        merged_count += 1
                    except Exception as e:
                        print(f"Error removing vertex: {e}")

        # Update bmesh
        try:
            bmesh.update_edit_mesh(obj.data)
            self.report({'INFO'}, f"Merged Vertices: {merged_count}")
        except Exception as e:
            self.report({'ERROR'}, f"Mesh update failed: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

def draw_panel(context, layout):
    """Draw function for vertex merge UI"""
    settings = context.scene.ztools_vertex_merge_settings
    
    box = layout.box()
    box.label(text="Vertex Merge Settings")
    box.prop(settings, "merge_distance")
    box.prop(settings, "merge_mode")
    box.prop(settings, "limit_to_selection")
    box.operator("ztools.advanced_vertex_merge", text="Merge Vertices")

def register():
    bpy.utils.register_class(ZTOOLS_PG_VertexMergeSettings)
    bpy.utils.register_class(ZTOOLS_OT_AdvancedVertexMerge)
    bpy.types.Scene.ztools_vertex_merge_settings = bpy.props.PointerProperty(type=ZTOOLS_PG_VertexMergeSettings)

def unregister():
    bpy.utils.unregister_class(ZTOOLS_PG_VertexMergeSettings)
    bpy.utils.unregister_class(ZTOOLS_OT_AdvancedVertexMerge)
    del bpy.types.Scene.ztools_vertex_merge_settings
