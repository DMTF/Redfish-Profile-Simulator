#!/usr/bin/env python3

from setuptools import setup

setup(name='Redfish-Profile-Simulator',
      version='0.1',
      description='Python implementation of a Redfish server',
      url='http://github.com/DMTF/Redfish-Profile-Simulator',
      author='DMTF',
      author_email='paul_vancil@dell.com',
      license='MIT',
      packages=['RedDrum'],
      scripts=['RedDrum-RedfishService.py'],
      zip_safe=False,
      install_requires=[
        'flask',
      ],
      )
