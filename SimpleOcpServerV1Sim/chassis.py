# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

import os
from .resource import RfResource

class RfChassisCollection(RfResource):
    # create instance of each chassis in the collection
    def createSubObjects(self,basePath,relPath):
        self.chassis1=RfChassisObj(basePath,os.path.normpath("redfish/v1/Chassis/1"))

class RfChassisObj(RfResource):
    # create the dependent sub-objects that live under the chassis object
    def createSubObjects(self,basePath,relPath):
        self.thermal=RfChassisThermal(basePath,os.path.normpath("redfish/v1/Chassis/1/Thermal"))
        self.power=RfChassisPower(basePath,os.path.normpath("redfish/v1/Chassis/1/Power"))

    def patchResource(self,patchData):
        #first verify client didn't send us a property we cant patch
        for key in patchData.keys():
            if( ( key != "AssetTag" ) and ( key != "IndicatorLED" ) ):
                return (4,400,"Invalid Patch Property Sent","")
        # now patch the valid properties sent
        if( "AssetTag" in patchData):
            self.resData['AssetTag']=patchData['AssetTag']
        if( "IndicatorLED" in patchData):
            self.resData['IndicatorLED']=patchData['IndicatorLED']
        return(0,204,None,None)




#subclass Thermal Metrics
class RfChassisThermal(RfResource):
    pass


#subclass Power Metrics
class RfChassisPower(RfResource):
          
    def patchResource(self,patchData):
        #first verify client didn't send us a property we cant patch
        for key in patchData.keys():
            if( key != "PowerControl" ):
                return (4,400,"Invalid Patch Property Sent","")
            else: # Powercontrol:
                for prop2 in patchData["PowerControl"][0].keys():
                    if( prop2 != "PowerLimit" ):
                        return (4,400,"Invalid Patch Property Sent","")
                    else:  #PowerLimit
                        for prop3 in patchData["PowerControl"][0]["PowerLimit"].keys():
                            if(  (prop3 != "LimitInWatts") and
                                    (prop3 != "LimitException") and
                                    (prop3 != "CorrectionInMs")  ):
                                return (4,400,"Invalid Patch Property Sent","")
        #now patch the valid properties sent
        if( "PowerControl" in patchData):
            if( "PowerLimit" in patchData["PowerControl"][0] ):
                patchPowerLimitDict =patchData["PowerControl"][0]["PowerLimit"]
                catfishPowerLimitDict=self.resData["PowerControl"][0]["PowerLimit"]
                if( "LimitInWatts" in patchPowerLimitDict):
                    self.resData["PowerControl"][0]["PowerLimit"]["LimitInWatts"]=patchPowerLimitDict['LimitInWatts']
                if( "LimitException" in patchPowerLimitDict ):
                    self.resData["PowerControl"][0]["PowerLimit"]['LimitException']=patchPowerLimitDict['LimitException']
                if( "CorrectionInMs" in patchPowerLimitDict ):
                    self.resData["PowerControl"][0]["PowerLimit"]['CorrectionInMs']=patchPowerLimitDict['CorrectionInMs']
        return(0,204,None,None)

        

