import bpy

class __PasteAccessorOperator(bpy.types.Operator):
    def _get_obj_accessor_str(self, obj) -> str:
        if obj.library != None:
            return f"(\"{obj.name}\", \"{obj.library.filepath}\")"
        else:
            return f"(\"{obj.name}\", None)"


class PasteSingleAccessorOperator(__PasteAccessorOperator):
    """Paste a line of code that creates an accessor for currently active object"""
    bl_idname = "ggltf.paste_active_obj_accessor"
    bl_label = "Paste Active Object Accessor"
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
        script.write(f"{obj.name}Acc = " + self._get_obj_accessor_str(obj))
        return {"FINISHED"}

class PasteAccessorsAsListOperator(__PasteAccessorOperator):
    """Paste a line of code that creates a list of accessors for currently selected objects"""    
    bl_idname = "ggltf.paste_selected_obj_accessors_list"
    bl_label = "Paste Selected Object Accessors As List"
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
        script.write(f"accessors = [{', '.join(accessors)}]")
        return {"FINISHED"}
    

class PasteAccessorsIndividuallyOperator(__PasteAccessorOperator):
    """Paste lines of code that creates an accessor for each currently selected object"""
    bl_idname = "ggltf.paste_selected_objs_accessors"
    bl_label = "Paste Selected Object Accessors"
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
            script.write(f"{objects[i].name}Acc = " + a + "\n")
        return {"FINISHED"}

classes = [
    PasteSingleAccessorOperator,
    PasteAccessorsAsListOperator,
    PasteAccessorsIndividuallyOperator
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
        

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)