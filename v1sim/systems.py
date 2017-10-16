# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

import os

from .common_services import RfLogServiceCollection
from .network import RfEthernetCollection, RfNetworkAdapterCollection
from .resource import RfResource, RfCollection
from .storage import RfSimpleStorageCollection, RfSmartStorage


class RfSystemsCollection(RfCollection):
    def element_type(self):
        return RfSystemObj


class RfSystemObj(RfResource):
    def create_sub_objects(self, base_path, rel_path):
        resource_path = os.path.join(base_path, rel_path)
        contents = os.listdir(resource_path)
        for item in contents:
            if item == "bios":
                self.components[item] = RfBios(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "EthernetInterfaces":
                self.components[item] = RfEthernetCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "LogServices":
                self.components[item] = RfLogServiceCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "Memory":
                self.components[item] = RfMemoryCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "Processors":
                self.components[item] = RfProcessorCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "SimpleStorage":
                self.components[item] = RfSimpleStorageCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "SmartStorage":
                self.components[item] = RfSmartStorage(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "SecureBoot":
                self.components[item] = RfSecureBoot(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "NetworkAdapters":
                self.components[item] = RfNetworkAdapterCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "PCIDevices":
                self.components[item] = RfPCIDeviceCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "PCISlots":
                self.components[item] = RfPCISlotCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "FirmwareInventory":
                self.components[item] = RfSystemFirmwareInventory(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "USBDevices":
                self.components[item] = RfUSBDeviceCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "USBPorts":
                self.components[item] = RfUSBPortCollection(base_path, os.path.join(rel_path, item), parent=self)

    def patch_resource(self, patch_data):
        # first verify client didn't send us a property we cant patch
        for key in patch_data.keys():
            if key != "AssetTag" and key != "IndicatorLED" and key != "Boot":
                return 4, 400, "Invalid Patch Property Sent", ""
            elif key == "Boot":
                for prop2 in patch_data["Boot"].keys():
                    if prop2 != "BootSourceOverrideEnabled" and prop2 != "BootSourceOverrideTarget":
                        return 4, 400, "Invalid Patch Property Sent", ""
        # now patch the valid properties sent
        if "AssetTag" in patch_data:
            print("assetTag:{}".format(patch_data["AssetTag"]))
            self.res_data['AssetTag'] = patch_data['AssetTag']
        if "IndicatorLED" in patch_data:
            self.res_data['IndicatorLED'] = patch_data['IndicatorLED']
        if "Boot" in patch_data:
            boot_data = patch_data["Boot"]
            if "BootSourceOverrideEnabled" in boot_data:
                value = boot_data["BootSourceOverrideEnabled"]
                valid_values = ["Once", "Disabled", "Continuous"]
                if value in valid_values:
                    self.res_data['Boot']['BootSourceOverrideEnabled'] = value
                else:
                    return 4, 400, "Invalid_Value_Specified: BootSourceOverrideEnable", ""
            if "BootSourceOverrideTarget" in boot_data:
                value = boot_data["BootSourceOverrideTarget"]
                valid_values = self.res_data['Boot']['BootSourceOverrideTarget@Redfish.AllowableValues']
                if value in valid_values:
                    self.res_data['Boot']['BootSourceOverrideTarget'] = value
                else:
                    return 4, 400, "Invalid_Value_Specified: BootSourceOverrideTarget", ""
        return 0, 204, None, None

    def reset_resource(self, reset_data):
        if "ResetType" in reset_data:
            # print("RESETDATA: {}".format(resetData))
            value = reset_data['ResetType']
            valid_values = self.res_data["Actions"]["#ComputerSystem.Reset"]["ResetType@Redfish.AllowableValues"]
            if value in valid_values:
                # it is a supoported reset action  modify other properties appropritely
                if value == "On" or value == "ForceRestart" or value == "GracefulRestart":
                    self.res_data["PowerState"] = "On"
                    print("PROFILE_SIM--SERVER WAS RESET. power now ON")
                elif value == "GracefulShutdown" or value == "ForceOff":
                    self.res_data["PowerState"] = "Off"
                    print("PROFILE_SIM--SERVER WAS RESET. Power now Off")
                return 0, 204, "System Reset", ""
            else:
                return 4, 400, "Invalid reset value: ResetType", ""
        else:  # invalid request
            return 4, 400, "Invalid request property", ""


# subclass Logs Collection
class RfMemoryCollection(RfCollection):
    def element_type(self):
        return RfMemory


class RfMemory(RfResource):
    pass


class RfProcessorCollection(RfCollection):
    def element_type(self):
        return RfProcessor


class RfProcessor(RfResource):
    pass


class RfBios(RfResource):
    def create_sub_objects(self, base_path, rel_path):
        resource_path = os.path.join(base_path, rel_path)
        contents = os.listdir(resource_path)
        for item in contents:
            if item == "Settings":
                self.components[item] = RfBiosSettings(base_path, os.path.join(rel_path, item), parent=self)

    def reset_resource(self, req_data):
        print("bios was reset")
        return 0, 204, "Bios Reset", ""

    def change_password(self, req_data):
        if "PasswordName" in req_data and "OldPassword" in req_data and "NewPassword" in req_data:
            print("changed password of type %s" % req_data["PasswordName"])
            return 0, 204, "Password Change", ""
        else:  # invalid request
            return 4, 400, "Invalid request property", ""


class RfBiosSettings(RfResource):
    def patch_resource(self, patch_data):
        if "Attributes" not in patch_data:
            return 4, 400, "Invalid Payload. No Attributes found", ""
        for key in patch_data["Attributes"].keys():
            # verify client didn't send us a property we cant patch
            if key not in self.res_data["Attributes"]:
                return 4, 400, "Invalid Patch Property Sent", ""
            else:
                self.parent.res_data["Attributes"][key] = patch_data["Attributes"][key]
        return 0, 204, None, None


class RfPCIDeviceCollection(RfCollection):
    def element_type(self):
        return RfPCIDevice


class RfPCIDevice(RfResource):
    pass


class RfPCISlotCollection(RfCollection):
    def element_type(self):
        return RfPCIDevice


class RfPCISlot(RfResource):
    pass


class RfSecureBoot(RfResource):
    pass


class RfSystemFirmwareInventory(RfResource):
    pass


class RfUSBDeviceCollection(RfCollection):
    def element_type(self):
        return RfUSBDevice


class RfUSBDevice(RfResource):
    pass


class RfUSBPortCollection(RfCollection):
    def element_type(self):
        return RfUSBPort


class RfUSBPort(RfResource):
    pass
