import bpy
from . import PanelGenerator, OperatorGenerator

__layoutTree = {}

def add_button(button):
    if not __button_exists(button):
        op = OperatorGenerator.generate_operator(button)
        if not __tab_exists(button):
            __make_tab(button)

        if not __panel_exists(button):
            __make_panel(button, op)

        bpy.utils.register_class(op)
        __layoutTree[button.tabName][button.panelName].buttons[button.label] = op
    else:
        __layoutTree[button.tabName][button.panelName].buttons[button.label].execute = button.function


@bpy.app.handlers.persistent
def __purge_all(*args):
    from io_ggltf.Core.BlenderUI.FastButtons import Register
    for tab in Register.__layoutTree.values():
        for panel in tab.values():
            for operator in panel.buttons.values():
                bpy.utils.unregister_class(operator)
                del operator
            bpy.utils.unregister_class(panel)
            del panel
        
    Register.__layoutTree = {}
        

def __make_tab(button):
    if not button.tabName in __layoutTree:
        __layoutTree[button.tabName] = {}

def __make_panel(button, operator):
    if not button.panelName in __layoutTree[button.tabName]:
        panel = PanelGenerator.generate_panel(button, buttonOperator=operator)
        bpy.utils.register_class(panel)
        __layoutTree[button.tabName][button.panelName] = panel

def __tab_exists(button):
    return button.tabName in __layoutTree

def __panel_exists(button):
    if __tab_exists(button):
        return button.panelName in __layoutTree[button.tabName]
    
    return False

def __button_exists(button):
    if __tab_exists(button):
        if __panel_exists(button):
            return button.label in __layoutTree[button.tabName][button.panelName].buttons

    return False

def register():
    bpy.app.handlers.load_pre.append(__purge_all)

def unregister():
    bpy.app.handlers.load_pre.remove(__purge_all)