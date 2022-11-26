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

    def find_issues(text: str) -> bool:
        matches = re.finditer("([eE]xception)|([eE]rror)", text)
        for m in matches:
            return True
            
        return False

    def strip_useless_errors(text: str) -> str:
        return text.replace("Error: Vertex not in group\n", "")

    ## export tests
    for i, test in enumerate(testList):
        testName = f"{os.path.basename(test[0]).replace('.blend', '')}_{os.path.basename(test[1]).replace('.py', '')}"
        try:
            sys.stdout.write("\033[2K\033[1G")
            print(f"\r({i}/{len(testList)}) Export test - {testName}", end="")
            process = subprocess.run([blenderPath, test[0], "-b", "--factory-startup", "--addons", addonName, "-P", test[1]], capture_output=True)
        except:
            print(f"\r{testName}", traceback.format_exc())
        finally:

            errString = str(process.stderr, encoding="ascii")
            outString = str(process.stdout, encoding="ascii")

            errString = strip_useless_errors(errString)
            outString = strip_useless_errors(outString)

            errHasIssues = find_issues(errString)
            outHasIssues = find_issues(outString)


            if errHasIssues or outHasIssues or _print:
                if errHasIssues or outHasIssues:
                    sys.stdout.write("\033[2K\033[1G")
                    print(f"\r{testName} failed, please check the .txt file for details")

                outputFilePath = f"{testOutputPath}_{testName}.txt"

                if os.path.exists(outputFilePath):
                    outputFile = open(outputFilePath, "w")
                else:
                    outputFile = open(outputFilePath, "x")

                outputFile.write(errString)
                outputFile.write(outString)
                outputFile.close()

    del testList

    sys.stdout.write("\033[2K\033[1G")
    print("\t\tExport tests finished")

####################################################################################### Export tests finished

    def compare_chunk(file1: io.FileIO, file2: io.FileIO, chunkSize, isBinary):
        """Return true if chunks do not match"""
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
                    yield True
            else:
                return None # end of file

    differ = difflib.HtmlDiff(wrapcolumn=80)

    ## comparison tests
    for outputFileName in os.listdir(testOutputPath):
        if re.search("(\.txt$)|(\.html$)", outputFileName):
            continue 
        sys.stdout.write("\033[2K\033[1G")
        print("\rComparison test:", outputFileName, end="")
        if os.path.exists(testComparisonOutputPath + outputFileName):
            
            newFileSize = os.stat(testOutputPath + outputFileName).st_size
            oldFileSize = os.stat(testComparisonOutputPath + outputFileName).st_size

            compareFailed = False
            compareBinary = re.search("(.*\.bin$)|(.*\.glb$)", outputFileName) != None

            if newFileSize != oldFileSize:
                print(f"\rFailure (file size mismatch): {outputFileName}")
                compareFailed = True

            if compareBinary:
                newFile = open(testOutputPath + outputFileName, "rb")
                oldFile = open(testComparisonOutputPath + outputFileName, "rb")
            else:
                newFile = open(testOutputPath + outputFileName, "r")
                oldFile = open(testComparisonOutputPath + outputFileName, "r")

            if not compareFailed:
                for chunkMismatched in compare_chunk(oldFile, newFile, 256, compareBinary):
                    if chunkMismatched != False:
                        compareFailed = True
                        print(f"\rFailure (file data mismatch): {outputFileName}")
                        break

            # binary takes far too long to produce a diff and its unreadable anyway
            if compareFailed and not compareBinary:
                newFile.seek(0)
                oldFile.seek(0)
                # if compareBinary:
                #     # newSeq = str(binascii.b2a_base64(bytes(newFile.read())))
                #     # oldSeq = str(binascii.b2a_base64(bytes(oldFile.read())))
                #     # newSeq = [newSeq[i:i+80] for i in range(0, len(newSeq), 80)]
                #     # oldSeq = [oldSeq[i:i+80] for i in range(0, len(oldSeq), 80)]
                # else:

                newSeq = newFile.readlines()
                oldSeq = oldFile.readlines()

                f = open(testOutputPath + f"__diff_{outputFileName}.html", "w")
                f.write(differ.make_file(oldSeq, newSeq))
                f.close()

            newFile.close()
            oldFile.close()

        else:
            print(f"Warning: {outputFileName} -- Failed to find comparison file")
            continue

    sys.stdout.write("\033[2K\033[1G")
    print("\t\tComparison tests finished")
