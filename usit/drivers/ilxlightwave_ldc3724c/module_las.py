# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 14:44:09 2019

@author: qchat
"""
import time


class LAS():
    
    def __init__(self,dev):
        
        self.dev = dev
        self.PRECISION = 0.1


    
    def write(self,command):
        self.dev.write(command)
        
    def query(self,command):
        return self.dev.query(command)
    
    
    
    
    
    def getCurrent(self):
        return float(self.query('LAS:LDI?'))

    def getCurrentSetpoint(self):
        return float(self.query('LAS:SET:LDI?'))
        
    def setCurrent(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.write(f'LAS:LDI {value}')
        self.query('*OPC?')
        if value > 0 :
            if self.isEnabled() is False :
                self.setEnabled(True)
            self.setMode('ILBW')
            self.waitForConvergence(self.getCurrent,value)
        elif value == 0 :
            if self.isEnabled() is True :
                self.setEnabled(False)




    def setPower(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.write(f'LAS:MDP {value}')
        self.query('*OPC?')
        if value > 0 :
            if self.isEnabled() is False :
                self.setEnabled(True)
            self.setMode('MDP')
            self.waitForConvergence(self.getPower,value)
        elif value == 0 :
            if self.isEnabled() is True :
                self.setEnabled(False)

    def getPower(self):
        self.query('*OPC?')
        return float(self.query('LAS:MDP?'))

    def getPowerSetpoint(self):
        return float(self.query('LAS:SET:MDP?'))
    
    
    
    
    def setEnabled(self,value):
        assert isinstance(value,bool)
        self.write(f'LAS:OUT {int(value)}')
        self.query('*OPC?')
        if value is True :
            mode = self.query('LAS:MODE?')
            if mode.startswith('I'):
                self.waitForConvergence(self.getCurrent,
                                        self.getCurrentSetpoint())
            elif mode.startswith('MD'):
                self.waitForConvergence(self.getPower,
                                        self.getPowerSetpoint())
        
    def isEnabled(self):
        return bool(int(self.query('LAS:OUT?')))

    
    
    
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
            self.write(f'LAS:MODE:{mode}')
            self.query('*OPC?')
            self.setEnabled(enabledMode)
            
    def getMode(self):
        return self.query('LAS:MODE?')
        
        
    
    
    