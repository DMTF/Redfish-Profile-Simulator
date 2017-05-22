# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

There are 4 main parts to the upgraded Redfish Service Simulator:
Each part is in a separate folder below.

--redDrumMain.py
    -- this is the entry point to startup the RedDrum Redfish Service.
    -- call by calling the function redDrumMain()
    
--Httpd-Config
    -- describes 4 different HTTPD front-end configurations
    -- The base simulator uses the Flask Buildin Config--which requires no special processing or config here
    -- see the README in Httpd-Config/README for much more detail

--RedfishService
    -- this is the main Redfish Service code
    -- it creates a resource model for each api, and then starts the Flask service running to handlin requests

--Backend
    -- this is the implementation-specific backend code
    -- this is where code resides to connect the "RedfishService" to implementation-specific resource managers
       where data exists
    -- see the README in Backend for much more detail
