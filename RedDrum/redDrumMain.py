# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

# Entry point for running RedDrum Redfish Service
#
# Initializes Http
#
# This program is dependent on the following Python packages that should be installed separately with pip:
#    pip install Flask
#
# standard python packages
import sys
import os
import configparser

from .RedfishService import getServiceName
from .RedfishService import RdRoot
from .Backend import RedDrumBackend

def redDrumMain(*args, **kwargs):
    # set top level redDrum defaults
    rdHost="127.0.0.1"
    rdPort=5001
    rdService = getServiceName()

    # create instance of RedDrum root data object and update program, version...
    # The root data currently is inside RedfishService.  Later, we may move it into RedDrum top-level
    rdr=RdRoot()
    rdr.program="redDrumMain"
    rdr.version="0.9.5"

    # startup the Backend
    #   Note that the Backend start code may change the root data in rdr to specify paths, etc
    #   cd the RedDrum/Backend and edit __init__.py to select a specific Backend
    rdbe = RedDrumBackend(rdr)
    rdr.backend=rdbe


    # if executing locally (keeping all data inside the installed directory), update paths to override backend
    #   this is over-riding whatever paths the Backend put in
    #   this is used when developer testing or if running simulator
    if kwargs["isLocal"]:
        rdSvcPath=os.getcwd() # where we are executing from
        rdr.RedDrumConfPath = os.path.join(rdSvcPath, "RedDrum","RedDrum.conf" ) # use the LOCAL RedDrum.conf
        rdr.varDataPath=os.path.join(rdSvcPath, "RedDrum", "RedfishService", rdService,  "Data", "var", "www", "rf")
        rdr.baseDataPath=os.path.join(rdSvcPath, "RedDrum","RedfishService", rdService,  "Data")
        print("   Local Execution")
        sys.stdout.flush()


    # Now update the default root data with any data stored in RedDrum.conf config file
    #    This includes the config parameteers for Authentication and header processing
    #    Anything from RedDrum.conf can be OVER_WRITTEN by Backend start code!
    try:
        config = configparser.ConfigParser(inline_comment_prefixes='#')
        config.read(rdr.RedDrumConfPath)
        rdr.HttpHeaderCacheControl = config['Server Section']['HttpHeaderCacheControl'][1:-1]
        rdr.HttpHeaderServer = config['Server Section']['HttpHeaderServer'][1:-1]
        rdr.JsonSchemasBasePath = config['Server Section']['JsonSchemasBasePath'][1:-1]
        rdr.RedfishAllowAuthNone = config['Auth Section']['RedfishAllowAuthNone']
        rdr.RedfishAllowAuthenticatedAPIsOverHttp = config['Auth Section']['RedfishAllowAuthenticatedAPIsOverHttp']
        rdr.RedfishAllowBasicAuthOverHttp = config['Auth Section']['RedfishAllowBasicAuthOverHttp']
        rdr.RedfishAllowSessionLoginOverHttp = config['Auth Section']['RedfishAllowSessionLoginOverHttp']
        rdr.RedfishAllowUserCredUpdateOverHttp = config['Auth Section']['RedfishAllowUserCredUpdateOverHttp']
    except IOError:
        print ("Error: RM Config File does not appear to exist.")


    # import the RedfishService classes and code we run from main.
    #     this instantiates all of the RedfishService resource--they all live "under" the ServiceRoot
    from .RedfishService import RfServiceRoot

    
    # import the API to the Main RedfishService function
    #     rfApi_RackManager  is a function in ./RedfishService/FlaskApp/redfishURIs.py.
    #     It loads the flask APIs (URIs), and starts the flask service
    from .RedfishService  import rfApi_RedDrum

    # Now create the root service resource object
    #     This will create Python dictionary for all resources under the root service 
    #     It also runs phase-1 discovery 
    rdr.root=RfServiceRoot(rdr )

    # start the flask REST API service for RackManager
    #     THis does not return unless the Flask App exits
    #     Once this is called, Flask is handling Fron-end APIs from user
    rfApi_RedDrum(rdr, rdbe, host=kwargs["rdHost"], port=kwargs["rdPort"])

    # Notes
    # http://127.0.0.1:5001/

    # flask api syntax
    # app.run(host="0.0.0.0") # run on all IPs
    # run(host=None, port=None, debug=None, **options)
    #   host=0.0.0.0 server avail externally -- all IPs
    #   host=127.0.0.1 is default
    #   port=5001 default, or port defined in SERVER_NAME config var



