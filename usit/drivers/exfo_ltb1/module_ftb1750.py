#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class FTB1750():
    
    def __init__(self,dev,slot):
        
        self.dev = dev
        self.SLOT = slot
        
        # Initialisation
        self.dev.write(f"LINS1:UNIT{self.SLOT}:POW W")                # Unité = Watts
        self.dev.write(f"LINS1:SENS{self.SLOT}:POW:RANG:AUTO 1")      # Ajuster la gamme de mesure automatiquement
        self.dev.write(f"LINS1:SENS{self.SLOT}:POW:REF:STAT 0")       # Set Absolute power measurment mode (dBm or W)
        self.dev.write('*OPC?')
    

    
    def setAveragingState(self,state):
        assert isinstance(state,bool)
        currentState=self.getAveragingState()
        if state != currentState :
            state = int(state)
            self.dev.write(f"LINS1:SENS{self.SLOT}:AVER:STAT {state}")
            self.dev.write('*OPC?')
    
    def getAveragingState(self):
        ans = self.dev.write(f"LINS1:SENS{self.SLOT}:AVER:STAT?")
        return bool(int(ans))



    
    
    def getBufferSize(self):
        ans = self.dev.write(f"LINS1:SENS{self.SLOT}:AVER:COUN?")
        return int(ans)
    
    def setBufferSize(self, value):
        assert isinstance(int(value),int)
        value=int(value)
        currentSize=self.getBufferSize()
        if currentSize != value :
            self.dev.write(f"LINS1:SENS{self.SLOT}:AVER:COUN {value}")
            self.dev.write('*OPC?')


 
       

    
    def getPower(self):
        ans = self.dev.write(f"LINS1:READ{self.SLOT}:SCAL:POW:DC?")
        return float(ans)
    

    
        
    def setWavelength(self,wavelength):
        assert isinstance(float(wavelength),float)
        wavelength=float(wavelength)
        currentWavelength=self.getWavelength()
        if wavelength != currentWavelength :
            self.dev.write(f"LINS1:SENS{self.SLOT}:POW:WAV {wavelength} nm")
            self.dev.write('*OPC?')

    
    def getWavelength(self):
        ans = self.dev.write(f"LINS1:SENS{self.SLOT}:POW:WAV?")
        return float(ans)
    
    
    def getDriverConfig(self):
        config = []
        config.append({'element':'variable','name':'averaging','type':bool,'read':self.getAveragingState,'write':self.setAveragingState,'help':'Average or not the measure'})
        config.append({'element':'variable','name':'bufferSize','type':int,'read':self.getBufferSize,'write':self.setBufferSize,'help':'Buffer size for the average'})
        config.append({'element':'variable','name':'wavelength','type':float,'unit':'nm','read':self.getWavelength,'write':self.setWavelength,'help':'Wavelength of the measure'})
        config.append({'element':'variable','name':'power','type':float,'unit':'W','read':self.getPower,'help':'Current power'})
        config.append({'element':'action','name':'safestate','do':self.setSafeState,'help':'Set the shutter'})
        return config
        
    
