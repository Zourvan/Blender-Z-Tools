import bpy
import bmesh
import mathutils
import numpy as np
from bpy.types import Operator, Panel, AddonPreferences
from bpy.props import FloatProperty, BoolProperty, IntProperty, StringProperty

bl_info = {
    "name": "Z-Tools: Neighborhood Face Dissolve",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (3, 3, 0),
    "location": "View3D > Z-Tools Panel",
    "description": "Advanced tool for dissolving faces based on neighborhood coplanarity",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}

class ZTOOLS_OT_Dissolve_Neighborhood_Faces(Operator):
    """Dissolve faces based on neighborhood coplanarity"""
    bl_idname = "ztools.dissolve_neighborhood_faces"
    bl_label = "Dissolve Neighborhood Faces"
    bl_options = {'REGISTER', 'UNDO'}

    angle_threshold: FloatProperty(
        name="Angle Threshold",
        description="Maximum angle between faces to be considered coplanar",
        default=5.0,
        min=0.0,
        max=180.0,
        subtype='ANGLE'
    )

    neighborhood_depth: IntProperty(
        name="Neighborhood Depth",
        description="Depth of face neighborhood to check",
        default=2,
        min=1,
        max=5
    )

    min_neighborhood_size: IntProperty(
        name="Min Neighborhood Size",
        description="Minimum number of faces in neighborhood to consider dissolution",
        default=3,
        min=2,
        max=10
    )

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and 
                context.active_object.type == 'MESH' and 
                context.active_object.mode == 'EDIT')

    def execute(self, context):
        obj = context.active_object
        total_dissolved_faces = 0

        # Convert angle to radians
        angle_radians = np.radians(self.angle_threshold)

        # Create bmesh
        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()

        # Track processed faces to avoid repeated processing
        processed_faces = set()

        # Iterate through all faces
        for base_face in bm.faces:
            if base_face in processed_faces:
                continue

            # Get neighborhood of faces
            neighborhood = self.get_face_neighborhood(base_face, self.neighborhood_depth)
            
            # Filter out invalid or already processed faces
            valid_neighborhood = [
                face for face in neighborhood 
                if face not in processed_faces and 
                face.calc_area() > 0 and 
                face.normal.length > 0
            ]

            # Check if neighborhood meets minimum size
            if len(valid_neighborhood) < self.min_neighborhood_size:
                continue

            # Check coplanarity of neighborhood
            if self.is_neighborhood_coplanar(valid_neighborhood, angle_radians):
                # Dissolve neighborhood faces
                try:
                    bmesh.ops.dissolve_faces(bm, faces=valid_neighborhood)
                    total_dissolved_faces += len(valid_neighborhood)
                    
                    # Mark processed faces
                    processed_faces.update(valid_neighborhood)
                except Exception as e:
                    self.report({'WARNING'}, f"Error dissolving neighborhood: {str(e)}")

        # Update mesh
        bmesh.update_edit_mesh(obj.data)

        # Report results
        if total_dissolved_faces > 0:
            self.report({'INFO'}, f"Dissolved {total_dissolved_faces} faces in neighborhoods")
        else:
            self.report({'INFO'}, "No suitable face neighborhoods found to dissolve")
        
        return {'FINISHED'}

    def get_face_neighborhood(self, base_face, depth):
        """
        Recursively get face neighborhood up to specified depth
        Uses a breadth-first search approach
        """
        neighborhood = {base_face}
        frontier = {base_face}
        
        for _ in range(depth):
            next_frontier = set()
            for face in frontier:
                # Get adjacent faces through edges
                for edge in face.edges:
                    for adj_face in edge.link_faces:
                        if adj_face not in neighborhood:
                            next_frontier.add(adj_face)
                            neighborhood.add(adj_face)
            
            frontier = next_frontier
            
            # Stop if no new faces found
            if not frontier:
                break
        
        return list(neighborhood)

    def is_neighborhood_coplanar(self, neighborhood, angle_threshold):
        """
        Check if all faces in neighborhood are coplanar
        Uses average normal and checks deviation
        """
        if not neighborhood:
            return False

        # Calculate average normal using mathutils.Vector
        avg_normal = mathutils.Vector(
            np.mean([np.array(face.normal) for face in neighborhood], axis=0)
        )

        # Check each face's normal against average
        for face in neighborhood:
            try:
                # Calculate angle between face normal and average normal
                angle = abs(face.normal.angle(avg_normal))
                
                # Check if angle exceeds threshold
                if angle > angle_threshold:
                    return False
            except Exception:
                # Handle potential calculation errors
                return False

        return True

class ZTOOLS_PT_NeighborhoodFacesPanel(Panel):
    """Panel for Neighborhood Face Dissolution"""
    bl_label = "Neighborhood Face Tools"
    bl_idname = "ZTOOLS_PT_neighborhood_faces_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Z-Tools'

    def draw(self, context):
        layout = self.layout
        
        # Main operator button
        layout.operator("ztools.dissolve_neighborhood_faces", text="Dissolve Neighborhood Faces")
        
        # Advanced settings
        box = layout.box()
        box.label(text="Advanced Settings:")
        box.prop(context.scene, "ztools_angle_threshold")
        box.prop(context.scene, "ztools_neighborhood_depth")
        box.prop(context.scene, "ztools_min_neighborhood_size")

class ZTOOLS_AddonPreferences(AddonPreferences):
    """Addon preferences for Z-Tools"""
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        layout.label(text="Z-Tools Neighborhood Face Dissolve Settings")

def register():
    # Register classes
    bpy.utils.register_class(ZTOOLS_OT_Dissolve_Neighborhood_Faces)
    bpy.utils.register_class(ZTOOLS_PT_NeighborhoodFacesPanel)
    bpy.utils.register_class(ZTOOLS_AddonPreferences)

    # Register scene properties
    bpy.types.Scene.ztools_angle_threshold = FloatProperty(
        name="Angle Threshold (Degrees)",
        description="Maximum angle between faces to consider coplanar",
        default=5.0,
        min=0.0,
        max=180.0,
        subtype='ANGLE'
    )
    bpy.types.Scene.ztools_neighborhood_depth = IntProperty(
        name="Neighborhood Depth",
        description="Depth of face neighborhood to check",
        default=2,
        min=1,
        max=5
    )
    bpy.types.Scene.ztools_min_neighborhood_size = IntProperty(
        name="Min Neighborhood Size",
        description="Minimum number of faces in neighborhood to dissolve",
        default=3,
        min=2,
        max=10
    )

def unregister():
    # Unregister scene properties
    del bpy.types.Scene.ztools_min_neighborhood_size
    del bpy.types.Scene.ztools_neighborhood_depth
    del bpy.types.Scene.ztools_angle_threshold

    # Unregister classes
    bpy.utils.unregister_class(ZTOOLS_AddonPreferences)
    bpy.utils.unregister_class(ZTOOLS_PT_NeighborhoodFacesPanel)
    bpy.utils.unregister_class(ZTOOLS_OT_Dissolve_Neighborhood_Faces)

if __name__ == "__main__":
    register()
