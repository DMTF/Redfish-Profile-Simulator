# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/blob/master/LICENSE.md

import json
import os

import flask


class RfResource:
    def __init__(self, base_path, rel_path, parent=None):
        self.parent = parent
        self.components = {}

        path = os.path.join(base_path, rel_path)
        indx_file_path = os.path.join(path, "index.json")
        print("*****Loading Mockup json file:{}".format(indx_file_path))
        if os.path.exists(indx_file_path):
            res_file = open(indx_file_path, "r")
            res_rawdata = res_file.read()
            self.res_data = json.loads(res_rawdata)
            self.create_sub_objects(base_path, rel_path)
            self.final_init_processing(base_path, rel_path)
        else:
            self.res_data = {}

    def create_sub_objects(self, base_path, rel_path):
        pass

    def final_init_processing(self, base_path, rel_path):
        pass

    def get_resource(self):
        return flask.jsonify(self.res_data)

    def get_attribute(self, attribute):
        return flask.jsonify(self.res_data[attribute])

    def get_component(self, component):
        if component in self.components:
            return self.components[component]
        else:
            return None

    def patch_resource(self, patch_data):
        for key in patch_data.keys():
            if key in self.res_data:
                self.res_data[key] = patch_data[key]
            else:
                raise Exception("attribute %s not found" % key)


class RfResourceRaw:
    def __init__(self, base_path, rel_path, parent=None):
        self.parent = parent
        path = os.path.join(base_path, rel_path)
        indx_file_path = os.path.join(path, "index.xml")
        print("*****Loading Mockup raw data file:{}".format(indx_file_path))
        res_file = open(indx_file_path, "r")
        res_raw_data = res_file.read()
        self.res_data = res_raw_data
        self.create_subobjects(base_path, rel_path)
        self.final_init_processing(base_path, rel_path)

    def create_subobjects(self, base_path, rel_path):
        pass

    def final_init_processing(self, base_path, rel_path):
        pass

    def get_resource(self):
        return self.res_data


class RfCollection(RfResource):
    def create_sub_objects(self, base_path, rel_path):
        self.elements = {}
        subpath = os.path.join(base_path, rel_path)
        contents = os.listdir(subpath)
        for item in contents:
            item_path = os.path.join(subpath, item)
            if os.path.isdir(item_path):
                etype = self.element_type()
                self.elements[item] = etype(base_path,
                                            os.path.normpath("%s/%s" % (rel_path, item)),
                                            parent=self)

    def element_type(self):
        pass

    def get_elements(self):
        return self.elements

    def get_element(self, element_id):
        return self.elements[element_id]
