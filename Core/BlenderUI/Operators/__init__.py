from . import TextEditorLibraryOps, TextEditorBoilerPlateOps, TextEditorDocsOps, TextEditorButtonsOps, TextEditorReferenceOps

def register():
    TextEditorDocsOps.register()
    TextEditorBoilerPlateOps.register()
    TextEditorButtonsOps.register()
    TextEditorReferenceOps.register()
    TextEditorLibraryOps.register()
        
def unregister():
    TextEditorDocsOps.unregister()
    TextEditorBoilerPlateOps.unregister()
    TextEditorButtonsOps.unregister()
    TextEditorReferenceOps.unregister()
    TextEditorLibraryOps.unregister()