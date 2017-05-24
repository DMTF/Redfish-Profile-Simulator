#!/usr/bin/env python3

from setuptools import setup

setup(name='Redfish-Profile-Simulator',
      version='0.1',
      description='Python implementation of a Redfish server',
      url='http://github.com/DMTF/Redfish-Profile-Simulator',
      author='DMTF',
      author_email='paul_vancil@dell.com',
      license='MIT',
      packages=[
        'RedDrum',
        'RedDrum.Backend',
        'RedDrum.Backend.BullRed_RackManager',
        'RedDrum.Backend.OpenBMC',
        'RedDrum.Backend.Simulator',
        'RedDrum.Httpd-Config',
        'RedDrum.RedfishService',
        'RedDrum.RedfishService.FlaskApp',
      ],
      data_files = [ ('RedDrum', ['RedDrum/RedDrum.conf']) ],
      scripts=['RedDrum-RedfishService.py'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'flask',
      ],
      )
