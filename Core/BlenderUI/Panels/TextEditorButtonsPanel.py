import bpy
from io_ggltf.Core.BlenderUI.Operators import TextEditorButtonsOps

class ButtonsPanel(bpy.types.Panel):
    """"""
    bl_label = "Buttons"
    bl_idname = "GGLTF_PT_panel_buttons_panel"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "gglTF"

    def draw(self, context):
        layout = self.layout
        for c in TextEditorButtonsOps.classes:
            row = layout.row()
            row.operator(c.bl_idname, text=c.bl_button_label, icon=c.bl_button_icon)

classes = [
    ButtonsPanel
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
        

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)