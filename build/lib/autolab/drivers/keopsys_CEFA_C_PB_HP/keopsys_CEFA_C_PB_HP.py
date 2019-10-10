#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- Keopsys CEFA-C-PB-HP
"""




class Driver() :
    
    category = 'Optical amplifier'
    
    def __init__(self):
        pass
        
    def getID(self):
        return self.query('*IDN?')
    
    def setPower(self, value):             # For this model range is from 20dBm to 30dBm, 200=20dBm here 
        self.write(f"CPU="+str(value))
        
    def getPower(self):
        return self.query('CPU?')
    
    def getDriverConfig(self):
        config = []
        config.append({'element':'variable','name':'power','type':float,'read':self.getPower,'write':self.setPower, 'help':'Set power.'})
        return config
    
#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::2::INSTR', **kwargs):
        import visa
        
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.write_termination = 0x00  #needed in order to read properly from the optical amplifier 
        self.controller.read_termination = 0x00

        Driver.__init__(self, **kwargs)

    def close(self):
        self.controller.close()
        
    def query(self,command):
        result = self.controller.query(command) 
        result = result.strip('\x00')
        if '=' in result : result = result.split('=')[1]
        try : result = float(result)
        except: pass
        return result

    def write(self,command):
        self.controller.write(command)
############################## Connections classes ##############################
#################################################################################
        
if __name__ == '__main__':
    ADDRESS = 'GPIB0::3::INSTR' #write here the address of your device
