import sys
import os

###########################################################################################
    
def separateEntry(linePrime,inputFile,entryKey,**kwargs):
    # Check entry
    headerLine = linePrime.split(',')
    if not headerLine[0].replace('\n','').strip() == entryKey:
        return linePrime
    # Treat the entry header
    headerData = {}
    if len(headerLine) > 1:
        for i in range(1,len(headerLine)):
            if headerLine[i].strip() != "":
                headerLineOption = headerLine[i].split("=")
                headerData[headerLineOption[0].strip()] = headerLineOption[1].replace("\n",'')
    # Create outputFileName
    outputFileName = (entryKey.replace('*','')).strip()
    if "subName" in kwargs and kwargs['subName'] in headerData:
        outputFileName += '-'+headerData[kwargs['subName']]
        print(outputFileName)
    # Treat folder path
    folderPath = ""
    if "path" in kwargs:
        folderPath = kwargs["path"]+"/"    
    # When file order is true
    if "fileOrder" in kwargs:
        outputFileName = kwargs['fileOrder']+"-"+outputFileName 
    openMode = "w"
    if "openMode" in kwargs:
        openMode = kwargs["openMode"]
    # Write data    
    with open(folderPath+"INPData-"+outputFileName+".txt",openMode) as File:
        # Write header
        line = entryKey
        for item in headerData:
            line += ', '+ item + '=' + headerData[item]
        line += '\n'
        File.write(line)
        # Write Data
        line = inputFile.readline()
        # bool stop
        bStopWriting = False
        while line[0] != '*':
            if line.strip() != '':
                File.write(line)
            line = inputFile.readline()
            # Skip line if empty
            if line.strip() == '':
                line = inputFile.readline()

    # Return active line        
    return line

def separateStepEntry(linePrime,inputFile,**kwargs):
    # Check entry
    headerLine = linePrime.split(',')
    if not headerLine[0].replace('\n','').strip() == "*Step":
        return linePrime
    # Treat folder path
    folderPath = ""
    if "path" in kwargs:
        folderPath = kwargs["path"]+"/"    
    # Init flag
    bFirstTimeCLoad = True    
    bFirstTimeDLoad = True
    bFirstTimeBoundary = True
    # Treat every line
    line= inputFile.readline()
    while line.strip() != '*End step' :
        # Treat CLoad
        if line.split(",")[0].strip().replace('*','') == "Cload":
            if bFirstTimeCLoad:
                line = separateEntry(line,inputFile,"*Cload",fileOrder="S1",path=folderPath)
                bFirstTimeCLoad = False
            else:
                line = separateEntry(line,inputFile,"*Cload",fileOrder="S1",openMode="a",path=folderPath)    
        # Treat DLoad        
        elif line.split(",")[0].strip().replace('*','') == "Dload":
            if bFirstTimeDLoad:
                line = separateEntry(line,inputFile,"*Dload",fileOrder="S2",path=folderPath)
                bFirstTimeDLoad = False
            else:
                line = separateEntry(line,inputFile,"*Dload",fileOrder="S2",openMode="a",path=folderPath)
        # Treat Boundary        
        elif line.split(",")[0].strip().replace('*','') == "Boundary":
            if bFirstTimeBoundary:
                line = separateEntry(line,inputFile,"*Boundary",fileOrder="S3",path=folderPath)
                bFirstTimeBoundary = False
            else:
                line = separateEntry(line,inputFile,"*Boundary",fileOrder="S3",openMode="a",path=folderPath)        
        #Treat any option
        elif line[0] == '*' and len(line) > 2 and line[1] != '*' and line.strip() != '*End step':
                line = separateEntry(line,inputFile,line.split(",")[0].strip(),fileOrder="S4",path=folderPath)  
        else:
            line = inputFile.readline()  

    return line
###########################################################################################

fileName = sys.argv[1]
entryData = []

# Sanity check
if fileName.split('.')[-1].strip() != 'inp':
    print("Wrong file format: ")
    sys.exit()
# Create folder
folderName = fileName[:-4]
if os.path.isdir(folderName):
    print("Warning: Target folder not empty")
else:
    os.mkdir(folderName)

with open(fileName,"r") as file:
    line = file.readline()
    while line != '' :
        line = separateEntry(line,file,'*Heading',fileOrder="00",path=folderName)
        line = separateEntry(line,file,'*Node',fileOrder="01",path=folderName)
        line = separateEntry(line,file,'*Element',fileOrder="02",path=folderName)
        while '*Nset' in line:
            line = separateEntry(line,file,'*Nset',fileOrder="03",subName="Nset",path=folderName)
        while '*Elset' in line:    
            line = separateEntry(line,file,'*Elset',fileOrder="04",subName="Elset",path=folderName)
        while '*Surface' in line:
            line = separateEntry(line,file,'*Surface',fileOrder="05",subName="Name",path=folderName)    
        line = separateEntry(line,file,'*Material',fileOrder="06",path=folderName)    
        line = separateEntry(line,file,'*Density',fileOrder="07",path=folderName)    
        line = separateEntry(line,file,'*Elastic',fileOrder="08",path=folderName)  
        line = separateEntry(line,file,'*Conductivity',fileOrder="09",path=folderName) 
        line = separateEntry(line,file,'*Specific heat',fileOrder="10",path=folderName)  
        line = separateEntry(line,file,'*Expansion',fileOrder="11",path=folderName) 
        line = separateEntry(line,file,'*Solid section',fileOrder="12",path=folderName)
        line = separateStepEntry(line,file,path=folderName)            
        # Go next line
        line = file.readline()  
