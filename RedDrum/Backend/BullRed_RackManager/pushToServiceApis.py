
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

# BullRed-RackManager Backend root class
class RdBackendPushToServiceApis():
    def __init__(self,rdr):
        # initialize data
        self.version = "0.1"
        self.backendStatus=None

    # **** Backend PUSH  APIs   -- initiated by Backend to send data to Frontend RedfishService ****
    #

    #add,delete,update,replace a major collection resource (a chassis, managers, or systems resource)
    #  action={"Add"| "Delete"| "Update"| "Replace"}
    #  collection="Chassis", "Managers", or "Systems" -> the major resource collections
    #  id= the Id of an existing collection resource or the new resource if action=Add
    #  data=a dict of the new resource data for Add or Replace, changed nonVolatile properties for Update.
    #       data is left to default None for Delete
    #  useRestTransport=boul flag. if True, the REST transport is called
    #       this is normal case after discovery when front-end is on a separate thread and the backend
    #       cannot safely call a frontend function to update its database

    def setCollectionResource(self,rdr,action,collection, id ,data=None, useRestTransport=True):
        data=dict()
        rc=0         #     0=ok
        return(rc,errInfo)

    # add,delete,update,replace a chassis sub-resource eg Fan, PowerSupply, TempSensor, VoltSensor,
    #   or powerControl resource.  these resource are indexed underneath a chassisid
    #  action= same as for setCollectionResource()
    #  collection="Fans", "PowerSupplies", "TempSensors", "VoltageSensors", "PowerControl"
    #  chassisid= the Id of the chassis that the chassis sub-resource is under
    #  subResourceId= the Id of an existing sub-resource or the new sub-resource if action=Add
    #  data=a dict of the new resource data for Add or Replace, changed nonVolatile properties for Update.
    #       data is left to default None for Delete
    #  useRestTransport= same as for setCollectionResource()
    #
    def setChassisSubResource(self,rdr,action,collection, chassisid, subResourceId ,data=None, useRestTransport=True):
        #send dict of static data, non-volatile value initial values, and list of volatiles 
        data=dict()
        rc=0         #     0=ok
        return(rc,errInfo)


