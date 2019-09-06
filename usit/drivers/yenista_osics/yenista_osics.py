# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 20:06:08 2019

@author: quentin.chateiller
"""
import visa

from module_sld import SLD
from module_t100 import T100

ADDRESS = 'GPIB0::11::INSTR'

modules_dict = {'sld':SLD,'t100':T100}

class Device():

    def __init__(self,address=ADDRESS,**kwargs):
        
        self.TIMEOUT = 60000 #ms
        
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.timeout = self.TIMEOUT

        self.write('*RST') # The input buffer is cleared. The command interpreter is reset and a reset instruction is sent to every module. The status and event registers are cleared. Sets the OPC bit to 1.
        self.write('*CLS') # Clears the Event Status Register and the output queue. Sets the OPC bit to 1.
        
        # Submodules
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix):
                slot_num = key[len(prefix):]
                module = modules_dict[ kwargs[key].split(',')[0].strip() ]
                name = kwargs[key].split(',')[1].strip()
                setattr(self,name,module(self,slot_num))



    def close(self):
        try : self.controller.close()
        except : pass

    
    
    
    def write(self,command):
        self.controller.write(command)
        
    def read(self):
        result = self.controller.read()
        result = result.strip('\n')
        return result
    
    def query(self,command):
        result = self.controller.query(command)
        result = result.strip('\n')
        return result
        
    
    
    
    def getID(self):
        return self.query('*IDN?')









        
    
    
  
  