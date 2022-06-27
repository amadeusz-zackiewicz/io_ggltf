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
comparisonFileName = "Comparison.txt"

if __name__ == "__main__":

    if os.path.exists(comparisonFileName):
        os.remove(comparisonFileName)

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
    testComparisonOutputPath = os.path.dirname(os.path.abspath(__file__)) + f"{pathSplit}Tests{pathSplit}expected_output{pathSplit}"

    testList = []

    testFolders = os.listdir(testFilesRootPath)

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

    for file in os.listdir(testOutputPath):
        absFilePath = testOutputPath + file
        if os.path.isfile(absFilePath):
            os.remove(absFilePath)

    ## export tests
    for test in testList:
        testName = f"{os.path.basename(test[0]).replace('.blend', '')}_{os.path.basename(test[1]).replace('.py', '')}"
        try:
            print(f"Export test - {testName}")
            process = subprocess.run([blenderPath, test[0], "-b", "--addons", addonName, "-P", test[1]], capture_output=True, encoding="utf8")
        except:
            print(testName, traceback.format_exc())
        finally:
            errString = process.stderr
            outString = process.stdout
            if len(errString) > 0:
                print("\tFailed, please check the .txt file for details")
                outputFilePath = f"{testOutputPath}{testName}.txt"

                if os.path.exists(outputFilePath):
                    outputFile = open(outputFilePath, "w")
                else:
                    outputFile = open(outputFilePath, "x")

                outputFile.write(outString)
                outputFile.write(errString)
                outputFile.close()

    del testList

    failures = []
    warnings = []

    def compare_chunk(file1: io.FileIO, file2: io.FileIO, chunkSize):
        while True:
            chunk1 = file1.read(chunkSize)
            chunk2 = file2.read(chunkSize)

            if chunk1 and chunk2:
                if chunk1 == chunk2:
                    yield False
                else:
                    yield len(chunk1) # both files have the same size, so it should be fine
            else:
                return None # end of file

    ## comparison tests
    for outputFileName in os.listdir(testOutputPath):
        if re.search(".txt$", outputFileName):
            continue 
        print("Comparison test:", outputFileName)
        if os.path.exists(testComparisonOutputPath + outputFileName):

            newFileSize = os.stat(testOutputPath + outputFileName).st_size
            oldFileSize = os.stat(testComparisonOutputPath + outputFileName).st_size

            if newFileSize == oldFileSize:
                try:
                    newFile = open(testOutputPath + outputFileName)
                    oldFile = open(testComparisonOutputPath + outputFileName)
                    chunkSize = 256
                    for comparison in compare_chunk(newFile, oldFile, chunkSize):
                        if comparison:
                            byteRange = (newFile.tell() - comparison, newFile.tell())
                            newFile.seek(newFile.tell() - comparison)
                            oldFile.seek(oldFile.tell() - comparison)
                            newFileChunk = repr(str(newFile.read(comparison)))
                            oldFileChunk = repr(str(oldFile.read(comparison)))
                            diff = io.StringIO()
                            for i, b in enumerate(newFileChunk):
                                match = b == oldFileChunk[i]
                                if match:
                                    diff.write(" ")
                                else:
                                    diff.write("^")
                            failures.append((outputFileName, f"Failed to match chunk between {format(byteRange[0], ',')} - {format(byteRange[1], ',')}bytes\n\t\tChunk diff: \n\t\t\t{newFileChunk}\n\t\t\t{oldFileChunk}\n\t\t\t{diff.getvalue()}"))
                            diff.close()
                            del diff
                            print(f"\tFailed due to chunk mismatch, check the {comparisonFileName} file for details")
                            break
                except:
                    print(outputFileName, traceback.format_exc())
                finally:
                    newFile.close()
                    oldFile.close
            else:
                failures.append((outputFileName, f"File size does not match: {format(newFileSize, ',')} bytes vs {format(oldFileSize, ',')} bytes"))
                print(f"\t\tFailed due to file size mismatch, check the {comparisonFileName} file for details")
        else:
            warnings.append((outputFileName, "Failed to find comparison file"))
            continue

    if len(warnings) > 0 or len(failures) > 0:
        if os.path.exists(comparisonFileName):
            output = open(comparisonFileName, "w")
        else:
            output = open(comparisonFileName, "x")
        try:
            if len(warnings) > 0:
                output.write("Warnings:\n")
                for w in warnings:
                    output.write("\t" + w[0] + ":\n")
                    output.write("\t\t")
                    output.write(w[1])
                    output.write("\n")
            
            if len(failures) > 0:
                output.write("Failures:\n")
                for f in failures:
                    output.write("\t" + f[0] + ":\n")
                    output.write("\t\t")
                    output.write(f[1])
                    output.write("\n")
        finally:
            output.close()
            if platform.system() == "Windows":
                os.startfile(comparisonFileName)