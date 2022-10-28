bl_info = {
    'name': 'gglTF (Game glTF) Exporter',
    'author': 'Amadeusz Zackiewicz',
    "version": (0, 1, 0),
    'blender': (3, 3, 0),
    'location': 'Text Editor',
    'description': 'Export glTF 2.0 files and enjoy time saving functionality via python scripts',
    'warning': '',
    'doc_url': "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki",
    'tracker_url': "https://github.com/amadeusz-zackiewicz/io_ggltf/issues",
    'support': 'COMMUNITY',
    'category': 'Import-Export',
}

from io_ggltf.Core.BlenderUI import Operators, Panels

def register():
    Operators.register()
    Panels.register()

def unregister():
    Operators.unregister()
    Panels.unregister()