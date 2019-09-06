# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 20:06:08 2019

@author: quentin.chateiller
"""
import visa
import time 

from module_las import LAS
from module_tec import TEC

ADDRESS = 'ASRL5::INSTR'

class Device():
    
    def __init__(self,address=ADDRESS):
        
        
        # Instantiation
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.baud_rate = 19200
        self.controller.timeout = 10000
        self.controller.read_termination='\n'
        self.controller.write_termination='\n'
#        
        # Initialisation
        self.write('*CLS')      # Clear status registers
        self.write('DELAY 0')   # User commands not delayed
        
        # Subdevices
        self.tec = TEC(self)
        self.las = LAS(self)
        
    def close(self):
        try : self.controller.close()
        except : pass

    def query(self,command):
        result = self.controller.query(command)
        if '=' in result : result = result.split('=')[1]
        try : result = float(result)
        except: pass
        return result
    
    def write(self,command):
        self.controller.write(command)
        time.sleep(0.1) # required by experience
        
        
        
        
        
        
        
    def getID(self):
        return self.query('*IDN?')
    
    
    


    
    

