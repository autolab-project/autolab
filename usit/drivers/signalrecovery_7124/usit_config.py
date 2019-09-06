# -*- coding: utf-8 -*-
"""
Created on Thu May  2 16:47:17 2019

@author: quentin.chateiller
"""

def configure(devDriver,devUsit):

    devUsit.addVariable('magnitude',
                        getFunction=devDriver.getMagnitude)
    
    devUsit.addVariable('phase',
                        getFunction=devDriver.getPhase)
    
    devUsit.addVariable('refFrequency',
                        getFunction=devDriver.getRefFrequency)
    
    devUsit.addVariable('timeConstant',
                        getFunction=devDriver.getTimeConstant)
    
    devUsit.addVariable('sensitivity',
                        getFunction=devDriver.getSensitivity)
    
    devUsit.addAction('waitFourTimeConstant',
                        function=devDriver.waitFourTimeConstant)
    
    