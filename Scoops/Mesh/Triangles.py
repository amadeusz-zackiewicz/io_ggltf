from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core.Managers import Tracer
from io_advanced_gltf2.Scoops.Mesh import MeshUtil

def scoop_indexed(bucket, meshObj, uvMaps, vertexColors, shapeKeys, tangents, skin):

    originalName = meshObj.original.name
    depsID = id(meshObj)

    tracker = Tracer.make_mesh_tracker(originalName, depsID, MESH_TYPE_TRIANGLES, uvMaps, vertexColors, shapeKeys, tangents, skin)

    print("---------------------",originalName)

    if tracker in bucket.trackers[BUCKET_TRACKER_MESHES]:
        return bucket.trackers[BUCKET_TRACKER_MESHES][tracker]

    uvIDs = []
    vColorIDs = []
    shapeKeyIDs = []

    for uvName in uvMaps:
        if uvName in meshObj.uv_layers:
            for i, uvLayer in enumerate(meshObj.uv_layers):
                if uvName == uvLayer.name:
                    uvIDs.append(i)
                    break
        else:
            print(uvName, " UV map not found inside ", originalName, " and will be ignored")

    for vColorName in vertexColors:
        if vColorName in meshObj.vertex_colors:
            for i, vColorLayer in enumerate(meshObj.vertex_colors):
                if vColorName == vColorLayer.name:
                    vColorIDs.append(i)
        else:
            print(vColorName, " Vertex Color not found inside ", originalName, " and will be ignored")

    for shapeKeyName in shapeKeys:
        if shapeKeyName in meshObj.shape_keys.key_blocks:
            for i, sk in enumerate(meshObj.shape_keys.key_blocks):
                if shapeKeyName == sk.name:
                    shapeKeyIDs.append(i)
        else:
            print(shapeKeyName, "Shape Key not found inside", originalName, "and will be ignored")

    primitives = MeshUtil.decompose_into_indexed_triangles(meshObj, uvIDs, vColorIDs, shapeKeyIDs)

    meshDict = {
        MESH_NAME: tracker,
        MESH_PRIMITIVES: []
        }

    for i, p in enumerate(primitives):
        primitiveDict = {
            MESH_PRIMITIVE_MODE: MESH_TYPE_TRIANGLES,
            MESH_PRIMITIVE_MATERIAL: 0, # TODO: materials are not yet supported
            }

        positionsAccessor = MeshUtil.get_accessor_positions(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, p.positions)
        normalsAccessor = MeshUtil.get_accessor_normals(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, p.normals)
        indicesAccessor = MeshUtil.get_accessor_indices(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, p.indices)

        primitiveDict[MESH_PRIMITIVE_INDICES] = indicesAccessor
        primitiveDict[MESH_PRIMITIVE_ATTRIBUTES] = {
            MESH_ATTRIBUTE_STR_POSITION: positionsAccessor,
            MESH_ATTRIBUTE_STR_NORMAL: normalsAccessor,
        }
        for i_uv, uvID in enumerate(uvIDs):
            uvAccessor = MeshUtil.get_accessor_uv(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, meshObj.uv_layers[uvID].name, p.uv[i_uv])
            primitiveDict[MESH_PRIMITIVE_ATTRIBUTES][MESH_ATTRIBUTE_STR_TEXCOORD + str(i_uv)] = uvAccessor
        for i_vc, vcID in enumerate(vColorIDs):
            vColorAccessor = MeshUtil.get_accessor_vertex_color(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, meshObj.vertex_colors[vcID].name, p.vertexColor[i_vc])
            primitiveDict[MESH_PRIMITIVE_ATTRIBUTES][MESH_ATTRIBUTE_STR_COLOR + str(i_vc)] = vColorAccessor

        targets = []
        for i_sk, skID in enumerate(shapeKeyIDs):
            morph = {}
            morphName = originalName + "//" + meshObj.shape_keys.key_blocks[skID].name
            print(__file__, "79 --", len(meshObj.loops), len(p.shapeKey[i_sk].positions))
            skPosAccessor = MeshUtil.get_accessor_positions(bucket, morphName, depsID, MESH_TYPE_TRIANGLES, i, p.shapeKey[i_sk].positions)
            skNmAccessor = MeshUtil.get_accessor_normals(bucket, morphName, depsID, MESH_TYPE_TRIANGLES, i, p.shapeKey[i_sk].normals)
            morph[MESH_ATTRIBUTE_STR_POSITION] = skPosAccessor
            morph[MESH_ATTRIBUTE_STR_NORMAL] = skNmAccessor
            targets.append(morph)

        if len(targets) > 0:
            primitiveDict[MESH_PRIMITIVE_TARGETS] = targets

        meshDict[MESH_PRIMITIVES].append(primitiveDict)

    if len(shapeKeyIDs) > 0:
        weights = [0.0] * len(shapeKeyIDs)

        #for i_sk, skID in enumerate(shapeKeyIDs):
            #weights[i_sk] = meshObj.shape_keys.key_blocks[skID].value # TODO: add setting to decide if weights should be zero or same as in blender

        meshDict[MESH_WEIGHTS] = weights


    meshID = len(bucket.data[BUCKET_DATA_MESHES])

    bucket.data[BUCKET_DATA_MESHES].append(meshDict)
    bucket.trackers[BUCKET_TRACKER_MESHES][tracker] = meshID

    return meshID