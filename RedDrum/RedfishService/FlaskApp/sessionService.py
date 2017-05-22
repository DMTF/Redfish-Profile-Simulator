
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

import os
from .resource import RfStaticResource
from .generateId import rfGenerateId
#from .rootData import RfRoot
import json
import time
import sys

class RfSessionService():  
    # Note that resource was created in serviceRoot for the session service.
    def __init__(self, rfr):
        self.loadResourceTemplates(rfr )
        self.loadSessionServiceDatabase(rfr )
        self.initializeSessionsDict(rfr )
        self.magic="123456"

    def loadResourceTemplates( self, rfr ):
        #load SessionService Template
        indxFilePath=os.path.join(rfr.baseDataPath,"templates", "SessionService.json")
        if os.path.isfile(indxFilePath):
            self.sessionServiceTemplate=json.loads( open(indxFilePath,"r").read() )
        else:
            print("*****ERROR: SessionService: Json Data file:{} Does not exist. Exiting.".format(indxFilePath))
            sys.exit(10)

        #load Sessions Collection Template
        indxFilePath=os.path.join(rfr.baseDataPath,"templates", "SessionCollection.json")
        if os.path.isfile(indxFilePath):
            self.sessionsCollectionTemplate=json.loads( open(indxFilePath,"r").read() )
        else:
            print("*****ERROR: SessionService: Json Data file:{} Does not exist. Exiting.".format(indxFilePath))
            sys.exit(10)

        #load Session Entry Template
        indxFilePath=os.path.join(rfr.baseDataPath,"templates", "SessionEntry.json")
        if os.path.isfile(indxFilePath):
            self.sessionEntryTemplate=json.loads( open(indxFilePath,"r").read() )
        else:
            print("*****ERROR: SessionService: Json Data file:{} Does not exist. Exiting.".format(indxFilePath))
            sys.exit(10)
        
    def loadSessionServiceDatabase(self,rfr ):
        sessionServiceDbFilename="SessionServiceDb.json"
        self.sessionServiceDbFilePath=os.path.join(rfr.varDataPath,"db", sessionServiceDbFilename )
        if os.path.isfile(self.sessionServiceDbFilePath):
            self.sessionServiceDb=json.loads( open(self.sessionServiceDbFilePath,"r").read() )
        else:
            print("*****WARNING: Json Data file:{} Does not exist. Creating default.".format(self.sessionServiceDbFilePath))
            # read the data in from the default database dir with the rm-tools package
            dfltDbFilePath=os.path.join(rfr.baseDataPath,"db", sessionServiceDbFilename)
            if os.path.isfile(dfltDbFilePath):
                self.sessionServiceDb=json.loads( open(dfltDbFilePath,"r").read() )
            else:
                print("*****ERROR: Default Json Database file:{} Does not exist. Exiting.".format(dfltDbFilePath))
                sys.exit(10)
            #write the data back out to the var directory where the dynamic db info is kept
            sessionServiceDbJson=json.dumps(self.sessionServiceDb,indent=4)
            with open( self.sessionServiceDbFilePath, 'w', encoding='utf-8') as f:
                f.write(sessionServiceDbJson)

    def initializeSessionsDict(self,rfr):
        # this is the in-memory database of open sessions
        # the sessionsDict is an dict indexed by   sessionsDict[sessionId][<sessionParameters>]
        #   self.sessionsDict[sessionid]=
        #       { "UserName": username,      "UserPrivileges": userPrivileges, "AccountId": accountid,
        #         "X-Auth-Token": authtoken, "LocationUri": locationUri,     "LastAccessTime": lastAccessTime }
        self.sessionsDict=dict() #create an empty dict of session entries
            
    def getSessionServiceResource(self):
        # create a copy of the SessionService resource template 
        resData2=dict(self.sessionServiceTemplate)

        # set the dynamic data in the template copy to the value in the sessionService database
        resData2["SessionTimeout"]=self.sessionServiceDb["SessionTimeout"]

        # create the response json data and return
        resp=json.dumps(resData2,indent=4)
        return(resp)

    def patchSessionServiceResource(self,patchData):
        #first verify client didn't send us a property we cant patch
        for key in patchData.keys():
            if( key != "SessionTimeout" ):
                return (4, 400, "Bad Request-Invalid Patch Property Sent", "")
        # now patch the valid properties sent
        if( "SessionTimeout" in patchData):
            newVal=patchData['SessionTimeout']
            if( (newVal < 30) or (newVal >86400) ):
                return(4, 400, "Bad Request-not in correct range", "")
            else:
                # the data is good and in range, save it and return ok
                self.sessionServiceDb["SessionTimeout"]=newVal

                # write the data back out to the sessionService database file
                sessionServiceDbJson=json.dumps(self.sessionServiceDb,indent=4)
                with open( self.sessionServiceDbFilePath, 'w', encoding='utf-8') as f:
                    f.write(sessionServiceDbJson)

                # return to URI handling OK, with no content
                return(0, 204, None, None)
        else:
            return (4, 400, "Bad Request-Invalid Patch Property Sent", "")


    # getSessionAuthInfo()
    #   returns: rc, errMsgString, sessionId, authToken, userPrivileges, accountId, username
    #      rc=404 if sessionId is invalid.  
    #      rc=401 if authToken is invalid or mismatches sessionid, or session is expired
    #   self.sessionsDict[sessionid]={"UserName": username, "UserPrivileges": userPrivileges, 
    #       "AccountId": accountid,
    #       "X-Auth-Token": authtoken, "LocationUri": locationUri, "LastAccessTime": lastAccessTime}
    def getSessionAuthInfo(self,sessionid=None, authtoken=None ):
        storedAuthToken=None
        storedSessionId=None
        storedPrivileges=None
        # if sessionid is not None, verify that the sessionId is valid
        if sessionid is not None:
            if sessionid not in self.sessionsDict.keys():
                return(404, "SessionId Not Found",None,None,None,None,None)
            else:
                #the sessionid exists, so get associated authToken
                storedSessionId=sessionid
                storedAuthToken=self.sessionsDict[sessionid]["X-Auth-Token"]
                storedPrivileges=self.sessionsDict[sessionid]["UserPrivileges"]
                storedUserName=self.sessionsDict[sessid]["UserName"]
                storedAccountId=self.sessionsDict[sessid]["AccountId"]
                # if authtoken was also passed in, check if it matches the stored value
                if authtoken is not None:
                    if(authtoken != storedAuthToken):
                        return(401, "Not Authroized-AuthToken Incorrect",None,None,None,None,None)

        # else if authtoken is not None, look it up, verify it exists
        elif authtoken is not None:
            # case where sessionid was not passed in, but authtoken was
            # we need to go lookup authtoken w/o sessionid
            foundToken=False
            for sessid in self.sessionsDict.keys():
                if( self.sessionsDict[sessid]["X-Auth-Token"] == authtoken ):
                    foundToken=True
                    storedSessionId=sessid
                    storedAuthToken=self.sessionsDict[sessid]["X-Auth-Token"]
                    storedPrivileges=self.sessionsDict[sessid]["UserPrivileges"]
                    storedUserName=self.sessionsDict[sessid]["UserName"]
                    storedAccountId=self.sessionsDict[sessid]["AccountId"]
                    break
            if foundToken is False:
                return(401, "Not Authroized-Token Not Found",None,None,None,None,None)

        # else, both sessionid and authtoken are None, which is invalid call
        else:
            return(500, "Invalid Auth Check",None,None,None,None,None)

        # verify that the session has not expired
        currentTime=int(time.time())
        lastAccessTime=self.sessionsDict[storedSessionId]["LastAccessTime"]
        sessionTimeout=self.sessionServiceDb["SessionTimeout"] 
        if( (currentTime - lastAccessTime) > sessionTimeout ):
            # it timed out.  delete the session, and return unauthorized
            del self.sessionsDict[storedSessionId]
            # return 404 since we deleted the session and the uri is no longer valid
            return(404, "Session Not Found-Expired",None,None,None,None,None)
        else:
            #else-update the timestamp--to indicate the session was used
            self.sessionsDict[storedSessionId]["LastAccessTime"]=currentTime

        # if here, all ok, return privileges
        #returns: rc, errMsgString, sessionId, authToken, userPrivileges
        return(0, "OK", storedSessionId, storedAuthToken, storedPrivileges, storedAccountId, storedUserName )


    # ------------Session Collection Functions----------------

    # POST to sessions collection  (login)
    def postSessionsResource(self,rfr,postData):
        # first verify that the client didn't send us a property we cant initialize the session with
        # we need to fail the request if we cant handle any properties sent
        for key in postData.keys():
            if( (key != "UserName") and (key != "Password") ):
                return (4, 400, "Bad Request-Invalid Post Property Sent", "","")
        # now check that all required on create properties were sent as post data
        username=None
        password=None
        if( "UserName" in postData):
            username=postData['UserName']

        if("Password" in postData):
            password=postData['Password']

        if( (username is None) or (password is None) ):
            return (4, 400, "Bad Request-Required On Create properties not all sent", "","")

        # now verify that the login credentials are valid and get the privileges
        rc,errMsg,accountid,roleId,userPrivileges=rfr.root.accountService.getAccountAuthInfo(username,password)
        if( rc != 0 ): # unauthenticated
            return(4, 401, "Unauthorized--invalid user or password","","")

        # otherwise, if here, it is an authenticated user
        # check if user has login privilege
        if( "Login" not in userPrivileges ):
            return(4, 401, "Unauthorized--User does not have login privilege","","")

        #get time to update timer in sessDict
        lastAccessTime=int(time.time())

        # now Generate a session ID and auth token as a random number
        sessionid=rfGenerateId(leading="S",size=8)
        authtoken=rfGenerateId(leading="A",size=8)

        # create response header data
        locationUri="/redfish/v1/SessionService/Sessions/" + sessionid
        respHeaderData={"X-Auth-Token": authtoken, "Location": locationUri}

        # add the new session entry to add to the sessionsDict
        self.sessionsDict[sessionid]={"UserName": username, "UserPrivileges": userPrivileges, "AccountId": accountid,
                  "X-Auth-Token": authtoken, "LocationUri": locationUri, "LastAccessTime": lastAccessTime}

        # get the response data
        rc,status,msg,respData,respHdr=self.getSessionEntry(sessionid)
        if( rc != 0):
            #something went wrong--return 500
            return(5, 500, "Error Getting New Session Data","","")

        #return to flask uri handler
        return(0, 201, "Created",respData,respHeaderData)


    # GET sessions Collection
    def getSessionsCollectionResource(self):
        # the routine copies a template file with the static redfish parameters
        # then it updates the dynamic properties from the sessionsDict
        # for SessionCollection GET, build the Members array

        # first walk the sessionsDict and check if any sessions have timed-out.
        # If any session has timed-out, delete it now
        currentTime=int(time.time())
        sessionTimeout=self.sessionServiceDb["SessionTimeout"]
        sessDict2=dict(self.sessionsDict)
        for sessionid in sessDict2.keys():
            # check if this session entry has timed-out.   If so, delete it.
            lastAccessTime=sessDict2[sessionid]["LastAccessTime"]
            if( (currentTime - lastAccessTime) > sessionTimeout ):
                # this session is timed out.  remove it from the original sessionDict
                del self.sessionsDict[sessionid]

        # Then copy the sessionsCollection template file (which has an empty sessions array)
        resData2=dict(self.sessionsCollectionTemplate)
        count=0
        # now walk through the entries in the sessionsDict and built the sessionsCollection Members array
        # not that it starts out an empty array
        for sessionEntry in self.sessionsDict.keys():
            # increment members count, and create the member for the next entry
            count=count+1
            newMember=[{"@odata.id": self.sessionsDict[sessionEntry]["LocationUri"] } ]

            # add the new member to the members array we are building
            resData2["Members"] = resData2["Members"] + newMember
        resData2["Members@odata.count"]=count

        # convert to json
        respData2=(json.dumps(resData2,indent=4))

        return( respData2)

    # Get Session Entry
    def getSessionEntry(self,sessionid):
        # First Check if the session has timed-out.
        # If it has timed-out, delete it now
        currentTime=int(time.time())
        sessionTimeout=self.sessionServiceDb["SessionTimeout"]
        lastAccessTime=self.sessionsDict[sessionid]["LastAccessTime"]
        if( (currentTime - lastAccessTime) > sessionTimeout ):
            # this session is timed out.  remove it from the sessionDict
            del self.sessionsDict[sessionid]

        # Proceed--and verify that the sessionId is valid
        if sessionid not in self.sessionsDict.keys():
                return(404, "Not Found","","")

        # first just copy the template sessionEntry resource
        resData=dict(self.sessionEntryTemplate)

        # now overwrite the dynamic data from the sessionsDict
        resData["Id"]=sessionid
        resData["UserName"]=self.sessionsDict[sessionid]["UserName"]
        resData["@odata.id"]=self.sessionsDict[sessionid]["LocationUri"]

        # convert to json
        respData=(json.dumps(resData,indent=4))

        return(0, 200, "",respData,"")

    # logout
    # delete the session
    # all we have to do is verify the sessionid is correct--
    # and then, if it is valid, delete the entry for that sessionid from the sessionsDict
    # For reference: the sessionsDict:
    #   self.sessionsDict[sessionid]={"UserName": username, "UserPrivileges": userPrivileges, 
    #             "X-Auth-Token": authtoken, "LocationUri": locationUri, "LastAccessTime": lastAccessTime}
    def deleteSession(self, sessionid):
        # First, verify that the sessionid is valid
        if sessionid not in self.sessionsDict.keys():
            return(4, 404, "Not Found","","","")
        else:
            del self.sessionsDict[sessionid]
            return(0, 204, "No Content","","")

# end
