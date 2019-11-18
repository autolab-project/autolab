# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 14:53:10 2019

@author: qchat
"""

import configparser
import autolab
import os

def create_defaults():
        
    config = configparser.ConfigParser()
    config['stats'] = {'enable': '1'}
    
    with open(autolab.paths.AUTOLAB_CONFIG, 'w') as file:
        config.write(file)
        
def load():
    
    if os.path.exists(autolab.paths.AUTOLAB_CONFIG) is False :
        create_defaults()
        
    config = configparser.ConfigParser()
    config.read(autolab.paths.AUTOLAB_CONFIG)
    
    return config
    