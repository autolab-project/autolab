# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 16:45:47 2019

@author: qchat
"""

class T100():   
    
    def __init__(self,dev,slot):
        
        self.dev = dev
        self.SLOT = slot
        self.prefix = f'CH{int(slot)}:'
        
        self.write(self.prefix+'NM')
        self.write(self.prefix+'MW')


    def write(self,command):
        self.dev.write(command)
        
    def read(self):
        return self.dev.read()
    
    def query(self,command):
        return self.dev.query(command)
    
    #--------------------------------------------------------------------------
    # Optional functions
    #--------------------------------------------------------------------------
    
    def setSafeState(self):
        self.setOutputState(False)
        if self.getOutputState() is False :
            return True
            

    def getID(self):
        result = self.query(self.prefix+'*IDN?')
        result = self.cleanResult(result)
        return result
        
        
    #--------------------------------------------------------------------------
    # Instrument variables
    #--------------------------------------------------------------------------
        
    def cleanResult(self,result):
        try:
            result=result.split(':')[1]
            result=result.split('=')[1]
            result=float(result)
        except:
            pass
        return result
    
    


    def setWavelength(self,value):
        self.write(self.prefix+f"L={value}")
        self.query('*OPC?')
        
    def getWavelength(self):
        result = self.query(self.prefix+'L?')
        result = self.cleanResult(result)
        return result
    
    
    
    
    
    def setFrequency(self,value):
        self.write(self.prefix+f"F={value}")
        self.query('*OPC?')
        
    def getFrequency(self):
        result = self.query(self.prefix+'F?')
        result = self.cleanResult(result)
        return result
    
    
    
    
    
    
    def setPower(self,value):
        if value == 0 :
            self.setOutputState(False)
        else :
            if self.getOutputState() is False :
                self.setOutputState(True)
            self.write(self.prefix+f"P={value}")
            self.query('*OPC?')
            
    def getPower(self):
        result = self.query(self.prefix+'P?')
        result = self.cleanResult(result)
        if result == 'Disabled':
            return 0
        else :
            return result
    




    
    def setIntensity(self,value):
        if value == 0 :
            self.setOutputState(False)
        else :
            if self.getOutputState() is False :
                self.setOutputState(True)
            self.write(self.prefix+f"I={value}")
            self.query('*OPC?')
        
    def getIntensity(self):
        result = self.query(self.prefix+'I?')
        result = self.cleanResult(result)
        if result == 'Disabled':
            return 0
        else :
            return result
        
        
    
    
    
    def setCoherenceControlState(self,state):
        if state is True :
            self.write(self.prefix+'CTRL ON')
        else :
            self.write(self.prefix+'CTRL OFF')
        self.query('*OPC?')
        
    def getCoherenceControlState(self):
        result = self.query(self.prefix+'CTRL?')
        result = self.cleanResult(result)
        return bool(int(result))
    
    
    
    
    def setAutoPeakFindControlState(self,state):
        if state is True :
            self.write(self.prefix+'APF ON')
        else :
            self.write(self.prefix+'APF OFF')
        self.query('*OPC?')
        
    def getAutoPeakFindControlState(self):
        result = self.query(self.prefix+'APF?')
        result = self.cleanResult(result)
        return bool(int(result))
    
    
    
    
    
    def setOutputState(self,state):
        if state is True :
            self.write(self.prefix+"ENABLE")
        else :
            self.write(self.prefix+"DISABLE")
        self.query('*OPC?')
        
    def getOutputState(self):
        result = self.query(self.prefix+'ENABLE?')
        result = self.cleanResult(result)
        return result == 'ENABLED'
    