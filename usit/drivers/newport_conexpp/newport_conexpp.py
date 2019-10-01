#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


from module_nsr1 import NSR1

modules = {'nsr1':NSR1}





class Device():
    
    slotNaming = 'slot<NUM> = <MODULE_NAME>,<SLOT_NAME>,<CALIBRATION_PATH>'
    
    def __init__(self,**kwargs):
        
        # Submodules
        self.slotnames = []
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix):
                slot_num = key[len(prefix):]
                module = modules[ kwargs[key].split(',')[0].strip() ]
                name = kwargs[key].split(',')[1].strip()
                calibpath = kwargs[key].split(',')[2].strip()
                setattr(self,name,module(self,slot_num,name,calibpath))
                self.slotnames.append(name)
        
        
    def getDriverConfig(self):
        
        config = []
        for name in self.slotnames :
            config.append({'element':'module','name':name,'object':getattr(self,name)})
        return config
        
        
    
#################################################################################
############################## Connections classes ##############################
class Device_VISA(Device):
    def __init__(self, address='GPIB0::2::INSTR'):
        import visa
        
        
        self.BAUDRATE = 115200
        
        # Initialisation
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.baud_rate = self.BAUDRATE
        
        Device.__init__(self)
        
        
        
    def close(self):
        try : self.controller.close()
        except : pass

    def query(self,command):
        result = self.controller.query(command)
        result = result.strip('\r\n')
        return result
    
    def write(self,command):
        self.controller.write(command)
        
        
############################## Connections classes ##############################
#################################################################################