# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

import os
from .resource import RfResource

class RfManagersCollection(RfResource):
    # create instance of each Manager in the collection
    def createSubObjects(self,basePath,relPath):
        self.managerBmc=RfManagerObj(basePath,os.path.normpath("redfish/v1/Managers/bmc"))

class RfManagerObj(RfResource):
    # create the dependent sub-objects that live under the chassis object
    def createSubObjects(self,basePath,relPath):
        self.ethernetColl=RfManagerEthernetColl(basePath,os.path.normpath("redfish/v1/Managers/bmc/EthernetInterfaces"))
        self.networkProtocol=RfManagerNetworkProtocol(basePath,os.path.normpath("redfish/v1/Managers/bmc/NetworkProtocol"))

    def patchResource(self,patchData):
        #first verify client didn't send us a property we cant patch
        for key in patchData.keys():
            if( ( key != "DateTime" ) and ( key != "DateTimeLocalOffset" ) ):
                return (4,400,"Invalid Patch Property Sent","")

        dateTime=None
        dateTimeOffset=None
        localOffset=None
        
        # now patch the valid properties sent
        if( "DateTime" in patchData):
            dateTime=patchData['DateTime']
            dateTimeOffset=dateTime[-6:]   # get last 6 chars ....+00:00 or -00:00
        if( "DateTimeLocalOffset" in patchData):
            localOffset=patchData['DateTimeLocalOffset']

        # verify that if both DateTime and DateTimeLocalOffset were sent, thant
        #  the offsets are the same.  (no reason to send both though)
        if( (dateTimeOffset is not None ) and (localOffset is not None) ):
            if( dateTimeOffset != localOffset ):              
                return(4,409,"Offsets in DateTime and DateTimeLocalOffset conflict",None)  # 409 Conflict

        # reconcile localOffset and the offset in DateTime to write back
        # if only DateTime was updated, also update dateTimeLocalOffset
        if( localOffset is None ):
            localOffset=dateTimeOffset
        # if only DateTimeLocalOffset was updated (timezone change), also update DateTime
        if( dateTime is None):
            dateTime=self.resData['DateTime']   #read current value to get time
            dateTime=dateTime[:-6]              # strip the offset
            dateTime=dateTime + localOffset     # add back the offset sent in in DateTimeLocalOFfset

        # TODO:  issue 1545 in SPMF is ambiguity of what patching DateTimeLocalOFfset should actually do.
        # this may need to be updated once issue is resolved
            
        # now write the valid properties with updated values
        self.resData['DateTime']=dateTime
        self.resData['DateTimeLocalOffset']=localOffset
        return(0,204,None,None)

    def resetResource(self,resetData):
        if( "ResetType" in resetData):
            #print("RESETDATA: {}".format(resetData))
            value=resetData['ResetType']
            validValues=self.resData["Actions"]["#Manager.Reset"]["ResetType@Redfish.AllowableValues"]
            if( value in validValues ):
                #it is a supoported reset action  modify other properties appropritely
                # nothing to do--manager always on in this profile
                return(0,204,"System Reset","")
            else:
                return(4,400,"Invalid reset value: ResetType","")
        else:  # invalid request
            return(4,400,"Invalid request property","")

class RfManagerNetworkProtocol(RfResource):
    pass



#the Manager Ethernet Collection
class RfManagerEthernetColl(RfResource):
    # create the dependent sub-objects that live under the chassis object
    def createSubObjects(self,basePath,relPath):
        self.eth0=RfManagerEthernet(basePath,os.path.normpath("redfish/v1/Managers/bmc/EthernetInterfaces/eth0"))



#the Manager Ethernet Instance
class RfManagerEthernet(RfResource):

    def patchResource(self,patchData):
        # TODO: check and save the data
        # for now, just return ok w/ 204 no content
        return(0,204,None,None)





        

