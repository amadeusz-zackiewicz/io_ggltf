import os
import subprocess
import platform

# This is meant to be used by the test files, please do not run this from here
def run_test(folderName: str, blendFiles: None or list or str, pythonFiles: None or list or str):
    
    if blendFiles != None:
        if type(blendFiles) == list:
            blendFiles = "--blend=" + '"' + " ".join(blendFiles) + '"'
        else:
            blendFiles = "-b " + blendFiles
    else:
        blendFiles = ""
    
    if pythonFiles != None:
        if type(pythonFiles) == list:
            pythonFiles = "--test=" + '"' + " ".join(pythonFiles) + '"'
        else:
            pythonFiles = "-t " + pythonFiles
    else:
        pythonFiles = ""

    python = "python" if platform.system() == "Windows" else "python3"
    #testScriptPath = os.path.abspath("../Test")
    testScriptPath = "Test"

    print(f'{python} -m "{testScriptPath}" -f {folderName} {blendFiles} {pythonFiles}')
    errno = subprocess.call(f'{python} -m "{testScriptPath}" -f {folderName} {blendFiles} {pythonFiles} -p')
    print("Limited Test exited with error number:", errno)

if __name__ == "__main__":
    run_test("testFolder", "blendFile", "pythonFile")
    run_test("testFolder", ["multiple", "files"], ["multiple", "files"])
    run_test("testFolder", None, None)