import bpy
from io_ggltf.Core.BlenderUI.Operators import TextEditorAccessorsOps

class PasteAccessorsPanel(bpy.types.Panel):
    """Panel containing methods that paste object accessors for the user"""
    bl_label = "Accessor Pasting"
    bl_idname = "GGLTF_PT_panel_accessors_pasting"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "gglTF"

    def draw(self, context):
        for c in TextEditorAccessorsOps.classes:
            layout = self.layout
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