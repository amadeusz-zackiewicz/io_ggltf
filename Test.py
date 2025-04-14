import platform
import os
import re
import subprocess
import io
import traceback
import sys
import getopt
import binascii
import difflib

sys.path.append("/")
os.system("")

from Tests.comparers import CompareFile as CompareFile

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
    skipExports = False

    cmdOptions, _ = getopt.gnu_getopt(sys.argv[1:], "f:b:t:prc", ["folder=", "blend=", "test=", "print", "report", "compare_only"])

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
        if o == "-c" or o == "--compare_only":
            skipExports = True
    
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

    def find_issues(text: str) -> bool:
        matches = re.finditer("([eE]xception)|([eE]rror)", text)
        for m in matches:
            return True
            
        return False

    def strip_useless_errors(text: str) -> str:
        return text.replace("Error: Vertex not in group\n", "")

    ## export tests
    if not skipExports:
        print("Export tests:")
        for file in os.listdir(testOutputPath):
            absFilePath = testOutputPath + file
            if os.path.isfile(absFilePath):
                os.remove(absFilePath)

        for i, test in enumerate(testList):
            testName = f"{os.path.basename(test[0]).replace('.blend', '')}_{os.path.basename(test[1]).replace('.py', '')}"
            try:
                print(f"\x1b[1A\x1b[2K({i}/{len(testList)}) Export test - {testName}")
                process = subprocess.run([blenderPath, test[0], "-b", "--factory-startup", "--addons", addonName, "-P", test[1]], capture_output=True)
            except:
                print(f"\x1b[1A\x1b[2K{testName}", traceback.format_exc())
            finally:

                errString = str(process.stderr, encoding="ascii")
                outString = str(process.stdout, encoding="ascii")

                errString = strip_useless_errors(errString)
                outString = strip_useless_errors(outString)

                errHasIssues = find_issues(errString)
                outHasIssues = find_issues(outString)


                if errHasIssues or outHasIssues or _print:
                    if errHasIssues or outHasIssues:
                        print(f"\x1b[1A\x1b[2K{testName} failed, please check the .txt file for details.\n")

                    outputFilePath = f"{testOutputPath}_{testName}.txt"

                    if os.path.exists(outputFilePath):
                        outputFile = open(outputFilePath, "w")
                    else:
                        outputFile = open(outputFilePath, "x")

                    outputFile.write(errString)
                    outputFile.write(outString)
                    outputFile.close()

        del testList

        print("\x1b[1A\x1b[2K\t\tExport tests finished")

####################################################################################### Export tests finished

    ## comparison tests
    print("")
    for outputFileName in os.listdir(testOutputPath):
        if re.search("(\.gltf$)|(\.glb$)", outputFileName):
            sys.stdout.flush()
            print("\x1b[1A\x1b[2KComparison test:", outputFileName)
            if os.path.exists(testComparisonOutputPath + outputFileName):
                errStr = CompareFile.compare_files(testComparisonOutputPath + outputFileName, testOutputPath + outputFileName)
                
                if errStr != "":
                    comparisonReport = open(testOutputPath + "_comparison__" + outputFileName + ".txt", "+w")
                    comparisonReport.write(errStr)
                    comparisonReport.close()

                    print(f"\x1b[1A\x1b[2KFailure (check .txt file for details): {outputFileName}\n")
            else:
                print(f"\x1b[1A\x1b[2KWarning: {outputFileName} -- Failed to find comparison file\n")
                continue

    sys.stdout.flush()
    print("\x1b[1A\x1b[2K\t\tComparison tests finished")
