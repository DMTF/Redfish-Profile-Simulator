# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/blob/main/LICENSE.md

import os

from .resource import RfResource, RfCollection


class RfSessionServiceObj(RfResource):
    # create instance of sessionService
    def create_sub_objects(self, base_path, rel_path):
        self.components["Sessions"] = RfSessionCollection(base_path,
                                                          os.path.normpath("redfish/v1/SessionService/Sessions"),
                                                          parent=self)

    def patch_resource(self, patch_data):
        # first verify client didn't send us a property we cant patch
        for key in patch_data.keys():
            if key != "SessionTimeout":
                return 4, 400, "Invalid Patch Property Sent", ""
        # now patch the valid properties sent
        if "SessionTimeout" in patch_data:
            new_val = patch_data['SessionTimeout']
            if new_val < 30 or new_val > 86400:
                return 4, 400, "Bad Request-not in correct range", ""
            else:
                self.res_data['SessionTimeout'] = new_val
                return 0, 204, None, None
        else:
            return 4, 400, "Invalid Patch Property Sent", ""


class RfSessionCollection(RfCollection):
    def element_type(self):
        return RfSessionObj


# Service Collection Entries
class RfSessionObj(RfResource):
    pass
