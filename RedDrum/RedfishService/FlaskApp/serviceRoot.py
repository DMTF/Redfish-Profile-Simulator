
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md


import os
import json
import sys

#from  .rootData         import RfRoot
from  .resource         import  RfStaticResource 
from  .resource         import  RfStaticResourceXml
from  .sessionService   import RfSessionService
from  .accountService   import RfAccountService

from  .systems          import  RfSystemsResource
from  .managers         import  RfManagersResource
from  .chassis          import  RfChassisResource


# called from main: RfServiceRoot(rfr )

class RfServiceRoot():       
    def __init__(self, rfr):
        self.loadServiceRootDict(rfr)
        self.createSubObjects(rfr)
        self.finalInitProcessing(rfr)
        self.magic="123456"



    def loadServiceRootDict(self,rfr):
        # load service root dict from template file
        rootFilePath=os.path.join(rfr.baseDataPath,"templates", "ServiceRoot.json")
        if os.path.isfile(rootFilePath):
            self.resData=json.loads( open(rootFilePath,"r").read() )
        else:
            print("*****ERROR: Json Data file:{} Does not exist. Exiting.".format(rootFilePath))
            sys.exit(10)

        # check if there is a ServiceRootUuidDb.json file in var path, and load it if there is
        uuidFilePath=os.path.join(rfr.varDataPath, "db", "ServiceRootUuidDb.json")
        if os.path.isfile(uuidFilePath):
            uuidDb=json.loads( open(uuidFilePath,"r").read() )
        else:
            print("*****WARNING: Json Data file:{} Does not exist. Creating default.".format(uuidFilePath))
            # generate a random uuid 
            # TODO-Update later
            import uuid
            uuidString=str(uuid.uuid4())
            uuidDb={"UUID": uuidString }

            #write the data back out to the var directory where the dynamic uuid db file is kept
            uuidDbJson=json.dumps(uuidDb,indent=4)
            with open( uuidFilePath, 'w', encoding='utf-8') as f:
                f.write(uuidDbJson)

        # now write the uuid to the serviceRoot resource data
        self.resData["UUID"]=uuidDb["UUID"]

    def createSubObjects(self, rfr):
        #create the in-memory resources based on the RfResource class, classes defined below
        self.serviceVersions=self.RfServiceVersions(rfr,"base","static","RedfishVersions.json")
        self.redDrumServiceInfo=self.RfRedDrumInfo(rfr,"base","static","G5info.json")

        #create the sessionService and AccountService classes
        self.sessionService=RfSessionService(rfr)
        self.accountService=RfAccountService(rfr)

        #create the three data resource
        self.chassis=RfChassisResource(rfr)
        self.managers=RfManagersResource(rfr)
        self.systems=RfSystemsResource(rfr)

    def finalInitProcessing(self,rfr):
        print("\n\n{}".format(self.resData['Name']))

    # GET service root resource
    def getResource(self):
        self.response=json.dumps(self.resData,indent=4)
        return(self.response)

    class RfServiceVersions(RfStaticResource):
        pass
    
    class RfRedDrumInfo(RfStaticResource):
        pass

