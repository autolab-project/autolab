# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 20:06:08 2019

@author: quentin.chateiller
"""

from module_nsr1 import NSR1
import visa


ADDRESS = 'ASRL4::INSTR'

modules_dict = {'nsr1':NSR1}

class Device():
    
    def __init__(self,address=ADDRESS,**kwargs):
        
        self.BAUDRATE = 115200
        
        # Initialisation
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.baud_rate = self.BAUDRATE
        
        # Submodules
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix):
                slot_num = key[len(prefix):]
                module = modules_dict[ kwargs[key].split(',')[0].strip() ]
                name = kwargs[key].split(',')[1].strip()
                calibpath = kwargs[key].split(',')[2].strip()
                setattr(self,name,module(self,slot_num,name,calibpath))
        
        
    def close(self):
        try : self.controller.close()
        except : pass

    def query(self,command):
        result = self.controller.query(command)
        result = result.strip('\r\n')
        return result
    
    def write(self,command):
        self.controller.write(command)
        
        

    