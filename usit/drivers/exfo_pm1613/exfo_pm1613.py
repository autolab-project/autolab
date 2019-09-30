#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- Exfo pm1613 
"""
import time




class Device():
    
    def __init__(self):
        
        # Initialisation
        self.write('*CLS')
        self.write('SENS:POW:RANG:AUTO 1')      # Ajuster la gamme de mesure automatiquement
        self.write('SENS:POW:REF:STAT 0')       # Set Absolute power measurment mode (dBm or W)
        self.write('SENS:POW W')                # Unité = Watts
        self.write('SENS:POW:UNIT W')
        
        
    def getID(self):
        return self.query('*IDN?')
    
    def setAveragingState(self,state):
        assert isinstance(state,bool)
        currentState=self.getAveragingState()
        if state != currentState :
            self.write('SENS:AVER:STAT %i'%int(state))
            self.query('*OPC?')
    
    def getAveragingState(self):
        return bool(self.query('SENS:AVER:STAT?'))
        
    def setZero(self):
        self.write('SENS:CORR:COLL:ZERO')
        self.query('*OPC?')
    
    def getBufferSize(self):
        return int(self.query('SENS:AVER:COUN?'))
    
    def setBufferSize(self, value):
        assert isinstance(int(value),int)
        value=int(value)
        currentSize=self.getBufferSize()
        if currentSize != value :
            self.write('SENS:AVER:COUN %i'%value)
            self.query('*OPC?')
        
    def getPower(self):
        while True :
            result=self.query('READ:ALL:POW:DC?')
            if isinstance(result,str) and '!' in result :
                time.sleep(0.1)
            else :
                break
        return float(result)

    def setWavelength(self,wavelength):
        assert isinstance(float(wavelength),float)
        wavelength=float(wavelength)
        currentWavelength=self.getWavelength()
        if wavelength != currentWavelength :
            self.write('SENS:POW:WAVE %f'%wavelength)
            self.query('*OPC?')
    
    def getWavelength(self):
        return float(self.query('SENS:POW:WAVE?'))
    
    
    def getDriverConfig(self):
        
        config = []
        config.append({'element':'variable','name':'averagingState','write':self.setAveragingState,'read':self.getAveragingState,'type':bool,'help':'This command activates or deactivates data averaging.'})
        config.append({'element':'variable','name':'bufferSize','write':self.setBufferSize,'read':self.getBufferSize,'type':int,'help':'This command sets the number of power measurements that will be used to compute data averaging.'})
        config.append({'element':'variable','name':'wavelength','write':self.setWavelength,'read':self.getWavelength,'type':float,'help':'The <numeric_value> parameter is an operating wavelength in nm. Any wavelength within the spectral range of the power meter optical detector at 0.01 nm resolution may be selected.'})
        config.append({'element':'variable','name':'power','read':self.getPower,'type':str,'help':'This command returns the power of both channels in their respective current unit.'})
        config.append({'element':'action','name':'zero','do':self.setZero, 'help':'This command performs an offset nulling measurement.'})       
        return config


#################################################################################
############################## Connections classes ##############################
class Device_VISA(Device):
    def __init__(self, address=None):
        import visa
        
        self.TIMEOUT = 10000 #ms
        
        # Instantiation
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.timeout = self.TIMEOUT
        Device.__init__(self)        

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
        
        
############################## Connections classes ##############################
#################################################################################
        
        
if __name__ == '__main__' :
    ADDRESS = 'GPIB0::12::INSTR'
