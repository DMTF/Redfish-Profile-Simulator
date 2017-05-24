
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

# BullRed-RackManager systemBackend resources
#
class  RdSystemsBackend():
    # class for backend systems resource APIs
    def __init__(self,rdr):
        self.version=1
        self.nonVolatileDataChanged=False

    # **** Backend PULL APIs   from Frontend RedfishService ****
    #
    # GET volatile system info 
    def getVolatileSystemInfo(self,rdr,systemid):
        resp=dict()
        # get some of the data from the ChassisBackend
        rc,respChas,nonVolChanged=rdr.backend.chassis.getVolatileChassisInfo(rdr,"Opc1")
        if( (rc==0) and ("IndicatorLED" in respChas) and ("PowerState" in respChas)):
            resp["IndicatorLED"]=respChas["IndicatorLED"]
            resp["PowerState"]=respChas["PowerState"]
        else:
            print("*****BACKEND-Systems: error getting chassis info from Chassis Backend")
            resp["IndicatorLED"]=null
            resp["PowerState"]=null
        resp["Status"]={"State": "Enabled", "Health": "OK"} #status: Enable|Disabled|Absent
        resp["BootSourceOverrideEnabled"]=True         # True/False
        resp["BootSourceOverrideTarget"]="Pxe"         # None,Pxe,Floppy, Cd, Usb, Hdd, BiosSetup, UefiTarget...
        resp["BootSourceOverrideMode"]="UEFI"          # "UEFI" |"Legacy"
        resp["UefiTargetBootSourceOverride"]="/dev/uefiTarget"
        rc=0     # 0=ok
        return(rc,resp,self.nonVolatileDataChanged)


    # DO action:  "Reset", "Hard,  ***this is being called by frontend xgOBMC
    def doSystemReset(self,rdr,systemid,resetType):
        if( resetType == "On"):
            # do powerOn - if powerstate is off, push power button
            # the service should have already verified power is off to get here
            print("BACKEND: got reset type: On")
            # hoot DBUS xgOBMC
            pass
        elif( resetType == "ForceOff"):
            # do Hard Poweroff - eg hold power button down for 6 sec in a thread
            print("BACKEND: got reset type: Force Off")
            # hoot DBUS xgOBMC
            pass
        elif( resetType == "ForceRestart"):
            # do Hard powerOff, then powerOn - 
            #    - hold power button down 6 sec, then after powerOff, push button for .5 sec to turn-on
            print("BACKEND: got reset type: FOrce Restart")
            # hoot DBUS xgOBMC
            pass
        elif( resetType == "GracefulShutdown"):
            # do ACPI shutdown - if system is now on, press power button for .5 sec
            print("BACKEND: got reset type: Graceful Shutdown")
            # hoot DBUS xgOBMC
            pass
        elif( resetType == "GracefulRestart"):
            # do gracefulShutdown, then press power button to turn back on
            print("BACKEND: got reset type: Graceful Restart")
            # hoot DBUS xgOBMC
            pass
        else:
            return(9)    # invalid request
        rc=0  #0=ok
        return(rc)


    # SET LED state   * see chassis.py
    def doSetLed(self,rdr,systemid,ledState):
        storedaVal=ledState
        rc=0  #0=ok
        return(rc, storedVal)


    # SET asset Tag   * see chassis.py
    def doSetAssetTag(self,rdr,systemid,assetTagVal):
        # This is non-volatile data so generally the backend will push any changes
        storedaVal=assetTagVal
        rc=0  #0=ok
        return(rc, storedVal)

    # SET Boot Source Overrides 
    def doSetBootSourceOverrides(self,rdr,systemid,enable,mode,target,UefiTarget):
        storedaVal=ledState
        rc=0  #0=ok
        return(rc, storedVal)

    # *****  read non-volatile data  *****   * see chassis.py
    # normally, the backend will push this if changes due to non-Redfish interface
    # but implementing a get for debug and case where backend can push
    def getNonVolatileSystemInfo(self,rdr,systemid):
        resp=dict()
        resp["AssetTag"]=None,
        resp["HostName"]=None,
        resp["BiosVersion"]=None,
        assetTag=None
        rc=0 #     0=ok
        return(rc,assetTag)

    '''
    # these not implemented in front-end yet

    # ***** non-volatile set etags APIs  from Front-End RedfishService ************

    # the backend saves the etags of non-volatile data cache in front-end
    # if the non-volatile data changes, then it should Push the change to the front-end,
    # or set the nonVolatileDataChanged flag so that on next get, the front-end will know to get it
    def setNonVolatileSystemInfoEtag(self,rdr,systemid,etag):
        #save etag to detect if data changed
        rc=0 #     0=ok
        return(rc)

    '''




