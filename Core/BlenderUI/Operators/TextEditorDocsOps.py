import bpy
import webbrowser

class OpenDocumentationOperator(bpy.types.Operator):
    """Open Documentation"""
    bl_idname = "ggltf.open_docs"
    bl_label = "Open Documentation"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        webbrowser.open_new_tab("https://github.com/amadeusz-zackiewicz/io_ggltf/wiki")
        return {"FINISHED"}

class OpenIssuesOperator(bpy.types.Operator):
    """Report issues"""
    bl_idname = "ggltf.report_issue"
    bl_label = "Report issues"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        webbrowser.open_new_tab("https://github.com/amadeusz-zackiewicz/io_ggltf/issues")
        return {"FINISHED"}

classes = [
    OpenDocumentationOperator,
    OpenIssuesOperator
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
        

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)