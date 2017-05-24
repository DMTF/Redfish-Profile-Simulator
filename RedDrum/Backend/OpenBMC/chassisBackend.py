# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

# BullRed-RackManager chassisBackend resources
#
class  RdChassisBackend():
    # class for backend chassis resource APIs
    def __init__(self,rdr):
        self.version=1

    # **** Backend PULL APIs   from Frontend RedfishService ****
    #
    # GET volatile chassis info for this chassis
    def getVolatileChassisInfo(self,rdr,chassisid):
        #for this chasssis:
        resp=dict()
        resp["IndicatorLED"]="Blinking"                 # ledstate
        resp["PowerState"]="Off"                        # powerstate
        resp["Status"]={"State": "Enabled", "Health": "OK"} #status
        nonVolatileDataChanged=False
        rc=0     # 0=ok
        return(rc,resp,nonVolatileDataChanged)

    def getStaticDiscoveryChassisInfo(self,rdr,chassisid):
        # for this chassis,
        resp=dict()
        resp["Manufacturer"]="IBM9"
        resp["Model"]="Power9MB"
        resp["SKU"]="1009"
        resp["SerialNumber"]="999999"
        resp["PartNumber"]="Power999"
        rc=0     # 0=ok
        return(rc,resp,nonVolatileDataChanged)

    # *****  read non-volatile data  *****
    # normally, the backend will push this if changes due to non-Redfish interface
    # but implementing a get for debug and case where backend can push
    def getNonVolatileChassisInfo(self,rdr,chassisid):
        resp=dict()
        #get assetTag()
        resp["AssetTag"]="ASSET9"
        rc=0 #     0=ok
        return(rc,resp)


    # GET volatile Power Supplies readings
    def getVolatilePowerSupplyReadings(self,rdr,chassisid,psuidlist):
        # return a dict of powerSupplyIds: reading/status eg:
        #   { "0": {"LineInputVoltage:240, LastPowerOutputWatts": 2000, Status: {...} },
        #     "1": {"LineInputVoltage:242, LastPowerOutputWatts": 1000, Status: {...} } }
        # for each PowerSupplyId in chassis, 
        resp=dict()
        for psu in psuidlist:
            memberData={} # empty dict
            memberData["LineInputVoltage"]=299
            memberData["LastPowerOutputWatts"]=2099
            memberData["Status"]={"State": "Enabled", "Health": "OK"}
            resp[psu]=memberData
 
        rc=0     # 0=ok
        return(rc,resp)

    # GET volatile Fan readings
    def getVolatileFanReadings(self,rdr,chassisid,fanidlist):
        # return dict of Fan readings and status
        #   { "0": {"Reading:2403, Status: {...} },
        #     "1": {"Reading:2533, Status: {...} } }
        # for each Fanid in chassis, add entry with reading and status
        resp=dict()
        for fanid in fanidlist:
            memberData={} # empty dict
            memberData["Reading"]=2399
            memberData["Status"]={"State": "Enabled", "Health": "OK"}
            resp[fanid]=memberData
        rc=0     # 0=ok
        return(rc,resp)

    # GET volatile TemperatureSensor readings
    def getVolatileTempSensorReadings(self,rdr,tempSensorsList):
        # return dict of Temperature Sensor readings and status
        #   { "0": {"ReadingCelsius:37, Status: {...} },
        #     "1": {"ReadingCelsius:38, Status: {...} } }
        # for each TemperatureSensor in chassis, add entry with reading and status
        resp=dict()
        for tempSensor in tempSensorsList:
            memberData={} # empty dict
            memberData["ReadingCelsius"]=99
            memberData["Status"]={"State": "Enabled", "Health": "OK"}
            resp[tempSensor]=memberData
        rc=0     # 0=ok
        return(rc,resp)

    # GET volatile VoltageSensor readings
    def getVolatileVoltageSensorReadings(self,rdr,voltageSensorsList):
        # return dict of VoltageSensor readings and status
        #   { "0": {"ReadingVolts:241, Status: {...} },
        #     "1": {"ReadingVolts:12, Status: {...} } }
        # for each VoltageSensor in chassis, add entry with reading and status
        resp=dict()
        for voltSensor in voltageSensorsList:
            memberData={} # empty dict
            memberData["ReadingVolts"]=249
            memberData["Status"]={"State": "Enabled", "Health": "OK"}
            resp[voltSensor]=memberData
        rc=0     # 0=ok
        return(rc,resp)

    # GET volatile PowerControl readings
    # is is power draw, and power limit settings
    def getVolatilePowerControlReadings(self,rdr,powerControlList):
        # return dict of PowerControl readings and status
        #   { "0": {"PowerConsumedWatts": 1109, Status: {...} },
        #     "1": {"PowerConsumedWatts": 1108, Status: {...} } }
        # for each PowerControl in chassis, add entry with reading and status
        # normally there is one powerControl
        resp=dict()
        for powerControlId in powerControlList:
            memberData={} # empty dict
            memberData["PowerConsumedWatts"]=1199
            resp[powerControlId]=memberData
        rc=0     # 0=ok
        return(rc,resp)

    # DO Reset Action:  
    def doChassisReset(self,rdr,chassisid,resetType):
        if( resetType == "On"):
            # do powerOn - if powerstate is off, push power button
            # the service should have already verified power is off to get here
            print("BACKEND: Power-on")
            pass
        elif( resetType == "ForceOff"):
            # do Hard Poweroff - eg hold power button down for 6 sec in a thread
            print("BACKEND: Force-off")
            pass
        elif( resetType == "ForceRestart"):
            # do Hard powerOff, then powerOn - 
            #    - hold power button down 6 sec, then after powerOff, push button for .5 sec to turn-on
            print("BACKEND: Force Restart")
            pass
        elif( resetType == "GracefulShutdown"):
            # do ACPI shutdown - if system is now on, press power button for .5 sec
            print("BACKEND: Graceful shutdown ")
            pass
        elif( resetType == "GracefulRestart"):
            # do gracefulShutdown, then press power button to turn back on
            print("BACKEND: Graceful Restart")
            pass
        else:
            return(9)    # invalid request
        rc=0  #0=ok
        return(rc)

    # SET LED state
    def doSetLed(self,rdr,chassisid,ledState):
        # set indicator LED  Lit, Blinking, or Off
        storedaVal=ledState
        rc=0  #0=ok
        return(rc, storedVal)

    # SET asset Tag
    def doSetAssetTag(self,rdr,chassisid,assetTagVal):
        # This is non-volatile data so generally the backend will push any changes
        storedaVal=assetTagVal
        rc=0  #0=ok
        return(rc, storedVal)

    '''
    # SET Power Limit
    # powerLimit is the limit in watts.  Null=disable
    # exception is what to do if power cannot be held below limit:  0=noAction, 1=powerOff, 2=logError
    def doSetPowerLimit(self,rdr,chassisid,PowerControlIndex,powerLimit,exception):
        storedaVal=ledState
        rc=0  #0=ok
        return(rc, storedVal)
    '''

    # ***** generate etag hash of NonVolatile data ************88
    def calculateNonVolatilesEtag(self,rdr):
        # nonvolatile chassis data is AssetTag, so hash is the tag itself
        #get assetTag()
        assetTag="EXAMPLE_ASSET_TAG"
        return(assetTag)


    # these not implemented in front-end yet

    # ***** non-volatile set etags APIs  from Front-End RedfishService ************

    '''
    # the backend saves the etags of non-volatile data cache in front-end
    # if the non-volatile data changes, then it should Push the change to the front-end,
    # or set the nonVolatileDataChanged flag so that on next get, the front-end will know to get it
    def setNonVolatileChassisInfoEtag(self,rdr,chassisid,etag):
        #save etag to detect if data changed
        rc=0 #     0=ok
        return(rc)

    # set non-volatile data etags
    # the backend saves this and knows if etag has changed thus needing to update 
    def setNonVolatilePowerSupplyInfoEtag(self,rdr,chassisid,etag):
        #save etag to detect if data changed
        rc=0 #     0=ok
        return(rc)

    # set non-volatile data etags
    # the backend saves this and knows if etag has changed thus needing to update 
    def setNonVolatileFanInfoEtag(self,rdr,chassisid,etag):
        #save etag to detect if data changed
        rc=0 #     0=ok
        return(rc)

    '''




