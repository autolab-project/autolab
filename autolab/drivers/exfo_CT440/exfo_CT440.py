#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified): EXFO CT440.
-
"""

# This driver is a copy of the ct400 driver using the ct440 option, and serves as a proxy for the ct440 driver.

# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # To get access to yenista_CT400

# from yenista_CT400.yenista_CT400 import Driver_DLL as Driver_DLL_ct400
from autolab.drivers.yenista_CT400.yenista_CT400 import Driver_DLL as Driver_DLL_ct400

#################################################################################
############################## Connections classes ##############################
class Driver_DLL(Driver_DLL_ct400):
    def __init__(self,
        libpath=r"C:\Program Files\EXFO\CT440\Library\Win64\CT440_lib.dll",
        configpath=r'C:\Users\Public\Documents\EXFO\CT440\Config\CT440.config',
        **kwargs):

        self.model = "CT440"
        Driver_DLL_ct400.__init__(self, libpath, configpath, model=self.model, **kwargs)
