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
from pkg_resources import resource_string, resource_filename

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

    rdr.RedDrumConf = resource_filename(__name__, 'RedDrum.conf')
    rdr.templatesBase = resource_filename(__name__, "/" )
    rdr.baseDataPath=os.path.join(rdr.templatesBase, "RedfishService", rdService,  "Data")
    print ("Startup CONF FILE: %s" % rdr.RedDrumConf )
    print ("Startup templatesBase: %s" % rdr.templatesBase )
    print ("Startup baseDataPath: %s" % rdr.baseDataPath )
    sys.stdout.flush()

    # Now update the default root data with any data stored in RedDrum.conf config file
    #    This includes the config parameteers for Authentication and header processing
    #    Anything from RedDrum.conf can be OVER_WRITTEN by Backend start code!
    config = configparser.ConfigParser(inline_comment_prefixes='#')
    # read multiple paths

    # system global read config
    config.read("/usr/share/RedDrum/RedDrum.conf")

    # system global writable config
    config.read("/etc/RedDrum/RedDrum.conf")

    # start with path inside tree (development or other)
    config.read(rdr.RedDrumConf)

    rdr.HttpHeaderCacheControl = config['Server Section']['HttpHeaderCacheControl'][1:-1]

    rdr.varDataPath = config['Server Section']['ServerCachePath']
    try:
        print ("Make dir: %s" % rdr.varDataPath)
        os.mkdir(rdr.varDataPath)
    except FileExistsError:
        pass
    for subdir in ["chassisDb", "db", "managersDb", "systemsDb", "static"]:
        try:
            print ("Make dir: %s" % os.path.join(rdr.varDataPath, subdir))
            os.mkdir(os.path.join(rdr.varDataPath, subdir))
        except FileExistsError:
            pass

    rdr.HttpHeaderServer = config['Server Section']['HttpHeaderServer'][1:-1]
    rdr.JsonSchemasBasePath = config['Server Section']['JsonSchemasBasePath'][1:-1]
    rdr.RedfishAllowAuthNone = config['Auth Section']['RedfishAllowAuthNone']
    rdr.RedfishAllowAuthenticatedAPIsOverHttp = config['Auth Section']['RedfishAllowAuthenticatedAPIsOverHttp']
    rdr.RedfishAllowBasicAuthOverHttp = config['Auth Section']['RedfishAllowBasicAuthOverHttp']
    rdr.RedfishAllowSessionLoginOverHttp = config['Auth Section']['RedfishAllowSessionLoginOverHttp']
    rdr.RedfishAllowUserCredUpdateOverHttp = config['Auth Section']['RedfishAllowUserCredUpdateOverHttp']


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



