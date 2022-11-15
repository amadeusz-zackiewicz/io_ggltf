import bpy
from io_ggltf.Core.BlenderUI.Operators import TextEditorLibraryOps

def __draw(self, context):
    layout = self.layout
    for pair in self.classPairs:
        row = layout.row()
        row.operator(pair[0].bl_idname, text=pair[0].funcName)
        if pair[1] != None:
            row.operator(pair[1].bl_idname, text="", icon=pair[1].bl_button_icon)

class PasteMethods(bpy.types.Panel):
    """Panel containing method that can be used with this addon"""
    bl_label = "Advanced Snippets"
    bl_idname = "GGLTF_PT_panel_adv_methods_pasting"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "gglTF"

    def draw(self, context):
        pass

classes = [
    PasteMethods
]

generatedClasses = []

def __generate_classes():
    for moduleName, classPairs in TextEditorLibraryOps.classes.items():
        newPanel = type(f"io_ggltf.adv_module_info_{moduleName}".lower(), (bpy.types.Panel, ), {
            "bl_label": moduleName,
            "bl_idname": f"GGLTF_PT_adv_methods_{moduleName.lower()}",
            "bl_parent_id": f"GGLTF_PT_panel_adv_methods_pasting",
            "bl_space_type": "TEXT_EDITOR",
            "bl_region_type": "UI",
            "classPairs": classPairs,
            "draw": __draw,
            "bl_options": {"DEFAULT_CLOSED"}
        })
        generatedClasses.append(newPanel)



def register():
    for c in classes:
        bpy.utils.register_class(c)

    __generate_classes()
    for c in generatedClasses:
        bpy.utils.register_class(c)
        

def unregister():
    from io_ggltf.Core.BlenderUI.Panels.TextEditorAdvFuncsPanel import generatedClasses
    for c in classes:
        bpy.utils.unregister_class(c)

    for c in generatedClasses:
        bpy.utils.unregister_class(c)
        del c

    generatedClasses = []
