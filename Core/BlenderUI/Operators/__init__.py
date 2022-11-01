from . import TextEditorAccessorsOps, TextEditorLibraryOps, TextEditorBoilerPlateOps, TextEditorDocsOps

def register():
    TextEditorDocsOps.register()
    TextEditorBoilerPlateOps.register()
    TextEditorAccessorsOps.register()
    TextEditorLibraryOps.register()
        
def unregister():
    TextEditorDocsOps.unregister()
    TextEditorBoilerPlateOps.unregister()
    TextEditorAccessorsOps.unregister()
    TextEditorLibraryOps.unregister()