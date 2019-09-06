# -*- coding: utf-8 -*-
"""
Created on Thu May  2 16:47:17 2019

@author: quentin.chateiller
"""

def configure(devDriver,devUsit):
    
    for subName,subDriver in [('slot1',devDriver.slot1),('slot2',devDriver.slot2)] :
    
        subDevUsit = devUsit.addModule(subName)  
        
        subDevUsit.addVariable('averagingState',
                           setFunction=subDriver.setAveragingState,
                           getFunction=subDriver.getAveragingState)
        
        subDevUsit.addVariable('bufferSize',
                           setFunction=subDriver.setBufferSize,
                           getFunction=subDriver.getBufferSize)
        
        subDevUsit.addVariable('wavelength',
                           setFunction=subDriver.setWavelength,
                           getFunction=subDriver.getWavelength)
        
        subDevUsit.addVariable('power',
                           getFunction=subDriver.getPower)
    
    
    