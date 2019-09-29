# -*- coding: utf-8 -*-
"""
Created on Thu May  2 16:47:17 2019

@author: quentin.chateiller
"""
import pandas as pd 
import numpy as np

def configure(devDriver,devUsit):
    
    devUsit.addVariable('amplitude',float,
                        getFunction=devDriver.getAmplitude,
                        setFunction=devDriver.setAmplitude,
                        unit='V')
    
    devUsit.addVariable('phase',float,
                        getFunction=devDriver.getPhase)
    
    devUsit.addAction('sth',
                        function=devDriver.doSth)
    
    devUsit.addVariable('dataframe',pd.DataFrame,
                        getFunction=devDriver.getDataframe)
    
    devUsit.addVariable('option',bool,
                        setFunction=devDriver.setOption,
                        getFunction=devDriver.getOption,)
    
    devUsit.addVariable('phrase',str,
                        setFunction=devDriver.setPhrase,
                        getFunction=devDriver.getPhrase,)
    
    devUsit.addVariable('array',type(np.array([])),
                        getFunction=devDriver.getArray,)
    
    
    for i,slot in [(1,devDriver.slot1),(2,devDriver.slot2)] : 
        mod = devUsit.addModule(f'slot{i}')
        mod.addVariable('power',float,getFunction=slot.getPower)
        mod.addVariable('wavelength',float,getFunction=slot.getWavelength)
