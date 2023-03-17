# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/blob/main/LICENSE.md

import os

from .resource import RfResource, RfCollection


class RfChassisCollection(RfCollection):
    def element_type(self):
        return RfChassisObj


class RfChassisObj(RfResource):
    # create the dependent sub-objects that live under the chassis object
    def create_sub_objects(self, base_path, rel_path):
        resource_path = os.path.join(base_path, rel_path);
        contents = os.listdir(resource_path)
        for item in contents:
            if item == "Thermal":
                self.components[item] = RfChassisThermal(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "Power":
                self.components[item] = RfChassisPower(base_path, os.path.join(rel_path, item), parent=self)

    def patch_resource(self, patch_data):
        # first verify client didn't send us a property we cant patch
        for key in patch_data.keys():
            if key != "AssetTag" and key != "IndicatorLED":
                return 4, 400, "Invalid Patch Property Sent", ""
        # now patch the valid properties sent
        if "AssetTag" in patch_data:
            self.res_data['AssetTag'] = patch_data['AssetTag']
        if "IndicatorLED" in patch_data:
            self.res_data['IndicatorLED'] = patch_data['IndicatorLED']
        return 0, 204, None, None

    def reset_resource(self, reset_data):
        if "ResetType" in reset_data:
            # print("RESETDATA: {}".format(resetData))
            value = reset_data['ResetType']
            valid_values = self.res_data["Actions"]["#Chassis.Reset"]["ResetType@Redfish.AllowableValues"]
            if value in valid_values:
                # it is a supoported reset action  modify other properties appropritely
                if value == "On":
                    self.res_data["PowerState"] = "On"
                    print("PROFILE_SIM--SERVER WAS RESET. power now ON")
                elif value == "ForceOff":
                    self.res_data["PowerState"] = "Off"
                    print("PROFILE_SIM--SERVER WAS RESET. Power now Off")
                return 0, 204, "Chassis Reset", ""
            else:
                return 4, 400, "Invalid reset value: ResetType", ""
        else:  # invalid request
            return 4, 400, "Invalid request property", ""


# subclass Thermal Metrics
class RfChassisThermal(RfResource):
    pass


# subclass Power Metrics
class RfChassisPower(RfResource):
    def create_sub_objects(self, base_path, rel_path):
        resource_path = os.path.join(base_path, rel_path);
        contents = os.listdir(resource_path)
        for item in contents:
            if item == "FastPowerMeter":
                self.components[item] = RfFastPowerMeter(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "FederatedGroupCapping":
                self.components[item] = RfFederatedGroupCapping(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "PowerMeter":
                self.components[item] = RfPowerMeter(base_path, os.path.join(rel_path, item), parent=self)

    def patch_resource(self, patchData):
        # first verify client didn't send us a property we cant patch
        for key in patchData.keys():
            if key != "PowerControl":
                return 4, 400, "Invalid Patch Property Sent", ""
            else:  # Powercontrol:
                for prop2 in patchData["PowerControl"][0].keys():
                    if prop2 != "PowerLimit":
                        return 4, 400, "Invalid Patch Property Sent", ""
                    else:  # PowerLimit
                        for prop3 in patchData["PowerControl"][0]["PowerLimit"].keys():
                            if prop3 != "LimitInWatts" and prop3 != "LimitException" and prop3 != "CorrectionInMs":
                                return 4, 400, "Invalid Patch Property Sent", ""
        # now patch the valid properties sent
        if "PowerControl" in patchData:
            if "PowerLimit" in patchData["PowerControl"][0]:
                patch_power_limit_dict = patchData["PowerControl"][0]["PowerLimit"]
                catfish_power_limit_dict = self.res_data["PowerControl"][0]["PowerLimit"]
                if "LimitInWatts" in patch_power_limit_dict:
                    self.res_data["PowerControl"][0]["PowerLimit"]["LimitInWatts"] = \
                        patch_power_limit_dict['LimitInWatts']
                if "LimitException" in patch_power_limit_dict:
                    self.res_data["PowerControl"][0]["PowerLimit"]['LimitException'] = \
                        patch_power_limit_dict['LimitException']
                if "CorrectionInMs" in patch_power_limit_dict:
                    self.res_data["PowerControl"][0]["PowerLimit"]['CorrectionInMs'] = \
                        patch_power_limit_dict['CorrectionInMs']
        return 0, 204, None, None


class RfFastPowerMeter(RfResource):
    pass


class RfFederatedGroupCapping(RfResource):
    pass


class RfPowerMeter(RfResource):
    pass
