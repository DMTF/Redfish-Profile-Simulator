# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

import os
from .resource import RfResource
import json


class RfAccountServiceObj(RfResource):  
    # create instance of each AccountService
    def createSubObjects(self,basePath,relPath):
        self.accounts=RfAccountCollection(basePath,os.path.normpath("redfish/v1/AccountService/Accounts"))
        self.roles=RfRoleCollection(basePath,os.path.normpath("redfish/v1/AccountService/Roles"))

    def patchResource(self,patchData):
        #first verify client didn't send us a property we cant patch
        patachables=("MinPasswordLength","AccountLockoutThreshold",
                     "AccountLockoutDuration","AccountLockoutCounterResetAfter")

        for key in patchData.keys():
            if( not key in patachables ):
                return (4,400,"Invalid Patch Property Sent","")

        # now patch the valid properties sent
        for key in patchData.keys():
            newVal=patchData[key]
            print("newVal:{}".format(newVal))
            try:
                numVal=round(newVal)
            except ValueError:
                return(4,400,"invalid value","")
            else:
                patchData[key]=numVal

        # if here, we know all the patch data is valid properties and properties
        newDuration=self.resData["AccountLockoutDuration"]
        newResetAfter=self.resData["AccountLockoutCounterResetAfter"]
        if( "AccountLockoutDuration" in patchData ):
            newDuration=patchData["AccountLockoutDuration"]
        if( "AccountLockoutCounterResetAfter" in patchData ):
            newResetAfter=patchData["AccountLockoutCounterResetAfter"]
        if( newDuration < newResetAfter ):
            return(4,400,"invalid value","")

        # if here, all values are good. set them
        for key in patchData.keys():
            self.resData[key]=patchData[key]
        return(0,204,None,None)




class RfAccountCollection(RfResource):
    # create all of the ENTRIES/members in the service collection-data drive from RfSysInfo
    def createSubObjects(self,basePath,relPath):
        self.account_root=self.RfAccountObj(basePath,os.path.normpath("redfish/v1/AccountService/Accounts/root"))
        self.account_jane=self.RfAccountObj(basePath,os.path.normpath("redfish/v1/AccountService/Accounts/jane"))
        self.account_john=self.RfAccountObj(basePath,os.path.normpath("redfish/v1/AccountService/Accounts/john"))
     
    #Service Collection Entries
    class RfAccountObj(RfResource):
        pass

class RfRoleCollection(RfResource):
    # create all of the ENTRIES/members in the service collection-data drive from RfSysInfo
    def createSubObjects(self,basePath,relPath):
        self.role_Admin=self.RfRoleObj(basePath,os.path.normpath("redfish/v1/AccountService/Roles/Admin"))
        self.role_Operator=self.RfRoleObj(basePath,os.path.normpath("redfish/v1/AccountService/Roles/Operator"))
        self.role_ReadOnlyUser=self.RfRoleObj(basePath,os.path.normpath("redfish/v1/AccountService/Roles/ReadOnlyUser"))
     
    #Service Collection Entries
    class RfRoleObj(RfResource):
        pass

