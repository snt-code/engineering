# %% Cut FRD into small file
import sys
import os

# Get Name
if len(sys.argv) < 2:
    sys.exit()
dataFileName = sys.argv[1]

# Sanity check
if dataFileName.split('.')[-1].strip() != 'frd':
    print("Wrong file format: ")
    sys.exit()

# Clean up the name
folderName = dataFileName[0:-4]+'/'
if os.path.isdir(folderName):
    print("Warning: Target folder not empty")
else:
    os.mkdir(folderName)


timeStamp = 0
timeCache = ''
stepFile = ''
with open(dataFileName) as dataFile:
    bFirstRun = True
    line = ''
    while bFirstRun or line != '':
        bFirstRun = False
        line = dataFile.readline()
        ## Read meta data
        if line[4:6] == '1C':
            with open(folderName+"FRDData_0_MetaData.txt",'w') as outputFile:
                outputFile.write(line)
                line = dataFile.readline()
                while line[4:6] == '1U':
                    outputFile.write(line)
                    line = dataFile.readline()
        ## Read coordinates            
        if line[4:6] == '2C' :
            with open(folderName+"FRDData_1_Coord.txt",'w') as outputFile:
                outputFile.write(line)
                line = dataFile.readline()
                while line[1:3] == '-1':
                    outputFile.write(line)
                    line = dataFile.readline()
        ## I don't know what these is         
        if line[4:6] == '3C' :  
            with open(folderName+"FRDData_2_UNKNOWN.txt",'w') as outputFile:
                outputFile.write(line)
                line = dataFile.readline()
                while (line[1:3] == '-1' or line[1:3] == '-2') and line[1:3] != '-3' :
                    outputFile.write(line)
                    line = dataFile.readline()
        ## Read STEP data
        if line[4:6] == '1P' :  
            if line[4:10] == '1PSTEP':
                ## Read first line
                line1 = line
                ## Read second line
                line = dataFile.readline()
                line2 = line
                timeStep = line2[13:25]
                if timeStep != timeCache:
                    timeStamp += 1
                    timeCache = timeStep
                
                ## Read third line
                line = dataFile.readline()
                line3 = line
                valueName = line3[5:12]
                outputName = folderName+'FRDData_3_STEP_'+str(timeStamp).zfill(10)+'_'+valueName.strip()+'.txt'
                with open(outputName,'w') as outputFile:
                    outputFile.write(line1)
                    outputFile.write(line2)
                    outputFile.write(line3)
                    while (line[1:3] == '-1' or line[1:3] == '-2' or line[1:3] == '-4' or line[1:3] == '-5') and line[1:3] != '-3':
                        outputFile.write(line)
                        line = dataFile.readline()
              
