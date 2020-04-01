# Imports
import os
import pathlib as pl
import sys


# Variables
allFiles = {}
intervalCounter = 0

# Configuration constants
rawMainPath = "/"
mainPath = pl.Path(rawMainPath)

openTextMarker = "\033[93m"
closeTextMarker = "\033[0m"

interactive = True
showPathErrors = True
showRmErrors = True
showIntervalPrints = True
reverseOrder = False
humanReadableOutput = True

orderBySize = True
if orderBySize == True:
    orderValue = lambda x: x[1]
else:
    orderValue = None

lineRange = 10
interval = 0
minFileSize = 1024 * 1024 * 10
maxFilesize = 10 ** 15

sizeNames = ["B", "KB", "MB", "GB", "TB"]


# Task functions
def waitKey():
    key = None

    if os.name == 'nt':
        import msvcrt
        key = bytes.decode(msvcrt.getch())
    else:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    return key

def getItemsInPath(path):
    filesInPath = {}
    directoriesInPath = []

    try:
        for item in os.scandir(path=path):
            if os.path.isfile(item.path):
                filesInPath[item.path] = item.stat().st_size

            elif os.path.isdir(item.path):
                directoriesInPath.append(item.path)

    except Exception as ex:
        if showPathErrors == True:
            print(f"{type(ex).__name__}: {path}")

    return filesInPath, directoriesInPath

def addFiles(fileDict):
    global intervalCounter

    for file, size in fileDict.items():
        if size >= minFileSize and size <= maxFilesize:
            allFiles[file] = size

            if showIntervalPrints == True and intervalCounter == interval:
                intervalCounter = 0

                if humanReadableOutput == True:
                    intervalPrintSize = makeHumanReadable(size)
                else:
                    intervalPrintSize = size

                print(f"{file}: {intervalPrintSize}")

            elif showIntervalPrints == True:
                intervalCounter = intervalCounter + 1

def makeHumanReadable(size):
    count = 0
    newSize = size

    while newSize >= 1024:
        newSize = newSize / 1024
        count = count + 1
    newSize = round(newSize, 2)

    return f"{newSize} {sizeNames[count]}"

def clear():
    if os.name == "posix":
        os.system("clear")
    else:
        os.system("cls")

# Main functions
def crawl(path):
    filesInPath, directoriesInPath = getItemsInPath(path)

    addFiles(filesInPath)

    for directory in directoriesInPath:
        crawl(directory)

def printCurrentRange(minShowedResult, maxShowedResult, rmList, currentSelection):
    clear()

    fileLoopCount = 0
    for file, size in sorted(allFiles.items(), reverse=reverseOrder, key=orderValue):
        if fileLoopCount >= minShowedResult and fileLoopCount <= maxShowedResult:
            rmMark = rmList[file]

            if humanReadableOutput == True:
                size = makeHumanReadable(size)

            if fileLoopCount == currentSelection:
                print(f"{openTextMarker}[{rmMark}] {file}: {size}{closeTextMarker}")
            else:
                print(f"[{rmMark}] {file}: {size}")

        if fileLoopCount == maxShowedResult:
            break

        fileLoopCount = fileLoopCount + 1

def wPressed(currentSelection, minShowedResult, maxShowedResult):
    if currentSelection - 1 < 0:
        return currentSelection, minShowedResult, maxShowedResult

    if currentSelection - 1 < minShowedResult:
        minShowedResult = minShowedResult - 1
        maxShowedResult = maxShowedResult - 1

    return currentSelection - 1, minShowedResult, maxShowedResult

def sPressed(currentSelection, minShowedResult, maxShowedResult):
    if currentSelection + 1 > len(allFiles) - 1:
        return currentSelection, minShowedResult, maxShowedResult

    if currentSelection + 1 > maxShowedResult:
        maxShowedResult = maxShowedResult + 1
        minShowedResult = minShowedResult + 1

    return currentSelection + 1, minShowedResult, maxShowedResult

def enterPressed(rmList):
    for file, rmMark in rmList.items():
        if rmMark == "X":
            try:
                os.remove(file)

            except Exception as ex:
                if showRmErrors == True:
                    print(f"{type(ex).__name__}: {file}")

    exit()

def spacebarPressed(rmList, currentSelection):
    rmLoopCounter = 0
    
    for file, rmMark in rmList.items():
        if rmLoopCounter == currentSelection:
            if rmMark == "X":
                rmList[file] = " "
            else:
                rmList[file] = "X"

        rmLoopCounter = rmLoopCounter + 1

    return rmList

def interactiveResults(orderValue):
    minShowedResult = len(allFiles) - lineRange
    maxShowedResult = len(allFiles) - 1
    currentSelection = maxShowedResult

    rmList = {}
    for file, _size in sorted(allFiles.items(), reverse=reverseOrder, key=orderValue):
        rmList[file] = " "
    
    while True:
        printCurrentRange(minShowedResult, maxShowedResult, rmList, currentSelection)
        print(f"[{currentSelection} / {len(allFiles) - 1}]")
            
        returnedKey = waitKey()
        if returnedKey == "w":
            currentSelection, minShowedResult, maxShowedResult = wPressed(currentSelection, minShowedResult, maxShowedResult)
        elif returnedKey == "s":
            currentSelection, minShowedResult, maxShowedResult = sPressed(currentSelection, minShowedResult, maxShowedResult)
        elif returnedKey == "\r":
            enterPressed(rmList)
        elif returnedKey == " ":
            rmList = spacebarPressed(rmList, currentSelection)
        elif returnedKey == "e":
            exit()
            
def printAllResults(orderValue):
    print("\n", end="")
    
    for file, size in sorted(allFiles.items(), reverse=reverseOrder, key=orderValue):
        if humanReadableOutput == True:
            size = makeHumanReadable(size)

        print(f"{file}: {size}")


# Execution
crawl(mainPath)

if len(allFiles) < lineRange:
    lineRange = len(allFiles)

print("Press key to continue... ")
waitKey()

if interactive == True:
    interactiveResults(orderValue)
else:
    printAllResults(orderValue)