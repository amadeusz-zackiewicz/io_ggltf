from . import TextEditorAccessorsPanel, TextEditorMethodsPanel, TextEditorBoilerPlatePanel

def register():
    TextEditorBoilerPlatePanel.register()
    TextEditorAccessorsPanel.register()
    TextEditorMethodsPanel.register()

def unregister():
    TextEditorBoilerPlatePanel.unregister()
    TextEditorAccessorsPanel.unregister()
    TextEditorMethodsPanel.unregister()