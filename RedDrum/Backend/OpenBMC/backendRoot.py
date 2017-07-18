# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

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
        # *** for initial OpenBMC integration, the OpenBMC backend will use static discovery.
        # *** this amounts to selecting the static resource data that the RedfishService will load from
        #     we are calling the config OpenBMC will start with:   "OBmcMonolythicPower8"
        #  ** it is a:  one chassis (Id=Opc1), one system(Id=sys1), one manager (Id=OBMC1)
        #  **    has:  4 fans, 2 power supplies, 1 processor(Power8), 64GB RAM
        # *** it is at:  RedDrum/RedfishService/FlaskApp/Data/resourceStaticDb/OBmcMonolythicPower8
        rdr.useCachedDiscoveryDb=True
        rdr.resourceDiscovery="Static"
        rdr.staticChassisConfig="OBmcMonolythicPower8"
        self.backendStatus="OK"

        # to move the data caches somewhere safe, edit these path and dont run with isLocal flat in RedDrumMain
        #rdSvcPath="/opt/dell/rm-tools/RMRedfishService"   # this is a read path  
        rdr.RedDrumConfPath = "/usr/share/RedDrum/RedDrum.conf"  # read path
        #rdr.varDataPath="/var/www/rf/"
        #rdr.baseDataPath=os.path.join(rdSvcPath, "RedDrum","RedfishService", "FlaskApp", "Data")

        print("****Initialized Backend using: {}".format(rdr.staticChassisConfig))

    def doPhase1Discovery(self,rdr):
        # called by RedfishService
        # executes phase-1 resource discovery while the RedfishService is blocked waiting
        self.discoveryState = 1
        self.discoveryStatus = "OK"
        # *** RedfishService isn't calling this yet

    def startHwMonitors(self,rdr):
        # called by RedfishService
        # at this point, the RedfishService front-end is running
        # start base HW monitors in background based on Phase-1 discovery resources and return
        self.discoveryState = 2
        self.discoveryStatus = "OK"
        # *** RedfishService isn't calling this yet

    def getBackendStatus(self,rdr):
        # called by RedfishService
        resp=dict()
        resp["Version"]=self.version
        resp["BackendStatus"]=self.backendStatus
        resp["DiscoveryState"]=self.discoveryState
        resp["DiscoveryStatus"]=self.discoveryStatus
        return (resp)
        # *** RedfishService isn't calling this yet
		


    # **** Backend PUSH  APIs   -- initiated by Backend to send data to Frontend RedfishService ****
    # these are in a separate class  RdBackendPushToServiceApis() 

