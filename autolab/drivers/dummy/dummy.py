# -*- coding: utf-8 -*-
"""
Created on Fri May 17 16:36:53 2019

@author: quentin.chateiller
"""
import numpy as np
import time
import pandas as pd



class Driver():
    
    def __init__(self):
        
        self.amp = 1
        
        self.slot1 = Slot(self,1)
        self.slot2 = Slot(self,2)
        
        self.option = True
        
        self.count = 0
        self.phrase = 'Coucou'
        self.sleep = 0
        #raise ValueError('Test error')
        
        self.verbose = False
        
    def set_sleep(self,value):
        self.sleep = value
        
    def get_sleep(self):
        return self.sleep
    
    def set_verbose(self,value):
        self.verbose = value
        
    def get_verbose(self):
        return self.verbose
    
    def get_amplitude(self):
        time.sleep(self.sleep)
        #raise ValueError('Test error')
        #self.count += 1
#        if np.random.uniform() > 0.5 : sign = 1
#        else : sign = -1
#        self.amp = self.amp*(1+sign*np.random.uniform()*0.1)
#        if self.count == 100 :
#            raise ValueError()
        value = self.amp + np.random.uniform(-1, 1)*0.01
        
        if self.verbose : print('get amplitude',value)

        return value
    
    def set_phrase(self,phrase):
        time.sleep(self.sleep)
        assert isinstance(phrase,str)
        self.phrase = phrase
        if self.verbose : print('set phrase',self.phrase)
        
    def get_phrase(self):
        time.sleep(self.sleep)
        if self.verbose : print('get phrase',self.phrase)
        return self.phrase
    
    def set_amplitude(self,value):
        time.sleep(self.sleep)
        self.amp = value
        if self.verbose : print('set amplitude',self.amp)
        #raise ValueError('Test error')
    
    def close(self):
        if self.verbose : print('DUMMY DEVICE CLOSED')
        
    def get_phase(self):
        time.sleep(self.sleep)
        value = np.random.uniform(-1, 1)
        if self.verbose : print('get phase',value)
        return value
    
    def set_phase(self,value):
        time.sleep(self.sleep)
        self.phase = value
        if self.verbose : print('set phase',value)
    
    def do_sth(self):
        time.sleep(self.sleep)
        if self.verbose : print('do sth')
        #raise ValueError('Test error')
        
    def get_dataframe(self):
        df = pd.DataFrame()
        d = {'e':1,'f':2}
        df=df.append(d,ignore_index=True)
        time.sleep(self.sleep)
        if self.verbose : print('get dataframe',d)
        return df
    
    def set_option(self,value):
        time.sleep(self.sleep)
        self.option = bool(value)
        if self.verbose : print('set option',self.option)
        
    def get_option(self):
        time.sleep(self.sleep)
        if self.verbose : print('get option',self.option)
        return self.option
    
    def get_array(self):
        time.sleep(self.sleep)
        return np.ones((3,4))
    
    def get_driver_model(self):
        
        model = []
        
        for i in range(10) :
            if hasattr(self,f'slot{i}') :
                model.append({'element':'module','name':f'slot{i}','object':getattr(self,f'slot{i}')})
        
        model.append({'element':'variable','name':'amplitude','type':float,'unit':'V','read':self.get_amplitude,'write':self.set_amplitude,'help':'This is the amplitude of the device...'})
        model.append({'element':'variable','name':'phrase','type':str,'read':self.get_phrase,'write':self.set_phrase})
        model.append({'element':'variable','name':'phase','type':float,'read':self.get_phase,'write':self.set_phase})
        model.append({'element':'action','name':'something','do':self.do_sth,'help':'This do something...'})
        model.append({'element':'variable','name':'dataframe','type':pd.DataFrame,'read':self.get_dataframe})
        model.append({'element':'variable','name':'option','type':bool,'read':self.get_option,'write':self.set_option})
        model.append({'element':'variable','name':'array','type':np.ndarray,'read':self.get_array})
        model.append({'element':'variable','name':'sleep','type':float,'read':self.get_sleep,'write':self.set_sleep})
        model.append({'element':'variable','name':'verbose','type':bool,'read':self.get_verbose,'write':self.set_verbose})
        
        return model
    
    
class Driver_CONN(Driver):
    
    def __init__(self,address='192.168.0.8',**kwargs):
        print('DUMMY DEVICE INSTANTIATED with address',address)
        
        Driver.__init__(self)
        
    
class Slot() :
    
    def __init__(self,dev,num):
        self.dev = dev
        self.num = num
        
    def get_power(self):
        time.sleep(self.dev.sleep)
        value = np.random.uniform()
        if self.dev.verbose : print(f'slot {self.num} get power',value)
        return value
    
    def get_wavelength(self):
        time.sleep(self.dev.sleep)
        value = np.random.uniform()
        if self.dev.verbose : print(f'slot {self.num} get wavelength',value)
        return value

    def get_driver_model(self):
        config = []
        config.append({'element':'variable','name':'power','type':float,'read':self.get_power,'unit':'W'})
        config.append({'element':'variable','name':'wavelength','type':float,'read':self.get_wavelength,'unit':'nm'})
        return config
