#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

from numpy import zeros,ones,linspace


class Driver():
    
    def __init__(self):
        pass
    def amplitude(self,amplitude):
        self.write(f'VOLT {amplitude}')
    def get_amplitude(self):
        return float(self.query(f'VOLT?'))
    def offset(self,offset):
        self.write(f'VOLT:OFFS {offset}')
    def get_offset(self):
        return float(self.query(f'VOLT:OFFS?'))
    def frequency(self,frequency):
        self.write(f'FREQ {frequency}')
    def get_frequency(self):
        return float(self.query(f'FREQ?'))
    def ramp(self,ramp):
        l   = list(zeros(5000) - 1)
        lll = list(ones(5000))
        ll  = list(linspace(-1,1,100+ramp))
        l.extend(ll);l.extend(lll)
        s = str(l)[1:-1]
        self.write(f'DATA VOLATILE,{s}')

    def idn(self):
        self.write('*IDN?')
        return self.read()
        
    def get_driver_model(self):
        
        model = []
        model.append({'element':'variable','name':'amplitude','write':self.amplitude,'read':self.get_amplitude,'unit':'V','type':float,'help':'Amplitude'})
        model.append({'element':'variable','name':'offset','write':self.offset,'read':self.get_offset,'unit':'V','type':float,'help':'Offset'})
        model.append({'element':'variable','name':'frequency','write':self.frequency,'read':self.get_frequency,'unit':'Hz','type':float,'help':'Frequency'})
        
        return model


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
        
class Driver_GPIB(Driver):
    def __init__(self,address=2,board_index=0,**kwargs):
        import Gpib
        
        self.inst = Gpib.Gpib(int(board_index),int(address))
        Driver.__init__(self, **kwargs)
    
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,command):
        self.inst.write(command)
    def read(self,length=1000000000):
        return self.inst.read(length).decode().strip('\r\n')
    def close(self):
        """WARNING: GPIB closing is automatic at sys.exit() doing it twice results in a gpib error"""
        #Gpib.gpib.close(self.inst.id)
        pass
############################## Connections classes ##############################
#################################################################################


