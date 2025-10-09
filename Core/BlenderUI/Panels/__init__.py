from . import TextEditorAdvFuncsPanel, TextEditorBoilerPlatePanel, TextEditorDocsPanel, TextEditorButtonsPanel, TextEditorReferencesPanel

def register():
    TextEditorDocsPanel.register()
    TextEditorBoilerPlatePanel.register()
    TextEditorButtonsPanel.register()
    TextEditorReferencesPanel.register()
    TextEditorAdvFuncsPanel.register()

def unregister():
    TextEditorDocsPanel.unregister()
    TextEditorBoilerPlatePanel.unregister()
    TextEditorButtonsPanel.unregister()
    TextEditorReferencesPanel.unregister()
    TextEditorAdvFuncsPanel.unregister()