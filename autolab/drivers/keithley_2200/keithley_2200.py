#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""



class Driver():
    
    def __init__(self):
        self.write('*CLS')
        
        
    def get_current(self):
        return float(self.query(f'MEASure:CURRent?'))
    def get_current_compliance(self):
        return float(self.query(f'CURRent?'))
    def set_current_compliance(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.write(f'CURRent {value}')
        self.query('*OPC?')

    def get_voltage(self):
        return float(self.query(f'MEASure:VOLTage?'))
    def get_voltage_compliance(self):
        return float(self.query(f'VOLTage?'))    
    def set_voltage_compliance(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        self.write(f'VOLTage {value}')
        self.query('*OPC?')

    def get_output_state(self):
        ans = self.query(f"OUTPut?")
        return bool(int(float(ans)))
    def set_output_state(self,state):
        assert isinstance(state,bool)
        if state is True:
            self.write(f"OUTPut ON")
        else:
            self.write(f"OUTPut OFF") 
        self.query('*OPC?')
    
    def get_id(self):
        return self.query('*IDN?')
    
    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'current','unit':'A','read':self.get_current,'type':float,'help':'Current at the output as measured (read only)'})
        model.append({'element':'variable','name':'current_compliance','unit':'A','read':self.get_current_compliance,'write':self.set_current_compliance,'type':float,'help':'Current compliance'})
        model.append({'element':'variable','name':'voltage','unit':'V','read':self.get_voltage,'type':float,'help':'Voltage at the output as measured (read only)'})
        model.append({'element':'variable','name':'voltage_compliance','unit':'V','read':self.get_voltage_compliance,'write':self.set_voltage_compliance,'type':float,'help':'Voltage compliance'})
        model.append({'element':'variable','name':'output','read':self.get_output_state,'write':self.set_output_state,'type':bool,'help':'Output state (on/off), passed as boolean to the function: True/False'})
        return model
        
        
#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::22::INSTR',**kwargs):
        import visa

        self.TIMEOUT = 5000 #ms
        # Instantiation
        rm = visa.ResourceManager()
        self.controller = rm.get_instrument(address)
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
    def read(self):
        result = self.controller.read()
        return result.strip('\n')
    

class Driver_GPIB(Driver):
    def __init__(self,address=2,board_index=0,**kwargs):
        import Gpib
        
        self.inst = Gpib.Gpib(int(board_index),int(address))
        Driver.__init__(self, **kwargs)
    
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,command):
        self.inst.write(command)
    def read(self,length=1000000000):
        return self.inst.read(length).decode().strip('\r\n')
    def close(self):
        """WARNING: GPIB closing is automatic at sys.exit() doing it twice results in a gpib error"""
        #Gpib.gpib.close(self.inst.id)
        pass
############################## Connections classes ##############################
#################################################################################

        
