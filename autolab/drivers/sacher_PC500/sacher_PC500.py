#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

class Driver():
    
    def __init__(self):
        pass
    def set_current_setpoint(self,current):
        self.write(f'L:CURR {current} mA')
        
    def get_current(self):
        return float(self.query('L:CURR?'))*1e3
        
    def get_current_setpoint(self):
        return float(self.query('L:CURR:S?'))*1e3
    
    
    def set_output(self,state):
        if state:
            self.write('L:STAT ON')
            while(self.get_output() != True): pass
        else: 
            self.write('L:STAT OFF')
            while(self.get_output() != False): pass
            
    def get_output(self):
        return "ON" == self.query('L:STAT?')

    
    def set_mode(self,mode):
        if mode.upper() == "P":
            self.write('L:MOD P')
        else:
            self.write('L:MOD I')
    def get_mode(self):
        return self.query('L:MOD?')


    def idn(self):
        return self.query('*IDN?')
      
    def get_driver_model(self):
        
        model = []
        model.append({'element':'variable','name':'current','read':self.get_current,'unit':'mA','type':float,'help':'Laser current'})
        model.append({'element':'variable','name':'current setpoint','read':self.get_current_setpoint,'write':self.set_current_setpoint,'unit':'mA','type':float,'help':'Laser current setpoint'})
        model.append({'element':'variable','name':'mode','read':self.get_mode,'write':self.set_mode,'type':str,'help':'"I": current mode, "P": power mode'})
        model.append({'element':'variable','name':'output','read':self.get_output,'write':self.set_output,'type':bool,'help':'True: laser output on. False: laser output off'})
        
        return model


#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::1::INSTR',**kwargs):
        import visa
        
        rm = visa.ResourceManager()
        self.inst = rm.get_instrument(address)
        
        Driver.__init__(self)
        
    def close(self):
        self.inst.close()
    def query(self,query):
        self.write(query)
        return self.read()
    def write(self,command):
        self.inst.write(command)
    def read(self):
        rep = self.inst.read()
        return rep.strip('\r\n')

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


