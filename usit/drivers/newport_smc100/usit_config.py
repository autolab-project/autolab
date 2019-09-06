# -*- coding: utf-8 -*-
"""
Created on Thu May  2 16:47:17 2019

@author: quentin.chateiller
"""

def configure(devDriver,devUsit):
        
    devUsit.addVariable('position',
                        setFunction=devDriver.setPosition,
                        getFunction=devDriver.getPosition)
    

    
    
    