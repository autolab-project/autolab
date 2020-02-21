#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- Exfo pm1613 
"""
import time

class Driver():
    
    def __init__(self):
        
        # Initialisation
        self.write('*CLS')
        self.write('SENS:POW:RANG:AUTO 1')      # Ajuster la gamme de mesure automatiquement
        self.write('SENS:POW:REF:STAT 0')       # Set Absolute power measurment mode (dBm or W)
        self.write('SENS:POW W')                # Unité = Watts
        self.write('SENS:POW:UNIT W')
        
        
    def get_id(self):
        return self.query('*IDN?')
    
    def set_averaging_state(self,state):
        assert isinstance(state,bool)
        currentState=self.get_averaging_state()
        if state != currentState :
            self.write('SENS:AVER:STAT %i'%int(state))
            self.query('*OPC?')
    
    def get_averaging_state(self):
        return bool(self.query('SENS:AVER:STAT?'))
        
    def zero(self):
        self.write('SENS:CORR:COLL:ZERO')
        self.query('*OPC?')
    
    def get_buffer_size(self):
        return int(self.query('SENS:AVER:COUN?'))
    
    def set_buffer_size(self, value):
        assert isinstance(int(value),int)
        value=int(value)
        current_size=self.get_buffer_size()
        if current_size != value :
            self.write('SENS:AVER:COUN %i'%value)
            self.query('*OPC?')
        
    def get_power(self):
        while True :
            result=self.query('READ:ALL:POW:DC?')
            if isinstance(result,str) and '*' in result :
                time.sleep(0.1)
            else :
                break
        return float(result)

    def set_wavelength(self,wavelength):
        assert isinstance(float(wavelength),float)
        wavelength=float(wavelength)
        current_wavelength=self.get_wavelength()
        if wavelength != current_wavelength :
            self.write('SENS:POW:WAVE %f'%wavelength)
            self.query('*OPC?')
    
    def get_wavelength(self):
        return float(self.query('SENS:POW:WAVE?'))
    
    
    def get_driver_model(self):
        
        model = []
        model.append({'element':'variable','name':'averaging','write':self.set_averaging_state,'read':self.get_averaging_state,'type':bool,'help':'This command activates or deactivates data averaging.'})
        model.append({'element':'variable','name':'buffer_size','write':self.set_buffer_size,'read':self.get_buffer_size,'type':int,'help':'This command sets the number of power measurements that will be used to compute data averaging.'})
        model.append({'element':'variable','name':'wavelength','write':self.set_wavelength,'read':self.get_wavelength,'type':float,'help':'The <numeric_value> parameter is an operating wavelength in nm. Any wavelength within the spectral range of the power meter optical detector at 0.01 nm resolution may be selected.'})
        model.append({'element':'variable','name':'power','read':self.get_power,'type':float,'help':'This command returns the power of both channels in their respective current unit.'})
        model.append({'element':'action','name':'zero','do':self.zero, 'help':'This command performs an offset nulling measurement.'})       
        return model


#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::2::INSTR',**kwargs):
        import visa
        
        self.TIMEOUT = 10000 #ms
        
        # Instantiation
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.timeout = self.TIMEOUT
        Driver.__init__(self)        

    def close(self):
        try : self.controller.close()
        except : pass

    def query(self,command):
        return self.controller.query(command).strip('\n')
    
    def write(self,command):
        self.controller.write(command)
        
        
############################## Connections classes ##############################
#################################################################################
        
        
