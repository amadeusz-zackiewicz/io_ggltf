import bpy

class PasteQuickStartOperator(bpy.types.Operator):
    """Paste quick start code"""
    bl_idname = "ggltf.paste_adv_quick_start"
    bl_label = "Paste quick start code"
    bl_button_label = "Quick start"
    bl_button_icon = "FILE_TEXT"

    @classmethod
    def __poll(cls, context):
        if context.area.spaces.active.type != "TEXT_EDITOR":
                return False
        return context.area.spaces.active.text != None       

    def execute(self, context):
        script = context.area.spaces.active.text
        script.write(f'from io_ggltf.Advanced import *\nfrom io_ggltf.Constants import *\n\nbucket = File.create_bucket(filePath="//", fileName="{script.name.replace(".py", "")}", binPath="bin/", fileType=FILE_TYPE_GLB)\nFile.dump_bucket(bucket)\n')
        return {"FINISHED"}

class PasteImportsOnlyOperator(bpy.types.Operator):
    """Paste required imports"""
    bl_idname = "ggltf.paste_imports"
    bl_label = "Paste required imports"
    bl_button_label = "Imports"
    bl_button_icon = "FILE_TEXT"

    @classmethod
    def __poll(cls, context):
        if context.area.spaces.active.type != "TEXT_EDITOR":
                return False
        return context.area.spaces.active.text != None  

    def execute(self, context):
        script = context.area.spaces.active.text
        script.write(f'from io_ggltf.Advanced import *\nfrom io_ggltf.Constants import\n')
        return {"FINISHED"}

class PasteMakeButtonOperator(bpy.types.Operator):
    """Paste an example button"""
    bl_idname = "ggltf.paste_make_button"
    bl_label = "Paste an example button"
    bl_button_label = "Button"
    bl_button_icon = "MOUSE_LMB"

    @classmethod
    def __poll(cls, context):
        if context.area.spaces.active.type != "TEXT_EDITOR":
                return False
        return context.area.spaces.active.text != None   

    def execute(self, context):
        script = context.area.spaces.active.text
        script.write('@MakeButton("My Tab/My Panel/My Button")\ndef example_func(self, context):\n\t#Do stuff here\n\treturn {"FINISHED"}')
        return {"FINISHED"}

classes = [
    PasteQuickStartOperator,
    PasteImportsOnlyOperator,
    PasteMakeButtonOperator
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
        

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)