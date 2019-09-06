# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 14:44:28 2019

@author: qchat
"""

import time

class TEC():
    
    def __init__(self,dev):
        
        self.dev = dev
        self.PRECISION = 0.05



    def write(self,command):
        self.dev.write(command)
        
    def query(self,command):
        return self.dev.query(command)
    
    
    

    def getResistance(self):
        return float(self.query('TEC:R?'))



    def setGain(self,value):
        assert isinstance(int(value),int)
        value = int(value)
        self.write(f'TEC:GAIN {value}')
        self.query('*OPC?')
        
    def getGain(self):
        return int(float(self.query('TEC:GAIN?')))
   
    

    
    def getCurrent(self):
        return float(self.query('TEC:ITE?'))

    def getCurrentSetpoint(self):
        return float(self.query('TEC:SET:ITE?'))
        
    def setCurrent(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.write(f'TEC:ITE {value}')
        self.query('*OPC?')
        if value > 0 :
            if self.isEnabled() is False :
                self.setEnabled(True)
            self.setMode('ITE')
            self.waitForConvergence(self.getCurrent,value)
        elif value == 0 :
            if self.isEnabled() is True :
                self.setEnabled(False)




    def setTemperature(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.write(f'TEC:T {value}')
        self.query('*OPC?')
        if value > 0 :
            if self.isEnabled() is False :
                self.setEnabled(True)
            self.setMode('T')
            self.waitForConvergence(self.getTemperature,value)
        elif value == 0 :
            if self.isEnabled() is True :
                self.setEnabled(False)

    def getTemperature(self):
        return float(self.query('TEC:T?'))

    def getTemperatureSetpoint(self):
        return float(self.query('TEC:SET:T?'))
    
    

    
    
    def setEnabled(self,value):
        assert isinstance(value,bool)
        self.write(f'TEC:OUT {int(value)}')
        self.query('*OPC?')
        if value is True :
            mode = self.query('TEC:MODE?')
            if mode.startswith('I'):
                self.waitForConvergence(self.getCurrent,
                                        self.getCurrentSetpoint())
            elif mode.startswith('T'):
                self.waitForConvergence(self.getTemperature,
                                        self.getTemperatureSetpoint())
        
    def isEnabled(self):
        return bool(int(self.query('TEC:OUT?')))
    
    
    
    
    
    def waitForConvergence(self,func,setPoint):
        tini = time.time()
        while True :
            try : 
                if abs(func()-setPoint) < self.PRECISION*setPoint :
                    break
                else :
                    time.sleep(0.5)
            except :
                pass
            if time.time() - tini > 5 :
                break
            
            
            
            
    def setMode(self,mode):
        assert isinstance(mode,str)
        currMode = self.getMode()
        enabledMode = self.isEnabled()
        if currMode != mode :
            self.write(f'TEC:MODE:{mode}')
            self.query('*OPC?')
            self.setEnabled(enabledMode)
            
    def getMode(self):
        return self.query('TEC:MODE?')
        
        
        