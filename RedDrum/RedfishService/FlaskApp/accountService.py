
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

import os
import json
import time
import sys
import re
#from .rootData import RfRoot
import hashlib


class RfAccountService():  
    # Note that this resource was created in serviceRoot for the Account service.
    def __init__(self,rfr ):
        self.loadResourceTemplates(rfr )
        self.loadAccountServiceDatabaseFiles(rfr )
        self.initializeAccountsDict(rfr)
        self.rfr=rfr
        self.magic="123456"

    def loadResourceTemplates( self, rfr ):
        #load AccountService Template
        self.accountServiceTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "AccountService.json")

        #load Accounts Collection Template
        self.accountsCollectionTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "AccountCollection.json")

        #load Account Entry Template
        self.accountEntryTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "AccountEntry.json")

        #load Roles Collection Template
        self.rolesCollectionTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "RoleCollection.json")

        #load Roles Entry Template
        self.roleEntryTemplate=self.loadResourceTemplateFile(rfr.baseDataPath,"templates", "RoleEntry.json")

    # worker function called by loadResourceTemplates() to load a specific template
    # returns a dict loaded of the template file, which calling function saves to a variable
    # if file does not exist, the service exits
    #    assumes good json in the template file
    def loadResourceTemplateFile( self, dataPath, subDir, filename ):
        indxFilePath=os.path.join(dataPath, subDir, filename)
        if os.path.isfile(indxFilePath):
            response=json.loads( open(indxFilePath,"r").read() )
            return(response)
        else:
            print("*****ERROR: AccountService: Json Data file:{} Does not exist. Exiting.".format(indxFilePath))
            sys.exit(10)
        
    def loadAccountServiceDatabaseFiles(self, rfr ):
        # load the AccountService database file:      "AccountServiceDb.json"
        filename="AccountServiceDb.json"
        self.accountServiceDbFilePath,self.accountServiceDb=self.loadDatabaseFile(rfr,"db",filename) 

        # load the Accounts collection database file: "AccountsDb.json"
        filename="AccountsDb.json"
        self.accountsDbFilePath,self.accountsDb=self.loadDatabaseFile(rfr,"db",filename) 

        # load the Roles collection  database file:     "RolesDb.json"
        filename="RolesDb.json"
        self.rolesDbFilePath,self.rolesDb=self.loadDatabaseFile(rfr,"db",filename) 

    # worker function called by loadAccountServiceDatabaseFiles() to load a specific database file
    # returns two positional parameters:
    #    the database filepath,
    #    a dict of the database file
    # if file does not exist in the varDataPath/subDir directory (the database dir), 
    #   then it loads the file from baseDataBath (the default database), and saves it back to the varDataPath dir
    # assumes good json in the database file
    def loadDatabaseFile( self, rfr, subDir, filename ):
        dbFilePath=os.path.join(rfr.varDataPath,subDir, filename)
        if os.path.isfile(dbFilePath):
            dbDict=json.loads( open(dbFilePath,"r").read() )
        else:
            print("*****WARNING: Json Data file:{} Does not exist. Creating default.".format(dbFilePath))
            # read the data in from the default database dir with the rm-tools package
            dfltDbFilePath=os.path.join(rfr.baseDataPath,subDir,filename)
            if os.path.isfile(dfltDbFilePath):
                dbDict=json.loads( open(dfltDbFilePath,"r").read() )
            else:
                print("*****ERROR: Default Json Database file:{} Does not exist. Exiting.".format(dfltDbFilePath))
                sys.exit(10)
            #write the data back out to the var directory where the dynamic db info is kept
            dbDictJson=json.dumps(dbDict,indent=4)
            with open( dbFilePath, 'w', encoding='utf-8') as f:
                f.write(dbDictJson)
        # return path and data
        return(dbFilePath,dbDict)

    def initializeAccountsDict(self,rfr):
        # this is the in-memory database of account properties that are not persistent
        # the accountsDict is a dict indexed by   accountsDict[accountid][<nonPersistentAccountParameters>]
        #   self.accountsDict[accountid]=
        #       { "Locked": <locked>,  "FailedLoginCount": <failedLoginCnt>, "LockedTime": <lockedTimestamp>,
        #         "AuthFailTime": <authFailTimestamp> }
        self.accountsDict=dict() #create an empty dict of Account entries
        curTime=time.time()

        #create the initial state of the accountsDict from the accountsDb
        for acct in self.accountsDb.keys():
            self.accountsDict[acct]={ "Locked": False, "FailedLoginCount": 0, "LockedTime": 0, "AuthFailTime": 0 }
        
            
    def getAccountServiceResource(self):
        # create a copy of the AccountService resource template 
        resData2=dict(self.accountServiceTemplate)

        # set the dynamic data in the template copy to the value in the accountService database
        resData2["AuthFailureLoggingThreshold"]=self.accountServiceDb["AuthFailureLoggingThreshold"]
        resData2["MinPasswordLength"]=self.accountServiceDb["MinPasswordLength"]
        resData2["AccountLockoutThreshold"]=self.accountServiceDb["AccountLockoutThreshold"]
        resData2["AccountLockoutDuration"]=self.accountServiceDb["AccountLockoutDuration"]
        resData2["AccountLockoutCounterResetAfter"]=self.accountServiceDb["AccountLockoutCounterResetAfter"]

        # create the response json data and return
        resp=json.dumps(resData2,indent=4)
        return(resp)


    def patchAccountServiceResource(self,patchData):
        #first verify client didn't send us a property we cant patch
        patachables=("MinPasswordLength","AccountLockoutThreshold", "AuthFailureLoggingThreshold",
                     "AccountLockoutDuration","AccountLockoutCounterResetAfter")
        for key in patchData.keys():
            if( not key in patachables ):
                return (4, 400, "Bad Request-Invalid Patch Property Sent", "")

        # then convert the patch properties passed-in to integers
        for key in patchData.keys():
            newVal=patchData[key]
            print("newVal:{}".format(newVal))
            try:
                numVal=round(newVal)
            except ValueError:
                return(4,400,"invalid value","")
            else:
                patchData[key]=numVal

        # then verify the properties passed-in are in valid ranges
        newDuration=self.accountServiceDb["AccountLockoutDuration"]
        newResetAfter=self.accountServiceDb["AccountLockoutCounterResetAfter"]
        if( "AccountLockoutDuration" in patchData ):
            newDuration=patchData["AccountLockoutDuration"]
        if( "AccountLockoutCounterResetAfter" in patchData ):
            newResetAfter=patchData["AccountLockoutCounterResetAfter"]
        if( newDuration < newResetAfter ):
            return(4,400,"Bad Request-Invalid value","")

        # if here, all values are good. Update the accountServiceDb dict
        for key in patchData.keys():
            self.accountServiceDb[key]=patchData[key]

        # write the data back out to the accountService database file
        accountServiceDbJson=json.dumps(self.accountServiceDb,indent=4)
        with open( self.accountServiceDbFilePath, 'w', encoding='utf-8') as f:
            f.write(accountServiceDbJson)
        return(0,204,None,None)

    # getAccountAuthInfo(username,password)
    #   returns: rc, errMsgString, accountId, roleId, userPrivileges
    #      rc=404 if username is not in accountsDb
    #      rc=401 if username is invalid or mismatches password, or account is locked or not enabled
    #        =0   if authenticated
    #   self.accountsDict[accountid]={ "Locked": False, "FailedLoginCount": 0, "LockedTime": 0, "AuthFailTime": 0 }

    def getAccountAuthInfo(self, username, password ):
        authFailed=False
        storedUsername=None
        storedPassword=None
        storedPrivileges=None
        # if username or password is not None, it is an error
        if username is None:
            return(500, "Invalid Auth Check for username",None,None,None)
        if password is None:
            return(500, "Invalid Auth Check for password",None,None,None)

        # from username, lookup accountId --- they are not necessarily the same
        accountid=None
        for acctid in self.accountsDb.keys():
            if( username == self.accountsDb[acctid]["UserName"] ):
                accountid=acctid
                break

        # if we didn't find the username, return error
        # since the username is invalid, we cant count invalid login attempts
        if accountid is None:
            return(404, "Not Found-Username Not Found",None,None,None)

        # check if the account is disabled
        if( self.accountsDb[accountid]["Enabled"] is False ): 
            return(401, "Not Authorized--Account Disabled",None,None,None)

        # check if account was locked 
        #    if it is locked but has now exceeded LockoutDuration then unlock and continue
        #    if it is locked and not exceeded lockout duration, return 401 Not authorized
        curTime=time.time()
        if self.accountsDict[accountid]["Locked"] is True:
            if( (curTime - self.accountsDict[accountid]["LockedTime"]) > self.accountServiceDb["AccountLockoutDuration"] ):
                # the lockout duration has expired.   unlock it.
                self.accountsDict[accountid]["Locked"]=False
                self.accountsDict[accountid]["LockedTime"]=0
                self.accountsDict[accountid]["FailedLoginCount"]=0
                self.accountsDict[accountid]["AuthFailTime"]=0
            else:
                # lockout duration has not expired, return auth error
                return(401, "Not Authorized--Account Locked By Service",None,None,None)

        #the accountid exists, and account is enabled and not locked

        #reset the AuthFailTime if time since last login failure is > AccountLockoutCounterResetAfter
        authFailTime=self.accountsDict[accountid]["AuthFailTime"]
        if( authFailTime != 0 ):
            # if we have had failures and are counting authentication failures
            resetAfterThreshold=self.accountServiceDb["AccountLockoutCounterResetAfter"]
            if( ( curTime - authFailTime ) > resetAfterThreshold ):
                # if time since last failure is greater than the reset counter threshold, then reset the counters
                self.accountsDict[accountid]["AuthFailTime"]=0
                self.accountsDict[accountid]["FailedLoginCount"]=0

        #now check the associated password to see if authentication passis this time 
        #check password
        if( password != self.accountsDb[accountid]["Password"] ): # TODO change to check hash
            # authentication failed.

            # check if lockout on authentication failures is enabled
            lockoutThreshold=self.accountServiceDb["AccountLockoutThreshold"]
            lockoutDuration=self.accountServiceDb["AccountLockoutDuration"]

            # lockoutThreshold and lockoutDuration must BOTH be non-zero to enable lock on auth failures
            if( (lockoutThreshold > 0) and (lockoutDuration > 0) ):
                # check if we have now exceeded the login failures and need to lock the account
                failedLoginCount=self.accountsDict[accountid]["FailedLoginCount"] + 1
                if( failedLoginCount >= lockoutThreshold ):
                    # lock the account and clear the AuthFailTime and FailedLogin counters
                    self.accountsDict[accountid]["Locked"]=True
                    self.accountsDict[accountid]["LockedTime"]=curTime
                    self.accountsDict[accountid]["AuthFailTime"]=0
                    self.accountsDict[accountid]["FailedLoginCount"]=0
                    print("EELOCK_---EEEEEEEEEEEE: accountsDict: {}".format( self.accountsDict))
                    return(401, "Not Authorized--Password Incorrect and Account is now Locked By Service",None,None,None)
                else:
                    # we have not exceeded the failed authN threshold, update the counter and continue
                    self.accountsDict[accountid]["FailedLoginCount"]=failedLoginCount
                    self.accountsDict[accountid]["AuthFailTime"]=curTime
                    return(401, "Not Authorized--Password Incorrect",None,None,None)

            else:
                # case where account lockout is not enabled
                return(401, "Not Authorized--Password Incorrect",None,None,None)

        #if here, the authentication was successful
        #reset the lockout timers
        self.accountsDict[accountid]["FailedLoginCount"]=0
        self.accountsDict[accountid]["AuthFailTime"]=0

        storedpassword=self.accountsDb[accountid]["Password"]
        storedRoleId=self.accountsDb[accountid]["RoleId"]
        storedPrivileges=self.rolesDb[storedRoleId]["AssignedPrivileges"]

        # if here, all ok, return privileges
        #   returns:  rc, errMsgString, userName, roleId, userPrivileges
        return(0, "OK", accountid, storedRoleId, storedPrivileges )




    # ------------Roles Collection Functions----------------

    # GET roles Collection
    def getRolesCollectionResource(self):
        # the routine copies a template file with the static redfish parameters
        # then it updates the dynamic properties from the rolesDb dict
        # for RolesCollection GET, we build the Members array

        # copy the rolesCollection template file (which has an empty roles array)
        resData2=dict(self.rolesCollectionTemplate)
        count=0
        # now walk through the entries in the rolesDb and build the rolesCollection Members array
        # note that the members array is an empty array in the template
        roleUriBase="/redfish/v1/AccountService/Roles/"
        for roleid in self.rolesDb.keys():
            # increment members count, and create the member for the next entry
            count=count+1
            memberUri=roleUriBase + roleid
            newMember=[{"@odata.id": memberUri}]

            # add the new member to the members array we are building
            resData2["Members"] = resData2["Members"] + newMember
        resData2["Members@odata.count"]=count

        # convert to json
        respData2=(json.dumps(resData2,indent=4))

        return(respData2)


    # Get Role Entry
    def getRoleEntry(self,roleid):
        # verify that the roleId is valid
        if roleid not in self.rolesDb.keys():
                return(404, "Not Found","","")

        # first just copy the template roleEntry resource
        resData2=dict(self.roleEntryTemplate)

        # now overwrite the dynamic data from the rolesDb 
        roleEntryUri="/redfish/v1/AccountService/Roles/" + roleid
        resData2["@odata.id"]=roleEntryUri
        resData2["Id"]=roleid
        resData2["Name"]=self.rolesDb[roleid]["Name"]
        resData2["Description"]=self.rolesDb[roleid]["Description"]
        resData2["IsPredefined"]=self.rolesDb[roleid]["IsPredefined"]
        resData2["AssignedPrivileges"]=self.rolesDb[roleid]["AssignedPrivileges"]

        # convert to json
        responseData=(json.dumps(resData2,indent=4))

        return(0, 200, "",responseData,"")


    # POST to roles collection  (add a custom role)
    def postRolesResource(self,postData):
        # first verify that the client didn't send us a property we cant patch
        # we need to fail the request if we cant handle any properties sent
        #   note that this implementation does not support OemPrivileges
        for key in postData.keys():
            if( (key != "Id") and (key != "AssignedPrivileges") ):
                return (4, 400, "Bad Request-Invalid Post Property Sent", "","")
        # now check that all required on create properties were sent as post data
        roleId=None
        privileges=None
        if( "Id" in postData):
            roleId=postData['Id']

        if("AsignedPrivileges" in postData):
            privileges=postData['AsignedPrivileges']

        if( (roleId is None) or (privileges is None) ):
            return (4, 400, "Bad Request-Required On Create properties not all sent", "","")
        # now verify that the post data properties have valid values
        if roleId in rolesDb.keys():   # if the roleId already exists, return error
            return (4, 400, "Bad Request-Invalid RoleId--RoleId already exists", "","")
        validPrivilegesList=("Login","ConfigureManager","ConfigureUsers","ConfigureSelf","ConfigureComponents")
        for priv in privileges:
            if priv not in validPrivilegesList:
                return (4, 400, "Bad Request-Invalid Privilige", "","")

        # create response header data
        locationUri="/redfish/v1/AccountService/Roles/" + roleId
        respHeaderData={"Location": locationUri}

        # create rolesDb data and response properties
        roleName=roleId + "Custom Role"
        roleDescription="Custom Role"
        isPredefined=False

        # add the new role entry to add to the roleDb
        self.rolesDb[roleId]={"Name": rolename, "Description": roleDescription, "IsPredefined": idPredefined, 
            "AssignedPrivileges": privileges }

        # get the response data
        rc,status,msg,respData,respHdr=self.getRoleEntry(roleId)
        if( rc != 0):
            #something went wrong--return 500
            return(5, 500, "Error Getting New Role Data","","")

        #return to flask uri handler, include location header
        return(0, 201, "Created",respData,respHeaderData)



    # delete the Role
    # all we have to do is verify the roleid is correct--
    # and then, if it is valid, delete the entry for that roleid from the rolesDb
    # For reference: the rolesDb:
    #    self.rolesDb[roleId]={"Name": rolename, "Description": roleDescription, "IsPredefined": idPredefined, 
    #       "AssignedPrivileges": privileges }
    def deleteRole(self, roleid):
        # First, verify that the roleid is valid
        if roleid not in self.rolesDb.keys():
            return(4, 404, "Not Found","","","")

        # then verify that the roleid is not configured for any user
        # TODO check if any user is assigned that roleid
        #     current redfish spec does not require this, so skipping for now

        # otherwise go ahead and delete the roleid
        del self.rolesDb[roleid]
        return(0, 204, "No Content","","")

    #xg7
    # PATCH a ROLE ENTRY
    def patchRoleEntry(self, roleId, patchData):
        # First, verify that the roleId is valid, 
        if roleId not in self.rolesDb:
            return(4, 404, "Not Found","","")

        # verify that the patch data is good

        # first verify that ALL of the properties sent in patch data are patchable for redfish spec
        for prop in patchData:
            if prop != "AssignedPrivileges":
                return (4, 400, "Bad Request-one or more properties not patchable", "","")

        # check if any privilege is not valid
        redfishPrivileges=("Login","ConfigureManager","ConfigureUsers","ConfigureSelf","ConfigureComponents")
        if "AssignedPrivileges" in patchData:
            for privilege in patchData["AssignedPrivileges"]:
                if not privilege in redfishPrivileges:
                    return (4, 400, "Bad Request-one or more Privileges are invalid", "","")

        # if here, all values are good. Update the accountServiceDb dict
        self.accountServiceDb["AssignedPrivilages"]=patchData["AssignedPrivilages"]

        #xg5 note: service currently does not support oem privileges

        # write the rolesDb back out to the file
        dbFilePath=os.path.join(rfr.varDataPath,"db", "RolesDb.json")
        dbDictJson=json.dumps(self.rolesDb, indent=4)
        with open( dbFilePath, 'w', encoding='utf-8') as f:
            f.write(dbDictJson)

        return(0, 204, "No Content","","")


    # ------------Accounts Collection Functions----------------


    # GET Accounts Collection
    def getAccountsCollectionResource(self):
        # the routine copies a template file with the static redfish parameters
        # then it updates the dynamic properties from the accountsDb and accountsDict

        # copy the accountsCollection template file (which has an empty accounts array)
        resData2=dict(self.accountsCollectionTemplate)
        count=0
        # now walk through the entries in the accountsDb and built the accountsCollection Members array
        # note that the template starts out an empty array
        accountUriBase="/redfish/v1/AccountService/Accounts/"
        for accountEntry in self.accountsDb.keys():
            # increment members count, and create the member for the next entry
            count=count+1
            memberUri=accountUriBase + accountEntry
            newMember=[{"@odata.id": memberUri}]

            # add the new member to the members array we are building
            resData2["Members"] = resData2["Members"] + newMember

        resData2["Members@odata.count"]=count

        # convert to json
        responseData2=(json.dumps(resData2,indent=4))

        return( responseData2)


    # Get Account Entry
    def getAccountEntry(self,accountid):
        # verify that the accountId is valid
        if accountid not in self.accountsDb.keys():
                return(404, "Not Found","","")

        # first just copy the template sessionEntry resource
        resData=dict(self.accountEntryTemplate)

        # check if account was locked but has now exceeded LockoutDuration
        #    if so, then unlock before returning data
        curTime=time.time()
        if self.accountsDict[accountid]["Locked"] is True:
            if( (curTime - self.accountsDict[accountid]["LockedTime"]) > self.accountServiceDb["AccountLockoutDuration"] ):
                # the lockout duration has expired.   unlock it.
                self.accountsDict[accountid]["Locked"]=False
                self.accountsDict[accountid]["LockedTime"]=0
                self.accountsDict[accountid]["FailedLoginCount"]=0
                self.accountsDict[accountid]["AuthFailTime"]=0

        # now overwrite the dynamic data from the accountsDb
        accountUri="/redfish/v1/AccountService/Accounts/" + accountid
        accountRoleId=self.accountsDb[accountid]["RoleId"]
        resData["@odata.id"]=accountUri
        resData["Id"]=accountid
        resData["Enabled"]=self.accountsDb[accountid]["Enabled"]
        resData["Password"]=None   # translates to Json: null
        resData["UserName"]=self.accountsDb[accountid]["UserName"]
        resData["RoleId"]=accountRoleId
        roleUri="/redfish/v1/AccountService/Roles/" + accountRoleId
        resData["Links"]["Role"]["@odata.id"]=roleUri

        # now overwrite the dynamic data from the sessionsDict
        # this is non-persistent account data
        resData["Locked"]=self.accountsDict[accountid]["Locked"]  

        # convert to json
        responseData=(json.dumps(resData,indent=4))

        # calculate eTag
        etagHeader=self.calculateAccountEtag(accountid)

        #return etagHeader in response back to URI processing.  It will merge it
        return(0, 200, "",responseData, etagHeader)

    # general account service function to calculate the AccountEntry Etag
    #    this is a STRONG Etag
    # xgAbi
    def calculateAccountEtag(self, accountid):
        enable   = self.accountsDb[accountid]["Enabled"]
        locked   = self.accountsDict[accountid]["Locked"]  
        username = self.accountsDb[accountid]["UserName"]
        password = self.accountsDb[accountid]["Password"]
        roleId   = self.accountsDb[accountid]["RoleId"]
        # xg9 HACK return hard coded string for initial test for now
        #etag="\"1234\""

        flag = 0
        m = hashlib.md5()
        if enable:
            flag = 1
        if locked:
            flag = 2
        m.update((username+password+roleId).encode('utf-8'))
        etagHdr={"ETag": "\"" + m.hexdigest() + "\"" }
        return(etagHdr)



    # POST to Accounts collection  (add user)
    def postAccountsResource(self,postData):
        # first verify that the client didn't send us a property we cant write when creating the account
        # we need to fail the request if we cant handle any properties sent
        patchables=("UserName","Password","RoleId","Enabled","Locked")
        for prop in postData:
            if not prop in patchables:
                return (4, 400, "Bad Request-Invalid Post Property Sent", "","")

        #get the data needed to create the account
        username=None
        password=None
        roleid=None
        enabled=True
        locked=False

        if( "UserName" in postData):
            username=postData['UserName']

        if("Password" in postData):
            password=postData['Password']

        if("RoleId" in postData):
            roleId=postData['RoleId']

        if("Enabled" in postData):
            enabled=postData['Enabled']

        if("Locked" in postData):
            locked=postData['Locked']

        # now check that all required on create properties were sent as post data
        if( (username is None) or (password is None) or (roleId is None ) ):
            return (4, 400, "Bad Request-Required On Create properties not all sent", "","")

        # now verify that the Post data is valid

        # check if this username already exists
        for userId in self.accountsDb:
            if (username == self.accountsDb[userId]["UserName"]):
                return (4, 400, "Bad Request-Username already exists", "","")

        # check if password length is less than value set in accountService MinPasswordLength
        if "MinPasswordLength" in self.accountServiceDb:
            if len(password) < self.accountServiceDb["MinPasswordLength"]:
                return (4, 400, "Bad Request-Password length less than min", "","")
        if "MaxPasswordLength" in self.accountServiceDb:
            if len(password) > self.accountServiceDb["MaxPasswordLength"]:
                return (4, 400, "Bad Request-Password length exceeds max", "","")
        # check if password meets regex requirements---no whitespace or ":"
        passwordMatchPattern="^[^\s:]+$"
        passwordMatch = re.search(passwordMatchPattern,password)
        if not passwordMatch:
            return (4, 400, "Bad Request-invalid password-whitespace or : is not allowed", "","")

        # check if roleId does not exist
        if not roleId in self.rolesDb:
            return (4, 400, "Bad Request-roleId does not exist", "","")

        # check if Enabled is a boul
        if (enabled is not True) and (enabled is not False):
            return (4, 400, "Bad Request-Enabled must be either True or False", "","")
        # check if Locked  is a boul
        if locked is not False:
            return (4, 400, "Bad Request-Locked can only be set to False by user", "","")

        # create response header data
        accountid=username
        locationUri="/redfish/v1/AccountService/Accounts/" + accountid
        respHeaderData={"Location": locationUri}

        # add the new account entry to the accountsDb
        self.accountsDb[accountid]={"UserName": username, "Password": password, 
                  "RoleId": roleId, "Enabled": enabled, "Deletable": True}

        # add the new account entry to the accountsDict
        dfltAccountDictEntry={ "Locked": False, "FailedLoginCount": 0, "LockedTime": 0, "AuthFailTime": 0 }
        self.accountsDict[accountid]=dfltAccountDictEntry

        # write the AccountDb back out to the file
        dbFilePath=os.path.join(self.rfr.varDataPath,"db", "AccountsDb.json")
        dbDictJson=json.dumps(self.accountsDb, indent=4)
        with open( dbFilePath, 'w', encoding='utf-8') as f:
            f.write(dbDictJson)
        
        # get the response data
        rc,status,msg,respData,respHdr=self.getAccountEntry(accountid)

        # add etag into responseHeader created above
        respHeaderData["ETag"]=respHdr["ETag"]

        if( rc != 0):
            #something went wrong--return 500
            return(5, 500, "Error Getting New Account Data","","")

        #return to flask uri handler
        return(0, 201, "Created",respData,respHeaderData)



    # delete the Account
    # all we have to do is verify the accountid is correct--
    # and then, if it is valid, delete the entry for that accountid from the accountsDb and accountsDict
    def deleteAccount(self, accountid):
        # First, verify that the accountid is valid, 
        if accountid not in self.accountsDb.keys():
            return(4, 404, "Not Found","","","")
        else:
            del self.accountsDb[accountid]

        # delete the accountid entry from the accountsDict also
        if accountid in self.accountsDict.keys():
            del self.accountsDict[accountid]

        # write the data back out to the accountService database file
        accountsDbJson=json.dumps(self.accountsDb,indent=4)
        filename="AccountsDb.json"
        with open( self.accountsDbFilePath, 'w', encoding='utf-8') as f:
            f.write(accountsDbJson)

        return(0, 204, "No Content","","")

    # patch an Account Entry 
    # used to update password or roleId, or unlock, or enable/disable the account
    def patchAccountEntry(self, accountid, userAccountId, userPrivileges, doIfMatchEtag, patchData):
        # First, verify that the accountid is valid, 
        if accountid not in self.accountsDb.keys():
            return(4, 404, "Not Found","","")

        # verify that the patch data is good

        # first verify that ALL of the properties sent in patch data are patchable for redfish spec
        patchables=("Password","RoleId","Locked","Enabled")
        for prop in patchData:
            if( not prop in patchables ):
                return (4, 400, "Bad Request-one or more properties not patchable", "","")

        # xg7 
        # verify privilege is sufficient to change this property
        #    Privilege "ConfigureSelf" allows a user to change THEIR password, but no other property
        #    Privilege "ConfigureUsers" is required to change the other passwords
        #
        # if "Password" in patchData:
        #     note: we know user has either privilege ConfigureUsers or ConfigureSelf or both
        # if "ConfigureUsers" in userPrivileges:
        #   hasPrivilegeToPatchProperties=["Password","RoleId","Locked","Enabled"]
        # elif current user's accountId == target accountId
        #   hasPrivilegeToPatchProperties=["Password"]
        # else:
        #   hasPrivilegeToPatchProperties=[]
        # for prop in patchData:
        #     if not prop in hasPrivilegeToPatchProperties:
        #         return error, not authorized

        # xg7 just FYI
        #   self.accountsDict[accountid]=
        #       { "Locked": <locked>,  "FailedLoginCount": <failedLoginCnt>, "LockedTime": <lockedTimestamp>,
        #         "AuthFailTime": <authFailTimestamp> }

        # verify that the etag requirements are met
        # if request header had an If-Match: <etag>, verify the etag is still valid
        if doIfMatchEtag is not None:
            # first calculate eTag
            currentEtag=self.calculateAccountEtag(accountid)
            # verify they match
            if( doIfMatchEtag  != currentEtag["ETag"]):
                    return (4, 412, "If-Match Condition Failed", "","")

        # if Password was in patchData, verify value is good 
        if "Password" in patchData:
            password=patchData["Password"]
            # check if password length is less than value set in accountService MinPasswordLength
            if "MinPasswordLength" in self.accountServiceDb:
                if len(password) < self.accountServiceDb["MinPasswordLength"]:
                    return (4, 400, "Bad Request-Password length less than min", "","")
            if "MaxPasswordLength" in self.accountServiceDb:
                if len(password) > self.accountServiceDb["MaxPasswordLength"]:
                    return (4, 400, "Bad Request-Password length exceeds max", "","")
            #xg7 TODO
            # check if password meets regex requirements---no whitespace or ":"
            # passwordMatchPattern="^[^\s:]+$"
            # passwordMatch = re.search(passwordMatchPattern)
            # if not passwordMatch:
            #     return (4, 400, "Bad Request-invalid password-whitespace or : is not allowed", "","")
            #

        # if roleId was in patchData, verify value is good 
        if "RoleId" in patchData: 
            if not patchData["RoleId"] in self.rolesDb:
                return (4, 400, "Bad Request-roleId does not exist", "","")

        # check if Enabled is a boul
        if "Enabled" in patchData: 
            if (patchData["Enabled"] is not True) and (patchData["Enabled"] is not False):
                return (4, 400, "Bad Request-Enabled must be either True or False", "","")

        # check if Locked is a legal value.   a user can only set locked to False, not true
        if "Locked" in patchData: 
            if patchData["Locked"] is not False:
                return (4, 400, "Bad Request-Locked can only be set to False by user", "","")

        # if here, all values are good. Update the account dict
        updateDb=False
        for prop in patchData:
            if (prop == "Locked"):
                self.accountsDict[accountid][prop]=patchData[prop]
            else:
                updateDb=True
                self.accountsDb[accountid][prop]=patchData[prop]

        # write the data back out to the accountService database file
        if updateDb is True:
            accountsDbJson=json.dumps(self.accountsDb,indent=4)
            filename="AccountsDb.json"
            with open( self.accountsDbFilePath, 'w', encoding='utf-8') as f:
                f.write(accountsDbJson)

        return(0, 204, "No Content","","")


# end
# NOTES TODO
# if you patch a roleId to a user, verify that the role exists--DONE I think
# if you delete a role, verify that no user is assigned that role
# search for other TODOs
