# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 20:06:08 2019

@author: quentin.chateiller
"""

from telnetlib import Telnet
from module_ftb1750 import FTB1750

ADDRESS = '192.168.0.1'
PORT = 5024

modules_dict = {'ftb1750':FTB1750}

class Device():
    
    def __init__(self,address=ADDRESS,port=PORT,**kwargs):
        
        self.TIMEOUT = 1 #s
        
        # Instantiation
        self.controller = Telnet(address,port)
        self.read()
        self.read()
        
        # Submodules
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix):
                slot_num = key[len(prefix):]
                module = modules_dict[ kwargs[key].split(',')[0].strip() ]
                name = kwargs[key].split(',')[1].strip()
                setattr(self,name,module(self,slot_num))
        
    # -------------------------------------------------------------------------
    # Read & Write
    # -------------------------------------------------------------------------
    
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
    
    
    
        
        
        
    def getID(self):
        return self.write('*IDN?')
    
    
    




