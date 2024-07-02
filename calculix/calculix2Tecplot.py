import os
import sys
import numpy as np
######################################################################
# S.TRAN 2024
# Standalone converter
######################################################################
# INP Handeling
######################################################################
def extractINPNodeFromFile(fileName):
    data = {}
    with open(fileName) as file:
        line = file.readline()
        while line != '':
            if line.replace('\n','').split(',')[0].strip().lower() == '*node':
                line = file.readline()
                while line[0] != '*':
                    # Clean the string line
                    stringLine = line.replace('\n','').strip()
                    # Action
                    stringList = stringLine.split(',')
                    id = int(stringList[0])
                    if not id in data:
                        data[id] = {}
                    data[id]['X'] = np.double(stringList[1]) 
                    data[id]['Y'] = np.double(stringList[2]) 
                    data[id]['Z'] = np.double(stringList[3])
                    # To the next line 
                    line = file.readline()
            line = file.readline()   
        return data    
######################################################################
def extractINPElementFromFile(fileName,nodeData):
    data = {}
    with open(fileName) as file:
        line = file.readline()
        while line != '':
            if line.replace('\n','').split(',')[0].strip().lower() == '*element':
                # Extract element type
                lineList = line.replace('\n','').split(',')
                lineList = [ item.lower().strip() for item in lineList]
                for item in lineList:
                    if item[:4]=='type':
                        elementType = item.split('=')[1]
                # Start the element extraction
                # Reading char by char
                if elementType == "c3d10":
                    elementSize = 10
                if elementType == "c3d20":
                    elementSize = 20
                valueList = [] 
                entryRaw = ""
                char = file.read(1)
                while char != '*':
                    if char == ',' or char == '\n':
                        if entryRaw.strip() != '':
                            valueList.append(entryRaw)
                        entryRaw = ''
                    else:
                        entryRaw += char
                    if len(valueList) == elementSize+1:
                        valueList = [item.strip() for item in valueList]   
                        #####################################
                        # Process the valueList
                        id = int(valueList[0])
                        if not id in data:
                            data[id] = {}
                        
                        data[id]['P1'] = int(valueList[1]) 
                        data[id]['P2'] = int(valueList[2])
                        data[id]['P3'] = int(valueList[3])
                        data[id]['P4'] = int(valueList[4])    

                        # register elem reference to node 
                        # if not "elemLink" in nodeData[data[id]['P1']]:
                        #     nodeData[data[id]['P1']]['elemLink'] = []
                        # nodeData[data[id]['P1']]['elemLink'].append(id)  

                        # if not "elemLink" in nodeData[data[id]['P2']]:
                        #     nodeData[data[id]['P2']]['elemLink'] = []
                        # nodeData[data[id]['P2']]['elemLink'].append(id) 

                        # if not "elemLink" in nodeData[data[id]['P3']]:
                        #     nodeData[data[id]['P3']]['elemLink'] = []
                        # nodeData[data[id]['P3']]['elemLink'].append(id) 

                        # if not "elemLink" in nodeData[data[id]['P4']]:
                        #     nodeData[data[id]['P4']]['elemLink'] = []
                        # nodeData[data[id]['P4']]['elemLink'].append(id) 

                        # Remove subnode
                        for point in valueList[5:]:
                            if point != "":
                                id = int(point)
                                if id in nodeData: 
                                    del nodeData[id]

                        #####################################
                        valueList = []
                    char = file.read(1)

            line = file.readline()  
        return data,nodeData   
    
# def removeINPInnerElement(nodeData,elemData):
#     for node in nodeData:
#         if len(nodeData[node]['elemLink']) < 6:
#             print(len(nodeData[node]['elemLink']))
#     return nodeData,elemData    
######################################################################
# FRD Handeling
######################################################################
def readFRDNodeDataFromFile(fileName,nodeData):
    indexSize = 9
    entrySize = 12
    with open(fileName) as file:
        line = file.readline()
        while line != '':
            line = line.replace('\n','')
            if line[:10] == '    1PSTEP':
                line = file.readline()
                line = file.readline()
                lineList = line.replace('\n','').strip().split()
                line = file.readline()
                #################################################################################
                # Encode displacement
                if lineList[1].strip().lower() == 'disp':
                    dataList = ["D1","D2","D3"] 
                    # Skipping header
                    while line[:3].strip() == '-5':
                        line = file.readline()
                    # Start to encode the data
                    while line[:3].strip() == '-1':
                        line = line.replace("\n","")
                        index = int(line[3:3+indexSize+1])
                        line = line[3+indexSize+1:]
                        valueList = []
                        while len(line) >= entrySize:
                            valueList.append(line[:entrySize])
                            line = line[entrySize:]
                        # Associate the data to the node
                        for i in range(len(dataList)):
                            if index in nodeData:
                                # print(index,dataList[i],np.double(valueList[i]))
                                nodeData[index][dataList[i]] = np.double(valueList[i])
                        # Compute the full distance
                        if index in nodeData:
                            nodeData[index]["DALL"] = np.sqrt( nodeData[index]["D1"]**2 + nodeData[index]["D2"]**2 + nodeData[index]["D3"]**2 )
                        # To the next line
                        line = file.readline()
                #################################################################################
                # Encode displacement
                if lineList[1].strip().lower() == 'stress':
                    dataList = ["SXX","SYY","SZZ","SXY","SYZ","SZX"] 
                    # Skipping header
                    while line[:3].strip() == '-5':
                        line = file.readline()
                    # Start to encode the data
                    while line[:3].strip() == '-1':
                        line = line.replace("\n","")
                        index = int(line[3:3+indexSize+1])
                        line = line[3+indexSize+1:]
                        valueList = []
                        while len(line) >= entrySize:
                            valueList.append(line[:entrySize])
                            line = line[entrySize:]
                        # Associate the data to the node
                        for i in range(len(dataList)):
                            if index in nodeData:
                                # print(index,dataList[i],np.double(valueList[i]))
                                nodeData[index][dataList[i]] = np.double(valueList[i])
                        # Compute the von Mises stress
                        if index in nodeData:
                            SXX =  nodeData[index]['SXX']  
                            SYY =  nodeData[index]['SYY']  
                            SZZ =  nodeData[index]['SZZ']
                            SXY =  nodeData[index]['SXY']  
                            SYZ =  nodeData[index]['SYZ']  
                            SZX =  nodeData[index]['SZX']
                            T1 = SXX - SYY
                            T2 = SYY - SZZ
                            T3 = SZZ - SXX
                            T4 = SXY**2 + SYZ**2 + SZX**2
                            nodeData[index]['SMISES'] = np.sqrt( 0.5*(T1**2+T2**2+T3**2+6*T4))      
                        # To the next line        
                        line = file.readline()    
            line = file.readline()

######################################################################
def writeMesh(nodeData,elemData,outpuFileName):
    nodeDataSize = len(nodeData.keys())
    elemDataSize = len(elemData.keys())

    outpuFileNameSafe = outpuFileName  
    count = 1
    while os.path.isfile(outpuFileNameSafe+"Mesh.dat"):
        outpuFileNameSafe = outpuFileName + "_" +str(count)
        count += 1  

    with open(outpuFileName+"Mesh.dat","w") as file:
        file.write("""TITLE = "Mesh"\n""")
        # Configure variables
        varList = ["X","Y","Z"]
        for var in nodeData[list(nodeData.keys())[0]].keys():
            if not var in varList:
                varList.append(var)
       
        varString = ""
        for var in varList:
            varString += var+","
        varString = varString[:-1]
        file.write("VARIABLES  = "+varString+"\n")

        # Configure zoning
        strN = "N="+str(nodeDataSize)
        strE = "E="+str(elemDataSize)
        strD = "DATAPACKING=POINT"
        strZ = "ZONETYPE=FETETRAHEDRON"
        file.write("ZONE "+strN+","+strE+","+strD+","+strZ+"\n")
        # Write node data
        # recounting the node to be sure
        nodeCount = 1
        for node in nodeData:
            stringLine = ""
            for var in varList :
                stringLine += str(nodeData[node][var])+" "
            nodeData[node]['write_NodeID'] = nodeCount
            file.write(stringLine+'\n')
            nodeCount += 1
        # Write element data based from the new index
        for elem in elemData:
            strP1 = str(nodeData[elemData[elem]['P1']]['write_NodeID'])
            strP2 = str(nodeData[elemData[elem]['P2']]['write_NodeID'])
            strP3 = str(nodeData[elemData[elem]['P3']]['write_NodeID'])
            strP4 = str(nodeData[elemData[elem]['P4']]['write_NodeID'])
            stringLine = strP1+" "+strP2+" "+strP3+" "+strP4
            file.write(stringLine+'\n')
######################################################################

if len(sys.argv) < 2:
    print("[ERROR] No data name specified")
    sys.exit() 

fileName = sys.argv[1]
if '.inp' in fileName:
    filename = fileName.replace(".inp","")
   
if not os.path.isfile(fileName+".inp"):
    print("[ERROR] INP file does not exist")
    sys.exit() 
nodeData = extractINPNodeFromFile(fileName+".inp")
elemData,nodeData = extractINPElementFromFile(fileName+".inp",nodeData)

if not os.path.isfile(fileName+".frd"):
    print("[INFO] FRD file not found, exporting only the mesh")
else:
    readFRDNodeDataFromFile(fileName+".frd",nodeData)

writeMesh(nodeData,elemData,fileName)
