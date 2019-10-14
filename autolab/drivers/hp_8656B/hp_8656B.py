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

    def set_frequency(self, frequency):
        self.write('FR' + frequency + 'HZ')

    def set_rfamp(self, amplitude):
        self.write('AP' + amplitude + 'MV')

    def RFdisable(self):
        self.write('R2')

    def RFenable(self):
        self.write('R3')


#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB::7::INSTR', **kwargs):
        import visa as v
        
        r = v.ResourceManager()
        self.scope = r.get_instrument(address)
        Driver.__init__(self, **kwargs)
        
    def query(self, query, length=1000000):
        self.write(query)
        r = self.read(length=length)
        return r
    def write(self, query):
        self.string = query + '\n'
        self.scope.write(self.string)
    def read(self, length=10000000):
        rep = self.scope.read_raw()
        return rep
        
############################## Connections classes ##############################
#################################################################################

