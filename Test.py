import platform
import os
import re
import subprocess
import io
import traceback
import sys
import getopt
import binascii

blenderPath = None
addonName = "io_ggltf"
pathSplit = os.path.sep
comparisonReportFilename = "Comparison.txt"

if __name__ == "__main__":

    if os.path.exists(comparisonReportFilename):
        os.remove(comparisonReportFilename)

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
    testFolders = [""]
    blendFiles = []
    pythonFiles = []
    _print = False
    report = False

    cmdOptions, _ = getopt.gnu_getopt(sys.argv[1:], "f:b:t:pr", ["folder=", "blend=", "test=", "print", "report"])

    for o, a in cmdOptions:
        if o == "-f" or o == "--folder":
            folders = a.split(" ")
            if len(folders) > 1:
                raise Exception("Multiple folders are not supported by this operation. If the folder has space in its name it will be treated as multiple folders.")
            else:
                testFolders[0] = folders[0]
        if o == "-b" or o == "--blend":
            bFiles = a.split(" ")
            for bFile in bFiles:
                blendFiles.append(bFile)
        if o == "-t" or o == "--test":
            tFiles = a.split(" ")
            for tFile in tFiles:
                pythonFiles.append(tFile)
        if o == "-p" or o == "--print":
            _print = True
        if o == "-r" or o == "--report":
            report = True
    
    if testFolders[0] == "":
        testFolders = os.listdir(testFilesRootPath)

    for folder in testFolders:
        absFolderPath = f"{testFilesRootPath}{folder}{pathSplit}"

        if os.path.isdir(absFolderPath):
            if len(blendFiles) == 0: # if -b/--blend arg was not used
                filesInFolder = os.listdir(absFolderPath)
                for file in filesInFolder:
                    absFilePath = f"{absFolderPath}{file}"
                    if os.path.isfile(absFilePath):
                        if re.search("\.blend$", file):
                            blendFiles.append(absFilePath)
            else:                
                for i, blFile in enumerate(blendFiles):
                        absFilePath = f"{absFolderPath}{blFile}.blend" # convert to absolute path
                        if os.path.isfile(absFilePath) and os.path.exists(absFilePath):
                            blendFiles[i] = absFilePath
                        else:
                            print(f"{blFile}.blend does not exist in {folder} and will be ignored.")
                            blendFiles[i] = None

            if len(pythonFiles) == 0: # if -t/--test arg was not used
                filesInFolder = os.listdir(absFolderPath)
                for file in filesInFolder:
                    absFilePath = f"{absFolderPath}{file}"
                    if os.path.isfile(absFilePath):
                        if re.search("\.py$", file):
                            pythonFiles.append(absFilePath)
            else:
                for i, pyFile in enumerate(pythonFiles):
                    absFilePath = f"{absFolderPath}{pyFile}.py" # convert to absolute path
                    if os.path.isfile(absFilePath) and os.path.exists(absFilePath):
                        pythonFiles[i] = absFilePath
                    else:
                        print(f"{pyFile}.py does not exist in {folder} and will be ignored.")
                        pythonFiles[i] = None

            for blFile in blendFiles:
                if blFile == None:
                    continue
                for pyFile in pythonFiles:
                    if pyFile == None:
                        continue
                    testList.append((blFile, pyFile))

            blendFiles = []
            pythonFiles = [] # clear the lists

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
            if len(errString) > 0 or _print:
                if not _print:
                    print("\tFailed, please check the .txt file for details")

                outputFilePath = f"{testOutputPath}_{testName}.txt"

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

    def compare_chunk(file1: io.FileIO, file2: io.FileIO, chunkSize, isBinary):
        while True:
            if isBinary:
                chunk1 = binascii.b2a_hex(file1.read(chunkSize))
                chunk2 = binascii.b2a_hex(file2.read(chunkSize))
            else:
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
                    binExt = re.search("(.*\.bin$)|(.*\.glb$)", outputFileName)
                    if binExt == None:
                        isBinary = False
                        newFile = open(testOutputPath + outputFileName, "r")
                        oldFile = open(testComparisonOutputPath + outputFileName, "r")
                    else:
                        isBinary = True
                        newFile = open(testOutputPath + outputFileName, "rb")
                        oldFile = open(testComparisonOutputPath + outputFileName, "rb")
                    chunkSize = 64
                    for comparison in compare_chunk(newFile, oldFile, chunkSize, isBinary):
                        if comparison:
                            byteRange = (max(newFile.tell() - comparison, 0), newFile.tell())
                            newFile.seek(byteRange[0])
                            oldFile.seek(byteRange[0])
                            newFileChunk = repr(str(newFile.read(comparison)))
                            oldFileChunk = repr(str(oldFile.read(comparison)))
                            diff = io.StringIO()
                            for i, b in enumerate(newFileChunk):
                                    try:
                                        match = b == oldFileChunk[i]
                                        if match:
                                            diff.write(" ")
                                        else:
                                            diff.write("^")
                                    except:
                                        break
                            failures.append((outputFileName, f"Failed to match chunk between {format(byteRange[0], ',')} - {format(byteRange[1], ',')} bytes\n\t\tChunk diff:\n\t\t\t{oldFileChunk}\n\t\t\t{newFileChunk}\n\t\t\t{diff.getvalue()}"))
                            diff.close()
                            del diff
                            print(f"\tFailed due to chunk mismatch, check the {comparisonReportFilename} file for details")
                            break
                except:
                    print(outputFileName, traceback.format_exc())
                finally:
                    newFile.close()
                    oldFile.close
            else:
                failures.append((outputFileName, f"File size does not match: {format(newFileSize, ',')} bytes vs {format(oldFileSize, ',')} bytes"))
                print(f"\t\tFailed due to file size mismatch, check the {comparisonReportFilename} file for details")
        else:
            warnings.append((outputFileName, "Failed to find comparison file"))
            continue

    if len(warnings) > 0 or len(failures) > 0:
        if os.path.exists(comparisonReportFilename):
            output = open(comparisonReportFilename, "w")
        else:
            output = open(comparisonReportFilename, "x")
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
            if report:
                if platform.system() == "Windows":
                    os.startfile(comparisonReportFilename)