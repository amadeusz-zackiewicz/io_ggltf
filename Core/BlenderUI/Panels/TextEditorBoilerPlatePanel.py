import bpy

class PasteBoilerPlatePanel(bpy.types.Panel):
    """Panel containing methods that paste object accessors for the user"""
    bl_label = "Boiler Plate"
    bl_idname = "GGLTF_PT_boiler_plate_pasting"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "gglTF"

    def draw(self, context):
        self.layout.row().operator("ggltf.paste_adv_boiler_plate", text="Boiler Plate", icon="FILE_TEXT")

classes = [
    PasteBoilerPlatePanel
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
        

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)