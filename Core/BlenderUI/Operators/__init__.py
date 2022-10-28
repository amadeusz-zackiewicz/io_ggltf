from . import TextEditorAccessorsOps, TextEditorLibraryOps, TextEditorBoilerPlateOps

def register():
    TextEditorBoilerPlateOps.register()
    TextEditorAccessorsOps.register()
    TextEditorLibraryOps.register()
        
def unregister():
    TextEditorBoilerPlateOps.unregister()
    TextEditorAccessorsOps.unregister()
    TextEditorLibraryOps.unregister()