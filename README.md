# Work in progress
Currently working on 0.1.0 release, there are still some bugs and usability issues. 

The documentation and how to pages are not yet complete but the addon is mostly functional.

Current data types supported:
Type | Support
:---: | :---:
Animation | <t style="color:red">0.2.0</t>
Scene | <t style="color:green">Yes</t>
Node (Object) | <t style="color:green">Yes</t>
Mesh | <t style="color:green">Yes</t>
Skin (Armature) | <t style="color:green">Yes</t>
Material | <t style="color:orange">No (meshes are still divided by materials)</t>
Texture | <t style="color:red">No</t>
Image | <t style="color:red">No</t>
Camera | <t style="color:red">No</t>
Light |  <t style="color:red">No</t>

# What does this addon do?
gglTF or game glTF is an addon that provides the user with a library that can export glTF files via python scripts, giving far more flexibility and allowing users to export exactly what they need and how they need it. The main area where this is useful is game development, where certain assets need to be optimised before being imported to the game engine and might need to be exported in many iterations.

If you do not need any of this functionality I highly advise you to stick to the default glTF exporter.

# Requirements
1. Blender 3.3 or higher
2. Basic python knowledge

# Features

## Regular expression filtering
Exclude objects with regular expressions, allowing you to exclude objects without having to delete them before exporting.

## Mesh merging
Merge all meshes in a hierarchy into one, with custom origin point of required, specify meshes you do not want included with blacklist or regular expression filter. 

## Rigify bone filtering and name stripping
Strip bones based on blacklist or filters, or use automated riify flags to exclude useless bones and automatically strip `DEF-` or `ORG-` prefix from the bones.