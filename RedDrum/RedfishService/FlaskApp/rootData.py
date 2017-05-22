
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

# global data structure class for RedDrum Redfish Service
class RdRoot():
    def __init__(self):
        self.program=None
        self.version=None
        self.profile=None
        self.baseDataPath=None
        self.varDataPath=None
        self.RedDrumConfPath=None
        self.root=None
        self.backend=None
        self.useCachedDiscoveryDb=True
        self.resourceDiscovery="Static"
        self.staticChassisConfig="dev112"

        self.magic=8899
        self.HttpHeaderCacheControl = None
        self.HttpHeaderServer = None
        self.JsonSchemasBasePath = None
        self.rsaDeepDiscovery=False

