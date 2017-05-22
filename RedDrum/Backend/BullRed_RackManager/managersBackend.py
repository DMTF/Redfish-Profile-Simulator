# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

# BullRed-RackManager managersBackend resources
#
class  RdManagersBackend():
    # class for backend managers resource APIs
    def __init__(self,rdr):
        self.version=1

    # **** Backend PULL APIs   from Frontend RedfishService ****
    #
    # GET volatile managers info 
    def getVolatileManagerInfo(self,rdr,managerid):
        resp=dict()
        resp["IndicatorLED"]=None          # ledState
        resp["PowerState"]=None            # powerState
        resp["DateTime"]=None              # datetime
        resp["DateTimeLocalOffset"]=None   # offset string
        resp["Status"]={"State": None, "Health": None}
        nonVolatileDataChanged=False
        rc=0     # 0=ok
        return(rc,resp,nonVolatileDataChanged)


    # DO action:  "Reset", "Hard,
    def doManagerReset(self,rdr,managerid,resetType):
        if( resetType == "ForceRestart"):
            # do Hard reset of BMC
            pass
        elif( resetType == "GracefulRestart"):
            # do gracefulShutdown, and restart of BMC
            pass
        else:
            return(9)    # invalid request
        rc=0  #0=ok
        return(rc)


    # SET LED state
    def doSetLed(self,rdr,managerid,ledState):
        storedaVal=ledState
        rc=0  #0=ok
        return(rc, storedVal)



    # *****  read non-volatile data  *****
    # normally, the backend will push this if changes due to non-Redfish interface
    # but implementing a get for debug and case where backend can push
    def getNonVolatileManagerInfo(self,rdr,managerid):
        resp=dict()
        resp["FirmwareVersion"]="A1.2.3"       # firmware version
        rc=0 #     0=ok
        return(rc,resp)

    '''
    # these not implemented in front-end yet

    # ***** non-volatile set etags APIs  from Front-End RedfishService ************

    # the backend saves the etags of non-volatile data cache in front-end
    # if the non-volatile data changes, then it should Push the change to the front-end,
    # or set the nonVolatileDataChanged flag so that on next get, the front-end will know to get it
    def setNonVolatileManagerInfoEtag(self,rdr,managerid,etag):
        #save etag to detect if data changed
        rc=0 #     0=ok
        return(rc)


    '''
