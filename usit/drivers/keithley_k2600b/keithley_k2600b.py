# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 20:06:08 2019

@author: quentin.chateiller
"""
import visa
from module_line import Line

ADDRESS = 'GPIB0::10::INSTR'

class Device():
    
    
    def __init__(self,address=ADDRESS):
        
        self.TIMEOUT = 1000 #ms
        
        # Instantiation
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(self.address)
        self.controller.timeout = self.TIMEOUT
        
        # Initialisation
        self.write('*CLS')
        
        # Subdevices
        self.source1 = Line(self,1)
        self.source2 = Line(self,2)
        
    def close(self):
        try : self.controller.close()
        except : pass

    def query(self,command):
        result = self.controller.query(command)
        result = result.strip('\n')
        if '=' in result : result = result.split('=')[1]
        try : result = float(result)
        except: pass
        return result
    
    def write(self,command):
        self.controller.write(command)
        
    
    
    def setSafeState(self):
        self.source1.setSafeState()
        self.source2.setSafeState()
    
    def getID(self):
        return self.query('*IDN?')
        
        

