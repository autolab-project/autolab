#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver():
    
    category = 'Function generator'
    
    def __init__(self):        
        pass
    
    def amplitude(self,amplitude):
        self.write('AMPL '+amplitude)
    def offset(self,offset):
        self.write('OFFS '+offset)
    def frequency(self,frequency):
        self.write('FREQ '+frequency)
    def phase(self,phase):
        self.write('PHSE '+phase)

    def idn(self):
        return self.query('*IDN?')
        
    def getDriverConfig(self):
        config = []
        config.append({'element':'variable','name':'amplitude','type':float,'unit':'V','write':self.amplitude,'help':'Voltage amplitude.'})
        config.append({'element':'variable','name':'offset','type':float,'unit':'V','write':self.offset,'help':'Voltage offset'})
        config.append({'element':'variable','name':'phase','type':float,'write':self.phase,'help':'Phase'})
        config.append({'element':'variable','name':'frequency','type':float,'unit':'Hz','write':self.frequency,'help':'Output frequency'})
        return config


#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::19::INSTR',**kwargs):
        import visa
        
        rm = visa.ResourceManager()
        self.inst = rm.get_instrument(address)
        
        Driver.__init__(self)
        
    def close(self):
        self.inst.close()
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,query):
        self.inst.write(query)
    def read(self):
        rep = self.inst.read()
        return rep
    
class Driver_GPIB(Driver):
    def __init__(self,address=19,board_index=0,**kwargs):
        import Gpib
        
        self.inst = Gpib.Gpib(int(address),int(board_index))
        Driver.__init__(self)
    
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,query):
        self.inst.write(query)
    def read(self):
        return self.inst.read()
    def close(self):
        """WARNING: GPIB closing is automatic at sys.exit() doing it twice results in a gpib error"""
        Gpib.gpib.close(self.inst.id)
############################## Connections classes ##############################
#################################################################################


