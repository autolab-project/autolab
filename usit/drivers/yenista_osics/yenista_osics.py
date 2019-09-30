#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

from module_sld import SLD
from module_t100 import T100

modules_dict = {'sld':SLD,'t100':T100}



class Device():

    def __init__(self,**kwargs):
        
        self.write('*RST') # The input buffer is cleared. The command interpreter is reset and a reset instruction is sent to every module. The status and event registers are cleared. Sets the OPC bit to 1.
        self.write('*CLS') # Clears the Event Status Register and the output queue. Sets the OPC bit to 1.
        
        # Submodules
        # DEVICE_CONFIG.ini : slot<NUM> = <MODULE>,<NAME>
        self.slotnames = []
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix):
                slot_num = key[len(prefix):]
                module = modules_dict[ kwargs[key].split(',')[0].strip() ]
                name = kwargs[key].split(',')[1].strip()
                setattr(self,name,module(self,slot_num))
                self.slotnames.append(name)


    def getID(self):
        return self.query('*IDN?')


    def getDriverConfig(self):
        config = []
        for name in self.slotnames :
            config.append({'element':'module','name':name,'object':getattr(self,name)})
        return config


#################################################################################
############################## Connections classes ##############################
class Device_VISA(Device):
    def __init__(self, address=None,**kwargs):
        
        import visa
        
        
        self.TIMEOUT = 60000 #ms
        
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.timeout = self.TIMEOUT
        
        Device.__init__(self,**kwargs)
        

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
        
############################## Connections classes ##############################
#################################################################################



#ADDRESS = 'GPIB0::11::INSTR'
        
    
    
  
  