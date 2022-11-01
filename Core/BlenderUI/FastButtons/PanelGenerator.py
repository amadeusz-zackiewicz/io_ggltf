import bpy
import uuid

def __draw(self, context):
    for label, operator in self.buttons.items():
        self.layout.row().operator(operator.bl_idname, text=label)

def generate_panel(button, buttonOperator: str):
    panel = type(
        f"{button.tabName.replace(' ', '_')}.{button.panelName.replace(' ', '_')}",
        (bpy.types.Panel, ),{
            "bl_label": button.panelName,
            "bl_idname": f"GGLTF_PT_ugen_{str(uuid.uuid4()).replace('-', '').lower()}",
            "bl_space_type": button.area,
            "bl_region_type": "UI",
            "bl_category": button.tabName,
            "buttons": {button.label: buttonOperator},
            "draw": __draw
        })

    return panel