# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

import os

from .common_services import RfLogServiceCollection
from .network import RfNetworkService
from .resource import RfResource, RfCollection
from .security import RfSecurityService


class RfManagersCollection(RfCollection):
    def element_type(self):
        return RfManagerObj


class RfManagerObj(RfResource):
    """
    create the dependent sub-objects that live under the Manager object
    """

    def create_sub_objects(self, base_path, rel_path):
        resource_path = os.path.join(base_path, rel_path);
        contents = os.listdir(resource_path)
        for item in contents:
            if item == "EthernetInterfaces":
                self.components[item] = RfManagerEthernetColl(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "NetworkProtocol":
                self.components[item] = RfManagerNetworkProtocol(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "SerialInterfaces":
                self.components[item] = RfSerialInterfaceCollection(base_path, os.path.join(rel_path, item),
                                                                    parent=self)
            elif item == "VirutalMedia":
                self.components[item] = RfVirtualMediaCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "NICs":
                self.components[item] = RfNics(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "LogServices":
                self.components[item] = RfLogServiceCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "ActiveHealthSystem":
                self.components[item] = RfActiveHealthSystem(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "DateTime":
                self.components[item] = RfDateTime(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "EmbeddedMedia":
                self.components[item] = RfEmbeddedMedia(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "FederationGroups":
                self.components[item] = RfFederationGroupCollection(base_path, os.path.join(rel_path, item),
                                                                    parent=self)
            elif item == "FederationPeers":
                self.components[item] = RfFederationPeerCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "LicenseService":
                self.components[item] = RfLicenseServiceCollection(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "SecurityService":
                self.components[item] = RfSecurityService(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "UpdateService":
                self.components[item] = RfManagerUpdateService(base_path, os.path.join(rel_path, item), parent=self)
            elif item == "NetworkService":
                self.components[item] = RfNetworkService(base_path, os.path.join(rel_path, item), parent=self)

    def patch_resource(self, patchData):
        # first verify client didn't send us a property we cant patch
        for key in patchData.keys():
            if key != "DateTime" and key != "DateTimeLocalOffset":
                return 4, 400, "Invalid Patch Property Sent", ""

        dateTime = None
        dateTimeOffset = None
        localOffset = None

        # now patch the valid properties sent
        if "DateTime" in patchData:
            dateTime = patchData['DateTime']
            dateTimeOffset = dateTime[-6:]  # get last 6 chars ....+00:00 or -00:00
        if "DateTimeLocalOffset" in patchData:
            localOffset = patchData['DateTimeLocalOffset']

        # verify that if both DateTime and DateTimeLocalOffset were sent, thant
        #  the offsets are the same.  (no reason to send both though)
        if ((dateTimeOffset is not None) and (localOffset is not None)):
            if (dateTimeOffset != localOffset):
                return (4, 409, "Offsets in DateTime and DateTimeLocalOffset conflict", None)  # 409 Conflict

        # reconcile localOffset and the offset in DateTime to write back
        # if only DateTime was updated, also update dateTimeLocalOffset
        if (localOffset is None):
            localOffset = dateTimeOffset
        # if only DateTimeLocalOffset was updated (timezone change), also update DateTime
        if (dateTime is None):
            dateTime = self.res_data['DateTime']  # read current value to get time
            dateTime = dateTime[:-6]  # strip the offset
            dateTime = dateTime + localOffset  # add back the offset sent in in DateTimeLocalOFfset

        # TODO:  issue 1545 in SPMF is ambiguity of what patching DateTimeLocalOFfset should actually do.
        # this may need to be updated once issue is resolved

        # now write the valid properties with updated values
        self.res_data['DateTime'] = dateTime
        self.res_data['DateTimeLocalOffset'] = localOffset
        return (0, 204, None, None)

    def reset_resource(self, resetData):
        if "ResetType" in resetData:
            value = resetData['ResetType']
            valid_values = self.res_data["Actions"]["#Manager.Reset"]["ResetType@Redfish.AllowableValues"]
            if value in valid_values:
                # it is a supoported reset action  modify other properties appropritely
                # nothing to do--manager always on in this profile
                return 0, 204, "System Reset", ""
            else:
                return 4, 400, "Invalid reset value: ResetType", ""
        else:  # invalid request
            return 4, 400, "Invalid request property", ""


class RfManagerNetworkProtocol(RfResource):
    pass


# the Manager Ethernet Collection
class RfManagerEthernetColl(RfCollection):
    def element_type(self):
        return RfManagerEthernet


# the Manager Ethernet Instance
class RfManagerEthernet(RfResource):
    def patchResource(self, patchData):
        # TODO: check and save the data
        # for now, just return ok w/ 204 no content
        return 0, 204, None, None


class RfSerialInterfaceCollection(RfCollection):
    def element_type(self):
        return RfSerialInterface


class RfSerialInterface(RfResource):
    pass


class RfVirtualMediaCollection(RfCollection):
    def element_type(self):
        return RfVirtualMedia


class RfVirtualMedia(RfResource):
    pass


class RfNics(RfResource):
    def create_sub_objects(self, base_path, rel_path):
        resource_path = os.path.join(base_path, rel_path);
        contents = os.listdir(resource_path)
        for item in contents:
            if item == "Dedicated":
                self.components[item] = RfDedicatedNicCollection(base_path,
                                                                 os.path.join(rel_path, item),
                                                                 parent=self)


class RfDedicatedNicCollection(RfCollection):
    def element_type(self):
        return RfNic


class RfNic(RfResource):
    pass


class RfActiveHealthSystem(RfResource):
    pass


class RfDateTime(RfResource):
    pass


class RfEmbeddedMedia(RfResource):
    pass


class RfLicenseServiceCollection(RfCollection):
    def element_type(self):
        return RfLicenseService


class RfLicenseService(RfResource):
    pass


class RfFederationGroupCollection(RfCollection):
    def element_type(self):
        return RfFederationGroup


class RfFederationGroup(RfResource):
    pass


class RfFederationPeerCollection(RfCollection):
    def element_type(self):
        return RfFederationPeer


class RfFederationPeer(RfResource):
    pass


class RfManagerUpdateService(RfResource):
    pass
