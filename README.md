![img](readme_resources/blender_market_cover.png)

# Requirements
1. Blender 3.0 or higher
2. Basic python / programming knowledge

# Data supported
This addon is still a work in progress, and does not support all data types:
Type | Support | Note
:---: | :---: | :---
Animation | <t style="color:red">0.2.0</t> | Animations are coming in the next release, they require a lot of features which are currently not implemented
Scene | <t style="color:green">Yes</t> | 
Node | <t style="color:green">Yes</t> |
Mesh | <t style="color:green">Yes</t> |
Skin | <t style="color:green">Yes</t> |
Material | <t style="color:orange">No</t> | Mesh material slots are retained
Texture | <t style="color:red">No</t> |
Image | <t style="color:red">No</t> |
Camera | <t style="color:red">No</t> |
Light |  <t style="color:red">No</t> |

# What is the purpose of this addon?
This addon is highly specialised in exporting assets into game engines using glTF file format. It achieves that by giving the user access to a library that does most of the heavy lifting and a very fast way to run your code via buttons minimising time between exporting and seeing new changes within the game engine.

Have a look at the features section below to see if it fits your purpose, if you do not need any of this functionality I highly advise you to stick to the default glTF exporter.

Otherwise get started [here](https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/GetStartedAdvP0)

# Features
* Additive workflow, start with nothing and add only what you need.

* Non-destructively merge multiple meshes into one.
  
* Add as many UV maps, vertex colors or shape keys to your meshes as you need.
  
* Break down your complex scene into smaller files.

* Easily add hierarchies, collections or singular objects.

* Non-destructively remove objects with with filters and blacklists.

* No glTF scenes required, making it possible to create asset libraries (for example file containing only meshes).

* Non-destructively strip bones from armatures with filters and blacklists.
  
* Automate excluding useless control bones and trimming bone prefixes when using rigify armatures.

* Easily create buttons to run your code from outside of the text editor.

# Limitations
* Cannot export base meshes, each mesh has to be assigned to an object in scene in order to be exported.
* Meshes can only be based on blender meshes, no curves, NURBS, etc.
