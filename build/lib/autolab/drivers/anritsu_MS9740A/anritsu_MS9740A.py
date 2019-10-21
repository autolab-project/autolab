#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver() :
    
    category = 'Optical Spectrum Analyzer'
    
    def __init__(self):
        pass

    def get_id(self):
        return self.query('*IDN?')
    
    def set_resol(self,value):
        self.write(f'RES {value}')
        self.query('*OPC?')
    
    def get_resol(self):
        return self.query('RES?')
    
    def set_span(self, value):
        self.write(f'SPN {value}')
        self.query('*OPC?')
        
    def get_span(self):
        return self.query('SPN?')
    
    def single_sweep(self):    #single sweep measurement
        self.write('SSI')
        self.query('*OPC?')
        
        
           
#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self,address='GPIB0::1::INSTR', **kwargs):
        import visa
        
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
    
        Driver.__init__(self)
    
    def close(self):
        self.controller.close()
    def query(self,command):
        return self.controller.query(command)
    def write(self,command):
        self.controller.write(command)
############################## Connections classes ##############################
#################################################################################
            


        
    
