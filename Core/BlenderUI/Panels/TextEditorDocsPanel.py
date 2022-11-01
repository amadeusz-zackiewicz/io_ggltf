import bpy

class DocumentationPanel(bpy.types.Panel):
    """Panel containing """
    bl_label = "Docs & Issues"
    bl_idname = "GGLTF_PT_docs_buttons"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "gglTF"

    def draw(self, context):
        self.layout.row().operator("ggltf.open_docs", text="Open Documentation", icon="HELP")
        self.layout.row().operator("ggltf.report_issue", text="Report Issues", icon="ERROR")

classes = [
    DocumentationPanel
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
        

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)