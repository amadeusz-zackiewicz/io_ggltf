import bpy

@classmethod
def poll(cls, context):
    return True

def execute(self, context):
    from io_ggltf.Core.BlenderUI.FastButtons.Register import __purge_all
    __purge_all()
    return {"FINISHED"}

classes = [type("PurgeButtonsOperator", (bpy.types.Operator, ), {
    "__doc__": """Purge all buttons""",
    "bl_idname": "ggltf.purge_all_buttons",
    "bl_label": "Purge all buttons",
    "bl_button_label": "Purge buttons",
    "bl_button_icon": "CANCEL",
    "poll": poll,
    "execute": execute
})]

def register():
    for c in classes:
        bpy.utils.register_class(c)
        

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)