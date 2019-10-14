#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

from numpy import zeros,ones,linspace


class Driver():
    
    category = 'Function generator'
    
    def __init__(self):
        pass
    def amplitude(self,amplitude):
        self.write('VOLT '+str(amplitude))
    def offset(self,offset):
        self.write('VOLT:OFFS '+str(offset))
    def frequency(self,frequency):
        self.write('FREQ '+str(frequency))
    def ramp(self,ramp):
        l   = list(zeros(5000) - 1)
        lll = list(ones(5000))
        ll  = list(linspace(-1,1,100+ramp))
        l.extend(ll);l.extend(lll)
        s = str(l)[1:-1]
        self.write('DATA VOLATILE,'+s)

    def idn(self):
        self.inst.write('*IDN?')
        self.read()
        
    def getDriverConfig(self):
        
        config = []
        
        config.append({'element':'variable','name':'amplitude','write':self.amplitude,'type':float,'help':'Amplitude'})
        config.append({'element':'variable','name':'offset','write':self.offset,'type':float,'help':'Offset'})
        config.append({'element':'variable','name':'frequency','write':self.frequency,'type':float,'help':'Frequency'})
        
        return config


#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::2::INSTR',**kwargs):
        import visa
        
        rm = visa.ResourceManager()
        self.inst = rm.get_instrument(address)
        
        Driver.__init__(self)
        
    def close(self):
        self.inst.close()
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,command):
        self.inst.write(command)
    def read(self):
        rep = self.inst.read()
        return rep
############################## Connections classes ##############################
#################################################################################


