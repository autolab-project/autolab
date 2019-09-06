# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 16:30:37 2019

@author: giuseppe
"""


import visa

ADDRESS = 'GPIB0::1::INSTR' #write here the address of your device

class Device() :
    def __init__(self,address=ADDRESS):
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        
        
    def close(self):
        self.controller.close()
        
        
    def query(self,command):
        return self.controller.query(command)

    
    def write(self,command):
        self.controller.write(command)
        

    

    def getID(self):
        return self.query('*IDN?')
    
    
    
    
    def setResol(self,value):
        self.write(f'RES {value}')
        self.query('*OPC?')
    
    
    def getResol(self):
        return self.query('RES?')
    
    
    
    
    def setSpan(self, value):
        self.write(f'SPN {value}')
        self.query('*OPC?')
        

    def getSpan(self):
        return self.query('SPN?')
    
    
    
    
    def singleweep(self):    #single sweep measurement
        self.write('SSI')
        self.query('*OPC?')
        
        
           
        
        
            


        
    