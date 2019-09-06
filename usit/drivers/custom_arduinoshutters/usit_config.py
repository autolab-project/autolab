# -*- coding: utf-8 -*-
"""
Created on Thu May  2 16:47:17 2019

@author: quentin.chateiller
"""

def configure(devDriver,devUsit):
    
    devUsit.addVariable('config',
                       setFunction=devDriver.setConfig,
                       getFunction=devDriver.getConfig)
    
    devUsit.addAction('invert',
                     function=devDriver.invertConfig)