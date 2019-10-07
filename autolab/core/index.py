# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 16:01:43 2019

@author: qchat
"""

import configparser

# =============================================================================
#                   DEVICES INDEX
# =============================================================================

def load(path):
    
    """ Returns the content of the DeviceIndex .ini file  """
    
    index = configparser.ConfigParser()
    index.read(path)
    assert len(set(index.sections())) == len(index.sections()), "Device index: 2 devices cannot have the same name."
    return index
