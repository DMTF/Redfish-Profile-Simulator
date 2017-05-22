
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md


import os
import json
import sys
#from .rootData import RfRoot

# Syntax: RfStaticResource( rfr, baseDataPath, varDataPath, flag, filePath, dataFile)
#    baseDataPath= path to service data:          eg: /RMRedfishService/<profile>/Data   
#    varDataPath=  path to data at /var/www/rf:   eg:/var/www/rf  
#    flag= string to indicate where to get initial data (baseData or varData, etc)
#        "var" or "base" are defined
#    filePath= path from the base data to the file.   Dont include a leading /, it can be empty ""
#    dataFile= the file to load
#         file is the json file to load

class RfStaticResource():
    def __init__(self, rfr, flag, filePath, dataFile):
        if( flag == "base" ):
            indxFilePath=os.path.join(rfr.baseDataPath,filePath, dataFile)
        elif( flag == "var" ):
            indxFilePath=os.path.join(rfr.varDataPath, filePath, dataFile)
        else:
            print(" resource.py: Internal error, invalid flag")
            sys.exit(9)

        #print("*****baseDataPath:{}    varDataPath:{}  flag:{},  filePath: {}  file:{}".format(
        #      rfr.baseDataPath, rfr.varDataPath, flag, filePath, dataFile)

        if os.path.isfile(indxFilePath):
            #print("*****Loading Json Data file:{}".format(indxFilePath))
            self.resData=json.loads( open(indxFilePath,"r").read() )
        else:
            print("*****ERROR: Json Data file:{} Does not exist. Exiting.".format(indxFilePath))
            sys.exit(10)

        self.createSubObjects(rfr, flag)
        self.finalInitProcessing(rfr, flag)
        self.magic="123456"

    def createSubObjects(self, rfr, flag):
        pass

    def finalInitProcessing(self, rfr, flag):
        pass

    def getResource(self):
        self.response=json.dumps(self.resData,indent=4)
        return(self.response)

class RfStaticResourceXml():
    def __init__(self,rfr, flag, filePath, dataFile):
        if( flag == "base" ):
            indxFilePath=os.path.join(rfr.baseDataPath,filePath, dataFile)
        elif( flag == "var" ):
            indxFilePath=os.path.join(rfr.varDataPath, filePath, dataFile)
        else:
            print(" error, invalid flag")
            sys.exit(9)

        #print("*****baseDataPath:{}    varDataPath:{}  flag:{},  filePath: {}  file:{}".format(
        #      rfr.baseDataPath, rfr.varDataPath, flag, filePath, dataFile)

        #print("*****Loading xml Data file:{}".format(indxFilePath))
        resFile=open(indxFilePath, "r")
        resRawData=resFile.read()
        self.resData=resRawData
        self.createSubObjects(rfr, flag)
        self.finalInitProcessing(rfr, flag)
        self.magic="123456"

    def createSubObjects(self,rfr, flag):
        pass

    def finalInitProcessing(self,rfr, flag):
        pass

    def getResource(self):
        self.response=self.resData
        return(self.response)



