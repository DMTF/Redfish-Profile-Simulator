
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

#
# un-commend the section of imports for the RedfishService implementation
#   that you want to run
#   Currently, only FlaskApp is implemented

# FlaskApp Service
from .FlaskApp import RfServiceRoot
from .FlaskApp import RdRoot
from .FlaskApp import rfApi_RedDrum
def getServiceName():
	return ("FlaskApp")



'''
# TBD BottleApp  Service
from .BottleApp import RfServiceRoot
from .BottleApp import RfRoot
from .BottleApp import rfApi_RackManager

def getServiceName():
	return ("BottleApp")

'''

