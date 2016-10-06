# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

from .resource import RfResource
import json
import os

class RfSystemsCollection(RfResource):       
    # create instance of each system in the collection
    def createSubObjects(self,basePath,relPath):
        self.system1=RfSystemObj(basePath,os.path.normpath("redfish/v1/Systems/1"))  

class RfSystemObj(RfResource):   
    # create the dependent sub-objects that live under the System object
    def createSubObjects(self,basePath,relPath):      
        #self.logs=RfLogServiceCollection(path,os.path.normpath("Systems/1/Logs"))
        #self.logSel=RfLogService(path,os.path.normpath("Systems/1/Logs/SEL"))
        #self.logSelEntries=RfLogEntries(path,os.path.normpath("Systems/1/Logs/SEL/Entries"))
        pass
    
    def getResource(self):
        self.response=json.dumps(self.resData,indent=4)
        return(self.response)
    
    def patchResource(self,patchData):
        #first verify client didn't send us a property we cant patch
        for key in patchData.keys():
            if( ( key != "AssetTag" ) and ( key != "IndicatorLED" ) and
                ( key != "Boot" ) ): 
                return (4,400,"Invalid Patch Property Sent","")
            elif( key == "Boot" ):
                for prop2 in patchData["Boot"].keys():
                    if(  (prop2 != "BootSourceOverrideEnabled") and
                         (prop2 != "BootSourceOverrideTarget") ):
                        return (4,400,"Invalid Patch Property Sent","")
        # now patch the valid properties sent
        if( "AssetTag" in patchData):
            print("assetTag:{}".format(patchData["AssetTag"]))
            self.resData['AssetTag']=patchData['AssetTag']
        if( "IndicatorLED" in patchData):
            self.resData['IndicatorLED']=patchData['IndicatorLED']
        if( "Boot" in patchData):
            bootData=patchData["Boot"]
            if("BootSourceOverrideEnabled" in bootData ):
                value=bootData["BootSourceOverrideEnabled"]
                validValues=["Once","Disabled","Continuous"]
                if( value in validValues ):
                    self.resData['Boot']['BootSourceOverrideEnabled']=value
                else:
                    return (4,400,"Invalid_Value_Specified: BootSourceOverrideEnable","")
            if("BootSourceOverrideTarget" in bootData ):
                value=bootData["BootSourceOverrideTarget"]
                validValues=self.resData['Boot']['BootSourceOverrideTarget@Redfish.AllowableValues']
                if( value in validValues ):
                    self.resData['Boot']['BootSourceOverrideTarget']=value
                else:
                    return (4,400,"Invalid_Value_Specified: BootSourceOverrideTarget","")
        return(0,204,None,None)


    def resetResource(self,resetData):
        if( "ResetType" in resetData):
            #print("RESETDATA: {}".format(resetData))
            value=resetData['ResetType']
            validValues=self.resData["Actions"]["#ComputerSystem.Reset"]["ResetType@Redfish.AllowableValues"]
            if( value in validValues ):
                #it is a supoported reset action  modify other properties appropritely
                if( value=="On" or value=="ForceRestart" or value=="GracefulRestart" ):
                    self.resData["PowerState"]="On"
                    print("PROFILE_SIM--SERVER WAS RESET. power now ON")
                elif(value=="GracefulShutdown" or value=="ForceOff"):
                    self.resData["PowerState"]="Off"
                    print("PROFILE_SIM--SERVER WAS RESET. Power now Off")
                return(0,204,"System Reset","")
            else:
                return(4,400,"Invalid reset value: ResetType","")
        else:  # invalid request
            return(4,400,"Invalid request property","")

#subclass Logs Collection
class RfLogServiceCollection(RfResource):
    def createLogServiceObjects(self,path):                        
        #self.log=self.RfSystemLogServiceObj(path,"Systems/1/SEL")
        pass
            
  
# sub sub class logService
class RfLogService(RfResource):
    def createLogEntryCollection(self,rfTime,rfSysInfo):                      
        #self.logEntryCollection=self.RfSystemLogEntryCollection(rfTime,rfSysInfo)
        pass
                

# sub/sub/sub class LogEntryCollection
class RfLogEntryCollection(RfResource):
    def createLogEntries(self,rfTime,rfSysInfo):
        #self.logEntry1=self.RfSystemLogEntry1(rfTime,rfSysInfo)
        pass
                    
    def getObject(self):
        #self.response=json.dumps(self.objData,indent=4)
        pass     
