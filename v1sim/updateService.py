# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

import os

from .resource import RfResource, RfCollection


class RfUpdateServiceObj(RfResource):
    def create_sub_objects(self, base_path, rel_path):
        if os.path.isdir(os.path.join(base_path, os.path.normpath("redfish/v1/UpdateService/ComponentRepository"))):
            self.components["ComponentRepository"] \
                = RfComponentRepositoryCollection(base_path,
                                                  os.path.normpath("redfish/v1/UpdateService/ComponentRepository"),
                                                  parent=self)
        if os.path.isdir(os.path.join(base_path, os.path.normpath("redfish/v1/UpdateService/FirmwareInventory"))):
            self.components["FirmwareInventory"] \
                = RfFirmwareInventoryCollection(base_path,
                                                os.path.normpath("redfish/v1/UpdateService/FirmwareInventory"),
                                                parent=self)

        if os.path.isdir(os.path.join(base_path, os.path.normpath("redfish/v1/UpdateService/InstallSets"))):
            self.components["InstallSets"] \
                = RfInstallSetCollection(base_path,
                                         os.path.normpath("redfish/v1/UpdateService/InstallSets"),
                                         parent=self)

        if os.path.isdir(os.path.join(base_path, os.path.normpath("redfish/v1/UpdateService/SoftwareInventory"))):
            self.components["SoftwareInventory"] \
                = RfSoftwareInventoryCollection(base_path,
                                                os.path.normpath("redfish/v1/UpdateService/SoftwareInventory"),
                                                parent=self)

        if os.path.isdir(os.path.join(base_path, os.path.normpath("redfish/v1/UpdateService/UpdateTaskQueue"))):
            self.components["UpdateTaskQueue"] \
                = RfUpdateTaskQueueCollection(base_path,
                                              os.path.normpath("redfish/v1/UpdateService/UpdateTaskQueue"),
                                              parent=self)


class RfComponentRepositoryCollection(RfCollection):
    def element_type(self):
        return RfComponentRepository


class RfComponentRepository(RfResource):
    pass


class RfFirmwareInventoryCollection(RfCollection):
    def element_type(self):
        return RfComponentRepository


class RfFirmwareInventory(RfResource):
    pass


class RfInstallSetCollection(RfCollection):
    def element_type(self):
        return RfInstallSet


class RfInstallSet(RfResource):
    pass


class RfSoftwareInventoryCollection(RfCollection):
    def element_type(self):
        return RfSoftwareInventory


class RfSoftwareInventory(RfResource):
    pass


class RfUpdateTaskQueueCollection(RfCollection):
    def element_type(self):
        return RfUpdateTaskQueue


class RfUpdateTaskQueue(RfResource):
    pass
