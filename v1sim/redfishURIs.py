# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/blob/master/LICENSE.md

import json

from flask import Flask
from flask import request

from .flask_redfish_auth import RfHTTPBasicOrTokenAuth
from .resource import RfResource, RfResourceRaw, RfCollection


def rfApi_SimpleServer(root, versions, host="127.0.0.1", port=5000):
    app = Flask(__name__)

    # create auth class that does basic or redifish session auth
    auth = RfHTTPBasicOrTokenAuth()

    # define basic auth decorator used by flask
    # for basic auth, we only support user=catfish, passwd=hunter
    @auth.verify_basic_password
    def verify_rf_passwd(user, passwd):
        if user == "root":
            if passwd == "password123456":
                return True
        return False

    # define Redfish Token/Session auth decorator used by flask
    # for session token auth, only support toden: 123456CATFISHauthcode
    @auth.verify_token
    def verify_rf_token(auth_token):
        # lookup the user for this token
        # lookup the privileges for this user
        # check privilege
        # print("at verify_rf_token. auth_token={}".format(auth_token))
        if auth_token == "123456SESSIONauthcode":  # the magic token
            return True
        else:
            return False

    # define redfish URI APIs for flask

    # GET /redfish
    @app.route("/redfish", methods=['GET'])
    @app.route("/redfish/", methods=['GET'])
    def rf_versions():
        return versions.get_resource()

    # GET /redfish/v1
    @app.route("/redfish/v1", methods=['GET'])
    @app.route("/redfish/v1/", methods=['GET'])
    def rf_service_root():
        return root.get_resource()

    # GET /redfish/v1/$metadata
    @app.route("/redfish/v1/$metadata", methods=['GET'])
    def rf_metadata(rf_path='$metadata'):
        return resolve_path(root, rf_path)

    # GET /redfish/v1/odata
    @app.route("/redfish/v1/odata", methods=['GET'])
    @app.route("/redfish/v1/odata/", methods=['GET'])
    def rf_odata(rf_path='odata'):
        return resolve_path(root, rf_path)

    @app.route("/redfish/v1/<path:rf_path>", methods=['GET'])
    @app.route("/redfish/v1/<path:rf_path>/", methods=['GET'])
    @auth.rfAuthRequired
    def rf_subsystems(rf_path):
        return resolve_path(root, rf_path)

    # this is a special test API -- an authenticated service root
    @app.route("/redfish/v1/A", methods=['GET'])
    @auth.rfAuthRequired
    def rf_service_root2():
        print("root2")
        return root.get_resource()

    @app.route("/redfish/v1/Systems/<path:sys_path>", methods=['PATCH'])
    @app.route("/redfish/v1/Systems/<path:sys_path>/", methods=['PATCH'])
    @auth.rfAuthRequired
    def rf_computer_systempatch(sys_path):
        rdata = request.get_json(cache=True)
        print("rdata:{}".format(rdata))
        obj = patch_path(root.systems, sys_path)
        rc, status_code, err_string, resp = obj.patch_resource(rdata)
        if rc == 0:
            return "", status_code
        else:
            return err_string, status_code

    @app.route("/redfish/v1/Systems/<string:system_id>/Actions/ComputerSystem.Reset", methods=['POST'])
    @app.route("/redfish/v1/Systems/<string:system_id>/Actions/ComputerSystem.Reset/", methods=['POST'])
    @auth.rfAuthRequired
    def rf_computer_systemreset(system_id):
        # print("in reset")
        rdata = request.get_json(cache=True)
        # print("rdata:{}".format(rdata))
        rc, status_code, err_string, resp = root.components['Systems'].get_element(system_id).reset_resource(rdata)
        if rc == 0:
            return "", status_code
        else:
            return err_string, status_code

    @app.route("/redfish/v1/Systems/<string:system_id>/bios/Actions/Bios.ResetBios", methods=['POST'])
    @app.route("/redfish/v1/Systems/<string:system_id>/bios/Actions/Bios.ResetBios/", methods=['POST'])
    @auth.rfAuthRequired
    def rf_computer_biosreset(system_id):
        # print("in reset")
        rdata = request.get_json(cache=True)
        # print("rdata:{}".format(rdata))
        system = root.systems.get_element(system_id)
        bios = system.get_component("bios")
        rc, status_code, err_string, resp = bios.reset_resource(rdata)
        if rc == 0:
            return "", status_code
        else:
            return err_string, status_code

    @app.route("/redfish/v1/Systems/<string:system_id>/bios/Actions/Bios.ChangePassword", methods=['PATCH'])
    @app.route("/redfish/v1/Systems/<string:system_id>/bios/Actions/Bios.ChangePassword/", methods=['PATCH'])
    @auth.rfAuthRequired
    def rf_computer_change_pswd(system_id):
        # print("in reset")
        rdata = request.get_json(cache=True)
        # print("rdata:{}".format(rdata))
        system = root.systems.get_element(system_id)
        bios = system.get_component("bios")
        rc, status_code, err_string, resp = bios.change_password(rdata)
        if rc == 0:
            return "", status_code
        else:
            return err_string, status_code

    @app.route("/redfish/v1/Chassis/<string:chassis_id>/Actions/Chassis.Reset", methods=['POST'])
    @app.route("/redfish/v1/Chassis/<string:chassis_id>/Actions/Chassis.Reset/", methods=['POST'])
    @auth.rfAuthRequired
    def rf_computer_chassisreset(chassis_id):
        # print("in reset")
        rdata = request.get_json(cache=True)
        # print("rdata:{}".format(rdata))
        rc, status_code, err_string, resp = root.chassis.get_element(chassis_id).reset_resource(rdata)
        if rc == 0:
            return "", status_code
        else:
            return err_string, status_code

    @app.route("/redfish/v1/Chassis/<string:chassis_id>/Power", methods=['PATCH'])
    @app.route("/redfish/v1/Chassis/<string:chassis_id>/Power/", methods=['PATCH'])
    @auth.rfAuthRequired
    def rf_chassis_powerpatch(chassis_id):
        # rawdata=request.data
        rdata = request.get_json(cache=True)
        # print("RRrdata:{}".format(rdata))
        rc, status_code, err_string, resp = root.chassis.get_element(chassis_id).power.patch_resource(rdata)
        if rc == 0:
            return "", status_code
        else:
            return err_string, status_code

    @app.route("/redfish/v1/Managers/<string:manager_id>", methods=['PATCH'])
    @app.route("/redfish/v1/Managers/<string:manager_id>/", methods=['PATCH'])
    @auth.rfAuthRequired
    def rf_patch_manager_entity(manager_id):
        rdata = request.get_json(cache=True)
        # print("RRrdata:{}".format(rdata))
        rc, status_code, err_string, resp = root.managers.get_element(manager_id).patch_resource(rdata)
        if rc == 0:
            return "", status_code
        else:
            return err_string, status_code

    # rest/v1/Managers/1
    @app.route("/redfish/v1/Managers/<string:manager_id>/Actions/Manager.Reset", methods=['POST'])
    @app.route("/redfish/v1/Managers/<string:manager_id>/Actions/Manager.Reset/", methods=['POST'])
    @auth.rfAuthRequired
    def rf_reset_manager(manager_id):
        rdata = request.get_json(cache=True)
        # print("rdata:{}".format(rdata))
        rc, status_code, err_string, resp = root.managers.get_element(manager_id).reset_resource(rdata)
        if rc == 0:
            return "", status_code
        else:
            return err_string, status_code

    @app.route("/redfish/v1/Managers/<string:manager_id>/EthernetInterfaces/<string:eth_id>", methods=['PATCH'])
    @app.route("/redfish/v1/Managers/<string:manager_id>/EthernetInterfaces/<string:eth_id>/", methods=['PATCH'])
    @auth.rfAuthRequired
    def rf_patch_manager_nic_entity(manager_id, eth_id):
        resp = root.managers.get_element(manager_id).ethernetColl.get_interface(eth_id).get_resource()
        rdata = request.get_json(cache=True)
        # print("RRrdata:{}".format(rdata))
        ethernet_coll = root.managers.get_element(manager_id).ethernetColl
        rc, status_code, err_string, resp = ethernet_coll.get_interface(eth_id).patch_resource(rdata)
        if rc == 0:
            return "", status_code
        else:
            return err_string, status_code

    @app.route("/redfish/v1/SessionService", methods=['PATCH'])
    @app.route("/redfish/v1/SessionService/", methods=['PATCH'])
    @auth.rfAuthRequired
    def rf_patch_session_service():
        rdata = request.get_json(cache=True)
        # print("RRrdata:{}".format(rdata))
        rc, status_code, err_string, resp = root.sessionService.patch_resource(rdata)
        if rc == 0:
            return "", status_code
        else:
            return err_string, status_code

    # TODO: call root.sessionService.sessions.sessionLogin(usr,pwd), return resp, status_code, hdr
    # login API,  user catfish, password=hunter, authToken=123456CATFISHauthcode
    @app.route("/redfish/v1/SessionService/Sessions", methods=['POST'])
    def rf_login():
        print("login")
        rdata = request.get_json(cache=True)
        print("rdata:{}".format(rdata))
        if rdata["UserName"] == "root" and rdata["Password"] == "password123456":
            x = {"Id": "SESSION123456"}
            resp = json.dumps(x)
            print("resp:{}".format(resp))
            hdr = {"X-Auth-Token": "123456SESSIONauthcode",
                   "Location": "/redfish/v1/SessionService/Sessions/SESSION123456"}
            return resp, 201, hdr
        else:
            return "", 401

    # TODO: call root.sessionService.sessions.delete(sessId), return resp,status,hdr
    # logout API
    @app.route("/redfish/v1/SessionService/Sessions/<string:session_id>", methods=['DELETE'])
    @auth.rfAuthRequired
    def rf_session_logout(session_id):
        print("session logout %s" % session_id)
        # rdata=request.get_json(cache=True)
        # print("rdata:{}".format(rdata))
        return "", 204

    @app.route("/redfish/v1/AccountService", methods=['PATCH'])
    @auth.rfAuthRequired
    def rf_patch_account_service():
        rdata = request.get_json(cache=True)
        rc, status_code, err_string, resp = root.accountService.patch_resource(rdata)
        if rc == 0:
            return "", status_code
        else:
            return err_string, status_code
        
    def resolve_path(service, path):
        parts = path.split('/')
        result = service
        current_obj = service
        for part in parts:
            if isinstance(current_obj, RfCollection):
                result = current_obj.get_element(part)
                current_obj = result
            elif isinstance(current_obj, RfResource):
                result = current_obj.get_component(part)
                if not result:
                    result = current_obj.get_attribute(part)
                    break
                else:
                    current_obj = result

        if isinstance(result, (RfResource, RfResourceRaw)):
            return result.get_resource()
        else:
            return result

    def patch_path(service, path):
        parts = path.split('/')
        result = None
        current_obj = service
        for part in parts:
            if isinstance(current_obj, RfCollection):
                result = current_obj.get_element(part)
                current_obj = result
            elif isinstance(current_obj, RfResource):
                result = current_obj.get_component(part)
                if not result:
                    result = current_obj
                    break
                else:
                    current_obj = result
        return result

    '''
    @app.route("/rest/v1/xxx/x", methods=['GET'])
    def rfXxxx():
        resp=xxx.getObject()
        return(resp)
    '''

    # END file redfishURIs

    # start Flask REST engine running
    app.run(host=host, port=port)

    # never returns


'''
reference source links:
https://gist.github.com/lrei/2408383
http://docs.python-requests.org/en/v0.10.6/api/
http://flask.pocoo.org/docs/0.10/quickstart/

'''
