import bpy

class __PasteReferenceOperator(bpy.types.Operator):
    def _get_obj_accessor_str(self, obj) -> str:
        if obj.library != None:
            return f"(\"{obj.name}\", \"{obj.library.filepath}\")"
        else:
            return f"(\"{obj.name}\", None)"


class PasteSingleReferenceOperator(__PasteReferenceOperator):
    """Paste a line of code that creates a reference for currently active object"""
    bl_idname = "ggltf.paste_active_obj_ref"
    bl_label = "Paste Active Object Reference"
    bl_button_label = "Active Only"
    bl_button_icon = "OBJECT_DATA"

    @classmethod
    def poll(cls, context):
        if context.active_object == None:
            return False
        if context.area.spaces.active.type != "TEXT_EDITOR":
            return False
        return context.area.spaces.active.text != None

    def execute(self, context):
        script = context.area.spaces.active.text
        obj = bpy.context.active_object
        script.write(self._get_obj_accessor_str(obj))
        return {"FINISHED"}

class PasteReferenceAsListOperator(__PasteReferenceOperator):
    """Paste a line of code that creates a list of referenced for currently selected objects"""    
    bl_idname = "ggltf.paste_selected_obj_ref_list"
    bl_label = "Paste Selected Object References As List"
    bl_button_label = "Selected As List"
    bl_button_icon = "OBJECT_DATA"

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) == 0:
            return False
        if context.area.spaces.active.type != "TEXT_EDITOR":
            return False
        return context.area.spaces.active.text != None


    def execute(self, context):
        script = context.area.spaces.active.text
        accessors = [self._get_obj_accessor_str(obj) for obj in context.selected_objects]
        script.write(f"[{', '.join(accessors)}]")
        return {"FINISHED"}
    

class PasteReferencesIndividuallyOperator(__PasteReferenceOperator):
    """Paste lines of code that creates a variable and reference for each currently selected object"""
    bl_idname = "ggltf.paste_selected_objs_refs_as_vars"
    bl_label = "Paste Selected Object References"
    bl_button_label = "Selected Individually"
    bl_button_icon = "OBJECT_DATA"

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) == 0:
            return False
        if context.area.spaces.active.type != "TEXT_EDITOR":
            return False
        return context.area.spaces.active.text != None


    def execute(self, context):
        script = context.area.spaces.active.text
        objects = context.selected_objects
        accessors = [self._get_obj_accessor_str(obj) for obj in context.selected_objects]
        for i, a in enumerate(accessors):
            script.write(f"{objects[i].name} = " + a + "\n")
        return {"FINISHED"}

classes = [
    PasteSingleReferenceOperator,
    PasteReferenceAsListOperator,
    PasteReferencesIndividuallyOperator
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
        

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)