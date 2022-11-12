from . import TextEditorAccessorsOps, TextEditorLibraryOps, TextEditorBoilerPlateOps, TextEditorDocsOps, TextEditorButtonsOps

def register():
    TextEditorDocsOps.register()
    TextEditorBoilerPlateOps.register()
    TextEditorButtonsOps.register()
    TextEditorAccessorsOps.register()
    TextEditorLibraryOps.register()
        
def unregister():
    TextEditorDocsOps.unregister()
    TextEditorBoilerPlateOps.unregister()
    TextEditorButtonsOps.unregister()
    TextEditorAccessorsOps.unregister()
    TextEditorLibraryOps.unregister()