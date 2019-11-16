#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 20:06:08 2019

@author: quentin.chateiller
"""

import time


class Driver():

    def __init__(self):
    
        # Initialisation
        self.write('*CLS')      # Clear status registers
        self.write('DELAY 0')   # User commands not delayed
        
        # Subdevices
        self.tec = TEC(self)
        self.las = LAS(self)
        
        
    def get_id(self):
        return self.query('*IDN?')
    
    
    def get_driver_model(self):
        model = []
        model.append({'element':'module','name':'tec','object':self.tec})
        model.append({'element':'module','name':'las','object':self.las})
        return model
    
    
#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::2::INSTR',**kwargs):
        import visa
        
        self.TIMEOUT = 15000 #ms
        
        # Instantiation
        rm = visa.ResourceManager()
        self.controller = rm.get_instrument(address)
        self.controller.timeout = self.TIMEOUT
        self.controller.read_termination='\n'
        self.controller.write_termination='\n'
        self.controller.baud_rate = 19200
        #self.controller.query_delay = 0.05
        
        Driver.__init__(self)

    def close(self):
        try : self.controller.close()
        except : pass

    def query(self,command):
        return self.controller.query(command)
    
    def write(self,command):
        self.controller.write(command)
        time.sleep(0.01)
        
class Driver_GPIB(Driver):
    def __init__(self,address=2,board_index=0,**kwargs):
        import Gpib
        
        self.inst = Gpib.Gpib(int(board_index),int(address))
        Driver.__init__(self)
    
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,query):
        self.inst.write(query)
    def read(self,length=1000000000):
        return self.inst.read().decode().strip('\r\n')
    def close(self):
        """WARNING: GPIB closing is automatic at sys.exit() doing it twice results in a gpib error"""
        #Gpib.gpib.close(self.inst.id)
        pass
############################## Connections classes ##############################
#################################################################################


class LAS():
    
    category = 'Electrical source'
    
    def __init__(self,dev):
        
        self.dev = dev
        self.PRECISION = 0.1

    def write(self,command):
        self.dev.write(command)
        
    def query(self,command):
        return self.dev.query(command)
    
    
    def get_current(self):
        return float(self.query('LAS:LDI?'))

    def get_current_setpoint(self):
        return float(self.query('LAS:SET:LDI?'))
        
    def set_current(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.write(f'LAS:LDI {value}')
        #self.query('*OPC?')
        if value > 0 :
            if self.is_enabled() is False :
                self.set_enabled(True)
            self.set_mode('ILBW')
            self.wait_for_convergence(self.get_current,value)
        elif value == 0 :
            if self.is_enabled() is True :
                self.set_enabled(False)




    def set_power(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.write(f'LAS:MDP {value}')
        #self.query('*OPC?')
        if value > 0 :
            if self.is_enabled() is False :
                self.set_enabled(True)
            self.set_mode('MDP')
            self.wait_for_convergence(self.get_power,value)
        elif value == 0 :
            if self.is_enabled() is True :
                self.set_enabled(False)

    def get_power(self):
        #self.query('*OPC?')
        return float(self.query('LAS:MDP?'))

    def get_power_setpoint(self):
        return float(self.query('LAS:SET:MDP?'))
    
    
    
    
    def set_enabled(self,value):
        assert isinstance(value,bool)
        self.write(f'LAS:OUT {int(value)}')
        #self.query('*OPC?')
        if value is True :
            mode = self.query('LAS:MODE?')
            if mode.startswith('I'):
                self.wait_for_convergence(self.get_current,
                                        self.get_current_setpoint())
            elif mode.startswith('MD'):
                self.wait_for_convergence(self.get_power,
                                        self.get_power_setpoint())
        
    def is_enabled(self):
        return bool(int(self.query('LAS:OUT?')))

    
    
    
    def wait_for_convergence(self,func,setpoint):
        tini = time.time()
        while True :
            try : 
                if abs(func()-setpoint) < self.PRECISION*setpoint :
                    break
                else :
                    time.sleep(0.5)
            except :
                pass
            if time.time() - tini > 5 :
                break
            
            
            
            
    def set_mode(self,mode):
        assert isinstance(mode,str)
        curr_mode = self.get_mode()
        enabled_mode = self.is_enabled()
        if curr_mode != mode :
            self.write(f'LAS:MODE:{mode}')
            #self.query('*OPC?')
            self.set_enabled(enabled_mode)
            
    def get_mode(self):
        return self.query('LAS:MODE?')
        
        
    
    
    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'current_setpoint','type':float,'unit':'mA','read':self.get_current_setpoint,'help':'Current setpoint'})
        model.append({'element':'variable','name':'current','type':float,'unit':'mA','read':self.get_current,'write':self.set_current,'help':'Current'})
        model.append({'element':'variable','name':'power_setpoint','type':float,'unit':'mW','read':self.get_power_setpoint,'help':'Output power setpoint'})
        model.append({'element':'variable','name':'power','type':float,'unit':'mW','write':self.set_power,'read':self.get_power,'help':'Output power'})
        model.append({'element':'variable','name':'output','type':bool,'read':self.is_enabled,'write':self.set_enabled,'help':'Output state'})
        model.append({'element':'variable','name':'mode','type':str,'read':self.get_mode,'write':self.set_mode,'help':'Control mode'})
        return model
    
    



class TEC():
    
    category = 'Temperature controller'
    
    def __init__(self,dev):
        
        self.dev = dev
        self.PRECISION = 0.05



    def write(self,command):
        self.dev.write(command)
        
    def query(self,command):
        return self.dev.query(command)
    
    
    

    def get_resistance(self):
        return float(self.query('TEC:R?'))



    def set_gain(self,value):
        assert isinstance(int(value),int)
        value = int(value)
        self.write(f'TEC:GAIN {value}')
        #self.query('*OPC?')
        
    def get_gain(self):
        return int(float(self.query('TEC:GAIN?')))
   
    

    
    def get_current(self):
        return float(self.query('TEC:ITE?'))

    def get_current_setpoint(self):
        return float(self.query('TEC:SET:ITE?'))
        
    def set_current(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.write(f'TEC:ITE {value}')
        #self.query('*OPC?')
        if value > 0 :
            if self.is_enabled() is False :
                self.set_enabled(True)
            self.set_mode('ITE')
            self.wait_for_convergence(self.get_current,value)
        elif value == 0 :
            if self.is_enabled() is True :
                self.set_enabled(False)




    def set_temperature(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.write(f'TEC:T {value}')
        #self.query('*OPC?')
        if value > 0 :
            if self.is_enabled() is False :
                self.set_enabled(True)
            self.set_mode('T')
            self.wait_for_convergence(self.get_temperature,value)
        elif value == 0 :
            if self.is_enabled() is True :
                self.set_enabled(False)

    def get_temperature(self):
        return float(self.query('TEC:T?'))

    def get_temperature_setpoint(self):
        return float(self.query('TEC:SET:T?'))
    
    

    
    
    def set_enabled(self,value):
        assert isinstance(value,bool)
        self.write(f'TEC:OUT {int(value)}')
        #self.query('*OPC?')
        if value is True :
            mode = self.query('TEC:MODE?')
            if mode.startswith('I'):
                self.wait_for_convergence(self.get_current,
                                        self.get_current_setpoint())
            elif mode.startswith('T'):
                self.wait_for_convergence(self.get_temperature,
                                        self.get_temperature_setpoint())
        
    def is_enabled(self):
        return bool(int(self.query('TEC:OUT?')))
    
    
    
    
    
    def wait_for_convergence(self,func,setpoint):
        tini = time.time()
        while True :
            try : 
                if abs(func()-setpoint) < self.PRECISION*setpoint :
                    break
                else :
                    time.sleep(0.5)
            except :
                pass
            if time.time() - tini > 5 :
                break
            
            
            
            
    def set_mode(self,mode):
        assert isinstance(mode,str)
        curr_mode = self.get_mode()
        enabled_mode = self.is_enabled()
        if curr_mode != mode :
            self.write(f'TEC:MODE:{mode}')
            #self.query('*OPC?')
            self.set_enabled(enabled_mode)
            
    def get_mode(self):
        return self.query('TEC:MODE?')
    
    
    
    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'resistance','type':float,'read':self.get_resistance,'help':'Resistance'})
        model.append({'element':'variable','name':'gain','type':int,'read':self.get_gain,'write':self.set_gain,'help':'Gain'})
        model.append({'element':'variable','name':'current_setpoint','type':float,'unit':'mA','read':self.get_current_setpoint,'help':'Current setpoint'})
        model.append({'element':'variable','name':'current','type':float,'unit':'mA','read':self.get_current,'write':self.set_current,'help':'Current'})
        model.append({'element':'variable','name':'temperature_setpoint','type':float,'unit':'°C','read':self.get_temperature_setpoint,'help':'Temperature setpoint'})
        model.append({'element':'variable','name':'temperature','type':float,'unit':'°C','read':self.get_temperature,'write':self.set_temperature,'help':'Actual temperature'})
        model.append({'element':'variable','name':'output','type':bool,'read':self.is_enabled,'write':self.set_enabled,'help':'Output state'})
        model.append({'element':'variable','name':'mode','type':str,'read':self.get_mode,'write':self.set_mode,'help':'Control mode'})
        return model
    
    

        
