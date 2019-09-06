# -*- coding: utf-8 -*-
"""
Created on Fri May 17 16:36:53 2019

@author: quentin.chateiller
"""
import numpy as np
import time
import pandas as pd

class Device():
    
    def __init__(self,address=2):
        
        self.amp = 1
        print('DUMMY DEVICE INSTANTIATED with address',address)
    
    def getAmplitude(self):
        return self.amp
    
    def setAmplitude(self,value):
        self.amp = value
        print('DUMMY DEVICE Amplitude set to '+str(value))
    
    def close(self):
        print('DUMMY DEVICE CLOSED')
        
    def getPhase(self):
        return np.random.uniform()
    
    def doSth(self):
        time.sleep(1)
        print('DUMMY DEVICE Action asked ')
        
    def getDataframe(self):
        df = pd.DataFrame()
        d = {'e':1,'f':2}
        df=df.append(d,ignore_index=True)
        return df
    
    