# -*- coding: utf-8 -*-
"""
Created on Thu May  2 16:47:17 2019

@author: quentin.chateiller
"""

def configure(devDriver,devUsit):
    
    devUsit.addVariable('amplitude',
                        getFunction=devDriver.getAmplitude,
                        setFunction=devDriver.setAmplitude,
                        unit='V')
    
    devUsit.addVariable('phase',
                        getFunction=devDriver.getPhase)
    
    devUsit.addAction('sth',
                        function=devDriver.doSth)
    
    devUsit.addVariable('dataframe',
                        getFunction=devDriver.getDataframe)