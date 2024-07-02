import os
import sys

# Sanity check
if len(sys.argv) == 1:
    sys.exit()

folderName = sys.argv[1]

# Folder check
if not os.path.isdir(folderName):
    print("Not a folder")
    sys.exit()

dirList = list(os.listdir(folderName))
dirList.sort()
STEPnameList = []

with open(folderName+"-repack.inp","w") as file:
    for name in dirList:
        #Sanity check
        if name.split('-')[0] == "INPData":
            # Treat every entry that is not a STEP
            if 'S' in name.split('-')[1]:
                STEPnameList.append(name)
            else:
                with open(folderName+'/'+name) as inputFile:
                    line = inputFile.readline()
                    while line != '':
                        file.write(line)
                        line = inputFile.readline()
    # Write down the step information
    file.write("*Step\n")                      
    for name in STEPnameList:
        with open(folderName+'/'+name) as inputFile:
            line = inputFile.readline()
            while line != '':
                file.write(line)
                line = inputFile.readline()
    file.write("*End Step") 
