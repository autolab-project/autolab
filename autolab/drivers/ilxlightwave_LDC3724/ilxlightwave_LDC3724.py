#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 20:06:08 2019

@author: quentin.chateiller
"""

import time


class Driver():
    
    category = 'Optical source'
    
    def __init__(self):
    
        # Initialisation
        self.write('*CLS')      # Clear status registers
        self.write('DELAY 0')   # User commands not delayed
        
        # Subdevices
        self.tec = TEC(self)
        self.las = LAS(self)
        
        
    def getID(self):
        return self.query('*IDN?')
    
    
    def getDriverConfig(self):
        config = []
        config.append({'element':'module','name':'tec','object':self.tec})
        config.append({'element':'module','name':'las','object':self.las})
        return config
    
    
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
        result = self.controller.query(command)
        if '=' in result : result = result.split('=')[1]
        try : result = float(result)
        except: pass
        return result
    
    def write(self,command):
        self.controller.write(command)
        time.sleep(0.01)
        
class Driver_GPIB(Driver):
    def __init__(self,address=2,board_index=0,**kwargs):
        import Gpib
        
        self.inst = Gpib.Gpib(int(address),int(board_index))
        Driver.__init__(self)
    
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,query):
        self.inst.write(query)
    def read(self):
        return self.inst.read()
    def close(self):
        """WARNING: GPIB closing is automatic at sys.exit() doing it twice results in a gpib error"""
        Gpib.gpib.close(self.inst.id) 
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
        
        
    
    
    def getDriverConfig(self):
        config = []
        config.append({'element':'variable','name':'currentSetpoint','type':float,'unit':'mA','read':self.getCurrentSetpoint,'help':'Current setpoint'})
        config.append({'element':'variable','name':'current','type':float,'unit':'mA','read':self.getCurrent,'write':self.setCurrent,'help':'Current'})
        config.append({'element':'variable','name':'powerSetpoint','type':float,'unit':'mW','read':self.getPowerSetpoint,'help':'Output power setpoint'})
        config.append({'element':'variable','name':'power','type':float,'unit':'mW','write':self.setPower,'read':self.getPower,'help':'Output power'})
        config.append({'element':'variable','name':'output','type':bool,'read':self.isEnabled,'write':self.setEnabled,'help':'Output state'})
        config.append({'element':'variable','name':'mode','type':str,'read':self.getMode,'write':self.setMode,'help':'Control mode'})
        return config
    
    



class TEC():
    
    category = 'Temperature controller'
    
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
    
    
    
    def getDriverConfig(self):
        config = []
        config.append({'element':'variable','name':'resistance','type':float,'read':self.getResistance,'help':'Resistance'})
        config.append({'element':'variable','name':'gain','type':int,'read':self.getGain,'write':self.setGain,'help':'Gain'})
        config.append({'element':'variable','name':'currentSetpoint','type':float,'unit':'mA','read':self.getCurrentSetpoint,'help':'Current setpoint'})
        config.append({'element':'variable','name':'current','type':float,'unit':'mA','read':self.getCurrent,'write':self.setCurrent,'help':'Current'})
        config.append({'element':'variable','name':'temperatureSetpoint','type':float,'unit':'°C','read':self.getTemperatureSetpoint,'help':'Temperature setpoint'})
        config.append({'element':'variable','name':'temperature','type':float,'unit':'°C','read':self.getTemperature,'write':self.setTemperature,'help':'Actual temperature'})
        config.append({'element':'variable','name':'output','type':bool,'read':self.isEnabled,'write':self.setEnabled,'help':'Output state'})
        config.append({'element':'variable','name':'mode','type':str,'read':self.getMode,'write':self.setMode,'help':'Control mode'})
        return config
    
    

        
