# when a script is run in blender it is considered to be __main__ but
# when we run this as a file using terminal there is only 1 argument and
# when blender launches a python file it has 2 arguments
# so if there is only 1 argument, we are running it as a standalone python file
# otherwise blender is running it
import sys
if __name__ == "__main__" and len(sys.argv) == 1:
    import os
    sys.path.append(os.path.abspath(""))
    import Tests.LimitedTestUtil as T
    T.run_test("animated_cube", "animated_cube", os.path.basename(__file__).replace(".py", ""))
else:
    from io_ggltf.Advanced import *
    from io_ggltf.Constants import *
    import json
    import bpy
    import os

    filePath = "//..\\..\\output\\"
    fileName = "animated_cube_test_internals"
    binPath = ""

    def test(bucket):
        tests = {"Expected Results": {}, "Results": {}, "Failures": 0}
        def new(name: str, expected, actual):
            tests["Expected Results"][name] = expected
            tests["Results"][name] = actual
        ##########################################################################
        # Add code here

        Node.based_on_object(bucket, "Cube")
        Node.based_on_object(bucket, "Sphere")
        Mesh.based_on_object(bucket, "Cube", uvMaps=False, shapeKeys=["Up", "Left"])
        Mesh.based_on_object(bucket, "Sphere", uvMaps=False)
        File.stage_bucket(bucket)

        new("Node Count", 2, len(bucket.data[BUCKET_DATA_NODES]))
        new("Mesh Count", 2, len(bucket.data[BUCKET_DATA_MESHES]))
        new("Node Basis", [("Cube", None), ("Sphere", None)], bucket.basis[BUCKET_DATA_NODES])
        new("Mesh Basis", [("Cube", None), ("Sphere", None)], bucket.basis[BUCKET_DATA_MESHES])

        from io_ggltf.Core.Blender import NLA, Timeline

        new("Track 1 start", 1.0, NLA.get_track_framerange(bpy.data.objects["Cube"], "RandomActionTrack")[0])
        new("Track 1 end", 199.0, NLA.get_track_framerange(bpy.data.objects["Cube"], "RandomActionTrack")[1])

        new("Track 2 start", 1.0, NLA.get_track_framerange(bpy.data.objects["Cube"], "UpActionTrack")[0])
        new("Track 2 end", 100.0, NLA.get_track_framerange(bpy.data.objects["Cube"], "UpActionTrack")[1])

        new("Node Properties",
            [[NODE_TRANSLATION, NODE_ROTATION, NODE_SCALE], [NODE_TRANSLATION, NODE_ROTATION, NODE_SCALE]],
            bucket.nodeProperties
        )

        new("Marker start", 1, Timeline.get_marker_frame("timeline_start"))
        new("Marker end", 140, Timeline.get_marker_frame("timeline_end"))
        
        # Finish code here
        ##########################################################################
        for k, v in tests["Expected Results"].items():
            rv = tests["Results"][k]

            if v != rv:
                tests["Failures"] += 1

        f = open(f"{os.path.abspath(bpy.path.abspath(filePath))}\\{fileName}.json", "w")
        json.dump(tests, f, indent=4)
        f.close()

    test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLB))