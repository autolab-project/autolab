# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 16:35:10 2019

@author: giuseppe
"""

import visa

ADDRESS = 'GPIB0::3::INSTR' #write here the address of your device

class Device() :
    def __init__(self,address=ADDRESS):
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.write_termination = 0x00  #needed in order to read properly from the optical amplifier 
        self.controller.read_termination = 0x00

        
        
        
    def close(self):
        self.controller.close()
        
        
    def query(self,command):
        result = self.controller.query(command) 
        result = result.strip('\x00')
        if '=' in result : result = result.split('=')[1]
        try : result = float(result)
        except: pass
        return result

    
    def write(self,command):
        self.controller.write(command)
        



    def getID(self):
        return self.query('*IDN?')
    
    
    
    
    def setPower(self, value):             # For this model range is from 20dBm to 30dBm, 200=20dBm here 
        self.write(f"CPU="+str(value))
        

    def getPower(self):
        return self.query('CPU?')
    
    