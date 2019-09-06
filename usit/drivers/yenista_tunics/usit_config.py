# -*- coding: utf-8 -*-
"""
Created on Thu May  2 16:47:17 2019

@author: quentin.chateiller
"""

def configure(devDriver,devUsit):
    
    devUsit.addVariable('wavelength',
                        setFunction=devDriver.setWavelength,
                        getFunction=devDriver.getWavelength)
    
    devUsit.addVariable('frequency',
                        setFunction=devDriver.setFrequency,
                        getFunction=devDriver.getFrequency)
    
    devUsit.addVariable('power',
                        setFunction=devDriver.setPower,
                        getFunction=devDriver.getPower)
    
    devUsit.addVariable('intensity',
                        setFunction=devDriver.setIntensity,
                        getFunction=devDriver.getIntensity)
    
    devUsit.addVariable('output',
                        setFunction=devDriver.setOutput,
                        getFunction=devDriver.getOutput)
    
    devUsit.addVariable('motorSpeed',
                        setFunction=devDriver.setMotorSpeed,
                        getFunction=devDriver.getMotorSpeed)
    
    