# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tools/LICENSE.md

import os

from  .resource import  RfResource
from  .resource import  RfResourceRaw
from  .systems  import  RfSystemsCollection
from  .managers  import RfManagersCollection
from  .sessionService       import RfSessionServiceObj
from  .chassis  import  RfChassisCollection
from  .accountService import RfAccountServiceObj
    
class RfServiceRoot(RfResource):       
    def createSubObjects(self,basePath,relPath):
        self.odataServiceDoc=self.RfOdataServiceDoc(basePath,os.path.normpath("redfish/v1/odata"))
        self.odataMetadata=self.RfOdataMetadata(basePath,os.path.normpath("redfish/v1/$metadata"))
        self.systems=RfSystemsCollection(basePath,os.path.normpath("redfish/v1/Systems"))
        self.chassis=RfChassisCollection(basePath,os.path.normpath("redfish/v1/Chassis"))
        self.managers=RfManagersCollection(basePath,os.path.normpath("redfish/v1/Managers"))
        self.accountService=RfAccountServiceObj(basePath,os.path.normpath("redfish/v1/AccountService"))
        self.sessionService=RfSessionServiceObj(basePath,os.path.normpath("redfish/v1/SessionService"))

    def finalInitProcessing(self,basePath,relPath):
        print("\n\n{}".format(self.resData['Name']))
        
    
    class RfOdataServiceDoc(RfResource):
        pass

    class RfOdataMetadata(RfResourceRaw):
        pass
