#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- Keopsys CEFA-C-PB-HP
"""




class Driver() :
    
    def __init__(self):
        pass
        
    def get_id(self):
        return self.query('*IDN?')
    
    def set_power(self, value):             # For this model range is from 20dBm to 30dBm, 200=20dBm here 
        self.write(f"CPU="+str(value))
        
    def get_power(self):
        return float(self.query('CPU?').split('=')[1])
    
    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'power','type':float,'read':self.get_power,'write':self.set_power, 'help':'Set power.'})
        return model
    
#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::2::INSTR', **kwargs):
        import visa
        
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.write_termination = 0x00  #needed in order to read properly from the optical amplifier 
        self.controller.read_termination = 0x00

        Driver.__init__(self)

    def close(self):
        self.controller.close()
        
    def query(self,command):
        result = self.controller.query(command) 
        result = result.strip('\x00')
        return result

    def write(self,command):
        self.controller.write(command)
############################## Connections classes ##############################
#################################################################################


