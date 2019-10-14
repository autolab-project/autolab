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
        self.write(f'POW {amplitude}')
    def frequency(self,frequency):
        self.write(f'FREQ {frequency}')

    def idn(self):
        self.write('*IDN?')
        self.read()

#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='TCPIP::192.168.0.3::INSTR', **kwargs):
        import visa as v
        
        rm        = v.ResourceManager()
        self.inst = rm.get_instrument(address)
        Driver.__init__(self, **kwargs)
        
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,query):
        self.inst.write(query)
    def read(self):
        return self.inst.read()
    def close(self):
        self.inst.close()
############################## Connections classes ##############################
#################################################################################


