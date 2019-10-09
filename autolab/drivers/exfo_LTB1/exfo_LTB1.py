#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver():
    
    category = 'Optical frame'
    slotNaming = 'slot<NUM> = <MODULE_NAME>,<SLOT_NAME>'
    
    def __init__(self,**kwargs):
        
        # Submodules
        self.slotnames = []
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix):
                slot_num = key[len(prefix):]
                module = globals()[ 'Module_'+kwargs[key].split(',')[0].strip() ]
                name = kwargs[key].split(',')[1].strip()
                setattr(self,name,module(self,slot_num))
                self.slotnames.append(name)       
        
    def getID(self):
        return self.write('*IDN?')
    
    
    def getDriverConfig(self):
        config = []
        for name in self.slotnames :
            config.append({'element':'module','name':name,'object':getattr(self,name)})
        return config
    
#################################################################################
############################## Connections classes ##############################
class Driver_TELNET(Driver):
    
    def __init__(self, address='192.168.0.9', **kwargs):
        from telnetlib import Telnet
        
        self.TIMEOUT = 1
        
        
        # Instantiation
        self.controller = Telnet(address,5024)
        self.read()
        self.read()
        
        Driver.__init__(self, **kwargs)
        
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
    
############################## Connections classes ##############################
#################################################################################    
    
    
    
class Module_FTB1750():
    
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
        wavelength=float(wavelength)*1e-9
        currentWavelength=self.getWavelength()
        if wavelength != currentWavelength :
            self.dev.write(f"LINS1:SENS{self.SLOT}:POW:WAV {wavelength} nm")
            self.dev.write('*OPC?')

    
    def getWavelength(self):
        ans = self.dev.write(f"LINS1:SENS{self.SLOT}:POW:WAV?")
        return float(ans)*1e9
    
    
    def getDriverConfig(self):
        config = []
        config.append({'element':'variable','name':'averaging','type':bool,'read':self.getAveragingState,'write':self.setAveragingState,'help':'Average or not the measure'})
        config.append({'element':'variable','name':'bufferSize','type':int,'read':self.getBufferSize,'write':self.setBufferSize,'help':'Buffer size for the average'})
        config.append({'element':'variable','name':'wavelength','type':float,'unit':'nm','read':self.getWavelength,'write':self.setWavelength,'help':'Wavelength of the measure'})
        config.append({'element':'variable','name':'power','type':float,'unit':'W','read':self.getPower,'help':'Current power'})
        return config
        
    

if __name__ == '__main__' :
    ADDRESS = '192.168.0.1'
    PORT = 5024


