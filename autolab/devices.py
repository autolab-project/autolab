# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 14:53:44 2020

@author: qchat
"""

from .core.devices import StructureManager, ElementWrapper

class DeviceManager() :

    ''' This is the main class of the Devices part.
    It represents the top level device of the device structure, 
    and as this, it inherits from the ElementWrapper class.
    The only difference is that its here that the StructureManager class 
    of the session is instantiated, and that this "top level Device" is
    connected automatically '''

    def __init__(self):
        
        # For the top level device, instantiate the StructureManager class
        self._sm = StructureManager()

    def summary(self):
        self._sm.print_summary(None)

    # Routines to access sub elements
    def get(self,attr):
        return ElementWrapper(self._sm,attr)
    def __getattr__(self,attr):
        return self.get(attr)
    def __getitem__(self,attr):
        return self.get(attr)

    # Routines for autocompletion
    def __dir__(self):
        pass