
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

import os
import json
import sys
#from .rootData import RfRoot
from .G5McUtils import RfG5IdUtils


#xg88-here
#xg88-working-to-here

class RfManagersResource():       
    # Class for all resources under /redfish/v1/Managers
    # Note that this resource was created in serviceRoot for the Managers Resource.
    def __init__(self,rfr ):
        self.loadResourceTemplates(rfr )
        self.loadManagersDbFiles(rfr)
        self.initializeManagersVolatileDict(rfr)
        self.g5utils=RfG5IdUtils()
        self.managersDbDiscovered=None
        self.magic="123456"

    def loadResourceTemplates( self, rfr ):
        # these are very bare-bones templates but we want to be able to update the resource version or context easily
        #   so the approach is to always start with a standard template for each resource type

        #load ManagersCollection Template
        self.managersCollectionTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates","ManagersCollection.json")

        #load ManagerEntry Template
        self.managerEntryTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates","ManagerEntry.json")

        #load ManagerNetworkProptocol Template
        #xg TODO

        #load ManagerEthernetInterfaceCollection Template
        #xg TODO
        #load ManagerEthernetInterface  Template
        #xg TODO

        #load ManagerSerialInterfaceCollection  Template
        #xg TODO
        #load ManagerSerialInterface Template
        #xg TODO


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
            print("*****ERROR: Manager Resource: Json Data file:{} Does not exist. Exiting.".format(filePath))
            sys.exit(10)

    def loadManagersDbFiles(self,rfr ):
        # if rfr.useCachedDiscoveryDb is True:
        #   then if the managers database files exist in /var/www/rf/managersDb/* then load them to in-memory dict
        #        else if rfr.resourceDiscovery=static, read static db files and save to the cache
        #        else,  kick-off job to discover the managers data from the MC
        # else, always run full discovery each time RM Redfish Service starts
        self.managersDbDiscovered=False
        if rfr.useCachedDiscoveryDb is True:
            # first make sure all of the manager DB files exist
            managersDbCacheExists=True
            managersDbFiles=["ManagersDb.json" ]
            for filenm in managersDbFiles:
                managersDbFilePath=os.path.join(rfr.varDataPath,"managersDb", filenm)
                if not os.path.isfile(managersDbFilePath):
                    managersDbCacheExists = False
                    break
            # then load them into dictionaries
            if managersDbCacheExists is True:
                self.managersDb=self.loadManagerDbFile(rfr.varDataPath, "managersDb", "ManagersDb.json") 


        # if self.managersDbDiscovery is false because either: 1) useCachedDiscovery is false or 2) no db cache exists
        # then if rfr.resourceDiscovery = Static, load the static db
        # otherwise leave self.managersDiscover set false and the root service will initiate the system discovery
        #    after chassis, manager, and system resources have all be created
        if self.managersDbDiscovered is False:
            if (rfr.resourceDiscovery == "Static" ):
                cfg=rfr.staticChassisConfig  #xg9-varName staticManagersConfig?
                self.managersDb=self.loadStaticManagersDbFile(rfr, "managersDb", cfg, "ManagersDb.json") 
                self.managersDbDiscovered=True

            elif (rfr.resourceDiscovery == "G5dynamic" ):
                self.managersDbDiscovered=False
                # the service root needs to run the discovery function

        return(0)

    # worker function to load CACHED manager db file into dict
    def loadManagerDbFile( self, dataPath, subDir, filename ):
        filePath=os.path.join(dataPath, subDir, filename)
        if os.path.isfile(filePath):
            response=json.loads( open(filePath,"r").read() )
            return(response)
        else:
            print("*****ERROR: Manager Resource: Json Data file:{} Does not exist. Exiting.".format(filePath))
            sys.exit(10)

    # worker function to load STATIC manager db file into dict and write it back out to cached db file
    def loadStaticManagersDbFile( self, rfr, subDir, cfgDir, filename ):
        filePath=os.path.join(rfr.baseDataPath, "resourceStaticDb", cfgDir, subDir, filename)
        if os.path.isfile(filePath):
            response=json.loads( open(filePath,"r").read() )
            varDbFilePath=os.path.join(rfr.varDataPath, subDir, filename)
            responseJson=json.dumps(response,indent=4)
            with open( varDbFilePath, 'w', encoding='utf-8') as f:
                f.write(responseJson)
            return(response)
        else:
            print("*****ERROR: Managers Resource: Json Data file:{} Does not exist. Exiting.".format(filePath))
            sys.exit(10)


    # worker function to write the manager Db Dict back to the STATIC manager db file
    # used by patch
    def updateStaticManagersDbFile( self ):
        varDbFilePath=os.path.join(self.rfr.varDataPath, "managersDb", "ManagerDb.json")
        responseJson=json.dumps(self.managersDb, indent=4)
        with open( varDbFilePath, 'w', encoding='utf-8') as f:
            f.write(responseJson)
        return(0)


    def fullG5ManagersDiscovery(self,rfr):
        pass

    def initializeManagersVolatileDict(self,rfr):
        # this is the in-memory dict of volatile Managers properties
        self.managersVolatileDict=dict()   #create an empty dict of Managers entries

        # initialize the Volatile Dicts
        for managerid in self.managersDb:
            # inialize with empty members for all known manager
            self.managersVolatileDict[managerid]={}


    # GET MANAGERS COLLECTION
    def getManagersCollectionResource(self):
        # first copy the Managers Collection template 
        # then updates the Members array will each manager previously discovered--in ManagersDb 

        # copy the ManagersCollection template file (which has an empty roles array)
        responseData2=dict(self.managersCollectionTemplate)
        count=0
        # now walk through the entries in the managersDb and build the managersCollection Members array
        # note that the members array is an empty array in the template
        uriBase="/redfish/v1/Managers/"
        for managerid in self.managersDb:
            # increment members count, and create the member for the next entry
            count=count+1
            memberUri=uriBase + managerid
            newMember=[{"@odata.id": memberUri}]

            # add the new member to the members array we are building
            responseData2["Members"] = responseData2["Members"] + newMember

        # update the members count
        responseData2["Members@odata.count"]=count

        # convert to json
        respData2=(json.dumps(responseData2,indent=4))

        return(respData2)



    # GET MANAGER ENTRY
    def getManagerEntry(self, managerid):
        # verify that the managerid is valid
        if managerid not in self.managersDb:
                return(4, 404, "Not Found",None,None)

        # first just copy the template resource
        responseData2=dict(self.managerEntryTemplate)

        # setup some variables to build response from
        basePath="/redfish/v1/Managers/"
        staticProperties=["Name", "Description", "ManagerType", "ServiceEntryPointUUID", "UUID", "Model" ]
        volatileProperties=[ "IndicatorLED", "PowerState","DateTime","DateTimeLocalOffset"]
        nonVolatileProperties=[ "FirmwareVersion" ]
        #xg "ManagerInChassis": "Rack1-PowerBay1",
        baseNavProperties=["LogServices", "EthernetInterfaces", "SerialInterfaces","NetworkProtocol","VirtualMedia"]
        statusSubProperties=["State", "Health"]
        linkNavProperties=["ManagerForServers", "ManagerForChassis", "ManagerInChassis" ]

        serialConsoleSubProperties=["ServiceEnabled","MaxConcurrentSessions","ConnectTypesSupported"]
        graphicalConsoleSubProperties=["ServiceEnabled","MaxConcurrentSessions","ConnectTypesSupported"]
        commandShellSubProperties=["ServiceEnabled","MaxConcurrentSessions","ConnectTypesSupported"]

        # assign the required properties
        responseData2["@odata.id"] = basePath + managerid
        responseData2["Id"] = managerid

        # set the base static properties that were assigned when the resource was created
        for prop in staticProperties:
            if prop in self.managersDb[managerid]:
                responseData2[prop] = self.managersDb[managerid][prop]

        # get the base non-volatile properties that were assigned when the resource was created
        # these are stored in the persistent cache but are not static--ex is assetTag
        for prop in nonVolatileProperties:
            if prop in self.managersDb[managerid]:
                responseData2[prop] = self.managersDb[managerid][prop]

        # get the serialConsole  properties 
        if "SerialConsole" in self.managersDb[managerid]:
            for subProp in serialConsoleSubProperties:
                if subProp in self.managersDb[managerid]["SerialConsole"]:
                    if "SerialConsole" not in responseData2:
                        responseData2["SerialConsole"]={}
                    responseData2["SerialConsole"][subProp] = self.managersDb[managerid]["SerialConsole"][subProp]

        # get the graphicalConsole  properties 
        if "GraphicalConsole" in self.managersDb[managerid]:
            for subProp in serialConsoleSubProperties:
                if subProp in self.managersDb[managerid]["GraphicalConsole"]:
                    if "SerialConsole" not in responseData2:
                        responseData2["GraphicalConsole"]={}
                    responseData2["SerialConsole"][subProp] = self.managersDb[managerid]["GraphicalConsole"][subProp]

        # get the commandShel  properties 
        if "CommandShell" in self.managersDb[managerid]:
            for subProp in serialConsoleSubProperties:
                if subProp in self.managersDb[managerid]["CommandShell"]:
                    if "SerialConsole" not in responseData2:
                        responseData2["SerialConsole"]={}
                    responseData2["CommandShell"][subProp] = self.managersDb[managerid]["CommandShell"][subProp]

        # generate the realtime properties into the volatileDict if they are listed in volatiles in the db
        if "Volatiles" in self.managersDb[managerid]:
            if "DateTime" in self.managersDb[managerid]["Volatiles"]:
                # set the current dateTime into the dict
                managersVolatileDict["DateTime"]="11am"   # xg99
            if "DateTimeLocalOffset" in self.managersDb[managerid]["Volatiles"]:
                # calculate the value from the dateTime value
                # set the value into the dict
                managersVolatileDict["DateTime"]="-05:00"   # xg99

        # get the volatile properties eg powerState
        volatileProps = self.getVolatileProperties(volatileProperties, None, None,
                        self.managersDb[managerid], self.managersVolatileDict[managerid])
        for prop in volatileProps:
            responseData2[prop] = volatileProps[prop]


        # get the status properties
        statusProps = self.getStatusProperties(statusSubProperties, None, None,
                      self.managersDb[managerid], self.managersVolatileDict[managerid])
        for prop in statusProps:
            responseData2[prop] = statusProps[prop]


        # set the base navigation properties:   /redfish/v1/Managers/<baseNavProp>
        for prop in baseNavProperties:
            if "BaseNavigationProperties" in self.managersDb[managerid]:
                if prop in self.managersDb[managerid]["BaseNavigationProperties"]:
                    responseData2[prop] = { "@odata.id": basePath + managerid + "/" + prop }

        # build the Actions data
        if "ActionsResetAllowableValues" in self.managersDb[managerid]:
            resetAction = { "target": basePath + managerid + "/Actions/Manager.Reset",
                "ResetType@Redfish.AllowableValues": self.managersDb[managerid]["ActionsResetAllowableValues"] }
            if "Actions" not in responseData2:
                responseData2["Actions"]={}
            responseData2["Actions"]["#Manager.Reset"]= resetAction

        # build Dell OEM Section 
        if "OemDellG5MCMgrInfo" in self.managersDb[managerid]:
            # define the legal oem properties 
            oemDellG5NonVolatileProps = ["LastUpdateStatus","SafeBoot","OpenLookupTableVersion"]

            # check if  each of the legal oem subProps are in the db
            oemData={}
            for prop in oemDellG5NonVolatileProps:
                if prop in self.managersDb[managerid]["OemDellG5MCMgrInfo"]:
                    # since these sub-properties are nonVolatile, read them from the database
                    oemData[prop]=self.managersDb[managerid]["OemDellG5MCMgrInfo"][prop]

            if "Oem" not in responseData2:
                responseData2["Oem"]={}
            responseData2["Oem"]["Dell_G5MC"] = oemData

        # build the navigation properties under Links : "ManagerForChassis", "ManagerInChassis", ManagerForServers
        responseData2["Links"]={}
        for navProp in linkNavProperties:
            if navProp in self.managersDb[managerid]:
                #first do single entry nav properties
                if( navProp == "ManagerInChassis" ):
                    linkBasePath="/redfish/v1/Chassis/"
                    member= { "@odata.id": linkBasePath + self.managersDb[managerid][navProp] }
                    responseData2["Links"][navProp] = member
                #otherwise, handle an array or list of nav properties
                else: 
                    if( navProp == "ManagerForChassis" ):
                        linkBasePath="/redfish/v1/Chassis/"
                    elif( navProp == "ManagerForServers") :
                        linkBasePath="/redfish/v1/Systems/"
                    else: # unknown assume managers here
                        linkBasePath="/redfish/v1/Managers/"

                    #start with an empty array
                    members = list()
                    # now create the array of members for this navProp
                    for memberId in self.managersDb[managerid][navProp]:
                        newMember= { "@odata.id": linkBasePath + memberId }
                        members.append(newMember)
                    # now add the members array to the response data
                    responseData2["Links"][navProp] = members

        # convert to json
        respData2=(json.dumps(responseData2,indent=4))

        return(0, 200, "SUCCESS", respData2, None)



    def patchManagerEntry(self, managerid, patchData):
        # verify that the managerid is valid
        if managerid not in self.managersDb:
            return(404, "Not Found","","")

        # define the patchable properties in Manager Resource
        patchableInRedfishProperties=["DateTime","DateTimeOffset"]
        patchableInRedfishComplexTypeManagerService=["SerialConsole","CommandShell","GraphicalConsole"]
        patchableInRedfishComplexTypeManagerServiceSupProperty="ServiceEnabled" # only one property is patchable

        #first verify client didn't send us a property we cant patch based on Redfish Schemas
        for prop in patchData:
            if prop in patchableInRedfishComplexTypeManagerService:
                for subProp in prop:
                    if subProp != patchableInRedfishComplexTypeManagerServiceSubProperty:
                        return(500, "Bad Request","Property: {}, subProperty {} not patachable per Redfish Spec".format(
                              prop,subProp),"")
            elif prop not in patchableInRedfishProperties: 
                return(500, "Bad Request","Property: {} not patachable per Redfish Spec".format(prop),"")

        #second check if this instance of manager allows the patch data to be patched
        #  if there is no Patchable property in managersDb, then nothing is patchable
        if "Patchable" not in self.managersDb[managerid]:
            return(500, "Bad Request","Resource is not patachable","")

        # check if the specific property is patchable
        for prop in patchData:
            if prop not in self.managersDb[managerid]["Patchable"]:
                return(500, "Bad Request","Property: {} not patachable for this resource".format(prop),"")

        # now patch the valid properties sent
        for prop in patchData:
            if prop in self.managersVolatileDict[managerid]:
                self.managersVolatileDict[managerid][prop]=patchData[prop]
                if "PendingUpdate" not in self.managersVolatileDict[managerid]:
                    self.managersDb[managerid]["PendingUpdate"] = []
                if prop not in self.managersVolatileDict[managerid]["PendingUpdate"]:
                    self.managersVolatileDict[managerid]["Pending"].append(prop)
                #xg JOB  setManagerProperty(managerid, prop, "Volatile", patchData[prop])

            elif prop in self.managersDb[managerid]:
                self.managersDb[managerid][prop]=patchData[prop]
                if "PendingUpdate" not in self.managersDb[managerid]:
                    self.managersDb[managerid]["PendingUpdate"] = []
                if prop not in self.managersDb[managerid]["PendingUpdate"]:
                    self.managersDb[managerid]["Pending"].append(prop)
                #xg JOB  setManagerProperty(managerid, prop, "NonVolatile", patchData[prop])

                # update the cached managers db file
                self.updateStaticManagersDbFile()

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
                    # elif the prop was assigned a default value in Db, then use that
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



