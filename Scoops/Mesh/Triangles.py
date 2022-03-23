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

    primitives = MeshUtil.decompose_into_indexed_triangles(meshObj, uvIDs, vColorIDs, [])

    meshDict = {
        MESH_NAME: tracker,
        MESH_PRIMITIVES: []
        }

    for i in range(len(primitives)):
        _min = [100000.0, 100000.0, 100000.0]
        _max = [-100000.0, -100000.0, -100000.0]


        for p in primitives[i].positions:
            _min[0] = min(_min[0], p.x)
            _min[1] = min(_min[1], p.y)
            _min[2] = min(_min[2], p.z)

            _max[0] = max(_max[0], p.x)
            _max[1] = max(_max[1], p.y)
            _max[2] = max(_max[2], p.z)
        positionsAccessor = MeshUtil.get_accessor_positions(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, primitives[i].positions, _min, _max)
        normalsAccessor = MeshUtil.get_accessor_normals(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, primitives[i].normals)
        indicesAccessor = MeshUtil.get_accessor_indices(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, primitives[i].indices)

        accessors = {
            MESH_ATTRIBUTE_STR_POSITION: positionsAccessor,
            MESH_ATTRIBUTE_STR_NORMAL: normalsAccessor
        }
        for i_uv, uvID in enumerate(uvIDs):
            uvAccessor = MeshUtil.get_accessor_uv(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, meshObj.uv_layers[uvID].name, primitives[i].uv[i_uv])
            accessors[MESH_ATTRIBUTE_STR_TEXCOORD + str(i_uv)] = uvAccessor


        meshDict[MESH_PRIMITIVES].append({
            MESH_PRIMITIVE_MODE: MESH_TYPE_TRIANGLES,
            MESH_PRIMITIVE_MATERIAL: 0, # TODO: materials are not yet supported
            MESH_PRIMITIVE_ATTRIBUTES: accessors,
            MESH_PRIMITIVE_INDICES: indicesAccessor
        })

    meshID = len(bucket.data[BUCKET_DATA_MESHES])

    bucket.data[BUCKET_DATA_MESHES].append(meshDict)
    bucket.trackers[BUCKET_TRACKER_MESHES][tracker] = meshID

    return meshID