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
    
    devUsit.addVariable('averagingState',
                       setFunction=devDriver.setAveragingState,
                       getFunction=devDriver.getAveragingState)
    
    devUsit.addVariable('bufferSize',
                       setFunction=devDriver.setBufferSize,
                       getFunction=devDriver.getBufferSize)
    
    devUsit.addVariable('wavelength',
                       setFunction=devDriver.setWavelength,
                       getFunction=devDriver.getWavelength)
    
    devUsit.addVariable('power',
                       getFunction=devDriver.getPower)
    
    devUsit.addAction('zero',
                     function=devDriver.setZero)
    