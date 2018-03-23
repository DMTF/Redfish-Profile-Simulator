# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/blob/master/LICENSE.md

import os

from .accountService import RfAccountServiceObj
from .chassis import RfChassisCollection
from .managers import RfManagersCollection
from .resource import RfResource, RfCollection
from .resource import RfResourceRaw
from .sessionService import RfSessionServiceObj
from .systems import RfSystemsCollection
from .updateService import RfUpdateServiceObj


class RfServiceRoot(RfResource):
    def create_sub_objects(self, base_path, rel_path):
        resource_path = os.path.join(base_path, rel_path);
        contents = os.listdir(resource_path)
        for item in contents:
            if item == "odata":
                self.components[item] = RfOdataServiceDoc(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "$metadata":
                self.components[item] = RfOdataMetadata(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "Systems":
                self.components[item] = RfSystemsCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "Chassis":
                self.components[item] = RfChassisCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "Managers":
                self.components[item] = RfManagersCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "AccountService":
                self.components[item] = RfAccountServiceObj(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "SessionService":
                self.components[item] = RfSessionServiceObj(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "ResourceDirectory":
                self.components[item] = RfResourceDirectoryObj(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "UpdateService":
                self.components[item] = RfUpdateServiceObj(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "Registries":
                self.components[item] = RfRegistryCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "EventService":
                self.components[item] = RfEventServiceObj(base_path, os.path.join(rel_path, item), parent=self)

    def final_init_processing(self, base_path, rel_path):
        print("\n\n{}".format(self.res_data['Name']))


class RfOdataServiceDoc(RfResource):
    pass


class RfOdataMetadata(RfResourceRaw):
    pass


class RfResourceDirectoryObj(RfResource):
    pass


class RfRegistryCollection(RfCollection):
    def element_type(self):
        return RfRegistry


class RfRegistry(RfResource):
    pass


class RfEventServiceObj(RfResource):
    def create_sub_objects(self, base_path, rel_path):
        resource_path = os.path.join(base_path, rel_path);
        contents = os.listdir(resource_path)
        for item in contents:
            if item == "EventSubscriptions":
                self.components[item] = RfEventSubscriptionCollection(base_path,
                                                                      os.path.join(rel_path, item),
                                                                      parent=self)


class RfEventSubscriptionCollection(RfCollection):
    def element_type(self):
        return RfEventSubscription


class RfEventSubscription(RfResource):
    pass
