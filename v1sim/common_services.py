import os

from .resource import RfCollection, RfResource


class RfLogServiceCollection(RfCollection):
    def element_type(self):
        return RfLogService


class RfLogService(RfResource):
    def create_sub_objects(self, base_path, rel_path):
        resource_path = os.path.join(base_path, rel_path);
        contents = os.listdir(resource_path)
        for item in contents:
            if item == "Entries":
                self.components[item] = RfLogEntriesCollection(base_path,
                                                               os.path.join(rel_path, item),
                                                               parent=self)


class RfLogEntriesCollection(RfCollection):
    def element_type(self):
        return RfLogEntry


class RfLogEntry(RfResource):
    pass
