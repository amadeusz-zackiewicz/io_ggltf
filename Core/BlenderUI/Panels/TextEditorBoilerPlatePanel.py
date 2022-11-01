import bpy
from io_ggltf.Core.BlenderUI.Operators import TextEditorBoilerPlateOps as Op

class PasteBoilerPlatePanel(bpy.types.Panel):
    """Panel containing methods that paste object accessors for the user"""
    bl_label = "Boiler Plate"
    bl_idname = "GGLTF_PT_boiler_plate_pasting"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "gglTF"

    def draw(self, context):
        self.layout.row().operator(Op.PasteImportsOnlyOperator.bl_idname, text=Op.PasteImportsOnlyOperator.bl_button_label, icon=Op.PasteImportsOnlyOperator.bl_button_icon)
        self.layout.row().operator(Op.PasteQuickStartOperator.bl_idname, text=Op.PasteQuickStartOperator.bl_button_label, icon=Op.PasteQuickStartOperator.bl_button_icon)
        self.layout.row().operator(Op.PasteMakeButtonOperator.bl_idname, text=Op.PasteMakeButtonOperator.bl_button_label, icon=Op.PasteMakeButtonOperator.bl_button_icon)

classes = [
    PasteBoilerPlatePanel
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
        

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)