import platform
import os
import re
import subprocess
import io
import traceback
import sys

blenderPath = None
addonName = "io_advanced_gltf2"
pathSplit = os.path.sep

if __name__ == "__main__":

    if blenderPath == None:
        # get the path to the blender executable
        blenderPath = os.path.abspath("../../../../")
        if platform.system() == "Windows": # os.access doesnt work correctly on windows
            print(platform.system(), "--- Scanning for blender executable file")
            blenderPath = blenderPath + pathSplit + "blender.exe"
            if not os.path.exists(blenderPath):
                blenderPath = None
        else:
            print(platform.system(), "--- Scanning for blender executable file")
            blenderDirFiles = os.listdir(blenderPath)
            for file in blenderDirFiles:
                exp = re.search("^blender(?![-_])", file)
                if exp:
                    print(blenderPath + pathSplit + exp.string, "--- Executable:", os.access(blenderPath + pathSplit + exp.string, os.X_OK))
                    if os.access(blenderPath + pathSplit + exp.string, os.X_OK):
                        blenderPath = blenderPath + pathSplit+ exp.string
                        break

        if blenderPath == None:
            raise Exception("Failed to find blender executable file, please manually override the 'blenderPath' variable")
        else:
            print("Executable found: ", blenderPath)
    else:
        if os.path.exists(blenderPath):
            print("Manual executable path:", blenderPath)
        else:
            raise Exception("Failed to find:", blenderPath)

    testFilesRootPath = os.path.dirname(os.path.abspath(__file__)) + f"{pathSplit}Tests{pathSplit}files{pathSplit}"
    testOutputPath = os.path.dirname(os.path.abspath(__file__)) + f"{pathSplit}Tests{pathSplit}output{pathSplit}"
    
    testFolders = os.listdir(testFilesRootPath)

    testList = []

    for folder in testFolders:
        absFolderPath = f"{testFilesRootPath}{folder}{pathSplit}"
        if os.path.isdir(absFolderPath):
            blendFiles = []
            pythonFiles = []
            filesInFolder = os.listdir(absFolderPath)
            for file in filesInFolder:
                absFilePath = f"{absFolderPath}{file}"
                if os.path.isfile(absFilePath):
                    if re.search("\.blend$", file):
                        blendFiles.append(absFilePath)
                    if re.search("\.py$", file):
                        pythonFiles.append(absFilePath)
            
            for blFile in blendFiles:
                for pyFile in pythonFiles:
                    testList.append((blFile, pyFile))

    oldFiles = os.listdir(testOutputPath)

    for file in oldFiles:
        absFilePath = testOutputPath + file
        if os.path.isfile(absFilePath):
            os.remove(absFilePath)

    ## export tests
    for test in testList:
        testName = f"{os.path.basename(test[0]).replace('.blend', '')}_{os.path.basename(test[1]).replace('.py', '')}"
        print()
        try:
            process = subprocess.run([blenderPath, test[0], "-b", "--addons", addonName, "-P", test[1]], capture_output=True, encoding="utf8")
        except:
            print(testName, traceback.format_exc())
        finally:
            errString = process.stderr
            outString = process.stdout
            if len(errString) > 0:
                print(f"Export test - {testName}:\n    Failed, please check the .txt file for details")
                outputFilePath = f"{testOutputPath}{testName}.txt"

                if os.path.exists(outputFilePath):
                    outputFile = open(outputFilePath, "w")
                else:
                    outputFile = open(outputFilePath, "x")

                outputFile.write(outString)
                outputFile.write(errString)
                outputFile.close()
            else:
                print(f"Export test - {testName}:\n    Passed")

    ## comparison tests
            