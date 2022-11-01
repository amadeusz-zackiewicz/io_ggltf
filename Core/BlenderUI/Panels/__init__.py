from . import TextEditorAccessorsPanel, TextEditorMethodsPanel, TextEditorBoilerPlatePanel, TextEditorDocsPanel

def register():
    TextEditorDocsPanel.register()
    TextEditorBoilerPlatePanel.register()
    TextEditorAccessorsPanel.register()
    TextEditorMethodsPanel.register()

def unregister():
    TextEditorDocsPanel.unregister()
    TextEditorBoilerPlatePanel.unregister()
    TextEditorAccessorsPanel.unregister()
    TextEditorMethodsPanel.unregister()