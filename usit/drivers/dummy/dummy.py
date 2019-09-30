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
        
        self.slot1 = Slot(1)
        self.slot2 = Slot(2)
        
        self.option = True
        
        self.count = 0
        self.phrase = 'Coucou'
        #raise ValueError('Test error')
    
    def getAmplitude(self):
        time.sleep(0.05)
        #raise ValueError('Test error')
        #self.count += 1
#        if np.random.uniform() > 0.5 : sign = 1
#        else : sign = -1
#        self.amp = self.amp*(1+sign*np.random.uniform()*0.1)
#        if self.count == 100 :
#            raise ValueError()
        value = self.amp + np.random.uniform(-1, 1)*0.01
        print('get amplitude',value)

        return value
    
    def setPhrase(self,phrase):
        assert isinstance(phrase,str)
        self.phrase = phrase
        print('set phrase',self.phrase)
        
    def getPhrase(self):
        print('get phrase',self.phrase)
        return self.phrase
    
    def setAmplitude(self,value):
        self.amp = value
        print('set amplitude',self.amp)
        #raise ValueError('Test error')
    
    def close(self):
        print('DUMMY DEVICE CLOSED')
        
    def getPhase(self):
        value = np.random.uniform(-1, 1)
        print('get phase',value)
        return value
    
    def doSth(self):
        time.sleep(1)
        print('do sth')
        #raise ValueError('Test error')
        
    def getDataframe(self):
        df = pd.DataFrame()
        d = {'e':1,'f':2}
        df=df.append(d,ignore_index=True)
        print('get dataframe',d)
        return df
    
    def setOption(self,value):
        self.option = bool(value)
        print('set option',self.option)
        
    def getOption(self):
        print('get option',self.option)
        return self.option
    
    def getArray(self):
        return np.ones((3,4))
    
    def getDriverConfig(self):
        
        config = []
        
        for i in range(10) :
            if hasattr(self,f'slot{i}') :
                config.append({'element':'module','name':f'slot{i}','object':getattr(self,f'slot{i}')})
        
        config.append({'element':'variable','name':'amplitude','type':float,'unit':'V',
                       'read':self.getAmplitude,'write':self.setAmplitude,
                       'help':'This is the amplitude of the device...'})
        config.append({'element':'variable','name':'phrase','type':str,
                       'read':self.getPhrase,'write':self.setPhrase})
        config.append({'element':'variable','name':'phase','type':float,'read':self.getPhase})
        config.append({'element':'action','name':'something','do':self.doSth,
                       'help':'This do something...'})
        config.append({'element':'variable','name':'dataframe','type':pd.DataFrame,
                       'read':self.getDataframe})
        config.append({'element':'variable','name':'option','type':bool,
                       'read':self.getOption,'write':self.setOption})
        config.append({'element':'variable','name':'array','type':np.ndarray,
                       'read':self.getArray})
        return config
    
    
class Slot() :
    
    def __init__(self,num):
        self.num = num
        
    def getPower(self):
        value = np.random.uniform()
        print(f'slot {self.num} get power',value)
        return value
    
    def getWavelength(self):
        value = np.random.uniform()
        print(f'slot {self.num} get wavelength',value)
        return value

    def getDriverConfig(self):
        config = []
        config.append({'element':'variable','name':'power','type':float,'read':self.getPower,'unit':'W'})
        config.append({'element':'variable','name':'wavelength','type':float,'read':self.getWavelength,'unit':'nm'})
        return config