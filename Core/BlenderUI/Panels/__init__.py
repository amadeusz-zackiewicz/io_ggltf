from . import TextEditorAccessorsPanel, TextEditorAdvFuncsPanel, TextEditorBoilerPlatePanel, TextEditorDocsPanel, TextEditorButtonsPanel

def register():
    TextEditorDocsPanel.register()
    TextEditorBoilerPlatePanel.register()
    TextEditorButtonsPanel.register()
    TextEditorAccessorsPanel.register()
    TextEditorAdvFuncsPanel.register()

def unregister():
    TextEditorDocsPanel.unregister()
    TextEditorBoilerPlatePanel.unregister()
    TextEditorButtonsPanel.unregister()
    TextEditorAccessorsPanel.unregister()
    TextEditorAdvFuncsPanel.unregister()