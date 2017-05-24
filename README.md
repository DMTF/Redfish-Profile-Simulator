Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# Redfish Profile Simulator
## About
***Redfish Profile Simulator***
is a Python34 real simulator of the "simple monolithic server" feature profile.

  *  A simple, minimal Redfish Service
  *  For a monolithic Server
  *  Aligned with: OCP Remote Machine Management Spec feature set

### v0.9.5 is a major upgrade based on the "RedDrum" RedfishService
* see the CHANGELOG for upgraded features
  * all authentication and authorization is now 100% supported, with multiple users
    * BasicAuth or SessionAuth
  * you can add users and roles
  * all hard codings of IDs in the main Rest engine are removed.
  * supports different front-end httpd configs or backends to handle real data (or simulatiosn)
    * unless you use a front-end httpd (as described in the Httpd-Configs README, the base simulator
      here runs only http
* Limitations
  * configureSelf is not working -- allws anyone to change any users passwords
  * GET JsonSchemas and GET Registeries is not complete 
  * 2nd level system resource not implemented since not in the Simple OCP profile
  * the initial simulation backend doesnt handle power state change when the system is powered-off/on using an action
    * easy fix, coming

* how to invoke:
  * pull the Redfish-Profile-Simulator to a local directory
  * from that directory, run `python3.4 redDrum-RedfishService.py`
  * the default IP/port is 127.0.0.1:5001
  * the root user/password is root:calvin
    * other users:   john:john123    jane:jane123     albert:albert123

### Description
* Based on flask


## Usage
* ` python3.4 RedDrum-RedfishService.py

* `[Options]`:

		-V,  --Version,--- the program version
		-h,  --help,   --- help
		-H<hostIP>,  --Host=<hostIp>   --- host IP address. dflt=127.0.0.1
		-P<port>,--Port=<port> --- the port to use. dflt=5000
    
    
## Implementation
* The simulation includes an http server, RestEngine, and dynamic Redfish datamodel.
* You can GET, PATHCH,... to the service just like a real Redfish service.
* Both Basic and Redfish Session/Token authentication are supported 
  * user root has password calvin
* By default, the simulation runs on localhost (127.0.0.1), on port 5001.
  * These can be changed with CLI options: -P<port> -H <hostIP>  | --port=<port> --host=<hostIp>

## Simple OCP Server V1 Mockup Description
* A Monolithic server:
  * One ComputerSystem
  * One Chassis
  * One Manager

* Provides basic management features aligned with OCP Remote Machine Management Spec 1.01:
  * Power-on/off/reset
  * Boot to PXE, HDD, BIOS setup (boot override)
  * 4 temp sensors per DCMI (CPU1, CPU2, Board, Inlet)
  * Simple Power Reading, and  DCMI Power Limiting
  * Fan Monitoring w/ redundancy
  * Set asset tag and Indicator LED
  * Basic inventory (serial#, model, SKU, Vendor, BIOS ver…)
  * User Management
  * BMC management: get/set IP, version, enable/disable protocol

* What it does NOT have -- that the Redfish 1.0 model supports
  * No ProcessorInfo, MemoryInfo, StorageInfo, System-EthernetInterfaceInfo
  * No Tasks


## TO DO
* ...








