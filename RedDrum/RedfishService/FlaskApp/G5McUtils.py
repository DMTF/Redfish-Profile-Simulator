
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

# NOTE--this code relates to implementation-specifics for how the Dell G5 Rackmanager (BullRed-RedfishService)
#       constructs IDs.  
# some of the RedfishService front-end code depends on these calls.
# in future we will probably move this into the Backend where implementation-specific code belongs,
#   for for now it is left here

# G5-specific ID construction and interpretation utilities
# NOTE:
#  in Redfish, it is generally not safe for a client to construct of assume construction of a URI
#  However, RackManager on G5 is tightly coupled with the G5 MC Redfish Service
#  Therefore RM knows how G5 MC constructs Ids and URIs and can make assumptions

import re

class RfG5IdUtils():
    def __init__(self):
        self.isRackRe=re.compile("^Rack[1-9]$")
        self.isBlockRe=re.compile("^Rack[1-9]-Block([1-9]|10)$")
        self.isPowerBayRe=re.compile("^Rack1-PowerBay[1-4]$")
        self.isSledRe=re.compile("^Rack[1-9]-Block([1-9]|10)-Sled([1-9]|1[0-2])$")

        # RE to match Rack1-Block2 Rack1-PowerBay1 or Rack1-Block2-Sled3
        # with group(1)=Rack1, group(2)=Block2, group(3)=Sled3 or "" if not a sled
        self.subId=re.compile("^(Rack.)-*([^-]*)-?(.*)$") 




    def isRack(self,chassid):
        return( re.search(self.isRackRe, chassid))

    def isBlock(self,chassid):
        return( re.search(self.isBlockRe, chassid))

    def isPowerBay(self,chassid):
        return( re.search(self.isPowerBayRe, chassid))

    def isSled(self,chassid):
        return( re.search(self.isSledRe, chassid))

    def getChassisSubIds(self, chassid):
        subIds=re.search(self.subId, chassid)
        rack=subIds.group(1)
        chas=subIds.group(2)
        sled=subIds.group(3)
        if chas == "":
            chas = None
        if sled == "":
            sled = None
        return(rack,chas,sled)

    def rsdLocation(self, chassid):
        rack,chas,sled=self.getChassisSubIds(chassid)
        #print("rack: {}, chas: {}, sled: {}".format(rack,chas,sled))
        if chas is None:
            id=rack
            parent=None
        elif sled is None:
            id=chas
            parent=rack
        else:
            id=sled
            parent=chas
        return( id, parent)

# usage
'''
        if( rr.isRack(chassid) ):
            print("found rack: {}".format(chassid))
        if( rr.isSled(chassid) ):
            print("found Sled: {}".format(chassid))
        if( rr.isPowerBay(chassid) ):
            print("found PowerBay: {}".format(chassid))
        if( rr.isBlock(chassid) ):
            print("found Block: {}".format(chassid))
'''

