#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""



class Driver():
    
    def __init__(self):
        
        # Initialisation
        self.write('*CLS')
        
        # Subdevices
        self.source1 = Line(self,1)
        self.source2 = Line(self,2)
    
    def setSafeState(self):
        self.source1.setSafeState()
        self.source2.setSafeState()
    
    def getID(self):
        return self.query('*IDN?')
        
    def getDriverConfig(self):
        config = []
        config.append({'element':'module','name':'source1','object':self.source1})
        config.append({'element':'module','name':'source2','object':self.source2})
        return config
 

#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::2::INSTR',**kwargs):
        import visa

        self.TIMEOUT = 1000 #ms
        
        # Instantiation
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(self.address)
        self.controller.timeout = self.TIMEOUT
        
        Driver.__init__(self)
    
        
   
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



class Line():
    
    def __init__(self,dev,slot):
        
        self.dev = dev
        self.SLOT = slot
        
        # Initialisation
        self.dev.write(f"smu{self.SLOT}.source.autorangev = smu{self.SLOT}.AUTORANGE_ON")
        self.dev.write(f"smu{self.SLOT}.source.autorangei = smu{self.SLOT}.AUTORANGE_ON")
        self.dev.query('*OPC?')
    
    def setSafeState(self):
        self.setVoltage(0)
        if self.setOutputState() is True :
            return False
        
        
        
    #--------------------------------------------------------------------------
    # Instrument variables
    #--------------------------------------------------------------------------
        


    def getResistance(self):
        self.dev.write(f'display.smu{self.SLOT}.measure.func = display.MEASURE_OHMS')
        self.dev.query('*OPC?')
        return float(self.dev.query(f"print(smu{self.SLOT}.measure.r())"))
    
    
    
    
    def getPower(self):
        self.dev.write(f'display.smu{self.SLOT}.measure.func = display.MEASURE_WHATTS')
        self.dev.query('*OPC?')
        return float(self.dev.query(f"print(smu{self.SLOT}.measure.p())"))




    def setPowerCompliance(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.dev.write("smu{self.SLOT}.source.limitp = {value}")
        self.dev.query('*OPC?')
        
    def getPowerCompliance(self):
        return float(self.dev.query(f"print(smu{self.SLOT}.source.limitp)"))




    
    def getCurrent(self):
        self.dev.write(f'display.smu{self.SLOT}.measure.func = display.MEASURE_DCAMPS')
        return float(self.dev.query(f"print(smu{self.SLOT}.measure.i())"))
    
    def setCurrent(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.dev.write(f"smu{self.SLOT}.source.func = smu{self.SLOT}.OUTPUT_DCAMPS")
        self.dev.write(f"smu{self.SLOT}.source.leveli = {value}")
        self.dev.query('*OPC?')
#        if value != 0. and self.getOutputState() is False :
#            self.setOutputState(True)
#        if value == 0. and self.getOutputState() is True :
#            self.setOutputState(False)
            
            
            
            
            
    def setCurrentCompliance(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.dev.write("smu{self.SLOT}.source.limiti = {value}")
        self.dev.query('*OPC?')
        
    def getCurrentCompliance(self):
        return float(self.dev.query("print(smu{self.SLOT}.source.limiti)"))





    
    def getVoltage(self):
        self.dev.write(f'display.smu{self.SLOT}.measure.func = display.MEASURE_DCVOLTS')
        self.dev.query('*OPC?')
        return float(self.dev.query(f"print(smu{self.SLOT}.measure.v())"))
    
    def setVoltage(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.dev.write(f"smu{self.SLOT}.source.func = smu{self.SLOT}.OUTPUT_DCVOLTS")
        self.dev.write(f"smu{self.SLOT}.source.levelv = {value}")
        self.dev.query('*OPC?')
#        if value != 0. and self.getOutputState() is False :
#            self.setOutputState(True)
#        if value == 0. and self.getOutputState() is True :
#            self.setOutputState(False)
            
            
            
    def setVoltageCompliance(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.dev.write("smu{self.SLOT}.source.limitv = {value}")
        self.dev.query('*OPC?')
        
    def getVoltageCompliance(self):
        return float(self.dev.query("print(smu{self.SLOT}.source.limitv)"))





        
    def getOutputState(self):
        ans = self.dev.query(f"print(smu{self.SLOT}.source.output)")
        return bool(int(float(ans)))
                
    def setOutputState(self,state):
        assert isinstance(state,bool)
        if state is True :
            self.dev.write(f"smu{self.SLOT}.source.output = smu{self.SLOT}.OUTPUT_ON")
        else :
            self.dev.write(f"smu{self.SLOT}.source.output = smu{self.SLOT}.OUTPUT_OFF") 
        self.dev.query('*OPC?')
        
    
            

    
    def set4wireModeState(self,state):
        assert isinstance(state,bool)
        if state is True :
            self.dev.write(f'smu{self.SLOT}.sense = smu{self.SLOT}.SENSE_REMOTE')
        else :
            self.dev.write(f'smu{self.SLOT}.sense = smu{self.SLOT}.SENSE_LOCAL')  
        self.dev.query('*OPC?')

    def get4wireModeState(self):
        result=int(float(self.dev.query(f"print(smu{self.SLOT}.sense)")))
        if result == 0 :
            return False
        else :
            return True
        
        
    def getDriverConfig(self):
        config = []
        config.append({'element':'variable','name':'resistance','read':self.getResistance,'type':float,'help':'Resistance'})
        config.append({'element':'variable','name':'power','read':self.getPower,'type':float,'help':'Power'})
        config.append({'element':'variable','name':'powerCompliance','read':self.getPowerCompliance,'write':self.setPowerCompliance,'type':float,'help':'Power compliance'})
        config.append({'element':'variable','name':'current','read':self.getCurrent,'type':float,'help':'Current'})
        config.append({'element':'variable','name':'currentCompliance','read':self.getCurrentCompliance,'write':self.setCurrentCompliance,'type':float,'help':'Current compliance'})
        config.append({'element':'variable','name':'voltage','read':self.getVoltage,'type':float,'help':'Voltage'})
        config.append({'element':'variable','name':'voltageCompliance','read':self.getVoltageCompliance,'write':self.setVoltageCompliance,'type':float,'help':'Voltage compliance'})
        config.append({'element':'variable','name':'output','read':self.getOutputState,'write':self.setOutputState,'type':bool,'help':'Output'})
        config.append({'element':'variable','name':'4wireMode','read':self.get4wireModeState,'write':self.set4wireModeState,'type':bool,'help':'4 wire mode'})
        return config
        
        
#ADDRESS = 'GPIB0::10::INSTR'
