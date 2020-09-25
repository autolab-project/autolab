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
        self.channelA = Channel(self,'a')
        self.channelB = Channel(self,'b')
    
    def safe_state(self):
        self.channelA.safe_state()
        self.channelB.safe_state()
    
    def get_id(self):
        return self.query('*IDN?')
        
    def get_driver_model(self):
        model = []
        model.append({'element':'module','name':'channelA','object':self.channelA})
        model.append({'element':'module','name':'channelB','object':self.channelB})
        return model
 

#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::26::INSTR',**kwargs):
        import visa

        self.TIMEOUT = 5000 #ms
        
        # Instantiation
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.timeout = self.TIMEOUT
        
        Driver.__init__(self)
    
        
   
    def close(self):
        try : self.controller.close()
        except : pass

    def query(self,command):
        result = self.controller.query(command)
        result = result.strip('\n')
        return result
    
    def write(self,command):
        self.controller.write(command)
        
        
############################## Connections classes ##############################
#################################################################################



class Channel():
    
    def __init__(self,dev,slot):
        
        self.dev = dev
        self.SLOT = slot.lower()
        
        # Initialisation
        self.dev.write(f"smu{self.SLOT}.source.autorangev = smu{self.SLOT}.AUTORANGE_ON")
        self.dev.write(f"smu{self.SLOT}.source.autorangei = smu{self.SLOT}.AUTORANGE_ON")
        self.dev.query('*OPC?')
    
    def safe_state(self):
        self.set_voltage(0)
        
        
        
    #--------------------------------------------------------------------------
    # Instrument variables
    #--------------------------------------------------------------------------
        


    def get_resistance(self):
        self.dev.write(f'display.smu{self.SLOT}.measure.func = display.MEASURE_OHMS')
        self.dev.query('*OPC?')
        return float(self.dev.query(f"print(smu{self.SLOT}.measure.r())"))
    
    
    
    
    def get_power(self):
        self.dev.write(f'display.smu{self.SLOT}.measure.func = display.MEASURE_WATTS')
        self.dev.query('*OPC?')
        return float(self.dev.query(f"print(smu{self.SLOT}.measure.p())"))




    def set_power_compliance(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.dev.write(f"smu{self.SLOT}.source.limitp = {value}")
        self.dev.query('*OPC?')
        
    def get_power_compliance(self):
        return float(self.dev.query(f"print(smu{self.SLOT}.source.limitp)"))




    
    def get_current(self):
        self.dev.write(f'display.smu{self.SLOT}.measure.func = display.MEASURE_DCAMPS')
        return float(self.dev.query(f"print(smu{self.SLOT}.measure.i())"))
    
    def set_current(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.dev.write(f"smu{self.SLOT}.source.func = smu{self.SLOT}.OUTPUT_DCAMPS")
        self.dev.write(f"smu{self.SLOT}.source.leveli = {value}")
        self.dev.query('*OPC?')
#        if value != 0. and self.get_output_state() is False :
#            self.set_output_state(True)
#        if value == 0. and self.get_output_state() is True :
#            self.set_output_state(False)
            
            
            
            
            
    def set_current_compliance(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.dev.write(f"smu{self.SLOT}.source.limiti = {value}")
        self.dev.query('*OPC?')
        
    def get_current_compliance(self):
        return float(self.dev.query(f"print(smu{self.SLOT}.source.limiti)"))





    
    def get_voltage(self):
        self.dev.write(f'display.smu{self.SLOT}.measure.func = display.MEASURE_DCVOLTS')
        self.dev.query('*OPC?')
        return float(self.dev.query(f"print(smu{self.SLOT}.measure.v())"))
    
    def set_voltage(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.dev.write(f"smu{self.SLOT}.source.func = smu{self.SLOT}.OUTPUT_DCVOLTS")
        self.dev.write(f"smu{self.SLOT}.source.levelv = {value}")
        self.dev.query('*OPC?')
#        if value != 0. and self.get_output_state() is False :
#            self.set_output_state(True)
#        if value == 0. and self.get_output_state() is True :
#            self.set_output_state(False)
            
            
            
    def set_voltage_compliance(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.dev.write(f"smu{self.SLOT}.source.limitv = {value}")
        self.dev.query('*OPC?')
        
    def get_voltage_compliance(self):
        return float(self.dev.query(f"print(smu{self.SLOT}.source.limitv)"))





        
    def get_output_state(self):
        ans = self.dev.query(f"print(smu{self.SLOT}.source.output)")
        return bool(int(float(ans)))
                
    def set_output_state(self,state):
        assert isinstance(state,bool)
        if state is True :
            self.dev.write(f"smu{self.SLOT}.source.output = smu{self.SLOT}.OUTPUT_ON")
        else :
            self.dev.write(f"smu{self.SLOT}.source.output = smu{self.SLOT}.OUTPUT_OFF") 
        self.dev.query('*OPC?')
        
    
            

    
    def set_4wire_mode_state(self,state):
        assert isinstance(state,bool)
        if state is True :
            self.dev.write(f'smu{self.SLOT}.sense = smu{self.SLOT}.SENSE_REMOTE')
        else :
            self.dev.write(f'smu{self.SLOT}.sense = smu{self.SLOT}.SENSE_LOCAL')  
        self.dev.query('*OPC?')

    def get_4wire_mode_state(self):
        result=int(float(self.dev.query(f"print(smu{self.SLOT}.sense)")))
        if result == 0 :
            return False
        else :
            return True
        
        
    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'resistance','unit':'ohm','read':self.get_resistance,'type':float,'help':'Resistance'})
        model.append({'element':'variable','name':'power','unit':'W','read':self.get_power,'type':float,'help':'Power'})
        model.append({'element':'variable','name':'power_compliance','unit':'W','read':self.get_power_compliance,'write':self.set_power_compliance,'type':float,'help':'Power compliance'})
        model.append({'element':'variable','name':'current','unit':'A','read':self.get_current,'write':self.set_current,'type':float,'help':'Current'})
        model.append({'element':'variable','name':'current_compliance','unit':'A','read':self.get_current_compliance,'write':self.set_current_compliance,'type':float,'help':'Current compliance'})
        model.append({'element':'variable','name':'voltage','unit':'V','read':self.get_voltage,'write':self.set_voltage,'type':float,'help':'Voltage'})
        model.append({'element':'variable','name':'voltage_compliance','unit':'V','read':self.get_voltage_compliance,'write':self.set_voltage_compliance,'type':float,'help':'Voltage compliance'})
        model.append({'element':'variable','name':'output','read':self.get_output_state,'write':self.set_output_state,'type':bool,'help':'Output'})
        model.append({'element':'variable','name':'4wire_mode','read':self.get_4wire_mode_state,'write':self.set_4wire_mode_state,'type':bool,'help':'4 wire mode'})
        return model
        
