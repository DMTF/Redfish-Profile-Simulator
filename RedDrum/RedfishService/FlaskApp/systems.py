
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

import os
import json
import sys
#from .rootData import RfRoot
from .G5McUtils import RfG5IdUtils

class RfSystemsResource():       
    # Class for all resources under /redfish/v1/Systems
    # Note that this resource was created in serviceRoot for the Systems Resource.
    def __init__(self,rfr ):
        self.loadResourceTemplates(rfr )
        self.loadSystemsDbFiles(rfr)
        self.initializeSystemsVolatileDict(rfr)
        sys.stdout.flush()
        self.g5utils=RfG5IdUtils()
        self.systemsDbDiscovered=None
        self.rfr=rfr

    def loadResourceTemplates( self, rfr ):
        # these are very bare-bones templates but we want to be able to update the resource version or context easily
        #   so the approach is to always start with a standard template for each resource type

        #load SystemsCollection Template
        self.systemsCollectionTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "SystemsCollection.json")

        #load SystemsEntry Template
        self.systemsEntryTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "ComputerSystem.json")

        #load sub-Collection Templates
        self.processorsCollectionTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "ProcessorsCollection.json")
        self.simpleStorageCollectionTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", 
                                                               "SimpleStorageCollection.json")
        self.ethernetInterfaceCollectionTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", 
                                                               "EthernetInterfaceCollection.json")
        self.memoryCollectionTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "MemoryCollection.json")

        #load sub-collection Entry Templates
        self.processorEntryTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "Processor.json")
        self.simpleStorageEntryTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "SimpleStorage.json")
        self.ethernetInterfaceEntryTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "EthernetInterface.json")
        self.memoryEntryTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "Memory.json")

    # worker function called by loadResourceTemplates() to load a specific template
    # returns a dict loaded with the template file
    # if file does not exist, the service exits
    #    assumes good json in the template file
    def loadResourceTemplateFile( self, dataPath, subDir, filename ):
        filePath=os.path.join(dataPath, subDir, filename)
        if os.path.isfile(filePath):
            response=json.loads( open(filePath,"r").read() )
            return(response)
        else:
            print("*****ERROR: System Resource: Json Data file:{} Does not exist. Exiting.".format(filePath))
            sys.exit(10)

        

    def loadSystemsDbFiles(self,rfr ):
        # if rfr.resourceDiscoveryUseDbCache is True:
        #   then if the systems database files exist in /var/www/rf/systemsDb/* then load them to in-memory dict
        self.systemsDbDiscovered=False
        if rfr.useCachedDiscoveryDb is True:
            # first make sure all of the systems DB files exist
            systemsDbCacheExists=True
            sysDbFiles=["SystemsDb.json","ProcessorsDb.json","SimpleStorageDb.json","EthernetInterfacesDb.json","MemoryDb.json"]
            for filenm in sysDbFiles:
                sysDbFilePath=os.path.join(rfr.varDataPath,"systemsDb", filenm)
                if not os.path.isfile(sysDbFilePath):
                    systemsDbCacheExists = False
                    break
            # then load them into dictionaries
            if systemsDbCacheExists is True:
                self.systemsDb=self.loadSystemsDbFile(rfr.varDataPath, "systemsDb", "SystemsDb.json",True) 
                self.processorsDb=self.loadSystemsDbFile(rfr.varDataPath, "systemsDb", "ProcessorsDb.json",False) 
                self.simpleStorageDb=self.loadSystemsDbFile(rfr.varDataPath, "systemsDb", "SimpleStorageDb.json",False) 
                self.ethernetInterfacesDb=self.loadSystemsDbFile(rfr.varDataPath, "systemsDb", "EthernetInterfacesDb.json",False) 
                self.memoryDb=self.loadSystemsDbFile(rfr.varDataPath, "systemsDb", "MemoryDb.json",False) 
                self.systemsDbDiscovered=True

        # if self.systemsDiscovery is false because either: 1) useCachedDiscovery is false or 2) no db cache exists
        # then if resourceDiscovery = Static, load the static db
        # otherwise leave self.systemsDiscover set false and the root service will initiate the system discovery
        #    after chassis, manager, and system resources have all be created
        if self.systemsDbDiscovered is False:
            if (rfr.resourceDiscovery == "Static" ):
                cfg=rfr.staticChassisConfig
                self.systemsDb=self.loadStaticSystemsDbFile(rfr, "systemsDb", cfg, "SystemsDb.json",True) 
                self.processorsDb=self.loadStaticSystemsDbFile(rfr, "systemsDb", cfg, "ProcessorsDb.json",False) 
                self.simpleStorageDb=self.loadStaticSystemsDbFile(rfr, "systemsDb", cfg, "SimpleStorageDb.json",False) 
                self.ethernetInterfacesDb=self.loadStaticSystemsDbFile(rfr, "systemsDb", cfg, "EthernetInterfacesDb.json",False) 
                self.memoryDb=self.loadStaticSystemsDbFile(rfr, "systemsDb", cfg, "MemoryDb.json",False) 
                self.systemsDbDiscovered=True

            elif (rfr.resourceDiscovery == "G5dynamic" ):
                self.systemsDbDiscovered=False
                # the service root needs to run the discovery function

        return(0)

    # worker function to load CACHED chassis db file into dict
    def loadSystemsDbFile( self, dataPath, subDir, filename, requiredFlag ):
        filePath=os.path.join(dataPath, subDir, filename)
        if os.path.isfile(filePath):
            response=json.loads( open(filePath,"r").read() )
            return(response)
        else:
            if requiredFlag is True:
                print("*****ERROR: Systems Resource: Json Data file:{} Does not exist. Exiting.".format(filePath))
                sys.exit(10)
            else:
                return(0)

    # worker function to load STATIC chassis db file into dict and write it back out to cached db file
    def loadStaticSystemsDbFile( self, rfr, subDir, cfgDir, filename, requiredFlag ):
        filePath=os.path.join(rfr.baseDataPath, "resourceStaticDb", cfgDir, subDir, filename)
        if os.path.isfile(filePath):
            response=json.loads( open(filePath,"r").read() )
            varDbFilePath=os.path.join(rfr.varDataPath, subDir, filename)
            responseJson=json.dumps(response,indent=4)
            with open( varDbFilePath, 'w', encoding='utf-8') as f:
                f.write(responseJson)
            return(response)
        else:
            if requiredFlag is True:
                print("*****ERROR: Systems Resource: Json Data file:{} Does not exist. Exiting.".format(filePath))
                sys.exit(10)
            else:
                return(0)

    # worker function to write the systems Db Dict back to the STATIC systems db file 
    # used by patch
    def updateStaticSystemsDbFile( self ):
        varDbFilePath=os.path.join(self.rfr.varDataPath, "systemsDb", "SystemsDb.json")
        responseJson=json.dumps(self.systemsDb, indent=4)
        with open( varDbFilePath, 'w', encoding='utf-8') as f:
            f.write(responseJson)
        return(0)


    def fullG5ChassisDiscovery(self,rfr):
        pass


    def initializeSystemsVolatileDict(self,rfr):
        # this is the in-memory dict of volatile systems properties
        # the systemsDict is an dict indexed by   systemsDict[systemid][<systemsParameters>]
        #   self.systemsVolatileDict[systemid]= a subset of the volatile systems properties
        #       subset of: volatileProperties=["IndicatorLED", "PowerState" ] and "Status"
        #       subset of: {"IndicatorLED": <led>, "PowerState": <ps>, "Status":{"State":<s>,"Health":<h>}} 
        self.systemsVolatileDict=dict()   #create an empty dict of Systems entries

        # initialize the Volatile Dicts
        for systemid in self.systemsDb:
            # inialize with empty members for all known systems
            self.systemsVolatileDict[systemid]={}


    # GET SYSTEMS COLLECTION
    def getSystemsCollectionResource(self):
        # first copy the systems Collection template 
        # then update the Members array for each system previously discovered--in SystemsDb 

        # copy the systemsCollection template file (which has an empty roles array)
        responseData2=dict(self.systemsCollectionTemplate)
        count=0
        # now walk through the entries in the systemsDb and build the systemsCollection Members array
        # note that the members array is an empty array in the template
        uriBase="/redfish/v1/Systems/"
        for systemid in self.systemsDb:
            # increment members count, and create the member for the next entry
            count=count+1
            memberUri=uriBase + systemid
            newMember=[{"@odata.id": memberUri}]

            # add the new member to the members array we are building
            responseData2["Members"] = responseData2["Members"] + newMember

        # update the members count
        responseData2["Members@odata.count"]=count

        # convert to json
        respData2=(json.dumps(responseData2,indent=4))

        return(respData2)


    # GET SYSTEM ENTRY
    def getSystemEntry(self, systemid):
        # verify that the systemid is valid
        if systemid not in self.systemsDb:
                return(4, 404, "Not Found",None,None)

        # first just copy the template resource
        responseData2=dict(self.systemsEntryTemplate)

        # setup some variables to build response from
        basePath="/redfish/v1/Systems/"
        staticProperties=["Name","Description","SystemType","Manufacturer","Model","SKU","SerialNumber","PartNumber","UUID"]
        volatileProperties=[ "IndicatorLED", "PowerState"]
        nonVolatileProperties=[ "AssetTag","HostName","BiosVersion" ]
        statusSubProperties=["State", "Health"]
        bootSourceVolatileProperties=["BootSourceOverrideEnabled","BootSourceOverrideMode","BootSourceOverrideTarget",
                              "UefiTargetBootSourceOverride"]

        processorSummaryProps=["Count", "Model", "Status" ]
        memorySummaryProps=["TotalSystemMemoryGiB","MemoryMirroring","Status"]

        baseNavProperties=[ "Processors","EthernetInterfaces","SimpleStorage","Memory", "SecureBoot","Bios", "Storage"
                      "NetworkInterfaces", "LogServices" ]
        #linkNavProperties=["ManagedBy","Chassis","PoweredBy","CooledBy","EndPoints"] # xg some not supported
        linkNavProperties=["ManagedBy","Chassis"] # xg Only managedBy and Chassis supported

        # assign the required properties
        responseData2["@odata.id"] = basePath + systemid
        responseData2["Id"] = systemid

        # get the base static properties that were assigned when the resource was created
        for prop in staticProperties:
            if prop in self.systemsDb[systemid]:
                responseData2[prop] = self.systemsDb[systemid][prop]

        # get the base non-volatile properties that were assigned when the resource was created
        # these are stored in the persistent cache but are not static--ex is assetTag
        for prop in nonVolatileProperties:
            if prop in self.systemsDb[systemid]:
                responseData2[prop] = self.systemsDb[systemid][prop]

        # get the volatile properties eg powerState
        volatileProps = self.getVolatileProperties(volatileProperties, None, None,
                        self.systemsDb[systemid], self.systemsVolatileDict[systemid])
        for prop in volatileProps:
            responseData2[prop] = volatileProps[prop]

        # get the status properties
        statusProps = self.getStatusProperties(statusSubProperties, None, None,
                      self.systemsDb[systemid], self.systemsVolatileDict[systemid])
        for prop in statusProps:
            responseData2[prop] = statusProps[prop]

        # set the base navigation properties:   /redfish/v1/Systems/<baseNavProp>
        for prop in baseNavProperties:
            if "BaseNavigationProperties"  in  self.systemsDb[systemid]:
                if prop in self.systemsDb[systemid]["BaseNavigationProperties"]:
                    responseData2[prop] = { "@odata.id": basePath + systemid + "/" + prop }


        # build the Actions data
        if "ActionsResetAllowableValues" in self.systemsDb[systemid]:
            resetAction = { "target": basePath + systemid + "/Actions/ComputerSystem.Reset",
                            "ResetType@Redfish.AllowableValues": self.systemsDb[systemid]["ActionsResetAllowableValues"] }
            if "Actions" not in responseData2:
                responseData2["Actions"]={}
            responseData2["Actions"]["#ComputerSystem.Reset"]= resetAction


        # build Dell OEM Section (Sleds only)
        if "OemDellG5MCBmcInfo" in self.systemsDb[systemid]:
            # define the legal oem properties
            oemDellG5NonVolatileProps = [ "BmcVersion", "BmcIp", "BmcMac" ]

            # check if each of the legal oem subProps are in the db
            oemData={}
            for prop in oemDellG5NonVolatileProps:
                if prop in self.systemsDb[systemid]["OemDellG5MCBmcInfo"]:
                    # since these sub-props are nonVolatile, read them from the database
                    oemData[prop] = self.systemsDb[systemid]["OemDellG5MCBmcInfo"][prop]
            if "Oem" not in responseData2:
                responseData2["Oem"]={}
            responseData2["Oem"]["Dell_G5MC"] = oemData

        # build Intel Rackscale OEM Section 
        if "OemRackScaleSystem" in self.systemsDb[systemid]:
            oemRackScaleProps = ["ProcessorSockets","MemorySockets","DiscoveryState" ]

            # check if each of the legal oem subProps are in the db
            oemData = {"@odata.type": "#Intel.Oem.ComputerSystem" }
            for prop in oemRackScaleProps:
                if prop in self.systemsDb[systemid]["OemRackScaleSystem"]:
                    # since these sub-props are nonVolatile, read them from the database
                    if prop == "DiscoveryState":
                        if self.rfr.rsaDeepDiscovery is True:
                            oemData["DiscoveryState"]="Basic"
                    else:
                        oemData[prop] = self.systemsDb[systemid]["OemRackScaleSystem"][prop]
            if "Oem" not in responseData2:
                responseData2["Oem"]={}
            responseData2["Oem"]["Intel_RackScale"] = oemData


        # build the navigation properties under Links : "Contains", "ContainedBy", ManagersIn...
        responseData2["Links"]={}
        for navProp in linkNavProperties:
            if navProp in self.systemsDb[systemid]:
                    if( navProp == "ManagedBy"):
                        linkBasePath="/redfish/v1/Managers/"
                    elif( navProp == "Chassis"):    # it is the /redfishg/v1/Chassis/
                        linkBasePath="/redfish/v1/Chassis/"
                    else:
                        pass

                    #start with an empty array
                    members = list()
                    # now create the array of members for this navProp
                    for memberId in self.systemsDb[systemid][navProp]:
                        newMember= { "@odata.id": linkBasePath + memberId }
                        members.append(newMember)
                    # now add the members array to the response data
                    responseData2["Links"][navProp] = members

        # get the Boot complex property 
        if "BootSourceAllowableValues" in self.systemsDb[systemid]:
            bootData={ "BootSourceOverrideTarget@Redfish.AllowableValues": self.systemsDb[systemid]["BootSourceAllowableValues"] }
            for prop in bootSourceVolatileProperties:
                if prop in self.systemsDb[systemid]["BootSourceVolatileProperties"]:
                    if prop in self.systemsVolatileDict[systemid]:
                        bootData[prop]=self.systemsVolatileDict[systemid][prop]
                    else:
                        bootData[prop]=None
            responseData2["Boot"]=bootData

        # get the ProcessorSummary data
        #   FYI processorSummaryProps=["Count", "Model", "Status" ]
        if "ProcessorSummary" in self.systemsDb[systemid]:
            for prop in processorSummaryProps:
                if prop in self.systemsDb[systemid]["ProcessorSummary"]:
                    procData=self.systemsDb[systemid]["ProcessorSummary"][prop]
            responseData2["ProcessorSummary"]=procData
                
        # get the MemorySummary data
        #   FYI memorySummaryProps=["TotalSystemMemoryGiB","MemoryMirroring","Status"]
        if "MemorySummary" in self.systemsDb[systemid]:
            for prop in memorySummaryProps:
                if prop in self.systemsDb[systemid]["MemorySummary"]:
                    memData=self.systemsDb[systemid]["MemorySummary"][prop]
            responseData2["MemorySummary"]=memData

        # convert to json
        respData2=(json.dumps(responseData2,indent=4))

        return(0, 200, "SUCCESS", respData2, None)



    #xg99
    def patchSystemEntry(self,systemid, patchData):
        # verify that the systemid is valid
        if systemid not in self.systemsDb:
            return(404, "Not Found","","")

        #define the patchable properties in Systems Resource
        patchableInRedfish=["AssetTag","IndicatorLED"]
        bootSourcePatchableInRedfish=["BootSourceOverrideEnabled","BootSourceOverrideMode","BootSourceOverrideTarget",
                                       "UefiTargetBootSourceOverride" ]

        #first verify client didn't send us a property we cant patch based on Redfish Schemas
        for prop in patchData:
            if( prop == "Boot" ):
                for subProp in patchData["Boot"]:
                    if subProp not in bootSourcePatchableInRedfish:
                        return(500, "Bad Request","Property: \"Boot\": {} not patachable per Redfish Spec".format(subProp),"")
            elif prop not in patchableInRedfish: 
                return(500, "Bad Request","Property: {} not patachable per Redfish Spec".format(prop),"")

        #second check if this instance of systems allows the patch data to be patched
        #  if there is no Patchable property in systemsDb, then nothing is patchable
        if "Patchable" not in self.systemsDb[systemid]:
            return(500, "Bad Request","Resource is not patachable","")

        # check if the specific property is patchable
        for prop in patchData:
            if( prop == "Boot" ):
                for subProp in patchData["Boot"]:
                    if subProp not in self.systemsDb[systemid]["BootSourcePatachableProperties"]:
                        return(500, "Bad Request","Property: \"Boot\": {} not patachable for this resource".format(subProp),"")
            elif prop not in self.systemsDb[systemid]["Patchable"]:
                return(500, "Bad Request","Property: {} not patachable for this resource".format(prop),"")


        # now patch the valid properties sent
        updateSystemsDb=False
        createJobToUpdateResource=False
        for prop in patchData:
            if( prop == "Boot" ):
                for subProp in patchData["Boot"]:
                    if subProp in self.systemsVolatileDict[systemid]["Boot"]:
                        if "PendingUpdate" not in self.systemsVolatileDict[systemid]:
                            self.systemsVolatileDict[systemid]["PendingUpdate"]=[]
                            self.systemsVolatileDict[systemid]["PendingUpdate"]=[]
                        if prop not in self.systemsVolatileDict[systemid]["PendingUpdate"]:
                            self.systemsVolatileDict[systemid]["PendingUpdate"].append(prop)
                        if subProp not in self.systemsVolatileDict[systemid]["PendingUpdate"][prop]:
                            self.systemsVolatileDict[systemid]["PendingUpdate"][prop].append(subProp)
                        createJobToUpdateResource=True

            if prop in self.systemsVolatileDict[systemid]:
                self.systemsVolatileDict[systemid][prop]=patchData[prop]
                if "PendingUpdate" not in self.systemsVolatileDict[systemid]:
                    self.systemsVolatileDict[systemid]["PendingUpdate"]=[]
                if prop not in self.systemsVolatileDict[systemid]["PendingUpdate"]:
                    self.systemsVolatileDict[systemid]["PendingUpdate"].append(prop)
                createJobToUpdateResource=True

            elif prop in self.systemsDb[systemid]:
                self.systemsDb[systemid][prop]=patchData[prop]
                if "PendingUpdate" not in self.systemsDb[systemid]:
                    self.systemsDb[systemid]["PendingUpdate"]=[]
                if prop not in self.systemsDb[systemid]["PendingUpdate"]:
                    self.systemsDb[systemid]["PendingUpdate"].append(prop)
                createJobToUpdateResource=True
                updateSystemsDb=True

        if updateSystemsDb is True:
            self.updateStaticSystemsDbFile( )

        if createJobToUpdateResource is True: 
            pass
            # create job to update properties in systemsDb[systemid]["PendingUpdate"] and 
            #    systemsVolatileDict[systemid]["PendingUpdate"]
            #xg JOB  setSystemsProperty(systemid )

        return(0,204,None,None)


    # GET VOLATILE PROPERTIES
    # get the volatile properties that were assigned when the resource was created
    #    volatileProperties = the list of properties that the service treats as volatile
    #    resourceDb=the non-volatile resource database dict
    #    volatileDict=the volatile resource dict
    #  return dict of properties to add to the output
    #  usage:  
    #     volatileProps = getVolatileProperties(volatileProperties,resourceDb,volatileDict):
    #     for prop in volatileProps:
    #         response[prop] = volatileProps[prop]
    def getVolatileProperties(self,volatileProperties,resId,sensorId,resourceDb,volatileDict):
        data={}
        # only include properties that are in the service volatileProperties list
        if resId is not None:
            for prop in volatileProperties:
                # if the property was also included in the database "Volatile" list
                if prop in resourceDb[resId][sensorId]["Volatile"]:
                    # if the property is in the volatile dict, then use that 
                    if (resId in volatileDict) and ( sensorId in volatileDict[resId]) and (prop in volatileDict[resId][sensorId]):
                        data[prop]=volatileDict[resId][sensorId][prop]
                    # else, if the prop was assigned a default value in Db, then use that
                    elif prop in resourceDb[resId][sensorId]:
                        data[prop]=resourceDb[resId][sensorId][prop]
                    else:
                        # the prop is a volatile prop, but there is no value in the volatile dict
                        # and there is no default in the database, so set to None which will map to Json null in response
                        data[prop]=None
                # else: case where the property is not part of the volatile list in the db for this resource
                else:
                    # if the prop itself is in the Db, then treat it as non-volatile and use value in the db
                    if prop in resourceDb[resId][sensorId]:
                        data[prop]=resourceDb[resId][sensorId][prop]
        else:
            for prop in volatileProperties:
                # if the property was also included in the database "Volatile" list
                if ("Volatile" in resourceDb) and (prop in resourceDb["Volatile"]):
                    # if the property is in the volatile dict, then use that 
                    if prop in volatileDict:
                        data[prop]=volatileDict[prop]
                    # else, if the prop was assigned a default value in Db, then use that
                    elif prop in resourceDb:
                        data[prop]=resourceDb[prop]
                    else:
                        # the prop is a volatile prop, but there is no value in the volatile dict
                        # and there is no default in the database, so set to None which will map to Json null in response
                        data[prop]=None
                # else: case where the property is not part of the volatile list in the db for this resource
                else:
                    # if the prop itself is in the Db, then treat it as non-volatile and use value in the db
                    if prop in resourceDb:
                        data[prop]=resourceDb[prop]

        return(data)


    # GET STATUS PROPERTIES
    #    statusSubProps  = the list of status sub-properties that this redfish service supports
    #    resourceDb=the non-volatile resource database dict
    #    volatileDict=the volatile resource dict
    #  return: dict of properties to add to the output
    # Usage example for systemsEntry:
    #    statusProps = getStatusProperties(statusSubProps, self.systemsDb[systemid],self.systemsVolatileDict[systemid]
    #
    def getStatusProperties(self,statusSubProps, resId, sensorId, resourceDb, volatileDict):
        # set the status properties
        resp={}
        if resId is not None:
            if "Status" in resourceDb[resId][sensorId]:
                for subProp in statusSubProps:
                    if subProp in resourceDb[resId][sensorId]["Status"]:
                        # if the volatile resource struct has captured the value, get it from there 
                        if (resId in volatileDict) and ( sensorId in volatileDict[resId]) and ("Status" in volatileDict[resId][sensorId]):
                            if subProp in volatileDict[resId][sensorId]["Status"]:
                                if "Status" not in resp:
                                     resp["Status"]={}
                                resp["Status"][subProp] = volatileDict[resId][sensorId]["Status"][subProp]
                            else:
                                if "Status" not in resp:
                                    resp["Status"]={}
                                resp["Status"][subProp] = resourceDb[resId][sensorId]["Status"][subProp]
                        else:
                            if "Status" not in resp:
                                resp["Status"]={}
                            resp["Status"][subProp] = resourceDb[resId][sensorId]["Status"][subProp]
        else:
            if "Status" in resourceDb:
                for subProp in statusSubProps:
                    if subProp in resourceDb["Status"]:
                        # if the volatile resource struct has captured the value, get it from there 
                        if "Status" in volatileDict:
                            if subProp in volatileDict["Status"]:
                                if "Status" not in resp:
                                    resp["Status"]={}
                                resp["Status"][subProp] = volatileDict["Status"][subProp]
                        else:
                            if "Status" not in resp:
                                resp["Status"]={}
                            resp["Status"][subProp] = resourceDb["Status"][subProp]
                    else:
                        if "Status" not in resp:
                            resp["Status"]={}
                        resp["Status"][subProp] = resourceDb["Status"][subProp]
        return(resp)




    '''
    #xg77
    # Get Chassis Thermal 
    #  related structures
    #    self.fansDb
    #    self.tempSensorsDb
    #    self.fansVolatileDict[systemid]
    #    self.tempSensorsVolatileDict[systemid]
    def getChassisEntryThermal(self, systemid):
        # verify that the systemid is valid
        if systemsid not in self.chassisDb:
                return(404, "Not Found","","")

        if not "BaseNavigationProperties" in self.chassisDb[chassisid]:
                return(404, "Not Found","","")
        if not "Thermal" in self.chassisDb[chassisid]["BaseNavigationProperties"]:
                return(404, "Not Found","","")

        # first just copy the template resource
        responseData2=dict(self.chassisThermalTemplate) 

        # setup some variables to build response from
        basePath="/redfish/v1/Chassis/"
        systemsBasePath="/redfish/v1/Systems/"

        # assign the required top-level properties
        responseData2["@odata.id"] = basePath + chassisid + "/Thermal"
        responseData2["Id"] = "Thermal"
        responseData2["Name"] = "Thermal"


        # completed creating response Data in responseData2 dict

        # convert to json
        respData2=(json.dumps(responseData2,indent=4))

        return(0, 200, "SUCCESS", respData2, None)
    '''


    #xg99
    def resetSystem(self,rfr, systemid, resetData):
        # verify that the systemid is valid
        if systemid not in self.systemsDb:
            return(404, "Not Found","","")

        #  if there is no ResetAllowable value property in systemsDb, then the system doesn't support reset
        if "ActionsResetAllowableValues" not in self.systemsDb[systemid]:
            return(404, "Not Found","","")

        # verify all the required properties were sent in the request
        if "ResetType" not in resetData: 
            return(4,400,"Required  request property not included in request","")
        else:
            # get the resetValue
            resetValue=resetData["ResetType"]

        # check if this is a valid resetTYpe for Redfish xgTODO-need to fix
        redfishValidResetValues=["On","ForceOff","GracefulShutdown","GracefulRestart","ForceRestart","Nmi"]
        if resetValue not in redfishValidResetValues:
            return(4,400,"invalid resetType","")

        # check if this is a resetTYpe that this system supports
        if resetValue not in self.systemsDb[systemid]["ActionsResetAllowableValues"]:
            return(4,400,"invalid resetType","")

        # if here we have a valid request and valid resetValue 
        # XGxg JOB send reset to backend
        # send request to reset system to backend
        print("*****FrontEnd: Send Reset signal to Backent:  ResetType: {}".format(resetValue))
        rc=rfr.backend.systems.doSystemReset(rfr,systemid,resetValue)

        if( rc==0):
            return(0, 204, "SUCCESS", None)
        else:
            return(rc,500, "ERROR",None)

        # DONE

