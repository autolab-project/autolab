# -*- coding: utf-8 -*-
"""
Created on Thu May  2 16:47:17 2019

@author: quentin.chateiller
"""

def configure(devDriver,devUsit):
    """
    This script configures Usit to use your device properly.
    devDriver is an instance of the class Device() located in the script driver.py
    devUsit is a Usit Device object that this function is supposed to configure, 
    by affecting the functions contained in devDriver to variable and actions objects 
    of the devUsit object.
    """
    
    for subName,subDriver in [('source1',devDriver.source1),('source2',devDriver.source2)] :
    
        subDevUsit = devUsit.addModule(subName)    
    
        subDevUsit.addVariable('resistance',
                        getFunction=subDriver.getResistance)
        
        subDevUsit.addVariable('power',
                        getFunction=subDriver.getPower)
        
        subDevUsit.addVariable('powerCompliance',
                        setFunction=subDriver.setPowerCompliance,
                        getFunction=subDriver.getPowerCompliance)
        
        subDevUsit.addVariable('current',
                        setFunction=subDriver.setCurrent,
                        getFunction=subDriver.getCurrent)
        
        subDevUsit.addVariable('currentCompliance',
                        setFunction=subDriver.setCurrentCompliance,
                        getFunction=subDriver.getCurrentCompliance)
        
        subDevUsit.addVariable('voltage',
                        setFunction=subDriver.setVoltage,
                        getFunction=subDriver.getVoltage)
        
        subDevUsit.addVariable('voltageCompliance',
                        setFunction=subDriver.setVoltageCompliance,
                        getFunction=subDriver.getVoltageCompliance)
        
        subDevUsit.addVariable('output',
                        setFunction=subDriver.setOutputState,
                        getFunction=subDriver.getOutputState)
        
        subDevUsit.addVariable('4wireMode',
                        setFunction=subDriver.set4wireModeState,
                        getFunction=subDriver.get4wireModeState)
