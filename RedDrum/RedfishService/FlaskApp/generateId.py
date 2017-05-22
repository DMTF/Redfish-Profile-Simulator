
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md


import string
import random
def  rfGenerateId(leading="",size=8):
    chars=string.ascii_uppercase+string.digits
    respp=''.join(random.choice(chars) for _ in range(size))
    respp=leading+respp
    return(respp)
