# Work in progress
Currently working on 0.1.0 release, there are still some bugs and usability issues. 

The documentation and wiki pages are not yet complete but the addon is mostly functional.

Current data types supported:
Type | Support
:---: | :---:
Animation | <t style="color:red">0.2.0</t>
Scene | <t style="color:green">Yes</t>
Node (Object) | <t style="color:green">Yes</t>
Mesh | <t style="color:green">Yes</t>
Skin (Armature) | <t style="color:green">Yes</t>
Material | <t style="color:orange">No (mesh materials slots still work)</t>
Texture | <t style="color:red">No</t>
Image | <t style="color:red">No</t>
Camera | <t style="color:red">No</t>
Light |  <t style="color:red">No</t>

# What does this addon do?
gglTF or game glTF is an addon that provides the user with a library that can export glTF files via python scripts, giving far more flexibility then the default exporter and allowing users to export exactly what they need and how they need it. The main area where this is useful is game development, where certain assets need to be optimised before being imported to the game engine and might need to be exported in many iterations.

If you do not need any of this functionality I highly advise you to stick to the default glTF exporter.

# Requirements
1. Blender 3.0 or higher
2. Basic python / programming knowledge

# Features
* Additive workflow, start with nothing and add what you need.

* No scenes required, making it possible to create asset libraries.

* Easily add hierarchies, collections or singular objects.

* Exclude objects with regular expressions, without being forced to delete them before exporting.

* Non-destructively merge multiple meshes into one without having to apply modifiers.

* Add as many UV maps, vertex colors or shape keys to your meshes as you need.

* Strip bones based on blacklists or filters.
  
* Automate excluding useless control bones and trimming bone prefixes when using rigify armatures.

* Easily make your scripts into buttons.

# Limitations
* Cannot export base meshes, each mesh has to be assigned to an object in scene in order to be exported.

* Requires file reload to clear buttons that were removed.