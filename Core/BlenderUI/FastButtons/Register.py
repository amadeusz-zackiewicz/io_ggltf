import bpy
from . import PanelGenerator, OperatorGenerator

__layoutTree = {}

def add_button(button):
    if not __button_exists(button):
        op = OperatorGenerator.generate_operator(button)
        __make_area(button)
        __make_tab(button)
        __make_panel(button, op)

        bpy.utils.register_class(op)
        __layoutTree[button.area][button.tabName][button.panelName].buttons[button.label] = op
    else:
        __layoutTree[button.area][button.tabName][button.panelName].buttons[button.label].execute = button.function


@bpy.app.handlers.persistent
def __purge_all(*args, **kwargs):
    from io_ggltf.Core.BlenderUI.FastButtons import Register
    for area in Register.__layoutTree.values():
        for tab in area.values():
            for panel in tab.values():
                for operator in panel.buttons.values():
                    bpy.utils.unregister_class(operator)
                    del operator
                bpy.utils.unregister_class(panel)
                del panel
        
    Register.__layoutTree = {}
        

def __make_area(button):
    if not __area_exists(button):
        __layoutTree[button.area] = {}

def __make_tab(button):
    if not __tab_exists(button):
        __layoutTree[button.area][button.tabName] = {}

def __make_panel(button, operator):
    if not __panel_exists(button):
        panel = PanelGenerator.generate_panel(button, buttonOperator=operator)
        bpy.utils.register_class(panel)
        __layoutTree[button.area][button.tabName][button.panelName] = panel

def __area_exists(button):
    return button.area in __layoutTree

def __tab_exists(button):
    return button.tabName in __layoutTree[button.area]

def __panel_exists(button):
    if __area_exists(button):
        if __tab_exists(button):
            return button.panelName in __layoutTree[button.area][button.tabName]
    
    return False

def __button_exists(button):
    if __area_exists(button):
        if __tab_exists(button):
            if __panel_exists(button):
                return button.label in __layoutTree[button.area][button.tabName][button.panelName].buttons

    return False

def register():
    bpy.app.handlers.load_pre.append(__purge_all)

def unregister():
    bpy.app.handlers.load_pre.remove(__purge_all)