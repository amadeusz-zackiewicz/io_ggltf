import bpy
import uuid

@classmethod
def __poll(cls, context):
    return True

def generate_operator(button):
    op = type(f"{button.tabName.replace(' ', '_')}_{button.panelName.replace(' ', '_')}_{button.label.replace(' ', '_')}", (bpy.types.Operator, ),{
        "bl_idname": f"ggltf.ug_{str(uuid.uuid4()).replace('-', '').lower()}",
        "bl_label": button.label,
        "poll": __poll,
        "execute": button.function
    })
    return op