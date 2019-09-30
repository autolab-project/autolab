#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


from module_nsr1 import NSR1

modules_dict = {'nsr1':NSR1}





class Device():
    
    def __init__(self,**kwargs):
        
        # Submodules
        # DEVICE_CONFIG.ini : slot<NUM> = <MODULE>,<NAME>,<CALIBPATH>
        self.slotnames = []
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix):
                slot_num = key[len(prefix):]
                module = modules_dict[ kwargs[key].split(',')[0].strip() ]
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
    def __init__(self, address):
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