# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 08:51:25 2019

@author: qchat
"""

import visa

from module_ils100cc import ILS100CC

modules_dict = {'ils100cc':ILS100CC}

ADDRESS = "ASRL1::INSTR"



class Device():
    
    def __init__(self,address=ADDRESS,**kwargs):
        
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.baud_rate = 57600
        self.controller.flow_control = visa.constants.VI_ASRL_FLOW_XON_XOFF
        self.controller.read_termination = '\r\n'
        
        
        # Submodules
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix):
                slot_num = key[len(prefix):]
                module = modules_dict[ kwargs[key].split(',')[0].strip() ]
                name = kwargs[key].split(',')[1].strip()
                setattr(self,name,module(self,slot_num))



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
    
    
    
            


