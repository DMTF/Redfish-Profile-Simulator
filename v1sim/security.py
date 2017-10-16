import os

from .resource import RfResource


class RfSecurityService(RfResource):
    def create_sub_objects(self, base_path, rel_path):
        resource_path = os.path.join(base_path, rel_path);
        contents = os.listdir(resource_path)
        for item in contents:
            if item == "ESKM":
                self.components[item] = RfESKM(base_path, os.path.join(rel_path, item), parent=self)
            if item == "HttpsCert":
                self.components[item] = RfHttpsCert(base_path, os.path.join(rel_path, item), parent=self)
            if item == "SSO":
                self.components[item] = RfSSO(base_path, os.path.join(rel_path, item), parent=self)
            if item == "CertificateAuthentication":
                self.components[item] = RfCertificateAuthentication(base_path, os.path.join(rel_path, item),
                                                                    parent=self)


class RfESKM(RfResource):
    pass


class RfHttpsCert(RfResource):
    pass


class RfSSO(RfResource):
    pass


class RfCertificateAuthentication(RfResource):
    pass
