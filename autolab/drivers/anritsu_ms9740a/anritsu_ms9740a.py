#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver() :
    def __init__(self):
        pass

    def getID(self):
        return self.query('*IDN?')
    
    def setResol(self,value):
        self.write(f'RES {value}')
        self.query('*OPC?')
    
    def getResol(self):
        return self.query('RES?')
    
    def setSpan(self, value):
        self.write(f'SPN {value}')
        self.query('*OPC?')
        
    def getSpan(self):
        return self.query('SPN?')
    
    def singleweep(self):    #single sweep measurement
        self.write('SSI')
        self.query('*OPC?')
        
        
           
#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self,address='GPIB0::1::INSTR', **kwargs):
        import visa
        
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
    
        Driver.__init__(self, **kwargs)
    
    def close(self):
        self.controller.close()
    def query(self,command):
        return self.controller.query(command)
    def write(self,command):
        self.controller.write(command)
############################## Connections classes ##############################
#################################################################################
            


        
    
