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
* Initial resources are loaded from a catfish mockup into python dictionary structures
  * After that, data is read/patched... to the dictionaries
* Supports BasicAuth, as well as Redfish Session Auth  (for one session, one user)
* Uses:
  * easy to add new URIs for testing a client
  * easy to tweak behavior or add bad responses to test a client
  * allows testing of authentication -- which current mockup servers dont do
  * easy to insert print statements in service to see if data coming across good..etc

### Current Limitation:
  * supports a single user/passwd and token
  * the user/passwd is:   root/password123456    
  * The authToken for Session Auth is: 123456SESSIONauthcode
  * Supports only HTTP  (not HTTPS)
  * with redfishtool, use options: redfishtool.py -r127.0.0.1:5000 -u root -p password123456 -S Never <subcmd>



## Usage
* ` python redfishProfileSimulatorMain.py [options]`

* `[Options]`:

		-V,  --Version,--- the program version
		-h,  --help,   --- help
		-H<hostIP>,  --Host=<hostIp>   --- host IP address. dflt=127.0.0.1
		-P<port>,--Port=<port> --- the port to use. dflt=5000
		-p<provile>, --profile=<profile>   --- the Redfish profile to use. dflt="SimpleOcpServerV1"
    
    
## Implementation
* The simulation includes an http server, RestEngine, and dynamic Redfish datamodel.
* You can GET, PATHCH,... to the service just like a real Redfish service.
* Both Basic and Redfish Session/Token authentication are supported 
  * for a single user/passwd and token
  * the user/passwd is:   root/password123456    
  * The authToken for Session Auth is: 123456SESSIONauthcode
  * these can be changed by editing the redfishURSs.py file---will make dynamic later.
* The http service and Rest engine is built on Flask, and all code is Python 3.4+
* The data model resources are "initialized" from the SPMF "SimpleOcpServerV1" Mockup.
  *  and stored as python dictionaries
  *  then the dictionaries are updated with patches, posts, deletes.
* The program can be extended to support other mockup \"profiles\".
* By default, the simulation runs on localhost (127.0.0.1), on port 5000.
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
  * No PSUs in model  (RMM spec did not include PSUs) 
  * No ProcessorInfo, MemoryInfo, StorageInfo, System-EthernetInterfaceInfo
  * No Tasks
  * JsonSchema and Registries collections left out (since that is optional)
  * No EventService--Remote Machine Management spec used basic PET alerts
  * Uses only the pre-defined privileges and roles


## TO DO
Some limitations to be extended in current implementation

* Auth supports a single hard-coded username, password, and AuthToken, although the protocol is 100% compliant with respect to testing clients trying to authenticate
  * ex with basic auth, you have to use the hard coded user/password
  * ex with Session Auth, you just use the hard coded AuthToken
* adding and deleting users not implemented--has 3 or 4 users predefined
* accountService properties can be written, but failed logins, lockouts, etc is not implemented
* system log not implemented yet









