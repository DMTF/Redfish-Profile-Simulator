
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

import os
import json
import sys
#from .rootData import RfRoot
from .G5McUtils import RfG5IdUtils

class RfChassisResource():       
    # Class for all resources under /redfish/v1/Chassis
    # Note that this resource was created in serviceRoot for the Chassis Resource.
    def __init__(self,rfr ):
        self.loadResourceTemplates(rfr )
        self.loadChassisDbFiles(rfr)
        self.initializeChassisVolatileDict(rfr)
        sys.stdout.flush()
        self.g5utils=RfG5IdUtils()
        self.chassisDbDiscovered=None
        self.rfr=rfr
        self.magic="123456"

    def loadResourceTemplates( self, rfr ):
        # these are very bare-bones templates but we want to be able to update the resource version or context easily
        #   so the approach is to always start with a standard template for each resource type

        #load ChassisCollection Template
        self.chassisCollectionTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "ChassisCollection.json")

        #load ChassisEntry Template
        self.chassisEntryTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "ChassisEntry.json")

        #load ChassisPower Template
        self.chassisPowerTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "Power.json")

        #load ChassisThermal Template
        self.chassisThermalTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "Thermal.json")


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
            print("*****ERROR: Chassis Resource: Json Data file:{} Does not exist. Exiting.".format(filePath))
            sys.exit(10)
        

    def loadChassisDbFiles(self,rfr ):
        # if rfr.resourceDiscoveryUseDbCache is True:
        #   then if the chassis database files exist in /var/www/rf/chassisDb/* then load them to in-memory dict
        #        else if rfr.resourceDiscover=static, read static db files and save to the cache
        #        else,  kick-off job to discover the chassis data from the MC--may take 1-2 minutes, and save in cache
        # else, always run full discovery each time RM Redfish Service starats
        self.chassisDbDiscovered=False
        if rfr.useCachedDiscoveryDb is True:
            # first make sure all of the chassis DB files exist
            chassisDbCacheExists=True
            chasDbFiles=["ChassisDb.json", "FansDb.json", "TempSensorsDb.json", "PowerSuppliesDb.json", "VoltageSensorsDb.json", "PowerControlDb.json"]
            for filenm in chasDbFiles:
                chasDbFilePath=os.path.join(rfr.varDataPath,"chassisDb", filenm)
                if not os.path.isfile(chasDbFilePath):
                    chassisDbCacheExists = False
                    break
            # then load them into dictionaries
            if chassisDbCacheExists is True:
                self.chassisDb=self.loadChassisDbFile(rfr.varDataPath, "chassisDb", "ChassisDb.json") 
                self.fansDb=self.loadChassisDbFile(rfr.varDataPath, "chassisDb", "FansDb.json") 
                self.tempSensorsDb=self.loadChassisDbFile(rfr.varDataPath, "chassisDb", "TempSensorsDb.json") 
                self.powerSuppliesDb=self.loadChassisDbFile(rfr.varDataPath, "chassisDb", "PowerSuppliesDb.json") 
                self.voltageSensorsDb=self.loadChassisDbFile(rfr.varDataPath, "chassisDb", "VoltageSensorsDb.json") 
                self.powerControlDb=self.loadChassisDbFile(rfr.varDataPath, "chassisDb", "PowerControlDb.json") 
                self.chassisDbDiscovered=True

        # if self.chassisDiscovery is false because either: 1) useCachedDiscovery is false or 2) no db cache exists
        # then if resourceDiscovery = Static, load the static db
        # otherwise leave self.chassisDiscover set false and the root service will initiate the system discovery
        #    after chassis, manager, and system resources have all be created
        if self.chassisDbDiscovered is False:
            if (rfr.resourceDiscovery == "Static" ):
                cfg=rfr.staticChassisConfig
                self.chassisDb=self.loadStaticChassisDbFile(rfr, "chassisDb", cfg, "ChassisDb.json") 
                self.fansDb=self.loadStaticChassisDbFile(rfr, "chassisDb", cfg, "FansDb.json") 
                self.tempSensorsDb=self.loadStaticChassisDbFile(rfr, "chassisDb", cfg, "TempSensorsDb.json") 
                self.powerSuppliesDb=self.loadStaticChassisDbFile(rfr, "chassisDb", cfg, "PowerSuppliesDb.json") 
                self.voltageSensorsDb=self.loadStaticChassisDbFile(rfr, "chassisDb", cfg, "VoltageSensorsDb.json") 
                self.powerControlDb=self.loadStaticChassisDbFile(rfr, "chassisDb", cfg, "PowerControlDb.json") 
                self.chassisDbDiscovered=True

            elif (rfr.resourceDiscovery == "G5dynamic" ):
                self.chassisDbDiscovered=False
                # the service root needs to run the discovery function

        return(0)

    # worker function to load CACHED chassis db file into dict
    def loadChassisDbFile( self, dataPath, subDir, filename ):
        filePath=os.path.join(dataPath, subDir, filename)
        if os.path.isfile(filePath):
            response=json.loads( open(filePath,"r").read() )
            return(response)
        else:
            print("*****ERROR: Chassis Resource: Json Data file:{} Does not exist. Exiting.".format(filePath))
            sys.exit(10)

    # worker function to load STATIC chassis db file into dict and write it back out to cached db file
    def loadStaticChassisDbFile( self, rfr, subDir, cfgDir, filename ):
        filePath=os.path.join(rfr.baseDataPath, "resourceStaticDb", cfgDir, subDir, filename)
        if os.path.isfile(filePath):
            response=json.loads( open(filePath,"r").read() )
            varDbFilePath=os.path.join(rfr.varDataPath, subDir, filename)
            responseJson=json.dumps(response,indent=4)
            with open( varDbFilePath, 'w', encoding='utf-8') as f:
                f.write(responseJson)
            return(response)
        else:
            print("*****ERROR: Chassis Resource: Json Data file:{} Does not exist. Exiting.".format(filePath))
            sys.exit(10)

    # worker function to write the chassis Db Dict back to the STATIC chassis db file 
    # used by patch
    def updateStaticChassisDbFile( self ):
        varDbFilePath=os.path.join(self.rfr.varDataPath, "chassisDb", "ChassisDb.json")
        responseJson=json.dumps(self.chassisDb, indent=4)
        with open( varDbFilePath, 'w', encoding='utf-8') as f:
            f.write(responseJson)
        return(0)


    def fullG5ChassisDiscovery(self,rfr):
        pass

    def initializeChassisVolatileDict(self,rfr):
        # this is the in-memory dict of volatile chassis properties
        # the sessionsDict is an dict indexed by   sessionsDict[sessionId][<sessionParameters>]
        #   self.chassisVolatileDict[chassisid]= a subset of the volatile chassid properties
        #       subset of: volatileProperties=["IndicatorLED", "PowerState" ] and "Status"
        #       subset of: {"IndicatorLED": <led>, "PowerState": <ps>, "Status":{"State":<s>,"Health":<h>}} 
        self.chassisVolatileDict=dict()   #create an empty dict of Chassis entries
        self.fansVolatileDict=dict()   #create an empty dict of Fans  entries
        self.tempSensorsVolatileDict=dict()   #create an empty dict of TempSensors  entries
        self.powerSuppliesVolatileDict=dict()   #create an empty dict of powerSupply entries
        self.voltageSensorsVolatileDict=dict()   #create an empty dict of voltage sensor entries
        self.powerControlVolatileDict=dict()   #create an empty dict of Power Control 

        # initialize the Volatile Dicts
        for chassisid in self.chassisDb:
            # inialize with empty members for all known chassis
            self.chassisVolatileDict[chassisid]={}
            self.fansVolatileDict[chassisid]={}
            self.tempSensorsVolatileDict[chassisid]={}
            self.powerSuppliesVolatileDict[chassisid]={}
            self.voltageSensorsVolatileDict[chassisid]={}
            self.powerControlVolatileDict[chassisid]={}


    # GET chassis Collection
    def getChassisCollectionResource(self):
        # first copy the chassis Collection template 
        # then updates the Members array will each chassis previously discovered--in ChassisDb 

        # copy the chassisCollection template file (which has an empty roles array)
        responseData2=dict(self.chassisCollectionTemplate)
        count=0
        # now walk through the entries in the chassisDb and build the chassisCollection Members array
        # note that the members array is an empty array in the template
        uriBase="/redfish/v1/Chassis/"
        for chassisid in self.chassisDb:
            # increment members count, and create the member for the next entry
            count=count+1
            memberUri=uriBase + chassisid
            newMember=[{"@odata.id": memberUri}]

            # add the new member to the members array we are building
            responseData2["Members"] = responseData2["Members"] + newMember

        # update the members count
        responseData2["Members@odata.count"]=count

        # convert to json
        respData2=(json.dumps(responseData2,indent=4))

        return(respData2)



    # Get Chassis Entry
    def getChassisEntry(self, chassisid):
        # verify that the chassisid is valid
        if chassisid not in self.chassisDb:
                return(4, 404, "Not Found",None,None)

        # first just copy the template resource
        responseData2=dict(self.chassisEntryTemplate)

        # setup some variables to build response from
        basePath="/redfish/v1/Chassis/"
        staticProperties=["Name", "Description", "ChassisType", "Manufacturer", "Model", "SKU", "SerialNumber", "PartNumber"]
        volatileProperties=[ "IndicatorLED", "PowerState"]
        nonVolatileProperties=[ "AssetTag" ]
        baseNavProperties=["LogServices", "Thermal", "Power"]
        statusSubProperties=["State", "Health"]
        linkNavProperties=["Contains", "ContainedBy", "PoweredBy", "CooledBy", "ManagedBy", "ComputerSystems", "ManagersInChassis"]

        # assign the required properties
        responseData2["@odata.id"] = basePath + chassisid
        responseData2["Id"] = chassisid

        # set the base static properties that were assigned when the resource was created
        for prop in staticProperties:
            if prop in self.chassisDb[chassisid]:
                responseData2[prop] = self.chassisDb[chassisid][prop]

        # get the base non-volatile properties that were assigned when the resource was created
        # these are stored in the persistent cache but are not static--ex is assetTag
        for prop in nonVolatileProperties:
            if prop in self.chassisDb[chassisid]:
                responseData2[prop] = self.chassisDb[chassisid][prop]

        # get the volatile properties eg powerState
        volatileProps = self.getVolatileProperties(volatileProperties, None, None,
                        self.chassisDb[chassisid], self.chassisVolatileDict[chassisid])
        for prop in volatileProps:
            responseData2[prop] = volatileProps[prop]

        # get the status properties
        statusProps = self.getStatusProperties(statusSubProperties, None, None,
                      self.chassisDb[chassisid], self.chassisVolatileDict[chassisid])
        for prop in statusProps:
            responseData2[prop] = statusProps[prop]


        # set the base navigation properties:   /redfish/v1/Chassis/<baseNavProp>
        for prop in baseNavProperties:
            if "BaseNavigationProperties"  in  self.chassisDb[chassisid]:
                if prop in self.chassisDb[chassisid]["BaseNavigationProperties"]:
                    responseData2[prop] = { "@odata.id": basePath + chassisid + "/" + prop }


        # build the Actions data
        if "ActionsResetAllowableValues" in self.chassisDb[chassisid]:
            resetAction = { "target": basePath + chassisid + "/Actions/Chassis.Reset",
                            "ResetType@Redfish.AllowableValues": self.chassisDb[chassisid]["ActionsResetAllowableValues"] }
            if "Actions" not in responseData2:
                responseData2["Actions"]={}
            responseData2["Actions"]["#Chassis.Reset"]= resetAction

        if "ActionsOemSledReseat" in self.chassisDb[chassisid]:
            if self.chassisDb[chassisid]["ActionsOemSledReseat"] is True:
                resetAction = { "target": basePath + chassisid + "/Actions/Chassis.Reseat" }
                if "Actions" not in responseData2:
                    responseData2["Actions"]={}
                if "Oem" not in responseData2["Actions"]:
                    responseData2["Actions"]["Oem"]={}
                responseData2["Actions"]["Oem"]["#Dell.G5SledReseat"]= resetAction

        # build Dell OEM Section (Sleds only)
        if "OemDellG5MCBmcInfo" in self.chassisDb[chassisid]:
            # define the legal oem properties
            oemDellG5NonVolatileProps = [ "BmcVersion", "BmcIp", "BmcMac" ]

            # check if each of the legal oem subProps are in the db
            oemData={}
            for prop in oemDellG5NonVolatileProps:
                if prop in self.chassisDb[chassisid]["OemDellG5MCBmcInfo"]:
                    # since these sub-props are nonVolatile, read them from the database
                    oemData[prop] = self.chassisDb[chassisid]["OemDellG5MCBmcInfo"][prop]
            if "Oem" not in responseData2:
                responseData2["Oem"]={}
            responseData2["Oem"]["Dell_G5MC"] = oemData

        # build Intel Rackscale OEM Section 
        if "hasOemRackScaleLocation" in self.chassisDb[chassisid]:
            if self.chassisDb[chassisid]["hasOemRackScaleLocation"] is True:
                locationId, parentId = self.g5utils.rsdLocation(chassisid)
                oemData = {"@odata.type": "http://RackScale.intel.com/schema#RackScale.Chassis",
                           "Location": { "Id": locationId } }
                if parentId is not None:
                    oemData["Location"]["ParentId"]=parentId 
                if "Oem" not in responseData2:
                    responseData2["Oem"]={}
                responseData2["Oem"]["Intel_RackScale"] = oemData


        # build the navigation properties under Links : "Contains", "ContainedBy", ManagersIn...
        responseData2["Links"]={}
        for navProp in linkNavProperties:
            if navProp in self.chassisDb[chassisid]:
                #first do single entry nav properties
                if( navProp == "ContainedBy" ):
                    member= { "@odata.id": basePath + self.chassisDb[chassisid][navProp] }
                    responseData2["Links"][navProp] = member
                #otherwise, handle an array or list of nav properties
                else: 
                    if( (navProp == "ManagedBy") or (navProp == "ManagersInChassis") ):
                        linkBasePath="/redfish/v1/Managers/"
                    elif( navProp == "ComputerSystems") :
                        linkBasePath="/redfish/v1/Systems/"
                    else: # it is the /redfishg/v1/Chassis/
                        #linkBasePath=basePath
                        linkBasePath="/redfish/v1/Chassis/"

                    #start with an empty array
                    members = list()
                    # now create the array of members for this navProp
                    for memberId in self.chassisDb[chassisid][navProp]:
                        newMember= { "@odata.id": linkBasePath + memberId }
                        #members = members + newMember
                        members.append(newMember)
                    # now add the members array to the response data
                    responseData2["Links"][navProp] = members

        # convert to json
        respData2=(json.dumps(responseData2,indent=4))

        return(0, 200, "SUCCESS", respData2, None)



    def patchChassisEntry(self,chassisid, patchData):
        # verify that the chassisid is valid
        if chassisid not in self.chassisDb:
            return(404, "Not Found","","")

        #define the patchable properties in Chassis Resource
        patchableInRedfish=["AssetTag","IndicatorLed"]

        #first verify client didn't send us a property we cant patch based on Redfish Schemas
        for prop in patchData:
            if prop not in patchableInRedfish: 
                return(500, "Bad Request","Property: {} not patachable per Redfish Spec".format(prop),"")

        #second check if this instance of chassis allows the patch data to be patched
        #  if there is no Patchable property in chassisDb, then nothing is patchable
        if "Patchable" not in self.chassisDb[chassisid]:
            return(500, "Bad Request","Resource is not patachable","")

        # check if the specific property is patchable
        for prop in patchData:
            if prop not in self.chassisDb[chassisid]["Patchable"]:
                return(500, "Bad Request","Property: {} not patachable for this resource".format(prop),"")

        # now patch the valid properties sent
        for prop in patchData:
            if prop in self.chassisVolatileDict[chassisid]:
                self.chassisVolatileDict[chassisid][prop]=patchData[prop]
                if "PendingUpdate" not in self.chassisVolatileDict[chassisid]:
                    self.chassisVolatileDict[chassisid]["PendingUpdate"]=[]
                if prop not in self.chassisVolatileDict[chassisid]["PendingUpdate"]:
                    self.chassisVolatileDict[chassisid]["PendingUpdate"].append(prop)
                #xg JOB  setChassisProperty(chassisid, prop, "Volatile", patchData[prop])

            elif prop in self.chassisDb[chassisid]:
                self.chassisDb[chassisid][prop]=patchData[prop]
                if "PendingUpdate" not in self.chassisDb[chassisid]:
                    self.chassisDb[chassisid]["PendingUpdate"]=[]
                if prop not in self.chassisDb[chassisid]["PendingUpdate"]:
                    self.chassisDb[chassisid]["PendingUpdate"].append(prop)
                #xg JOB  setChassisProperty(chassisid, prop, "NonVolatile", patchData[prop])

                self.updateStaticChassisDbFile( )

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
    # Usage example for chassisEntry:
    #    statusProps = getStatusProperties(statusSubProps, self.chassisDb[chassisid],self.chassisVolatileDict[chassisid]
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




    #xg77
    # Get Chassis Thermal 
    #  related structures
    #    self.fansDb
    #    self.tempSensorsDb
    #    self.fansVolatileDict[chassisid]
    #    self.tempSensorsVolatileDict[chassisid]
    def getChassisEntryThermal(self, chassisid):
        # verify that the chassisid is valid
        if chassisid not in self.chassisDb:
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

        # set temperature array variables to build response from
        temperatureStaticProperties=["Name", "SensorNumber", "UpperThresholdNonCritical", "UpperThresholdCritical", 
             "UpperThresholdFatal", "LowerThresholdNonCritical", "LowerThresholdCritical", "LowerThresholdFatal", 
             "MinReadingRangeTemp", "MaxReadingRangeTemp", "PhysicalContext"  ]
        temperatureVolatileProperties=["ReadingCelsius" ]
        temperatureNonVolatileProperties=[]
        temperatureStatusSubProperties=["State", "Health"]

        # Add temperature sensors
        # if temperatureSensors in this chassis, add them
        if chassisid in self.tempSensorsDb:
            # set the base static properties that were assigned when the resource was created
            temperatureArray=list()
            for sensorId in self.tempSensorsDb[chassisid]["Id"]:   # sensors "0", "1", ...
                sensorData={}

                # add the required Id and MemberId properties
                sensorData["@odata.id"] = basePath + chassisid + "/Thermal#/Temperatures/" + sensorId
                sensorData["MemberId"]  = sensorId

                # add the static properties
                for prop in temperatureStaticProperties:
                    if prop in self.tempSensorsDb[chassisid]["Id"][sensorId]:
                        sensorData[prop] = self.tempSensorsDb[chassisid]["Id"][sensorId][prop]

                # add the non-volatile properties -- xg currently empty for G5
                for prop in temperatureNonVolatileProperties:
                    if prop in self.tempSensorsDb[chassisid]["Id"][sensorId]:
                        sensorData[prop] = self.tempSensorsDb[chassisid]["Id"][sensorId][prop]

                # add the volatile properties that were assigned when the resource was created
                volatileProps = self.getVolatileProperties(temperatureVolatileProperties, "Id", sensorId,
                                      self.tempSensorsDb[chassisid], self.tempSensorsVolatileDict[chassisid])
                for prop in volatileProps:
                    sensorData[prop] = volatileProps[prop]

                # add the status properties 
                statusProps = self.getStatusProperties(temperatureStatusSubProperties, "Id", sensorId,
                                      self.tempSensorsDb[chassisid],
                                      self.tempSensorsVolatileDict[chassisid])
                for prop in statusProps:
                    sensorData[prop] = statusProps[prop]

                # Add Temp Sensor related-items 
                # The service will create relatedItems entries pointing to the related chassis and system
                #  based on the AddRelatedItems property in the Temp Db entry
                if "AddRelatedItems" in self.tempSensorsDb[chassisid]["Id"][sensorId]:
                    relatedItemMembers=list()
                    if "Chassis" in self.tempSensorsDb[chassisid]["Id"][sensorId]["AddRelatedItems"]:
                        relatedItemMember = {"@odata.id": basePath + chassisid }
                        relatedItemMembers.append(relatedItemMember)
                    if "System" in self.tempSensorsDb[chassisid]["Id"][sensorId]["AddRelatedItems"]:
                        sysid=self.chassisDb[chassisid]["ComputerSystems"]
                        relatedItemMember = {"@odata.id": systemsBasePath + sysid[0] }
                        relatedItemMembers.append(relatedItemMember)
                        
                    # add the RelatedItem Property to the response
                    if( len(relatedItemMembers) > 0):
                        sensorData["RelatedItems"] = relatedItemMembers

                # add the Temperatures entry array to the Temperatures array
                temperatureArray.append(sensorData)

            # Add the new member to the Temperatures array
            if "Temperatures" not in responseData2:
                responseData2["Temperatures"]={}
            responseData2["Temperatures"] = temperatureArray

        # set fan array variables to build response from
        fansStaticProperties=["Name", "UpperThresholdNonCritical", "UpperThresholdCritical", "UpperThresholdFatal", 
             "LowerThresholdNonCritical", "LowerThresholdCritical", "LowerThresholdFatal", "MinReadingRange", 
             "MaxReadingRange", "PhysicalContext", "RelatedItem","Redundancy", "Manufacturer", "Model","SerialNumber",
             "PartNumber","SparePartNumber", "ReadingUnits" ]
        fansVolatileProperties=["Reading", "IndicatorLED" ]
        fansNonVolatileProperties=[]
        fansStatusSubProperties=["State", "Health"]

        # Create a resundancy set list to collect all of the fan redundancy group members for the fans
        redundancySetMembers=list()

        # add Fan Array properties
        if chassisid in self.fansDb:
            fanArray=list()
            # set the base static properties that were assigned when the resource was created
            for fanId in self.fansDb[chassisid]["FanId"]:   # fan "0", "1", ...
                sensorData={}

                # add the required Id and MemberId properties
                sensorData["@odata.id"] = basePath + chassisid + "/Thermal#/Fans/" + fanId
                sensorData["MemberId"]  = fanId

                # add the static properties
                for prop in fansStaticProperties:
                    if prop in self.fansDb[chassisid]["FanId"][fanId]:
                        sensorData[prop] = self.fansDb[chassisid]["FanId"][fanId][prop]

                # add the non-volatile properties -- initiall empty for G5
                for prop in fansNonVolatileProperties:
                    if prop in self.fansDb[chassisid]["FanId"][fanId]:
                        sensorData[prop] = self.fansDb[chassisid]["FanId"][fanId][prop]

                # add the volatile properties that were assigned when the resource was created
                volatileProps = self.getVolatileProperties(fansVolatileProperties, "FanId", fanId,
                                      self.fansDb[chassisid],
                                      self.fansVolatileDict[chassisid])
                for prop in volatileProps:
                    sensorData[prop] = volatileProps[prop]

                # add the status properties 
                statusProps = self.getStatusProperties(fansStatusSubProperties, "FanId", fanId,
                                      self.fansDb[chassisid],
                                      self.fansVolatileDict[chassisid])
                for prop in statusProps:
                    sensorData[prop] = statusProps[prop]

                # add fan self-generated properties 
                #  set depricated property FanName = same value as Name
                if "Name" in sensorData:
                    sensorData["FanName"]=sensorData["Name"]

                # Add Fan entry Redundancy information
                #  if the Fan entry in the fan database has a "RedundancyGroup" property,
                #  then the service will create one Redundancy member for the fan
                #  This member will point to a single redundancy group 
                if "RedundancyGroup" in self.fansDb[chassisid]["FanId"][fanId]:
                    redundancyGroup = self.fansDb[chassisid]["FanId"][fanId]["RedundancyGroup"]
                    # create the redundancy group member 
                    redundancyMember    = {"@odata.id": basePath + chassisid + "/Thermal#/Redundancy/" + redundancyGroup }
                    redundancySetMember = {"@odata.id": basePath + chassisid + "/Thermal#/Fans/" + fanId }

                    # add the member to the Redundancy array for this fan 
                    # note that the service only supports one redundancy group per fan
                    redundancyMembers=list()
                    redundancyMembers.append(redundancyMember)
                        
                    # add redundancyMembers to the fan data
                    sensorData["Redundancy"] = redundancyMembers

                    # Finally, add the redundancy group to the redundancySet array 
                    redundancySetMembers.append(redundancySetMember)

                fanArray.append(sensorData)

            # Add the new member to the Fan array
            if "Fans" not in responseData2:
                responseData2["Fans"]={}
            responseData2["Fans"] = fanArray

        # Add the redundancy group information
        #  remember we had earlier in the function created a redundancySetMembers=list()
        #  if this has any redundancy groups in it, we create the redundancy property
        if chassisid in self.fansDb:
            #if we collected any redundancy groups when building the Fans array, 
            # and we have a redundancy entry in the fan db entry for the chassis, then create the redundancy entry
            if( (len(redundancySetMembers) > 0) and ("RedundancyGroup" in self.fansDb[chassisid]) ):
                # define the list of redundancy properties
                redundancyProperties=["Name", "Mode", "MinNumNeeded", "MaxNumSupported"]
                fansRedundancyStatusSubProperties=["State", "Health"]

                redundancyArray=list()
                # set the base static properties for this redundancy group
                for redundancyGroup in self.fansDb[chassisid]["RedundancyGroup"]:
                    sensorData={}

                    # add the required Id and MemberId properties
                    sensorData["@odata.id"] = basePath + chassisid + "/Thermal#/Redundancy/" + redundancyGroup
                    sensorData["MemberId"]  = redundancyGroup
 
                    # add the standard redundancyProperty Properties that this service uses
                    for prop in redundancyProperties:
                        if prop in self.fansDb[chassisid]["RedundancyGroup"][redundancyGroup]:
                            sensorData[prop] = self.fansDb[chassisid]["RedundancyGroup"][redundancyGroup][prop]

                    # add the RedundancySet property
                    # note that when we created the fan entries, we built the redundancySetMembers array
                    # so all we have to do is add it to the property
                    sensorData["RedundancySet"] = redundancySetMembers

                    # add status to the redundancy array
                    # add the status properties 
                    statusProps = self.getStatusProperties(fansRedundancyStatusSubProperties, "RedundancyGroup", 
                                       redundancyGroup, self.fansDb[chassisid], self.fansVolatileDict[chassisid])
                    for prop in statusProps:
                        sensorData[prop] = statusProps[prop]

                redundancyArray.append(sensorData)

                # Add the new member to the Redundancy array
                if "Redundancy" not in responseData2:
                    responseData2["Redundancy"]={}
                responseData2["Redundancy"] = redundancyArray

        # completed creating response Data in responseData2 dict

        # convert to json
        respData2=(json.dumps(responseData2,indent=4))

        return(0, 200, "SUCCESS", respData2, None)


    #xg88
    # Get Chassis Power 
    #  related structures
    #    self.powerSuppliesDb   from .../chassisDb/PowerSuppliesDb.json
    #    self.voltageSensorsDb  from .../chassisDb/VoltageSensorsDb.json
    #    self.powerControlDb    from .../chassisDb/PowerControlDb.json
    #    self.powerSuppliesVolatileDict
    #    self.voltageSensorsVolatileDict
    #    self.powerControlVolatileDict

    def getChassisEntryPower(self, chassisid):
        # verify that the chassisid is valid
        if chassisid not in self.chassisDb:
                return(404, "Not Found","","")

        if not "BaseNavigationProperties" in self.chassisDb[chassisid]:
                return(404, "Not Found","","")

        if not "Power" in self.chassisDb[chassisid]["BaseNavigationProperties"]:
                return(404, "Not Found","","")

        # first just copy the template resource
        responseData2=dict(self.chassisPowerTemplate) 

        # setup some variables to build response from
        basePath="/redfish/v1/Chassis/"
        systemsBasePath="/redfish/v1/Systems/"

        # assign the required top-level properties
        responseData2["@odata.id"] = basePath + chassisid + "/Power"
        responseData2["Id"] = "Power"
        responseData2["Name"] = "Power"

        # set Voltages array variables to build response from
        voltagesStaticProperties=["Name", "SensorNumber", "UpperThresholdNonCritical", "UpperThresholdCritical", 
             "UpperThresholdFatal", "LowerThresholdNonCritical", "LowerThresholdCritical", "LowerThresholdFatal", 
             "MinReadingRange", "MaxReadingRange", "PhysicalContext"  ]
        voltagesVolatileProperties=["ReadingVolts" ]
        voltagesNonVolatileProperties=[]
        voltagesStatusSubProperties=["State", "Health"]

        # Add voltage sensors
        # if voltageSensors in this chassis, add them
        if chassisid in self.voltageSensorsDb:
            # set the base static properties that were assigned when the resource was created
            voltagesArray=list()
            for sensorId in self.voltageSensorsDb[chassisid]["Id"]:   # sensors "0", "1", ...
                sensorData={}

                # add the required Id and MemberId properties
                sensorData["@odata.id"] = basePath + chassisid + "/Power#/Voltages/" + sensorId
                sensorData["MemberId"]  = sensorId

                # add the static properties
                for prop in voltagesStaticProperties:
                    if prop in self.voltageSensorsDb[chassisid]["Id"][sensorId]:
                        sensorData[prop] = self.voltageSensorsDb[chassisid]["Id"][sensorId][prop]

                # add the non-volatile properties -- xg currently empty for G5
                for prop in voltagesNonVolatileProperties:
                    if prop in self.voltageSensorsDb[chassisid]["Id"][sensorId]:
                        sensorData[prop] = self.voltageSensorsDb[chassisid]["Id"][sensorId][prop]

                # add the volatile properties that were assigned when the resource was created
                volatileProps = self.getVolatileProperties(voltagesVolatileProperties, "Id", sensorId,
                                self.voltageSensorsDb[chassisid], self.voltageSensorsVolatileDict[chassisid])
                for prop in volatileProps:
                    sensorData[prop] = volatileProps[prop]

                # add the status properties 
                statusProps = self.getStatusProperties(voltagesStatusSubProperties, "Id", sensorId,
                                      self.voltageSensorsDb[chassisid],
                                      self.voltageSensorsVolatileDict[chassisid])
                for prop in statusProps:
                    sensorData[prop] = statusProps[prop]

                # Add Voltage Sensor related-items 
                # if the chassis is above sled level, no related item
                if "AddRelatedItems" in self.voltageSensorsDb[chassisid]["Id"][sensorId]:
                    relatedItemMembers=list()
                    if "Chassis" in self.voltageSensorsDb[chassisid]["Id"][sensorId]["AddRelatedItems"]:
                        relatedItemMember = {"@odata.id": basePath + chassisid }
                        relatedItemMembers.append(relatedItemMember)
                    if "G5Blocks" in self.voltageSensorsDb[chassisid]["Id"][sensorId]["AddRelatedItems"]:
                        for chas in self.chassisDb:
                            if self.g5utils.isBlock(chas) is True:
                                relatedItemMember = {"@odata.id": basePath + chas}
                                relatedItemMembers.append(relatedItemMember)
                    if "G5PowerBays" in self.voltageSensorsDb[chassisid]["Id"][sensorId]["AddRelatedItems"]:
                        for chas in self.chassisDb:
                            if self.g5utils.isPowerBay(chas) is True:
                                relatedItemMember = {"@odata.id": basePath + chas}
                                relatedItemMembers.append(relatedItemMember)
                        
                    # add the RelatedItem Property to the response
                    if( len(relatedItemMembers) > 0):
                        sensorData["RelatedItems"] = relatedItemMembers

                # add the Voltages entry array to the voltage array
                voltagesArray.append(sensorData)

            # Add the new member to the Voltages array
            if "Voltages" not in responseData2:
                responseData2["Voltages"]={}
            responseData2["Voltages"] = voltagesArray



        # Add the PowerControl array
        #  Note: This initial service implementation only supports what G5 currently uses.
        #        The only properties supported are: static Name, and volatile PowerConsumedWatts
        #        Status is statically assigned Enabled, OK
        #   related structures:
        #      self.powerControlDb    from file: .../chassisDb/ PowerControlDb.json
        #      self.powerControlVolatileDict

        # set PowerControl array variables to build response from
        powerControlStaticProperties=["Name" ]
        powerControlStatusSubProperties=["State", "Health"]
        powerControlVolatileProperties=[ "PowerConsumedWatts" ]

        # add the powerControl members to the array
        if chassisid in self.powerControlDb:

            powerControlArray=list()
            for powerControlId  in self.powerControlDb[chassisid]["Id"]:
                sensorData={}

                # add the required Id and MemberId properties
                sensorData["@odata.id"] = basePath + chassisid + "/Power#/PowerControl/" + powerControlId
                sensorData["MemberId"]  = powerControlId
 
                # add the standard static Properties that this service uses
                for prop in powerControlStaticProperties:
                    if prop in self.powerControlDb[chassisid]["Id"][powerControlId]:
                        sensorData[prop] = self.powerControlDb[chassisid]["Id"][powerControlId][prop]

                # add the volatile Properties that this service uses
                #for prop in powerControlVolatileProperties:
                #    if prop in self.powerControlDb[chassisid]["Id"][powerControlId]["Volatile"]:
                #        sensorData[prop] = self.powerControlVolatileDict[chassisid]["Id"][powerControlId][prop]


                # add the volatile properties that were assigned when the resource was created
                volatileProps = self.getVolatileProperties(powerControlVolatileProperties, "Id", powerControlId,
                                self.powerControlDb[chassisid], self.powerControlVolatileDict[chassisid])
                for prop in volatileProps:
                    sensorData[prop] = volatileProps[prop]

                # add status to the redundancy array
                # add the status properties 
                statusProps = self.getStatusProperties(powerControlStatusSubProperties, "Id", powerControlId, 
                              self.powerControlDb[chassisid], self.powerControlVolatileDict[chassisid])
                for prop in statusProps:
                    sensorData[prop] = statusProps[prop]

                powerControlArray.append(sensorData)

            # Add the new member to the Redundancy array
            if "PowerControl" not in responseData2:
                responseData2["PowerControl"]={}
            responseData2["PowerControl"] = powerControlArray



        # Add PowerSupplies array
        #
        # first: setup PowerSupply array variables to build response from
        psusStaticProperties=["Name", "PowerSupplyType", "LineInputVoltageType", 
             "PowerCapacityWatts", "Manufacturer", "Model","SerialNumber","FirmwareVersion", 
             "PartNumber","SparePartNumber"  ]
        #xg-Note: Service does not support the powerSupply InputRanges array 
        #xg   add InputRange complexType to the db and add separate pseInputRangeStaticProperties 
        psusVolatileProperties=["LineInputVoltage", "LastPowerOutputWatts", "IndicatorLED" ]
        psusNonVolatileProperties=[]
        psusStatusSubProperties=["State", "Health"]

        # Create a resundancy set list to collect all of the PowerSupply redundancy group members 
        redundancySetMembers=list()

        # add PowerSupply Array properties
        if chassisid in self.powerSuppliesDb:
            psusArray=list()
            # set the base static properties that were assigned when the resource was created
            for psuId in self.powerSuppliesDb[chassisid]["Id"]:   # powerSupply "0", "1", ...
                sensorData={}

                # add the required Id and MemberId properties
                sensorData["@odata.id"] = basePath + chassisid + "/Power#/PowerSupplies/" + psuId
                sensorData["MemberId"]  = psuId

                # add the static properties
                for prop in psusStaticProperties:
                    if prop in self.powerSuppliesDb[chassisid]["Id"][psuId]:
                        sensorData[prop] = self.powerSuppliesDb[chassisid]["Id"][psuId][prop]

                # add the non-volatile properties -- initiall empty for G5
                for prop in psusNonVolatileProperties:
                    if prop in self.powerSuppliesDb[chassisid]["Id"][psuId]:
                        sensorData[prop] = self.powerSuppliesDb[chassisid]["Id"][psuId][prop]

                # add the volatile properties that were assigned when the resource was created
                volatileProps = self.getVolatileProperties(psusVolatileProperties, "Id", psuId,
                                      self.powerSuppliesDb[chassisid],
                                      self.powerSuppliesVolatileDict[chassisid])
                for prop in volatileProps:
                    sensorData[prop] = volatileProps[prop]

                # add the status properties 
                statusProps = self.getStatusProperties(psusStatusSubProperties, "Id", psuId,
                                      self.powerSuppliesDb[chassisid],
                                      self.powerSuppliesVolatileDict[chassisid])
                for prop in statusProps:
                    sensorData[prop] = statusProps[prop]

                # Add PowerSupply Redundancy information
                #  if the PowerSupply entry in the PowerSupply database has a "RedundancyGroup" property,
                #  then the service will create one Redundancy member for the PowerSupply
                #  This member will point to a single redundancy group 
                if "RedundancyGroup" in self.powerSuppliesDb[chassisid]["Id"][psuId]:
                    redundancyGroup = self.powerSuppliesDb[chassisid]["Id"][psuId]["RedundancyGroup"]
                    # create the redundancy group member 
                    redundancyMember    = {"@odata.id": basePath + chassisid + "/Power#/Redundancy/" + redundancyGroup }
                    redundancySetMember = {"@odata.id": basePath + chassisid + "/Power#/PowerSupplies/" + psuId }

                    # add the member to the Redundancy array for this powerSupply 
                    # note that the service only supports one redundancy group per powerSupply
                    redundancyMembers=list()
                    redundancyMembers.append(redundancyMember)
                        
                    # add redundancyMembers to the powerSupply data
                    sensorData["Redundancy"] = redundancyMembers

                    # Finally, add the redundancy group to the redundancySet array 
                    redundancySetMembers.append(redundancySetMember)

                psusArray.append(sensorData)

            # Add the new member to the PowerSupplies (psus) array
            if "PowerSupplies" not in responseData2:
                responseData2["PowerSupplies"]={}
            responseData2["PowerSupplies"] = psusArray

        # Add the redundancy group information
        #  remember we had earlier in the function created a redundancySetMembers=list()
        #  if this has any redundancy groups in it, we create the redundancy property
        if chassisid in self.powerSuppliesDb:
            #if we collected any redundancy groups when building the PowerSupplies array, 
            # and we have a redundancy entry in the PowerSupplies db entry for the chassis, then create the redundancy entry
            if( (len(redundancySetMembers) > 0) and ("RedundancyGroup" in self.powerSuppliesDb[chassisid]) ):
                # define the list of redundancy properties
                redundancyProperties=["Name", "Mode", "MinNumNeeded", "MaxNumSupported"]
                psusRedundancyStatusSubProperties=["State", "Health"]

                redundancyArray=list()
                # set the base static properties for this redundancy group
                for redundancyGroup in self.powerSuppliesDb[chassisid]["RedundancyGroup"]:
                    sensorData={}

                    # add the required Id and MemberId properties
                    sensorData["@odata.id"] = basePath + chassisid + "/Power#/Redundancy/" + redundancyGroup
                    sensorData["MemberId"]  = redundancyGroup
 
                    # add the standard redundancyProperty Properties that this service uses
                    for prop in redundancyProperties:
                        if prop in self.powerSuppliesDb[chassisid]["RedundancyGroup"][redundancyGroup]:
                            sensorData[prop] = self.powerSuppliesDb[chassisid]["RedundancyGroup"][redundancyGroup][prop]

                    # add the RedundancySet property
                    # note that when we created the fan entries, we built the redundancySetMembers array
                    # so all we have to do is add it to the property
                    sensorData["RedundancySet"] = redundancySetMembers

                    # add status to the redundancy array
                    # add the status properties 
                    statusProps = self.getStatusProperties(psusRedundancyStatusSubProperties, "RedundancyGroup", 
                                  redundancyGroup, self.powerSuppliesDb[chassisid], self.fansVolatileDict[chassisid])
                    for prop in statusProps:
                        sensorData[prop] = statusProps[prop]

                redundancyArray.append(sensorData)

                # Add the new member to the Redundancy array
                if "Redundancy" not in responseData2:
                    responseData2["Redundancy"]={}
                responseData2["Redundancy"] = redundancyArray

        # completed creating response Data in responseData2 dict

        # convert to json
        respData2=(json.dumps(responseData2,indent=4))

        return(0, 200, "SUCCESS", respData2, None)


    '''
    THIS API NOT SUPPORTED CURRENTLY ON G5
          
    def patchPowerResource(self,patchData):
        #first verify client didn't send us a property we cant patch
        # ACTUALLY, the PATCHABLE DATA IS A FUNCTION OF WHICH CHASSIS IT IS
        # THE BELOW CODE IS FOR A SLED
        for key in patchData:
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
        
    '''

'''
DO:
1. sls spec to
   a) put mgt netwokr info in ChassisEntry
   b) put jbod parent/child info in chassisEntry
   c) put lastboottime in node
   d) put inserttime in chassisEntry?
2. rackscale change to
   a) josh CA spec
   b) PUID in rack chassis
   
3. we will
   a) get fanSpeed from iDrac
   b) get powerSupplies from MC
   c) DONE move to cellery new scheduler
   d) get mockups of MC and iDrac
   e) cache idrac data
   f) mem,proc,necs every 2 min.   HDs every 20sec
   g) update caches at boot or insert/discovery
   h) run disc from rootservice, 
      x) note we can derive everything in sled except mgtNetwork, jbod info
   i) get led and powerstate from iDrac for chassis

'''
