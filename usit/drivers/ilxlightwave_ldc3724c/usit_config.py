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
    
    las = devUsit.addModule('laserDiode')
    
    
    las.addVariable('current',
                    setFunction=devDriver.las.setCurrentSetpoint,
                    getFunction=devDriver.las.getCurrentSetpoint)
    
    las.addVariable('current',
                    getFunction=devDriver.las.getCurrent)
    
    las.addVariable('powerSetpoint',
                    setFunction=devDriver.las.setPowerSetpoint,
                    getFunction=devDriver.las.getPowerSetpoint)
    
    las.addVariable('power',
                    getFunction=devDriver.las.getPower)
    
    las.addVariable('enabled',
                    setFunction=devDriver.las.setEnabled,
                    getFunction=devDriver.las.isEnabled)
    
    las.addVariable('mode',
                    setFunction=devDriver.las.setMode,
                    getFunction=devDriver.las.getMode)
    
    
    
    tec = devUsit.addModule('tec')
    
    tec.addVariable('resistance',
                    getFunction=devDriver.tec.getResistance)
    
    tec.addVariable('gain',
                    setFunction=devDriver.tec.setGain,
                    getFunction=devDriver.tec.getGain)
    
    tec.addVariable('currentSetpoint',
                    setFunction=devDriver.tec.setCurrentSetpoint,
                    getFunction=devDriver.tec.getCurrentSetpoint)
    
    tec.addVariable('current',
                    getFunction=devDriver.tec.getCurrent)
    
    tec.addVariable('temperatureSetpoint',
                    setFunction=devDriver.tec.setTemperatureSetpoint,
                    getFunction=devDriver.tec.getTemperatureSetpoint)
    
    tec.addVariable('temperature',
                    getFunction=devDriver.tec.getTemperature)
    
    tec.addVariable('enabled',
                    setFunction=devDriver.tec.setEnabled,
                    getFunction=devDriver.tec.isEnabled)
    
    tec.addVariable('mode',
                    setFunction=devDriver.tec.setMode,
                    getFunction=devDriver.tec.getMode)
    