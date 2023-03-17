# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/blob/main/LICENSE.md

import os

from .resource import RfResource, RfCollection


class RfSimpleStorageCollection(RfCollection):
    def element_type(self):
        return RfSimpleStorage


class RfSimpleStorage(RfResource):
    pass


class RfSmartStorage(RfResource):
    def create_sub_objects(self, base_path, rel_path):
        resource_path = os.path.join(base_path, rel_path);
        contents = os.listdir(resource_path)
        for item in contents:
            if item == "ArrayControllers":
                self.components[item] = RfArrayControllerCollection(base_path,
                                                                    os.path.join(rel_path, item),
                                                                    parent=self)
            if item == "HostBusAdapters":
                self.components[item] = RfHostBusAdapterCollection(base_path,
                                                                   os.path.join(rel_path, item),
                                                                   parent=self)


class RfArrayControllerCollection(RfCollection):
    def element_type(self):
        return RfArrayController


class RfArrayController(RfResource):
    def create_sub_objects(self, base_path, rel_path):
        resource_path = os.path.join(base_path, rel_path);
        contents = os.listdir(resource_path)
        for item in contents:
            if item == "DiskDrives":
                self.components[item] = RfDiskDriveCollection(base_path, os.path.join(rel_path, item),
                                                              parent=self)
            if item == "LogicalDrives":
                self.components[item] = RfLogicalDriveCollection(base_path, os.path.join(rel_path, item),
                                                                 parent=self)

            if item == "StorageEnclosures":
                self.components[item] = RfStorageEnclosureCollection(base_path, os.path.join(rel_path, item),
                                                                     parent=self)
            if item == "UnconfiguredDrives":
                self.components[item] = RfUnconfiguredDriveCollection(base_path, os.path.join(rel_path, item),
                                                                      parent=self)


class RfHostBusAdapterCollection(RfCollection):
    def element_type(self):
        return RfHostBusAdapter


class RfHostBusAdapter(RfResource):
    pass


class RfDiskDriveCollection(RfCollection):
    def element_type(self):
        return RfDiskDrive


class RfDiskDrive(RfResource):
    pass


class RfLogicalDriveCollection(RfCollection):
    def element_type(self):
        return RfLogicalDrive


class RfLogicalDrive(RfResource):
    def create_sub_objects(self, base_path, rel_path):
        resource_path = os.path.join(base_path, rel_path);
        contents = os.listdir(resource_path)
        for item in contents:
            if item == "DataDrives":
                self.components[item] = RfDataDriveCollection(base_path, os.path.join(rel_path, item),
                                                              parent=self)


class RfDataDriveCollection(RfCollection):
    def element_type(self):
        return RfDataDrive


class RfDataDrive(RfResource):
    pass


class RfStorageEnclosureCollection(RfCollection):
    def element_type(self):
        return RfStorageEnclosure


class RfStorageEnclosure(RfResource):
    pass


class RfUnconfiguredDriveCollection(RfCollection):
    def element_type(self):
        return RfUnconfiguredDrive


class RfUnconfiguredDrive(RfResource):
    pass
