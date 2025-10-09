import bpy
from io_ggltf.Core.BlenderUI.Operators import TextEditorReferenceOps

class PasteAccessorsPanel(bpy.types.Panel):
    """Panel containing buttons that paste object accessors for the user"""
    bl_label = "Get references"
    bl_idname = "GGLTF_PT_panel_ref_pasting"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "gglTF"

    def draw(self, context):
        layout = self.layout
        for c in TextEditorReferenceOps.classes:
            row = layout.row()
            row.operator(c.bl_idname, text=c.bl_button_label, icon=c.bl_button_icon)

classes = [
    PasteAccessorsPanel
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
        

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)