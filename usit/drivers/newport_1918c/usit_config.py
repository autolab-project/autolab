# -*- coding: utf-8 -*-
"""
Created on Thu May  2 16:47:17 2019

@author: quentin.chateiller
"""

def configure(devDriver,devUsit):

    devUsit.addAction('zero',
                       function=devDriver.setZero)
    
    devUsit.addVariable('autorange',
                       setFunction=devDriver.setAutoRange,
                       getFunction=devDriver.getAutoRange)
    
    devUsit.addVariable('zeroValue',
                       setFunction=devDriver.setZeroValue,
                       getFunction=devDriver.getZeroValue)
    
    devUsit.addVariable('bufferSize',
                       setFunction=devDriver.setBufferSize,
                       getFunction=devDriver.getBufferSize)
    
    devUsit.addVariable('bufferInterval',
                       setFunction=devDriver.setBufferInterval,
                       getFunction=devDriver.getBufferInterval)
    
    devUsit.addVariable('wavelength',
                       setFunction=devDriver.setWavelength,
                       getFunction=devDriver.getWavelength)
    
    devUsit.addVariable('power',
                       getFunction=devDriver.getPower)
    
    devUsit.addVariable('powerMean',
                       getFunction=devDriver.getPowerMean)
    

    