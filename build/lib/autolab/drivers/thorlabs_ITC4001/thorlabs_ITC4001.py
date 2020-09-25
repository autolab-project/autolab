#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- thorlabs ITC4001
"""


class Driver():
    
    def __init__(self):
        pass

    def amplitude(self,amplitude):
        self.write(f'SOUR:CURR {amplitude}\n')
            
    def get_driver_model(self):
        config = []        
        config.append({'element':'variable','name':'amplitude','write':self.amplitude,'type':float,'help':"Set the pumping current value"})
        return config


#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::2::INSTR',**kwargs):
        import visa

        rm = visa.ResourceManager()
        self.inst = rm.get_instrument(address)
        Driver.__init__(self)
        
    def query(self, cmd):
        self.write(cmd)
        r = self.read()
        return r
    def read(self):
        return self.inst.read()
    def write(self,cmd):
        self.inst.write(cmd+'\n')
    def close(self):
        self.inst.close()
############################## Connections classes ##############################
#################################################################################
        
