# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 16:47:10 2019

@author: qchat
"""

  

class SLD():   
    
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
        return self.dev.query(self.prefix+'*IDN?')
        
        
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
    
    

        
    def getWavelength(self):
        result = self.query(self.prefix+'L?')
        result = self.cleanResult(result)
        return result
    
    
   
    
    
    def setPower(self,value):
        if value < 5:
            self.setOutputState(False)
        elif 5<=value<10 :
            if self.getOutputState() is False :
                self.setOutputState(True)
            self.write(self.prefix+'P=LOW')
            self.query('*OPC?')
        else :
            if self.getOutputState() is False :
                self.setOutputState(True)
            self.write(self.prefix+'P=HIGH')
            self.query('*OPC?')   
            
            
        
    def getPower(self):
        result = self.query(self.prefix+'P?')
        result = self.cleanResult(result)
        if result == 'Disabled':
            return 0
        elif result == 'HIGH':
            return 10
        elif result == 'LOW' :
            return 5
    
    
  
    
    
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
    

    