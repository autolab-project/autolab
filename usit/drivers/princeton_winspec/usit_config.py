# -*- coding: utf-8 -*-
"""
Created on Thu May  2 16:47:17 2019

@author: quentin.chateiller
"""

def configure(devDriver,devUsit):

    devUsit.addVariable('exposureTime',
                        setFunction=devDriver.setExposureTime,
                        getFunction=devDriver.getExposureTime)
    
    devUsit.addVariable('autoExposureTime',
                        setFunction=devDriver.setAutoExposureTimeEnabled,
                        getFunction=devDriver.isAutoExposureTimeEnabled)
    
    devUsit.addVariable('autoBackgroundRemoval',
                        setFunction=devDriver.setAutoBackgroundRemovalEnabled,
                        getFunction=devDriver.isAutoBackgroundRemovalEnabled)
    
    devUsit.addVariable('spectrum',
                        getFunction=devDriver.getSpectrum)
    
    devUsit.addVariable('temperature',
                        getFunction=devDriver.getTemperature)
    
    devUsit.addVariable('mainPeakWavelength',
                        getFunction=devDriver.getMainPeakWavelength)
    
    devUsit.addVariable('mainPeakFwhm',
                        getFunction=devDriver.getMainPeakFWHM)
    
    devUsit.addVariable('maxPower',
                        getFunction=devDriver.getMaxPower)
    
    devUsit.addVariable('integratedPower',
                        getFunction=devDriver.getIntegratedPower)
    
    devUsit.addAction('acquire',
                      function=devDriver.acquireSpectrum)
    
    
    