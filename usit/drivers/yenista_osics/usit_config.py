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
    
    sld = devUsit.addModule('sld')
    
    
    sld.addVariable('power',
                        setFunction=devDriver.sld.setPower,
                        getFunction=devDriver.sld.getPower)
    
    sld.addVariable('output',
                        setFunction=devDriver.sld.setOutputState,
                        getFunction=devDriver.sld.getOutputState)
    
    
    t100 = devUsit.addModule('t100')

    t100.addVariable('wavelength',
                        setFunction=devDriver.t100.setWavelength,
                        getFunction=devDriver.t100.getWavelength)
    
    t100.addVariable('frequency',
                        setFunction=devDriver.t100.setFrequency,
                        getFunction=devDriver.t100.getFrequency)
    
    t100.addVariable('power',
                        setFunction=devDriver.t100.setPower,
                        getFunction=devDriver.t100.getPower)
    
    t100.addVariable('intensity',
                        setFunction=devDriver.t100.setIntensity,
                        getFunction=devDriver.t100.getIntensity)
    
    t100.addVariable('output',
                        setFunction=devDriver.t100.setOutputState,
                        getFunction=devDriver.t100.getOutputState)
    
    t100.addVariable('coherenceControl',
                        setFunction=devDriver.t100.setCoherenceControlState,
                        getFunction=devDriver.t100.getCoherenceControlState)

    t100.addVariable('autoPeakFindControl',
                        setFunction=devDriver.t100.setAutoPeakFindControlState,
                        getFunction=devDriver.t100.getAutoPeakFindControlState)