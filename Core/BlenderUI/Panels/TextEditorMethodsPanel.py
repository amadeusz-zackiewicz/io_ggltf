import bpy
from io_ggltf.Core.BlenderUI.Operators import TextEditorLibraryOps

def __draw(self, context):
    layout = self.layout
    for method in self._methods:
        row = layout.row()
        row.operator(method.bl_idname, text=method.methodName)

class PasteMethods(bpy.types.Panel):
    """Panel containing method that can be used with this addon"""
    bl_label = "Advanced Methods Library"
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
    for k, v in TextEditorLibraryOps.classes.items():
        newPanel = type(f"io_ggltf.adv_method_paste_{k}".lower(), (bpy.types.Panel, ), {
            "bl_label": k,
            "bl_idname": f"GGLTF_PT_adv_methods_{k.lower()}",
            "bl_parent_id": f"GGLTF_PT_panel_adv_methods_pasting",
            "bl_space_type": "TEXT_EDITOR",
            "bl_region_type": "UI",
            "_methods": v,
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
    for c in classes:
        bpy.utils.unregister_class(c)

    for c in generatedClasses:
        bpy.utils.unregister_class(c)
        del c

    generatedClasses = []
