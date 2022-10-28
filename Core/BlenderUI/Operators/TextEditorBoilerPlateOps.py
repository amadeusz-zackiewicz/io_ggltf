import bpy

class PasteBoilerPlateOperator(bpy.types.Operator):
    """Paste quick start code"""
    bl_idname = "ggltf.paste_adv_boiler_plate"
    bl_label = "Paste quick start code"

    @classmethod
    def poll(cls, context):
        if context.area.spaces.active.type != "TEXT_EDITOR":
            return False
        return context.area.spaces.active.text != None

    def execute(self, context):
        script = context.area.spaces.active.text
        script.write(f'from io_ggltf.Advanced import *\nfrom io_ggltf.Constants import *\n\nbucket = File.create_bucket(filePath="//", fileName="{script.name.replace(".py", "")}", binPath="bin/", fileType=FILE_TYPE_GLB)\nFile.dump_bucket(bucket)\n')
        return {"FINISHED"}

classes = [
    PasteBoilerPlateOperator
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
        

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)