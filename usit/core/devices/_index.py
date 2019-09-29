# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 16:01:43 2019

@author: qchat
"""

import configparser
import os
import usit

# =============================================================================
#                   DEVICES INDEX
# =============================================================================



def loadIndex():
    
    
    # LOADING
    # -------------------------------------------------------------------------
    
    """ Returns the content of the DeviceIndex .ini file  """
    
    index = configparser.ConfigParser()
    index.read(usit.core.DEVICES_INDEX_PATH)
    
    # CHECKING
    # -------------------------------------------------------------------------
    
    namelist = index.sections()
    
    # Name uniqueness
    assert len(set(namelist)) == len(namelist), "Device index: 2 devices cannot have the same name."
    
    for name in namelist :
        
        # Driver provided
        assert 'driver' in index[name].keys(), f"Device index: Device '{name}' has no driver provided"
        
        # Driver existing
        driver = index[name]['driver']
        assert driver in usit.drivers.list()
        
        # Configuration file  --- to be changed
        assert os.path.exists(os.path.join(usit.core.DRIVERS_PATH,driver,'usit_config.py')), f"Device index: Missing usit_config.py file for device '{name}'"
        
        
    return index
