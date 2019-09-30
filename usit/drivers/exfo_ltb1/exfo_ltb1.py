#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


from module_ftb1750 import FTB1750

modules_dict = {'ftb1750':FTB1750}






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
        
    def getID(self):
        return self.write('*IDN?')
    
    
    def getDriverConfig(self):
        config = []
        for name in self.slotnames :
            config.append({'element':'module','name':name,'object':getattr(self,name)})
        return config
    
#################################################################################
############################## Connections classes ##############################
class Device_TELNET(Device):
    
    def __init__(self, address=None, port=None, **kwargs):
        from telnetlib import Telnet
        
        self.TIMEOUT = 1
        
        # Instantiation
        self.controller = Telnet(address,str(port))
        self.read()
        self.read()
        
        Device.__init__(self)
        
    def write(self,command):
        try : self.controller.write(f'{command}\r\n'.encode())
        except : pass
        return self.read()
        
        
    def read(self):
        try :
            ans = self.controller.read_until('READY>'.encode(),timeout=self.TIMEOUT)
            ans = ans.decode().replace('READY>','').strip() 
            assert ans != ''
            return ans
        except :
            pass
        
    def close(self):
        try : self.controller.close()
        except : pass
    
############################## Connections classes ##############################
#################################################################################    
    

if __name__ == '__main__' :
    ADDRESS = '192.168.0.1'
    PORT = 5024


