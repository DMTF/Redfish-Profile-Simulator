# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

import os
import json

class RfResource():
    def __init__(self,basePath,relPath):
        path=os.path.join(basePath,relPath)
        #print("*****base:{}    rel:{}".format(basePath,relPath))
        indxFilePath=os.path.join(path,"index.json")
        print("*****Loading Mockup json file:{}".format(indxFilePath))
        resFile=open(indxFilePath, "r")
        resRawData=resFile.read()
        self.resData=json.loads( resRawData )
        self.createSubObjects(basePath,relPath)
        self.finalInitProcessing(basePath,relPath)
        self.magic="1234"

    def createSubObjects(self,basePath,relPath):
        pass

    def finalInitProcessing(self,basePath,relPath):
        pass

    def getResource(self):
        self.response=json.dumps(self.resData,indent=4)
        return(self.response)



class RfResourceRaw():
    def __init__(self,basePath,relPath):
        path=os.path.join(basePath,relPath)
        indxFilePath=os.path.join(path,"index.xml")
        print("*****Loading Mockup raw data file:{}".format(indxFilePath))
        resFile=open(indxFilePath, "r")
        resRawData=resFile.read()
        self.resData=resRawData
        self.createSubObjects(basePath,relPath)
        self.finalInitProcessing(basePath,relPath)

    def createSubObjects(self,basePath,relPath):
        pass

    def finalInitProcessing(self,basePath,relPath):
        pass

    def getResource(self):
        self.response=self.resData
        return(self.response)
