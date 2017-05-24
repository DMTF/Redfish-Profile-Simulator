# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

import os
# BullRed-RackManager Backend root class
from .chassisBackend   import RdChassisBackend
from .managersBackend  import RdManagersBackend
from .systemsBackend   import RdSystemsBackend

class RdBackendRoot():
    def __init__(self,rdr):
        # initialize data
        self.version = "0.1"
        self.backendStatus=None
        self.discoveryState = None
        self.discoveryStatus = None

        # create backend sub-classes
        self.createSubObjects(rdr)

        # run startup tasks
        self.startup(rdr)

    def createSubObjects(self,rdr):
        #create subObjects that implement backend APIs
        self.chassis=RdChassisBackend(rdr)
        self.managers=RdManagersBackend(rdr)
        self.systems=RdSystemsBackend(rdr)

    def startup(self,rdr):
        #starts base BullRed-RackManager backend processes
        # set paths to data
        rdSvcPath="/opt/dell/rm-tools/RMRedfishService"
        rdr.RedDrumConfPath = "/etc/opt/dell/rm-tools/RedDrum.conf"
        rdr.varDataPath="/var/www/rf/"
        rdr.baseDataPath=os.path.join(rdSvcPath, "RedDrum","RedfishService", "FlaskApp", "Data")

        self.backendStatus="OK"
        pass

    def doPhase1Discovery(self,rdr):
        # executes phase-1 resource discovery while the RedfishService is blocked waiting
        self.discoveryState = 1
        self.discoveryStatus = "OK"
        pass

    def startHwMonitors(self,rdr):
        # at this point, the RedfishService front-end is running
        # start base HW monitors in background based on Phase-1 discovery resources and return
        self.discoveryState = 2
        self.discoveryStatus = "OK"
        pass

    def getBackendStatus(self,rdr):
        resp=dict()
        resp["Version"]=self.version
        resp["BackendStatus"]=self.backendStatus
        resp["DiscoveryState"]=self.discoveryState
        resp["DiscoveryStatus"]=self.discoveryStatus
        return (resp)
		


    # **** Backend PUSH  APIs   -- initiated by Backend to send data to Frontend RedfishService ****
    #  these are now in separate class: RdBackendPushToServiceApis, in pushToService....py