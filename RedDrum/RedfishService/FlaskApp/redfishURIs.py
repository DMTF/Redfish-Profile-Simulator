
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md


from flask import Flask
from flask import request, Response, send_from_directory 
import json
import os,re
from .flask_redfish_auth import RfHTTPBasicOrTokenAuth
from .authenticate import rfRegisterBasicAuthVerify
from .authenticate import rfRegisterTokenAuthVerify
#from .rootData import RfRoot
from .redfish_headers import rfcheckHeaders,rfaddHeaders
from flask import g
import base64

# Base RackManager class
#   rfr is a class with global data.
#   it includes rfr.root which is the root resource that everything hangs below
#   

def rfApi_RedDrum(rfr, rdm, host="127.0.0.1", port=5001):


    baseStaticPath=os.path.join(rfr.baseDataPath, "static" )
    varStaticPath=os.path.join(rfr.varDataPath, "static" )

    #app = Flask(__name__, static_folder=staticPath)
    app = Flask(__name__)

    # create auth class that does basic or redifish session auth
    auth=RfHTTPBasicOrTokenAuth()

    # register the authentication callback routines 
    # these functions are in ./authenticate.py
    rfRegisterBasicAuthVerify(auth,rfr)
    rfRegisterTokenAuthVerify(auth,rfr)



    # -----------------------------------------------------------------------
    #define redfish URI APIs for flask
    # -----------------------------------------------------------------------


    #GET /redfish      
    #  -no auth, static, json -- get for memory cached resource
    @app.route("/redfish",methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    def rfGetVersions():
        resp=rfr.root.serviceVersions.getResource()
        g.resp = json.loads(resp)
        if request.method=='GET':
            return(resp)
        else:
            return ("")

    #GET /redfish/v1/   
    #  -no auth, static, json -- get for memory cached resource
    @app.route("/redfish/v1/", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    def rfServiceRoot1():
        resp=rfr.root.getResource()
        g.resp = json.loads(resp)
        if request.method=='GET':
            return(resp)
        else:
            return ("")

    #GET /redfish/v1    
    #  -no auth, static, json -- get for memory cached resource
    @app.route("/redfish/v1", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    def rfServiceRoot():
        resp=rfr.root.getResource()
        g.resp = json.loads(resp)
        if request.method=='GET':
            return(resp)
        else:
            print(g.resp)
            return ("")

    # -----------------------------------------------------------------------

    #GET /redfish/v1/odata    
    #  -no auth, static, json -- get from file
    @app.route("/redfish/v1/odata",methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    def rfOdataServiceDoc():
        g.resp = json.loads(open(os.path.join(baseStaticPath,"OdataServiceDocument.json")).read())
        if request.method=='GET':
            return send_from_directory( baseStaticPath, "OdataServiceDocument.json", 
                                    add_etags=False, mimetype='application/json')
        else:
            return("")

    #GET /redfish/v1/$metadata    
    #  -no auth, static, xml --get from file
    @app.route("/redfish/v1/$metadata",methods=['GET','HEAD'])
    @rfcheckHeaders(rfr,metadata=True)
    @rfaddHeaders(rfr,metadata=True)
    def rfOdataMetadata():
        if request.method=='GET':
            return send_from_directory( baseStaticPath, "ServiceMetadata.xml", 
                                    add_etags=False, mimetype='application/xml')
        else:
            return("")
    # -----------------------------------------------------------------------

    #GET /redfish/v1/redDrumInfo    
    #  -auth/login, static, json -- get for memory cached resource
    @app.route("/redfish/v1/redDrumInfo", methods=['GET','HEAD'])
    #@auth.rfAuthRequired(privilege=[["ConfigureUsers","Login"],["Login","ME"]])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfGetRedDrumServiceInfo():
        resp=rfr.root.redDrumServiceInfo.getResource()
        g.resp = json.loads(resp)
        if request.method=='GET':
            return(resp)
        else:
            return ("")
    
    # -----------------------------------------------------------------------

    #GET /redfish/v1/Registries    
    #  -auth, static, json -- get from file
    @app.route("/redfish/v1/Registries",methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfRegistriesCollection():
        g.resp = json.loads(open(os.path.join(baseStaticPath,"RegistriesCollection.json")).read()) 
        if request.method=='GET':
            return send_from_directory( baseStaticPath, "RegistriesCollection.json", 
                                    add_etags=False, mimetype='application/json')
        else:
            return("")

    #GET /redfish/v1/Registries/<registry>    
    #  -auth, static, json -- get from file
    @app.route("/redfish/v1/Registries/<registry>",methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfRegistriesFile(registry):
        registriesStaticPath=os.path.join(rfr.baseDataPath, "Registries" )
        registryFile=registry + ".json"
        g.resp = json.loads(open(os.path.join(registriesStaticPath, registryFile)).read()) 
        print(" path: {},  file: {}".format(registriesStaticPath, registryFile))
        if request.method=='GET':
            return send_from_directory( registriesStaticPath, registryFile, 
                                    add_etags=False, mimetype='application/json')
        else:
            return("")
    # -----------------------------------------------------------------------

    #GET /redfish/v1/JsonSchemas    
    #  -auth, static, json -- get from file
    @app.route("/redfish/v1/JsonSchemas",methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfJsonSchemasCollection():
        g.resp = json.loads(open(os.path.join(baseStaticPath,"JsonSchemaCollection.json")).read())
        if request.method=='GET':
            return send_from_directory( baseStaticPath, "JsonSchemaCollection.json", 
                                    add_etags=False, mimetype='application/json')
        else:
            return("")

    #GET /redfish/v1/JsonSchemas/<jsonSchema>    
    #  -auth, static, json -- get from file
    @app.route("/redfish/v1/JsonSchemas/<jsonSchema>",methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfJsonSchemaFile(jsonSchema):
        jsonSchemaStaticPath=os.path.join(rfr.baseDataPath, "JsonSchemas" )
        jsonSchemaFile=jsonSchema  + ".json"
        g.resp = json.loads(open(os.path.join(jsonSchemaStaticPath,jsonSchemaFile)).read())
        print(" path: {},  file: {}".format(jsonSchemaStaticPath, jsonSchemaFile))
        if request.method=='GET':
            return send_from_directory( jsonSchemaStaticPath, jsonSchemaFile, 
                                    add_etags=False, mimetype='application/json')
        else:
            return("")

# -----------------------------------------------------------------------
    #   API to read one of the static DMTF-defined json-formatted Redfish schema files
    #   this is not strictly part of Redfish
    #   but the JsonSchema files we generate point to these APIs
    #   this GET returns the full file
    #GET /redfish/v1/DmtfJsonSchemaFiles/<schemaFile>    
    #  -unauthenticated static, json -- get from file
    @app.route("/redfish/v1/DmtfJsonSchemaFiles/<schemaFile>",methods=['GET','HEAD'])
    #@rfcheckHeaders(rfr,schemafile=True)
    @rfaddHeaders(rfr,schemafile=True)
    #@auth.rfAuthRequired(privilege=[["None"]])
    def rfDmtfJsonSchemaFiles(schemaFile):
        dmtfJsonSchemaStaticPath=os.path.join(rfr.baseDataPath, "DMTFSchemas" )
        #g.resp = json.loads(open(os.path.join(jsonSchemaStaticPath,schemaFile)).read())
        #print(" path: {},  file: {}".format(jsonSchemaStaticPath, jsonSchemaFile))
        if request.method=='GET':
            return send_from_directory( dmtfJsonSchemaStaticPath, schemaFile, 
                                    add_etags=False, mimetype='application/json')
        else:
            return("")


    # -----------------------------------------------------------------------

    # SessionService URIs

    # GET /redfish/v1/SessionService
    #   -auth, generated from template and sessionServiceDb
    @app.route("/redfish/v1/SessionService", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfGetSessionService():
        resp=rfr.root.sessionService.getSessionServiceResource()
        g.resp = json.loads(resp)
        if request.method=='GET':
            return(resp)
        else:
            return ("")


    # PATCH /redfish/v1/SessionService
    #    -auth, updates sessionServiceDb
    @app.route("/redfish/v1/SessionService", methods=['PATCH'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["ConfigureManager"]],rdata=rfr)
    def rfPatchSessionService():     
        rdata=request.get_json(cache=True)
        rc,statusCode,errString,resp=rfr.root.sessionService.patchSessionServiceResource(rdata)
        if(rc==0):
            return("",statusCode)
        else: # error
            return("",statusCode)


    # GET /redfish/v1/SessionService/Sessions  --get sessions collection
    #    -auth, generated from template and sessionsDict    
    @app.route("/redfish/v1/SessionService/Sessions", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfGetSessions():
        resp=rfr.root.sessionService.getSessionsCollectionResource()
        g.resp = json.loads(resp)
        if request.method=='GET':
            return(resp)
        else:
            return ("")
    
    # GET /redfish/v1/SessionService/Sessions/<sessionid> --get session entry
    #    -auth, generated from template and sessionsDict
    @app.route("/redfish/v1/SessionService/Sessions/<sessionid>", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    # TODO: check privilege?
    def rfGetSessionsEntry(sessionid):
        rc,statusCode,errString,resp,hdr=rfr.root.sessionService.getSessionEntry(sessionid)
        g.resp = json.loads(resp)
        if request.method=='GET':
            if(rc==0):
                return(resp,statusCode,hdr)
            else:
                return("",statusCode,"")
        else:
            return ("")

    # login API
    # POST to /redfish/v1/SessionService/Sessions
    #  -No auth required,  adds another session entry to the sessionsDict
    @app.route("/redfish/v1/SessionService/Sessions", methods=['POST'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    def rfLogin():
        if request.scheme == 'https':
            pass
        elif rfr.RedfishAllowSessionLoginOverHttp == 'true':
            pass
        elif 'X_RM_HTTPS_ENABLED' in request.headers and request.headers['X_RM_HTTPS_ENABLED'] == 'True':
            return Response('301-Redirection', 301, {'Location': 'https://redfish/v1/SessionService/Sessions' } )
        else:
            return Response('401-Unauthorized', 401)

        rdata=request.get_json(cache=True)
        rc,statusCode,errString,resp,hdr=rfr.root.sessionService.postSessionsResource(rfr,rdata)
        g.location = True
        g.loc_hdr = hdr
        if(rc==0):
            return(resp,statusCode,hdr)
        else:
            return("",statusCode,"")


    # logout API
    # DELETE /redfish/v1/SessionService/Sessions/<sessionid> 
    #   -auth,  removes the session entry from the sessionsDict
    @app.route("/redfish/v1/SessionService/Sessions/<sessionid>", methods=['DELETE'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    #@auth.rfAuthRequired(privilege=[["ConfigureManager"],["ConfigureSelf"]])
    @auth.rfAuthRequired(privilege=[["ConfigureUser"],["Login"]],rdata=rfr)
    def rfSessionLogout(sessionid):
        rc,statusCode,errString,resp,hdr=rfr.root.sessionService.deleteSession(sessionid)
        if(rc==0):
            return(resp,statusCode,hdr)
        else:
            return("",statusCode,"")

    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    #  AccountService URIs

    # GET /redfish/v1/AccountService   --get account service
    #    -auth, generated from template and accountService database file
    @app.route("/redfish/v1/AccountService", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    #@auth.rfAuthRequired(privilege=[["ConfigureManager"],["ConfigureUser"]])
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfGetAccountService():
        resp=rfr.root.accountService.getAccountServiceResource()
        g.resp = json.loads(resp)
        if request.method=='GET':
            return(resp)
        else:
            return ("")

    # PATCH /redfish/v1/AccountService   --patch account service
    #    -auth, update patch properties in AccountService database file
    #    -returns 204-No Content
    @app.route("/redfish/v1/AccountService", methods=['PATCH'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["ConfigureUser"]],rdata=rfr)
    def rfPatchAccountService():     
        rdata=request.get_json(cache=True)
        rc,statusCode,errString,resp=rfr.root.accountService.patchAccountServiceResource(rdata)
        if(rc==0):
            return("",statusCode)
        else: # error
            return("",statusCode)


    # ------------------------------------------------------------

    # GET /redfish/v1/AccountService/Roles -- get roles collection
    #    -auth, generated from template and roleDb file
    @app.route("/redfish/v1/AccountService/Roles", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfGetRoles():
        resp=rfr.root.accountService.getRolesCollectionResource()
        g.resp = json.loads(resp)
        if request.method=='GET':
            return(resp)
        else:
            return ("")


    # GET /redfish/v1/AccountService/Role/<roleId>  -- get role entry
    #    -auth, generated from template and roleDb file and rolesDict
    @app.route("/redfish/v1/AccountService/Roles/<roleId>", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfGetRoleId(roleId):
        rc,statusCode,errString,resp,hdr=rfr.root.accountService.getRoleEntry(roleId)
        g.resp = json.loads(resp)
        if request.method=='GET':
            if(rc==0):
                return(resp,statusCode,hdr)
            else:
                return("",statusCode,"")  
        else:
            return ("")
        



    # add a custom Role
    # POST to /redfish/v1/AccountService/Roles
    #  -auth required,  adds another role entry to the rolesDb
    @app.route("/redfish/v1/AccountService/Roles", methods=['POST'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["ConfigureUser"]],rdata=rfr)
    def rfPostRoles():
        rdata=request.get_json(cache=True)
        rc,statusCode,errString,resp,hdr=rfr.root.accountService.postRolesResource(rdata)
        g.location = True
        g.loc_hdr = hdr
        if(rc==0):
            return(resp,statusCode,hdr)
        else:
            return("",statusCode,"")   

    # delete a custom role
    # DELETE /redfish/v1/AccountService/Roles/<roleid> 
    #   -auth,  removes the role entry from the rolesDb
    @app.route("/redfish/v1/AccountService/Roles/<roleid>", methods=['DELETE'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["ConfigureUsers"]],rdata=rfr)
    def rfDeleteRole(roleid):
        rc,statusCode,errString,resp,hdr=rfr.root.accountService.deleteRole(roleid)
        if(rc==0):
            return(resp,statusCode,hdr)
        else:
            return("",statusCode,"")   

    #xg7
    # update a custom role entry -- patch user account
    # PATCH /redfish/v1/AccountService/Roles/<roleId>
    #    -auth, write to a property in the role
    @app.route("/redfish/v1/AccountService/Roles/<roleId>", methods=['PATCH'])
    @auth.rfAuthRequired(privilege=[["ConfigureUsers"]],rdata=rfr)
    def rfPatchRoleEntry(roleId):     
        rdata=request.get_json(cache=True)
        rc,statusCode,errString,resp,hdr=rfr.root.accountService.patchRoleEntry(roleId, rdata)
        if(rc==0):
            return("",statusCode)
        else: # error
            return("",statusCode)

    # ------------------------------------------------------------
    
    # GET /redfish/v1/AccountService/Accounts -- get accounts collection
    #    -auth, generated from template and accountsDb file
    @app.route("/redfish/v1/AccountService/Accounts", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfGetAccounts():
        resp=rfr.root.accountService.getAccountsCollectionResource()
        g.resp = json.loads(resp)
        if request.method=='GET':
            return(resp)
        else:
            return ("")
    

    # GET /redfish/v1/AccountService/Accounts/<accountId>  -- get account entry
    #    -auth, generated from template and accountsDb file and accountsDict
    @app.route("/redfish/v1/AccountService/Accounts/<accountId>", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    #@auth.rfAuthRequired(privilege=[["ConfigureUsers"],["ConfigureSelf"]])
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfGetAccountId(accountId):
        rc,statusCode,errString,resp,hdr=rfr.root.accountService.getAccountEntry(accountId)
        #xgAbi NOTE this is returning the etag header in hdr
        g.accountService=True
        g.etag_hdr = hdr
        g.resp = json.loads(resp)
        if request.method=='GET':
            if(rc==0):
                return(resp,statusCode,hdr) #etag returned in hdr
            else:
                return("",statusCode,"")
        else:
            return ("")


    # This is a flask hook for after request. 
    # It is invoked for every post-request.
    # We would be able to update the response headers here.
    @app.after_request
    def after_request_call(response):
        req = g.get('accountService')
        etag_hdr = g.get('etag_hdr')
        resp = g.get('resp')
        if req and 'ETag' in etag_hdr:
           response.headers['etag'] = etag_hdr.get('ETag', None) 
        
        if ('Allow' in response.headers and any (x in response.headers['Allow'] for x in ('GET', 'HEAD') ) ):            
            if resp is not None and "@odata.type" in resp:    
                resourceOdataType=resp["@odata.type"]
                #the odataType format is:  <namespace>.<version>.<type>   where version may have periods in it 
                odataTypeMatch = re.compile('^#([a-zA-Z0-9]*)\.([a-zA-Z0-9\._]*)\.([a-zA-Z0-9]*)$')  
                resourceMatch = re.match(odataTypeMatch, resourceOdataType)
                if(resourceMatch is not None):                
                    namespace=resourceMatch.group(1)
                    version=resourceMatch.group(2)
                    uriofscheme = rfr.JsonSchemasBasePath + namespace +'.'+ version + ".json"
                    response.headers['Link'] = uriofscheme
        
        location_hdr = g.get('loc_hdr')
        # updated code to check 'Location' key in location_hdr.
        # This way it handles every scenario. If the location_hdr is None,
        #  the 'get' method is not available.
        if g.get('location') and 'Location' in location_hdr:
            response.headers['Location'] = location_hdr.get('Location', None)

        return response



    # add a user
    # POST to /redfish/v1/AccountService/Accounts
    #  -auth required,  adds another user to the accountsDb and accountsDict
    @app.route("/redfish/v1/AccountService/Accounts", methods=['POST'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["ConfigureUsers"]],rdata=rfr)
    def rfPostAccounts():
        rdata=request.get_json(cache=True)
        rc,statusCode,errString,resp,hdr=rfr.root.accountService.postAccountsResource(rdata)
        g.location = True
        g.loc_hdr = hdr
        if(rc==0):
            return(resp,statusCode,hdr) # hdr includes Etag and Location
        else:
            return("",statusCode,"")       

    # delete a user
    # DELETE /redfish/v1/AccountService/Accounts/<accountId> 
    #   -auth,  removes the account entry from the accountsDb and accountsDict
    @app.route("/redfish/v1/AccountService/Accounts/<accountId>", methods=['DELETE'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["ConfigureUsers"]],rdata=rfr)
    def rfDeleteAccount(accountId):
        rc,statusCode,errString,resp,hdr=rfr.root.accountService.deleteAccount(accountId)
        if(rc==0):
            return(resp,statusCode,hdr)
        else:
            return("",statusCode,"")   

    #xg7
    # update a user account-- patch user account
    # PATCH /redfish/v1/AccountService/Accounts/<accountId>
    #    -auth, write to a property in the account
    #    an admin with privilege "ConfigureUsers" can modify ANY account
    #    a user with privilege "ConfigureSelf" can modify only his account--the current authenticated acct
    @app.route("/redfish/v1/AccountService/Accounts/<accountId>", methods=['PATCH'])
    @auth.rfAuthRequired(privilege=[["ConfigureUsers"],["ConfigureSelf"]],rdata=rfr)
    def rfPatchAccountEntry(accountId):
        if request.scheme == 'https':
            pass
        elif rfr.RedfishAllowUserCredUpdateOverHttp == 'true':
            pass
        elif 'X_RM_HTTPS_ENABLED' in request.headers and request.headers['X_RM_HTTPS_ENABLED'] == 'True':
            return Response('302-Redirection', 302, {'Location': 'https://redfish/v1/AccountService/Accounts/'+accountId } )
        else:
            return Response('401-Unauthorized', 401)


        rdata=request.get_json(cache=True)

        # if an "if-match": <etag>  header was sent, then get the etag value. send None if no if-match was sent
        doIfMatchEtag=None
        if request.headers.get('if-match'):
            doIfMatchEtag=request.headers['if-match']  # get the etag sent with If-Match header to send

        # we will also send the privileges and accountId of the user that executed this API to patchAccountEntry 
        #    it needs this info to  process the complex per-property permissions associated with this resource
        # if using Basic Auth
        if request.headers.get('Authorization',None):
            # xgAbi)**** getusername,passwd from Authroization header.   HACK: usernm=root, passwd=calvin
            # -- Completed getting username, passwd from Authorizatioin header.
            # usernm="root"    #xg HACK
            # passwd="calvin"  #xg HACK
            auth = (str(base64.b64decode(str(request.headers['Authorization'])[6:])).replace('b','')).replace("'" , "").split(":")
            rc,errMsg,userAccountId,roleid,userPrivileges=rfr.root.accountService.getAccountAuthInfo(auth[0],auth[1])
            if( rc != 0 ):  # it didn't authenticate this time!   bugout 
                return("",401)
        # else if user was using Session Auth
        elif request.headers.get('X-Auth-Token',None):
            authTok=request.headers['X-Auth-Token']
            rc,errMsg,sessionid,authtoken,userPrivileges,userAccountId,usernm=rfr.root.sessionService.getSessionAuthInfo(
                   authtoken=authTok)
            if( rc != 0 ):  # it didn't authenticate this time!   bugout 
                return("",401)

        # call the patchAccountEntry function in accountService
        # Note that the patchAccountEntry() will return the Etag with the response in property "hdrs"
        rc,statusCode,errString,resp,hdrs=rfr.root.accountService.patchAccountEntry( accountId, 
                                                userAccountId, userPrivileges, doIfMatchEtag, rdata)
        if(rc==0):
            return("",statusCode)
        else: # error
            return("",statusCode)

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # Top-level Systems, Chassis, Managers Collection GETs

    # GET /redfish/v1/Systems
    #  -auth, 
    @app.route("/redfish/v1/Systems", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfSystems():
        resp=rfr.root.systems.getSystemsCollectionResource()
        g.resp = json.loads(resp)
        if request.method=='GET':
            return(resp)
        else:
            return ("")

    # GET /redfish/v1/Chassis
    #  -auth, 
    @app.route("/redfish/v1/Chassis", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfChassis():
        resp=rfr.root.chassis.getChassisCollectionResource()
        g.resp = json.loads(resp)
        if request.method=='GET':
            return(resp)
        else:
            return ("")

    # GET /redfish/v1/Managers
    #  -auth, 
    @app.route("/redfish/v1/Managers", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfManagers():
        resp=rfr.root.managers.getManagersCollectionResource()
        g.resp = json.loads(resp)
        if request.method=='GET':
            return(resp)
        else:
            return ("")

    # -----------------------------------------------------------------------
    # Top-level Systems, Chassis, Managers   Member GETs


    # GET /redfish/v1/Systems/<sysid>  -- get system entry
    #    -auth, 
    @app.route("/redfish/v1/Systems/<sysid>", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfGetSystems(sysid):
        rc,statusCode,errString,resp,hdr=rfr.root.systems.getSystemEntry(sysid)
        g.resp = json.loads(resp)
        if request.method=='GET':
            if(rc==0):
                return(resp,statusCode,hdr)
            else:
                return("",statusCode,"")   
        else:
            return ("")


    # GET /redfish/v1/Chassis/<chassisid>  -- get account entry
    #    -auth, 
    @app.route("/redfish/v1/Chassis/<chassisid>", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfGetChassis(chassisid):
        rc,statusCode,errString,resp,hdr=rfr.root.chassis.getChassisEntry(chassisid)
        g.resp = json.loads(resp)
        if request.method=='GET':
            if(rc==0):
                return(resp,statusCode,hdr)
            else:
                return("",statusCode,"")   
        else:
            return ("")


    # GET /redfish/v1/Managers/<mgrid>  -- get account entry
    #    -auth, 
    @app.route("/redfish/v1/Managers/<mgrid>", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfGetManagers(mgrid):
        rc,statusCode,errString,resp,hdr=rfr.root.managers.getManagerEntry(mgrid)
        g.resp = json.loads(resp)
        if request.method=='GET':
            if(rc==0):
                return(resp,statusCode,hdr)
            else:
                return("",statusCode,"")   
        else:
            return ("")

    # -----------------------------------------------------------------------
    # Chassis  Power and Thermal resources

    # GET /redfish/v1/Chassis/<chassisid>/Power  -- get account entry
    #    -auth, 
    @app.route("/redfish/v1/Chassis/<chassisid>/Power", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfGetChassisPower(chassisid):
        rc,statusCode,errString,resp,hdr=rfr.root.chassis.getChassisEntryPower(chassisid)
        g.resp = json.loads(resp)
        if request.method=='GET':
            if(rc==0):
                return(resp,statusCode,hdr)
            else:
                return("",statusCode,"")   
        else:
            return ("")

    # GET /redfish/v1/Chassis/<chassisid>/Thermal  -- get account entry
    #    -auth, 
    #xg77
    @app.route("/redfish/v1/Chassis/<chassisid>/Thermal", methods=['GET','HEAD'])
    @rfcheckHeaders(rfr)
    @rfaddHeaders(rfr)
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfGetChassisThermal(chassisid):
        rc,statusCode,errString,resp,hdr=rfr.root.chassis.getChassisEntryThermal(chassisid)
        g.resp = json.loads(resp)
        if request.method=='GET':
            if(rc==0):
                return(resp,statusCode,hdr)
            else:
                return("",statusCode,"")   
        else:
            return ("")

    # -----------------------------------------------------------------------

    # PATCH /redfish/v1/Chassis/<chassisid>
    #    -auth, write to IndicatorLED or AssetTag
    # xg999 fix priv 
    @app.route("/redfish/v1/Chassis/<chassisid>", methods=['PATCH'])
    @auth.rfAuthRequired(privilege=[["Login"]],rdata=rfr)
    def rfPatchChassisEntry(chassisid):     
        rdata=request.get_json(cache=True)
        rc,statusCode,errString,resp=rfr.root.chassis.patchChassisEntry(chassisid, rdata)
        if(rc==0):
            return("",statusCode)
        else: # error
            return("",statusCode)

    # -----------------------------------------------------------------------
    '''
    
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
    
    # -----------------------------------------------------------------------

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


    # -----------------------------------------------------------------------


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

    '''
    '''
    #this is a special test API -- an authenticated service rfr.root        
    @app.route("/redfish/v1/A", methods=['GET'])
    @auth.rfAuthRequired(privilege=[["Login"]])
    def rfServiceRoot2():
         print("root2")
         resp=root.getResource()
         return(resp)
    '''

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

    
