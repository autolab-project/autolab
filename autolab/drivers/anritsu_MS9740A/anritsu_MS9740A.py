#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver() :
    
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
        
    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'resolution','write':self.set_resol,'read':self.get_resol,'type':float,'help':"Resolution"})
        model.append({'element':'variable','name':'span','write':self.set_span,'read':self.get_span,'type':float,'help':"Span"})
        model.append({'element':'action','name':'single_sweep','do':self.single_sweep,'help':"Perform a single sweep"})

        return model
           
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
            


        
    
