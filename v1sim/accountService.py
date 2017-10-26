# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

import os

from .resource import RfResource, RfCollection


class RfAccountServiceObj(RfResource):
    # create instance of each AccountService
    def create_sub_objects(self, base_path, rel_path):
        if os.path.isdir(os.path.join(base_path, "Accounts")):
            self.components["Accounts"] = RfAccountCollection(base_path,
                                                              os.path.normpath("redfish/v1/AccountService/Accounts"),
                                                              parent=self)

        if os.path.isdir(os.path.join(base_path, "Accounts")):
            self.components["Roles"] = RfRoleCollection(base_path,
                                                        os.path.normpath("redfish/v1/AccountService/Roles"),
                                                        parent=self)

    def patch_resource(self, patch_data):
        # first verify client didn't send us a property we cant patch
        patachables = ("MinPasswordLength", "AccountLockoutThreshold",
                       "AccountLockoutDuration", "AccountLockoutCounterResetAfter")

        for key in patch_data.keys():
            if key not in patachables:
                return 4, 400, "Invalid Patch Property Sent", ""

        # now patch the valid properties sent
        for key in patch_data.keys():
            new_val = patch_data[key]
            print("new_val:{}".format(new_val))
            try:
                num_val = round(new_val)
            except ValueError:
                return 4, 400, "invalid value", ""
            else:
                patch_data[key] = num_val

        # if here, we know all the patch data is valid properties and properties
        new_duration = self.res_data["AccountLockoutDuration"]
        new_reset_after = self.res_data["AccountLockoutCounterResetAfter"]
        if "AccountLockoutDuration" in patch_data:
            new_duration = patch_data["AccountLockoutDuration"]
        if "AccountLockoutCounterResetAfter" in patch_data:
            new_reset_after = patch_data["AccountLockoutCounterResetAfter"]
        if new_duration < new_reset_after:
            return 4, 400, "invalid value", ""

        # if here, all values are good. set them
        for key in patch_data.keys():
            self.res_data[key] = patch_data[key]
        return 0, 204, None, None


class RfAccountCollection(RfCollection):
    def element_type(self):
        return RfAccountObj


# Service Collection Entries
class RfAccountObj(RfResource):
    pass


class RfRoleCollection(RfCollection):
    def element_type(self):
        return RfRoleObj


# Service Collection Entries
class RfRoleObj(RfResource):
    pass
