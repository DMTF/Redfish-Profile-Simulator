# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tools/LICENSE.md

from flask import Flask
from flask import request
import json
from .flask_redfish_auth import RfHTTPBasicOrTokenAuth

def rfApi_SimpleServer(root,versions,host="127.0.0.1",port=5000):
    app = Flask(__name__)

    # create auth class that does basic or redifish session auth
    auth=RfHTTPBasicOrTokenAuth()

    #define basic auth decorator used by flask
    # for basic auth, we only support user=catfish, passwd=hunter
    @auth.verify_basic_password
    def  verifyRfPasswd(user,passwd):
        if( user=="root"):
            if(passwd=="password123456"):
                return(True)
        return(False) 


    #define Redfish Token/Session auth decorator used by flask
    # for session token auth, only support toden: 123456CATFISHauthcode
    @auth.verify_token
    def  verifyRfToken(auth_token):
        #lookup the user for this token
        #lookup the privileges for this user
        #check privilege
        #print("at verifyRfToken. auth_token={}".format(auth_token))
        if(auth_token=="123456SESSIONauthcode"):   #the magic token
            return(True)
        else:
            return(False)        



    #define redfish URI APIs for flask

    #GET /redfish
    @app.route("/redfish",methods=['GET'])
    def rfVersions():
        resp=versions.getResource()
        return(resp)

    #GET /redfish/odata
    @app.route("/redfish/v1/odata",methods=['GET'])
    def rfOdataServiceDoc():
        resp=root.odataServiceDoc.getResource()
        return(resp)
    
    #GET /redfish/$metadata
    @app.route("/redfish/v1/$metadata",methods=['GET'])
    def rfOdataMetadata():
        resp=root.odataMetadata.getResource()
        return(resp)
    
    #GET /rest/v1
    @app.route("/redfish/v1", methods=['GET'])
    def rfServiceRoot():
         resp=root.getResource()
         return(resp)
    #GET /rest/v1
        
    @app.route("/redfish/v1/", methods=['GET'])
    def rfServiceRoot1():
         resp=root.getResource()
         return(resp)

    #this is a special test API -- an authenticated service root        
    @app.route("/redfish/v1/A", methods=['GET'])
    @auth.rfAuthRequired
    def rfServiceRoot2():
         print("root2")
         resp=root.getResource()
         return(resp)

    #rest/v1/systems
    @app.route("/redfish/v1/Systems", methods=['GET'])
    @auth.rfAuthRequired
    def rfSystems():
        resp=root.systems.getResource()
        return(resp)

    #rest/v1/systems/1    
    @app.route("/redfish/v1/Systems/1", methods=['GET'])
    @auth.rfAuthRequired
    def rfComputerSystem1():
            resp=root.systems.system1.getResource()
            return(resp)

    
    #rest/v1/systems/1    
    @app.route("/redfish/v1/Systems/1", methods=['PATCH'])
    @auth.rfAuthRequired
    def rfComputerSystem1patch():
            rdata=request.get_json(cache=True)
            #print("rdata:{}".format(rdata))
            rc,statusCode,errString,resp=root.systems.system1.patchResource(rdata)
            if(rc==0):
                return("",statusCode)
            else: # error
                return("",statusCode)


    #rest/v1/systems/1    
    @app.route("/redfish/v1/Systems/1/Actions/ComputerSystem.Reset", methods=['POST'])
    @auth.rfAuthRequired
    def rfComputerSystem1reset():
            #print("in reset")
            rdata=request.get_json(cache=True)
            #print("rdata:{}".format(rdata))
            rc,statusCode,errString,resp=root.systems.system1.resetResource(rdata)
            if(rc==0):
                return("",statusCode)
            else: # error
                return("",statusCode)
            
    '''
    #/rest/v1/systems/1/Logs
    @app.route("/redfish/v1/Systems/1/Logs", methods=['GET']) 
    def rfSystem1LogsCollection():
            resp=root.systems.system1.logsCollection.getResource()
            return(resp)

    #/rest/v1/systems/1/Logs/SEL
    @app.route("/redfish/v1/Systems/1/Logs/SEL", methods=['GET']) 
    def rfSystem1LogService():
            resp=root.systems.system1.logsCollection.logService.getResource()
            return(resp)
        
    #/rest/v1/systems/1/Logs/SEL/Entries
    @app.route("/redfish/v1/Systems/1/Logs/SEL/Entries", methods=['GET']) 
    def rfSystem1LogEntryCollection():
            resp=root.systems.system1.logsCollection.logService.logEntryCollection.getResource()
            return(resp)
        
    #/rest/v1/systems/1/Logs/SEL/Entries/1 -- this is a stub for 1st entry
    @app.route("/redfish/v1/Systems/1/Logs/SEL/Entries/1", methods=['GET']) 
    def rfSystem1LogEntry1():
            resp=root.systems.system1.logsCollection.logService.logEntryCollection.logEntry1.getResource()
            return(resp)
    '''
    
    #rest/v1/chassis
    @app.route("/redfish/v1/Chassis", methods=['GET'])
    @auth.rfAuthRequired
    def rfChassis():
        resp=root.chassis.getResource()
        return(resp)
    
    @app.route("/redfish/v1/Chassis/1", methods=['GET'])
    @auth.rfAuthRequired
    def rfRackmountChassis1():
        resp=root.chassis.chassis1.getResource()
        return(resp)
    
    @app.route("/redfish/v1/Chassis/1/Power", methods=['GET'])
    @auth.rfAuthRequired
    def rfRackmountChassis1PowerMetrics():
        resp=root.chassis.chassis1.power.getResource()
        return(resp)

    @app.route("/redfish/v1/Chassis/1/Power", methods=['PATCH'])
    @auth.rfAuthRequired
    def rfChassisPowerpatch():
            #rawdata=request.data
            rdata=request.get_json(cache=True)
            #print("RRrdata:{}".format(rdata))
            rc,statusCode,errString,resp=root.chassis.chassis1.power.patchResource(rdata)
            if(rc==0):
                return("",statusCode)
            else: # error
                return("",statusCode)


    @app.route("/redfish/v1/Chassis/1/Thermal", methods=['GET'])
    @auth.rfAuthRequired
    def rfRackmountChassis1ThermalMetrics():
        resp=root.chassis.chassis1.thermal.getResource()
        return(resp)



    #/Managers URIs
    @app.route("/redfish/v1/Managers", methods=['GET'])
    @auth.rfAuthRequired
    def rfGetManagers():
        resp=root.managers.getResource()
        return(resp)

    @app.route("/redfish/v1/Managers/bmc", methods=['GET'])
    @auth.rfAuthRequired
    def rfGetManagerEntity():
        resp=root.managers.managerBmc.getResource()
        return(resp)

    @app.route("/redfish/v1/Managers/bmc", methods=['PATCH'])
    @auth.rfAuthRequired
    def rfPatchManagerEntity():     
        rdata=request.get_json(cache=True)
        #print("RRrdata:{}".format(rdata))
        rc,statusCode,errString,resp=root.managers.managerBmc.patchResource(rdata)
        if(rc==0):
            return("",statusCode)
        else: # error
            return("",statusCode)

    #rest/v1/Managers/1    
    @app.route("/redfish/v1/Managers/bmc/Actions/Manager.Reset", methods=['POST'])
    @auth.rfAuthRequired
    def rfResetManager():
            rdata=request.get_json(cache=True)
            #print("rdata:{}".format(rdata))
            rc,statusCode,errString,resp=root.managers.managerBmc.resetResource(rdata)
            if(rc==0):
                return("",statusCode)
            else: # error
                return("",statusCode)


    @app.route("/redfish/v1/Managers/bmc/NetworkProtocol", methods=['GET'])
    @auth.rfAuthRequired
    def rfGetManagerNetworkService():
        resp=root.managers.managerBmc.networkProtocol.getResource()
        return(resp)

    @app.route("/redfish/v1/Managers/bmc/EthernetInterfaces", methods=['GET'])
    @auth.rfAuthRequired
    def rfGetManagerNICsCollection():
        resp=root.managers.managerBmc.ethernetColl.getResource()
        return(resp)

    @app.route("/redfish/v1/Managers/bmc/EthernetInterfaces/eth0", methods=['GET'])
    @auth.rfAuthRequired
    def rfGetManagerNicEntity():
        resp=root.managers.managerBmc.ethernetColl.eth0.getResource()
        return(resp)
    
    @app.route("/redfish/v1/Managers/bmc/EthernetInterfaces/eth0", methods=['PATCH'])
    @auth.rfAuthRequired
    def rfPatchManagerNicEntity():
        resp=root.managers.managerBmc.ethernetColl.eth0.getResource()
        rdata=request.get_json(cache=True)
        #print("RRrdata:{}".format(rdata))
        rc,statusCode,errString,resp=root.managers.managerBmc.ethernetColl.eth0.patchResource(rdata)
        if(rc==0):
            return("",statusCode)
        else: # error
            return("",statusCode)


    
    #/SessionService URIs
    @app.route("/redfish/v1/SessionService", methods=['GET'])
    @auth.rfAuthRequired
    def rfGetSessionService():
        resp=root.sessionService.getResource()
        return(resp)

    
    @app.route("/redfish/v1/SessionService", methods=['PATCH'])
    @auth.rfAuthRequired
    def rfPatchSessionService():     
        rdata=request.get_json(cache=True)
        #print("RRrdata:{}".format(rdata))
        rc,statusCode,errString,resp=root.sessionService.patchResource(rdata)
        if(rc==0):
            return("",statusCode)
        else: # error
            return("",statusCode)

        
    @app.route("/redfish/v1/SessionService/Sessions", methods=['GET'])
    @auth.rfAuthRequired
    def rfGetSessions():
        resp=root.sessionService.sessions.getResource()
        return(resp)



    #TODO: root.sessionService.sessions.sessionGet(sessId)
    @app.route("/redfish/v1/SessionService/Sessions/SESSION123456", methods=['GET'])
    @auth.rfAuthRequired
    def rfGetSessionsEntry():
        resp=root.sessionService.sessions.session1.getResource()
        return(resp)

    # TODO: call root.sessionService.sessions.sessionLogin(usr,pwd), return resp, statuscode, hdr
    # login API,  user catfish, password=hunter, authToken=123456CATFISHauthcode
    @app.route("/redfish/v1/SessionService/Sessions", methods=['POST'])
    def rfLogin():
        print("login")
        rdata=request.get_json(cache=True)
        print("rdata:{}".format(rdata))
        if( ( rdata["UserName"] == "root" ) and ( rdata["Password"] == "password123456")):
            x={"Id": "SESSION123456"}
            resp=(json.dumps(x))
            print("resp:{}".format(resp))
            hdr={"X-Auth-Token": "123456SESSIONauthcode", "Location": "/redfish/v1/SessionService/Sessions/SESSION123456"}
            return(resp,200,hdr)
        else:
            return("",401)

    # TODO: call root.sessionService.sessions.delete(sessId), return resp,status,hdr
    # logout API
    @app.route("/redfish/v1/SessionService/Sessions/SESSION123456", methods=['DELETE'])
    @auth.rfAuthRequired
    def rfSessionLogout():
        print("session logout")
        #rdata=request.get_json(cache=True)
        #print("rdata:{}".format(rdata))
        return("",204)
 


    #AccountService URIs
    @app.route("/redfish/v1/AccountService", methods=['GET'])
    @auth.rfAuthRequired
    def rfGetAccountService():
        resp=root.accountService.getResource()
        return(resp)

    @app.route("/redfish/v1/AccountService", methods=['PATCH'])
    @auth.rfAuthRequired
    def rfPatchAccountService():     
        rdata=request.get_json(cache=True)
        #print("RRrdata:{}".format(rdata))
        rc,statusCode,errString,resp=root.accountService.patchResource(rdata)
        if(rc==0):
            return("",statusCode)
        else: # error
            return("",statusCode)
    
    @app.route("/redfish/v1/AccountService/Accounts", methods=['GET'])
    @auth.rfAuthRequired
    def rfGetAccounts():
        resp=root.accountService.accounts.getResource()
        return(resp)
    
    @app.route("/redfish/v1/AccountService/Roles", methods=['GET'])
    @auth.rfAuthRequired
    def rfGetRoles():
        resp=root.accountService.roles.getResource()
        return(resp)

    @app.route("/redfish/v1/AccountService/Accounts/<accountId>", methods=['GET'])
    @auth.rfAuthRequired
    def rfGetAccountId(accountId):
        #print("account:{}".format(accountId))
        if(accountId=="root"):
            resp=root.accountService.accounts.account_root.getResource()
        if(accountId=="jane"):
            resp=root.accountService.accounts.account_jane.getResource()
        if(accountId=="john"):
            resp=root.accountService.accounts.account_john.getResource()
        return(resp)

    @app.route("/redfish/v1/AccountService/Roles/<roleId>", methods=['GET'])
    @auth.rfAuthRequired
    def rfGetRoleId(roleId):
        if(roleId=="Admin"):
            resp=root.accountService.roles.role_Admin.getResource()
        if(roleId=="Operator"):
            resp=root.accountService.roles.role_Operator.getResource()
        if(roleId=="ReadOnlyUser"):
            resp=root.accountService.roles.role_ReadOnlyUser.getResource()
        return(resp)


        
        resp=root.accountService.roles.role[roleId].getResource(roleId)
        return(resp)


    '''
    @app.route("/rest/v1/xxx/x", methods=['GET'])
    def rfXxxx():
        resp=xxx.getObject()
        return(resp)
    '''

    #END file redfishURIs

    # start Flask REST engine running
    app.run(host=host,port=port)

    #never returns

'''
reference source links:
https://gist.github.com/lrei/2408383
http://docs.python-requests.org/en/v0.10.6/api/
http://flask.pocoo.org/docs/0.10/quickstart/

'''
    
