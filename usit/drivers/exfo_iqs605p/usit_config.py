# -*- coding: utf-8 -*-
"""
Created on Thu May  2 16:47:17 2019

@author: quentin.chateiller
"""

def configure(devDriver,devUsit):
    
    iqs9100b = devUsit.addModule('iqs9100b')
    
    
    iqs9100b.addVariable('route',
                    setFunction=devDriver.iqs9100b.setRoute,
                    getFunction=devDriver.iqs9100b.getRoute)
    
    iqs9100b.addVariable('shutter',
                    setFunction=devDriver.iqs9100b.setShutter,
                    getFunction=devDriver.iqs9100b.isShuttered)
    