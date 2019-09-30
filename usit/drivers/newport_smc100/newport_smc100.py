#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- Newport smc100
"""

from module_ils100cc import ILS100CC

modules_dict = {'ils100cc':ILS100CC}




class Device():
    
    def __init__(self,**kwargs):
        
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


    def getDriverConfig(self):
        
        config = []
        for name in self.slotnames:
            config.append({'element':'module','name':name,'object':getattr(self,name)})
        return config
    
#################################################################################
############################## Connections classes ##############################
class Device_VISA(Device):
    def __init__(self, address, **kwargs):
        import visa
        
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.baud_rate = 57600
        self.controller.flow_control = visa.constants.VI_ASRL_FLOW_XON_XOFF
        self.controller.read_termination = '\r\n'
        
        Device.__init__(self, **kwargs)
    

    def query(self,command,unwrap=True) :
        result = self.controller.query(command)
        if unwrap is True :
            try:
                prefix=self.SLOT+command[0:2]
                result = result.replace(prefix,'')
                result = result.strip()
                result = float(result)
            except:
                pass
        return result
        
    def write(self,command) :
        self.controller.write(command)

############################## Connections classes ##############################
#################################################################################
        
            
if __name__ == '__main__' :
    ADDRESS = "ASRL1::INSTR"

