FILE_EXT_GLTF   = ".gltf"
FILE_EXT_GLB    = ".glb"
FILE_EXT_BIN    = ".bin"

FILE_TYPE_GLTF          = "GLTF"
FILE_TYPE_GLB           = "GLB"
FILE_TYPE_GLTF_EMBEDDED = "GLTF_E"

COLLECT_MODE_SIMPLE   = 0
COLLECT_MODE_ADVANCED = 1

LIST_FILTER_WHITELIST = 0
LIST_FILTER_BLACKLIST = 1

MESH_TYPE_POINTS              = 0
MESH_TYPE_LINES               = 1
MESH_TYPE_LINE_LOOP           = 2
MESH_TYPE_LINE_STRIP          = 3
MESH_TYPE_TRIANGLES           = 4
MESH_TYPE_TRIANGLE_STRIP      = 5
MESH_TYPE_TRIANGLE_FAN        = 6

MESH_ATTRIBUTE_STR_POSITION       = "POSITION"
MESH_ATTRIBUTE_STR_NORMAL         = "NORMAL"
MESH_ATTRIBUTE_STR_TANGENT        = "TANGENT"
MESH_ATTRIBUTE_STR_TEXCOORD       = "TEXCOORD_"
MESH_ATTRIBUTE_STR_TEXCOORD_0     = MESH_ATTRIBUTE_STR_TEXCOORD + "0"
MESH_ATTRIBUTE_STR_TEXCOORD_1     = MESH_ATTRIBUTE_STR_TEXCOORD + "1"
MESH_ATTRIBUTE_STR_TEXCOORD_2     = MESH_ATTRIBUTE_STR_TEXCOORD + "2"
MESH_ATTRIBUTE_STR_TEXCOORD_3     = MESH_ATTRIBUTE_STR_TEXCOORD + "3"
MESH_ATTRIBUTE_STR_TEXCOORD_4     = MESH_ATTRIBUTE_STR_TEXCOORD + "4"
MESH_ATTRIBUTE_STR_TEXCOORD_5     = MESH_ATTRIBUTE_STR_TEXCOORD + "5"
MESH_ATTRIBUTE_STR_TEXCOORD_6     = MESH_ATTRIBUTE_STR_TEXCOORD + "6"
MESH_ATTRIBUTE_STR_TEXCOORD_7     = MESH_ATTRIBUTE_STR_TEXCOORD + "7"
MESH_ATTRIBUTE_STR_COLOR          = "COLOR_"
MESH_ATTRIBUTE_STR_COLOR_0        = MESH_ATTRIBUTE_STR_COLOR + "0"
MESH_ATTRIBUTE_STR_COLOR_1        = MESH_ATTRIBUTE_STR_COLOR + "1"
MESH_ATTRIBUTE_STR_COLOR_2        = MESH_ATTRIBUTE_STR_COLOR + "2"
MESH_ATTRIBUTE_STR_COLOR_3        = MESH_ATTRIBUTE_STR_COLOR + "3"
MESH_ATTRIBUTE_STR_COLOR_4        = MESH_ATTRIBUTE_STR_COLOR + "4"
MESH_ATTRIBUTE_STR_COLOR_5        = MESH_ATTRIBUTE_STR_COLOR + "5"
MESH_ATTRIBUTE_STR_COLOR_6        = MESH_ATTRIBUTE_STR_COLOR + "6"
MESH_ATTRIBUTE_STR_COLOR_7        = MESH_ATTRIBUTE_STR_COLOR + "7"
MESH_ATTRIBUTE_STR_JOINT          = "JOINTS_"
MESH_ATTRIBUTE_STR_JOINT_0        = MESH_ATTRIBUTE_STR_JOINT + "0"
MESH_ATTRIBUTE_STR_JOINT_1        = MESH_ATTRIBUTE_STR_JOINT + "1"
MESH_ATTRIBUTE_STR_JOINT_2        = MESH_ATTRIBUTE_STR_JOINT + "2"
MESH_ATTRIBUTE_STR_JOINT_3        = MESH_ATTRIBUTE_STR_JOINT + "3"
MESH_ATTRIBUTE_STR_JOINT_4        = MESH_ATTRIBUTE_STR_JOINT + "4"
MESH_ATTRIBUTE_STR_JOINT_5        = MESH_ATTRIBUTE_STR_JOINT + "5"
MESH_ATTRIBUTE_STR_JOINT_6        = MESH_ATTRIBUTE_STR_JOINT + "6"
MESH_ATTRIBUTE_STR_JOINT_7        = MESH_ATTRIBUTE_STR_JOINT + "7"
MESH_ATTRIBUTE_STR_WEIGHT         = "WEIGHTS_"
MESH_ATTRIBUTE_STR_WEIGHT_0       = MESH_ATTRIBUTE_STR_WEIGHT + "0"
MESH_ATTRIBUTE_STR_WEIGHT_1       = MESH_ATTRIBUTE_STR_WEIGHT + "1"
MESH_ATTRIBUTE_STR_WEIGHT_2       = MESH_ATTRIBUTE_STR_WEIGHT + "2"
MESH_ATTRIBUTE_STR_WEIGHT_3       = MESH_ATTRIBUTE_STR_WEIGHT + "3"
MESH_ATTRIBUTE_STR_WEIGHT_4       = MESH_ATTRIBUTE_STR_WEIGHT + "4"
MESH_ATTRIBUTE_STR_WEIGHT_5       = MESH_ATTRIBUTE_STR_WEIGHT + "5"
MESH_ATTRIBUTE_STR_WEIGHT_6       = MESH_ATTRIBUTE_STR_WEIGHT + "6"
MESH_ATTRIBUTE_STR_WEIGHT_7       = MESH_ATTRIBUTE_STR_WEIGHT + "7"



######### for repeating values

__VAR_BUFFER_VIEW           = "bufferView"
__VAR_BYTE_OFFSET           = "byteOffset"
__VAR_COMPONENT_TYPE        = "componentType"
__VAR_EXTENSION             = "extensions"
__VAR_EXTRA                 = "extras"
__VAR_NAME                  = "name"
__VAR_COUNT                 = "count"
__VAR_URI                   = "uri"
__VAR_ROTATION              = "rotation"
__VAR_TRANSLATION           = "translation"
__VAR_SCALE                 = "scale"
__VAR_MATRIX                = "matrix"

__TYPE_ID_BYTE                  = 5120
__TYPE_ID_UNSIGNED_BYTE         = 5121
__TYPE_ID_SHORT                 = 5122
__TYPE_ID_UNSIGNED_SHORT        = 5123
__TYPE_ID_INT                   = 5124
__TYPE_ID_UNSIGNED_INT          = 5125
__TYPE_ID_FLOAT                 = 5126
__TYPE_ID_ARRAY_BUFFER          = 34962
__TYPE_ID_ELEMENT_ARRAY_BUFFER  = 34963

__TYPE_STR_SCALAR                   = "SCALAR"
__TYPE_STR_VECTOR_2                 = "VEC2"
__TYPE_STR_VECTOR_3                 = "VEC3"
__TYPE_STR_VECTOR_4                 = "VEC4"
__TYPE_STR_MATRIX_2                 = "MAT2"
__TYPE_STR_MATRIX_3                 = "MAT3"
__TYPE_STR_MATRIX_4                 = "MAT4"

PACKING_FORMAT_PAD_BYTE     = "<x"
PACKING_FORMAT_CHAR         = "<c"
PACKING_FORMAT_SIGNED_CHAR  = "<b"
PACKING_FORMAT_U_CHAR       = "<B"
PACKING_FORMAT_BOOL         = "<?"
PACKING_FORMAT_SHORT        = "<h"
PACKING_FORMAT_U_SHORT      = "<H"
PACKING_FORMAT_INT          = "<i"
PACKING_FORMAT_U_INT        = "<I"
PACKING_FORMAT_LONG         = "<l"
PACKING_FORMAT_U_LONG       = "<L"
PACKING_FORMAT_LONG_LONG    = "<q"
PACKING_FORMAT_U_LONG_LONG  = "<Q"
PACKING_FORMAT_SIZE_T       = "<n"
PACKING_FORMAT_U_SIZE_T     = "<N"
PACKING_FORMAT_FLOAT        = "<f"
PACKING_FORMAT_DOUBLE       = "<d"
PACKING_FORMAT_CHAR_VOID    = "<P"

BLENDER_TYPE_ARMATURE       = "ARMATURE"
BLENDER_TYPE_BONE           = "BONE"
BLENDER_TYPE_CAMERA         = "CAMERA"
BLENDER_TYPE_CURVE          = "CURVE"
BLENDER_TYPE_EMPTY          = "EMPTY"
BLENDER_TYPE_SURFACE        = "SURFACE"
BLENDER_TYPE_MESH           = "MESH"

BLENDER_INSTANCE_TYPE_NONE          = "NONE"
BLENDER_INSTANCE_TYPE_VERTS         = "VERTS"
BLENDER_INSTANCE_TYPE_FACES         = "FACES"
BLENDER_INSTANCE_TYPE_COLLECTION    = "COLLECTION"

BLENDER_ARMATURE_POSE_MODE  = "POSE"
BLENDER_ARMATURE_REST_MODE  = "REST"

BLENDER_MODIFIER_ARMATURE   = "ARMATURE"

BLENDER_DEPSGRAPH_MODE_VIEWPORT     = "VIEWPORT"
BLENDER_DEPSGRAPH_MODE_RENDER       = "RENDER"

BLENDER_MESH_CONVERTIBLE    = [BLENDER_TYPE_MESH, BLENDER_TYPE_CURVE, BLENDER_TYPE_SURFACE]

RIGIFY_INCLUDE_CONTROLS     = 0b00000001
RIGIFY_INCLUDE_ORIGINAL     = 0b00000010
RIGIFY_INCLUDE_DEFORMS      = 0b00000100
RIGIFY_INCLUDE_ROOT         = 0b00001000
RIGIFY_TRIM_NAMES           = 0b00010000
RIGIFY_ONLY_ORIGINAL        = RIGIFY_INCLUDE_ORIGINAL | RIGIFY_INCLUDE_ROOT | RIGIFY_TRIM_NAMES
RIGIFY_ONLY_DEFORMS         = RIGIFY_INCLUDE_DEFORMS | RIGIFY_INCLUDE_ROOT | RIGIFY_TRIM_NAMES
RIGIFY_ONLY_CONTROLS        = RIGIFY_INCLUDE_CONTROLS | RIGIFY_INCLUDE_ROOT

BUCKET_SETTING_FILEPATH             = "filepath"
BUCKET_SETTING_BINPATH              = "binpath"
BUCKET_SETTING_FILENAME             = "filename"
BUCKET_SETTING_FILE_TYPE            = "file_type"
############## Node specific settings
BUCKET_SETTING_REDUNDANCY_CHECK_NODE        = "redundancy_check_node"
BUCKET_SETTING_NODE_DEFAULT_WORLD_SPACE     = "top_node_world_space"
############## Mesh specific settings
BUCKET_SETTING_INCLUDE_MESH                 = "get_mesh"
BUCKET_SETTING_REDUNDANCY_CHECK_MESH        = "redundancy_check_mesh"
BUCKET_SETTING_MESH_GET_NORMALS             = "get_normals"
BUCKET_SETTING_MESH_GET_TANGENTS            = "get_tangents"
BUCKET_SETTING_MESH_GET_UVS                 = "get_uvs"
BUCKET_SETTING_MESH_GET_VERTEX_COLORS       = "get_vcolors"
BUCKET_SETTING_MESH_GET_BONE_INFLUENCE      = "get_bone_influences"
BUCKET_SETTING_MESH_GET_SHAPE_KEYS          = "get_skeys"
BUCKET_SETTING_MESH_GET_SHAPE_KEYS_NORMALS  = "get_skeys_normals"
BUCKET_SETTING_MESH_GET_SHAPE_KEYS_TANGENTS = "get_skeys_tangents"
BUCKET_SETTING_MESH_GET_SHAPE_KEYS_UV       = "get_skeys_uv"
BUCKET_SETTING_MESH_MAX_BONES               = "mesh_maximum_bones"
############## Skin specific settings
BUCKET_SETTING_REDUNDANCY_CHECK_SKIN        = "redundancy_check_skin"
BUCKET_SETTING_INCLUDE_SKIN                 = "get_skin"
BUCKET_SETTING_SKIN_GET_INVERSED_BINDS      = "get_inversed_binds"
BUCKET_SETTING_SKIN_FORCE_REST_POSE         = "force_armature_rest"

COMMAND_QUEUE_SETUP             = 0
COMMAND_QUEUE_SKIN              = 1
COMMAND_QUEUE_MESH              = 2
COMMAND_QUEUE_NODE              = 3
COMMAND_QUEUE_NAMING            = 4
COMMAND_QUEUE_LINKER            = 5
COMMAND_QUEUE_ANIM_SETUP        = 6
COMMAND_QUEUE_CLEAN_UP          = 7

BUCKET_COMMAND_QUEUE_TYPES      = 8

#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.17 glTF
BUCKET_DATA_EXTENSIONS_USED          = "extensionsUsed"
BUCKET_DATA_EXTENSIONS_REQUIRED      = "extensionsRequired"
BUCKET_DATA_ACCESSORS                = "accessors"
BUCKET_DATA_ANIMATIONS               = "animations"
BUCKET_DATA_ASSET                    = "asset"
BUCKET_DATA_BUFFERS                  = "buffers"
BUCKET_DATA_BUFFER_VIEWS             = "bufferViews"
BUCKET_DATA_CAMERAS                  = "cameras"
BUCKET_DATA_IMAGES                   = "images"
BUCKET_DATA_MATERIALS                = "materials"
BUCKET_DATA_MESHES                   = "meshes"
BUCKET_DATA_NODES                    = "nodes"
BUCKET_DATA_SAMPLERS                 = "samplers"
BUCKET_DATA_SCENES                   = "scenes"
BUCKET_DATA_SKINS                    = "skins"
BUCKET_DATA_TEXTURES                 = "textures"
BUCKET_DATA_EXTENSIONS               = "extensions"
BUCKET_DATA_EXTRAS                   = "extras"


#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.1 Accessor
ACCESSOR_BUFFER_VIEW                   = __VAR_BUFFER_VIEW
ACCESSOR_BYTE_OFFSET                   = __VAR_BYTE_OFFSET
ACCESSOR_COMPONENT_TYPE                = __VAR_COMPONENT_TYPE
ACCESSOR_NORMALIZED                    = "normalized"
ACCESSOR_COUNT                         = __VAR_COUNT
ACCESSOR_TYPE                          = "type"
ACCESSOR_MAX                           = "max"
ACCESSOR_MIN                           = "min"
ACCESSOR_SPARSE                        = "sparse"
ACCESSOR_NAME                          = __VAR_NAME
ACCESSOR_EXTENSION                     = __VAR_EXTENSION
ACCESSOR_EXTRA                         = __VAR_EXTRA
#accessor.componentType
ACCESSOR_COMPONENT_TYPE_BYTE           = __TYPE_ID_BYTE
ACCESSOR_COMPONENT_TYPE_UNSIGNED_BYTE  = __TYPE_ID_UNSIGNED_BYTE
ACCESSOR_COMPONENT_TYPE_SHORT          = __TYPE_ID_SHORT
ACCESSOR_COMPONENT_TYPE_UNSIGNED_SHORT = __TYPE_ID_UNSIGNED_SHORT
ACCESSOR_COMPONENT_TYPE_UNSIGNED_INT   = __TYPE_ID_UNSIGNED_INT
ACCESSOR_COMPONENT_TYPE_FLOAT          = __TYPE_ID_FLOAT
#accessor.type
ACCESSOR_TYPE_SCALAR                   = __TYPE_STR_SCALAR
ACCESSOR_TYPE_VECTOR_2                 = __TYPE_STR_VECTOR_2
ACCESSOR_TYPE_VECTOR_3                 = __TYPE_STR_VECTOR_3
ACCESSOR_TYPE_VECTOR_4                 = __TYPE_STR_VECTOR_4
ACCESSOR_TYPE_MATRIX_2                 = __TYPE_STR_MATRIX_2
ACCESSOR_TYPE_MATRIX_3                 = __TYPE_STR_MATRIX_3
ACCESSOR_TYPE_MATRIX_4                 = __TYPE_STR_MATRIX_4
#accessor.sparse
ACCESSOR_SPARSE_COUNT                  = __VAR_COUNT
ACCESSOR_SPARSE_INDICES                = "indices"
ACCESSOR_SPARSE_VALUE                  = "values"
ACCESSOR_SPARSE_EXTENSION              = __VAR_EXTENSION
ACCESSOR_SPARSE_EXTRA                  = __VAR_EXTRA
# accessor.sparse.indices
ACCESSOR_SPARSE_INDICES_BUFFER_VIEW    = __VAR_BUFFER_VIEW
ACCESSOR_SPARSE_INDICES_BYTE_OFFSET    = __VAR_BYTE_OFFSET
ACCESSOR_SPARSE_INDICES_COMPONENT_TYPE = __VAR_COMPONENT_TYPE
ACCESSOR_SPARSE_INDICES_EXTENSION      = __VAR_EXTENSION
ACCESSOR_SPARSE_INDICES_EXTRA          = __VAR_EXTRA
#accessor.sparse.indices.componentType
ACCESSOR_SPARSE_INDICES_COMPONENT_TYPE_UNSIGNED_BYTE   = __TYPE_ID_UNSIGNED_BYTE
ACCESSOR_SPARSE_INDICES_COMPONENT_TYPE_UNSIGNED_SHORT  = __TYPE_ID_UNSIGNED_SHORT
ACCESSOR_SPARSE_INDICES_COMPONENT_TYPE_UNSIGNED_INT    = __TYPE_ID_UNSIGNED_INT
#accessor.sparse.value
ACCESSOR_SPARSE_VALUE_BUFFER_VIEW      = __VAR_BUFFER_VIEW
ACCESSOR_SPARSE_VALUE_BYTE_OFFSET      = __VAR_BYTE_OFFSET
ACCESSOR_SPARSE_VALUE_EXTENSION        = __VAR_EXTENSION
ACCESSOR_SPARSE_VALUE_EXTRA            = __VAR_EXTRA

#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.5 Animation
ANIMATION_CHANNEL                               = "channels"
ANIMATION_SAMPLER                               = "samplers"
ANIMATION_NAME                                  = __VAR_NAME
ANIMATION_EXTENSION                             = __VAR_EXTENSION
ANIMATION_EXTRA                                 = __VAR_EXTRA
#animation.channel
ANIMATION_CHANNEL_SAMPLER                       = "sampler"
ANIMATION_CHANNEL_TARGET                        = "target"
ANIMATION_CHANNEL_EXTENSION                     = __VAR_EXTENSION
ANIMATION_CHANNEL_EXTRA                         = __VAR_EXTRA
#animation.channel.target
ANIMATION_CHANNEL_TARGET_NODE                   = "node"
ANIMATION_CHANNEL_TARGET_PATH                   = "path"
ANIMATION_CHANNEL_TARGET_EXTENSION              = __VAR_EXTENSION
ANIMATION_CHANNEL_TARGET_EXTRA                  = __VAR_EXTRA
#animation.channel.target.path
ANIMATION_CHANNEL_TARGET_TYPE_TRANSLATION       = "translation"
ANIMATION_CHANNEL_TARGET_TYPE_ROTATION          = "rotation"
ANIMATION_CHANNEL_TARGET_TYPE_SCALE             = "scale"
ANIMATION_CHANNEL_TARGET_TYPE_WEIGHT            = "weights"
#animation.sampler
ANIMATION_SAMPLER_INPUT                         = "input"
ANIMATION_SAMPLER_INTERPOLATION                 = "interpolation"
ANIMATION_SAMPLER_OUTPUT                        = "output"
ANIMATION_SAMPLER_EXTENSION                     = __VAR_EXTENSION
ANIMATION_SAMPLER_EXTRA                         = __VAR_EXTRA
#animation.sampler.interpolation
ANIMATION_SAMPLER_INTERPOLATION_TYPE_LINEAR     = "LINEAR"
ANIMATION_SAMPLER_INTERPOLATION_TYPE_STEP       = "STEP"
ANIMATION_SAMPLER_INTERPOLATION_TYPE_CUBIC      = "CUBICSPLINE"

#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.9 Asset
#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.10 Buffer
BUFFER_URI                                      = "uri"
BUFFER_BYTE_LENGTH                              = "byteLength"
BUFFER_NAME                                     = __VAR_NAME
BUFFER_EXTENSIONS                               = __VAR_EXTENSION
BUFFER_EXTRA                                    = __VAR_EXTRA
BUFFER_TEMP_BYTES                               = "tempBytes"

#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.11 Buffer View
BUFFER_VIEW_BUFFER = "buffer"
BUFFER_VIEW_BYTE_OFFSET = "byteOffset"
BUFFER_VIEW_BYTE_LENGTH = "byteLength"
BUFFER_VIEW_BYTE_STRIDE = "byteStride"
BUFFER_VIEW_TARGET = "target"
BUFFER_VIEW_NAME = __VAR_NAME
BUFFER_VIEW_EXTENSIONS = __VAR_EXTENSION
BUFFER_VIEW_EXTRA = __VAR_EXTRA

#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.12 Camera
#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.15 Extension
#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.16 Extras

#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.18 Image
IMAGE_URI                               = __VAR_URI
IMAGE_MIME_TYPE                         = "mimeType"
IMAGE_BUFFER_VIEW                       = __VAR_BUFFER_VIEW
IMAGE_NAME                              = __VAR_NAME
IMAGE_EXTENSION                         = __VAR_EXTENSION
IMAGE_EXTRA                             = __VAR_EXTRA

#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.19 Material
MATERIAL_NAME                           = __VAR_NAME
MATERIAL_EXTENSION                      = __VAR_EXTENSION
MATERIAL_EXTRA                          = __VAR_EXTRA
PBR_METAL_ROUGH                         = "pbrMetallicRoughness"
TEXTURE_NORMAL                          = "normalTexture"
MATERIAL_TEXTURE_OCCLUSION              = "occlusionTexture"
MATERIAL_TEXTURE_EMISSIVE               = "emissiveTexture"
MATERIAL_EMISSIVE_FACTOR                = "emissiveFactor"
MATERIAL_ALPHA_MODE                     = "alphaMode"
MATERIAL_ALPHA_CUTOFF                   = "alphaCutoff"
MATERIAL_DOUBLE_SIDED                   = "doubleSided"

#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.23 Mesh
MESH_PRIMITIVES                         = "primitives"
MESH_WEIGHTS                            = "weights"
MESH_NAME                               = __VAR_NAME
MESH_EXTENSIONS                         = __VAR_EXTENSION
MESH_EXTRA                              = __VAR_EXTRA

#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.24 Mesh Primitive
MESH_PRIMITIVE_ATTRIBUTES               = "attributes"
MESH_PRIMITIVE_INDICES                  = "indices"
MESH_PRIMITIVE_MATERIAL                 = "material"
MESH_PRIMITIVE_MODE                     = "mode"
MESH_PRIMITIVE_TARGETS                  = "targets"
MESH_PRIMITIVE_EXTENSIONS               = __VAR_EXTENSION
MESH_PRIMITIVE_EXTRA                    = __VAR_EXTRA
#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.25 Node
NODE_CAMERA                             = "camera"
NODE_CHILDREN                           = "children"
NODE_SKIN                               = "skin"
NODE_MATRIX                             = __VAR_MATRIX
NODE_MESH                               = "mesh"
NODE_ROTATION                           = __VAR_ROTATION
NODE_SCALE                              = __VAR_SCALE
NODE_TRANSLATION                        = __VAR_TRANSLATION
NODE_WEIGHTS                            = "weights"
NODE_NAME                               = __VAR_NAME
NODE_EXTENSION                          = __VAR_EXTENSION
NODE_EXTRA                              = __VAR_EXTRA

#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.26 Sampler
#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.27 Scene
SCENE_NAME                              = __VAR_NAME
SCENE_NODES                             = "nodes"
#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.28 Skin
SKIN_NAME                       = __VAR_NAME
SKIN_INVERSE_BIND_MATRICES      = "inverseBindMatrices"
SKIN_SKELETON                   = "skeleton"
SKIN_JOINTS                     = "joints"
SKIN_EXTENSION                  = __VAR_EXTENSION
SKIN_EXTRA                      = __VAR_EXTRA
#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.29 Texture
#https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf --- 5.30 Texture Info
