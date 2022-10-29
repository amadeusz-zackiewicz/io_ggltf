import bpy
import uuid
from io_ggltf.Core.Decorators import ShowInUI

@classmethod
def __poll(cls, context):
    if context.area.spaces.active.type != "TEXT_EDITOR":
        return False
    if context.area.spaces.active.text == None:
        return False
    return True

def __execute(self, context):
    script = context.area.spaces.active.text
    script.write(f"{self.moduleName}.{self.methodName}(")
    return {"FINISHED"}

classes = {}

def __generate_classes():
    from io_ggltf import Advanced
    modules = [
        Advanced.Attach, 
        Advanced.File, 
        Advanced.Mesh,
        Advanced.Node,
        Advanced.Scene,
        Advanced.Settings,
        Advanced.Skin,
        Advanced.Util
        ]
    generated = []
    for module in modules:
        methods = ShowInUI.scan_module(module)
        splitName = module.__name__.split('.')
        moduleName = splitName[-1]
        classes[moduleName] = []
        for k, v in methods.items():
            cleanName = f"{splitName[-2]}_{splitName[-1]}_{k}".replace(".", "_")
            newClass = type(f"DOCS_GENERATED_{cleanName}", (bpy.types.Operator, ), {
                "bl_idname": f"ggltf.{str(uuid.uuid4()).replace('-', '').lower()}",
                "bl_label": f"Paste method: {moduleName}.{k}." if v == None or v == "" else v,
                "bl_button_label": k,
                "moduleName": moduleName,
                "methodName": k,
                "poll": __poll,
                "execute": __execute,
                "__doc__": f"Paste method: {k}" if v == None or v == "" else v
            })
            classes[moduleName].append(newClass)


    return classes

def register():
    classes = __generate_classes()
    for k, v in classes.items():
        for c in v:
            bpy.utils.register_class(c)


def unregister():
    for k, v in classes.items():
        for c in v:
            bpy.utils.unregister_class(c)
            del c

    classes = {}