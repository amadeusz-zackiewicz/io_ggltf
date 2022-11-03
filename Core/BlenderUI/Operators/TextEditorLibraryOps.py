import bpy
import uuid
import webbrowser
from io_ggltf.Core.Decorators import _DocsUI

@classmethod
def __paste_poll(cls, context):
    if context.area.spaces.active.type != "TEXT_EDITOR":
        return False
    if context.area.spaces.active.text == None:
        return False
    return True

def __paste_execute(self, context):
    script = context.area.spaces.active.text
    script.write(f"{self.moduleName}.{self.methodName}(")
    return {"FINISHED"}

@classmethod
def __docs_poll(cls, context):
    return True

def __docs_execute(self, context):
    webbrowser.open_new_tab(self.url)
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
    for module in modules:
        methods = _DocsUI.scan_module(module)
        splitName = module.__name__.split('.')
        moduleName = splitName[-1]
        classes[moduleName] = []

        for methodName, (classDocs, classURL) in methods.items():
            cleanName = f"{splitName[-2]}_{splitName[-1]}_{methodName}".replace(".", "_")
            pasteClass = type(f"PASTE_GEN_{cleanName}", (bpy.types.Operator, ), {
                "bl_idname": f"ggltf.p_{str(uuid.uuid4()).replace('-', '').lower()}",
                "bl_label": f"Paste method: {moduleName}.{methodName}." if classDocs == None or classDocs == "" else classDocs,
                "bl_button_label": methodName,
                "moduleName": moduleName,
                "methodName": methodName,
                "poll": __paste_poll,
                "execute": __paste_execute,
                "__doc__": f"Paste method: {methodName}" if classDocs == None or classDocs == "" else classDocs
            })
            if classURL == None or classURL == "":
                classes[moduleName].append((pasteClass, None))
            else:
                docsClass = type(f"DOCS_GEN_{cleanName}", (bpy.types.Operator, ), {
                    "bl_idname": f"ggltf.d_{str(uuid.uuid4()).replace('-', '').lower()}",
                    "bl_label": f"Open docs: {moduleName}.{methodName}",
                    "bl_button_icon": "HELP",
                    "poll": __docs_poll,
                    "execute": __docs_execute,
                    "url": classURL,
                    "__doc__": f"Open URL:\n{classURL}"
                })
                classes[moduleName].append((pasteClass, docsClass))
                


    return classes

def register():
    classes = __generate_classes()
    for moduleName, classPair in classes.items():
        for c in classPair:
            bpy.utils.register_class(c[0])
            if c[1] != None:
                bpy.utils.register_class(c[1])


def unregister():
    from io_ggltf.Core.BlenderUI.Operators.TextEditorLibraryOps import classes
    for moduleName, classPair in classes.items():
        for c in classPair:
            bpy.utils.unregister_class(c[0])
            if c[1] != None:
                bpy.utils.unregister_class(c[1])
            del c

    classes = {}