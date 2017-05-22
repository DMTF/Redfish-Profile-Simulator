# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

# un-comment the sub-folder for the Backend that you want to enable

#from .BullRed_RackManager import RedDrumBackend
from .OpenBMC import RedDrumBackend
#from .Simulator import RedDrumBackend
