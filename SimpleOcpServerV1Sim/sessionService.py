# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tools/LICENSE.md

import os
from .resource import RfResource
import json


class RfSessionServiceObj(RfResource):  
    # create instance of sessionService
    def createSubObjects(self,basePath,relPath):
        self.sessions=RfSessionCollection(basePath,os.path.normpath("redfish/v1/SessionService/Sessions"))
        
    def patchResource(self,patchData):
        #first verify client didn't send us a property we cant patch
        for key in patchData.keys():
            if( key != "SessionTimeout" ):
                return (4,400,"Invalid Patch Property Sent","")
        # now patch the valid properties sent
        if( "SessionTimeout" in patchData):
            newVal=patchData['SessionTimeout']
            if( (newVal < 30) or (newVal >86400) ):
                return(4,400,"Bad Request-not in correct range","")
            else:
                self.resData['SessionTimeout']=newVal
                return(0,204,None,None)
        else:
            return (4,400,"Invalid Patch Property Sent","")



class RfSessionCollection(RfResource):
    # create all of the ENTRIES/members in the service collection-data drive from RfSysInfo
    def createSubObjects(self,basePath,relPath):
        self.session1=self.RfSessionObj(basePath,os.path.normpath("redfish/v1/SessionService/Sessions/SESSION123456"))
     


    #Service Collection Entries
    class RfSessionObj(RfResource):
        pass
    

