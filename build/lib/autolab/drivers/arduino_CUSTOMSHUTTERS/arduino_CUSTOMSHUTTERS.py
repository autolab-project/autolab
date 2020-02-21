#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import numpy as np
        
    

class Driver():
    
    def __init__(self):
        
        self.queue = []
    
        # Angle configuration : True = Shutter closed  ; False = Shutter open
        self.shutter1 = Shutter(self,1,{True:30,False:60})
        self.shutter2 = Shutter(self,2,{True:125,False:85})
        self.shutter3 = Shutter(self,3,{True:25,False:70})
                
        # Close every shutters at startup
        self.safe_state()       
        
        
    
    def get_id(self):
        
        ''' Returns the ID of the Arduino '''
        
        return self.query('ID?')
    
    
    
    def get_shutter(self,num):
        
        ''' Returns the shutter object with corresponding num '''
        
        return getattr(self,f'shutter{num}')
        
    
    
    def append_instruction(self,instruction):
        
        ''' Append a new element to the queue of instructions '''
        
        self.queue.append(instruction)
        
        
        
    def execute_queue(self):
        
        ''' Execute the queue of instructions '''
        
        if len(self.queue) > 0 :
            self.query(','.join(self.queue))
            self.queue = []
        
        
        
    def invert(self):
        
        ''' Invert the state of all shutters '''
        
        for num in range(3) : self.get_shutter(num+1).invert(execute=False)
        self.execute_queue()
      
        
        
    def safe_state(self):
        
        ''' Close every shutters '''
        
        for num in range(3) : self.get_shutter(num+1).set_state(True,execute=False)
        self.execute_queue()
        


    def set_global_state(self,global_state):
        
        ''' Set the given global_state '''
        
        assert isinstance(global_state,str)
        assert len(global_state) == 3
        for i in range(len(global_state)):
            if global_state[i] in ['0','1'] :
                num = i+1
                state = bool(int(global_state[i]))
                self.get_shutter(num).set_state(state,execute=False)
                
        self.execute_queue()
        


    def danse(self):
        
        ''' Little danse followed by a safe state '''
        
        for i in range(6) :
            for j in range(3) :
                self.get_shutter(j+1).set_angle(round(np.random.random()*180),execute=False)
        
        for j in range(3) :
            self.get_shutter(j+1).set_state(True, execute=False)
            self.get_shutter(j+1).set_state(True, execute=False)
                
        self.inst.timeout = 15000
        self.execute_queue()
        self.inst.timeout = 5000
        
        
        
        
    def get_driver_model(self):
        
        model = []
        
        for i in range(3):
            model.append({'element':'module','name':f'shutter{i+1}','object':getattr(self,f'shutter{i+1}')})
        
        model.append({'element':'variable','name':'global_state','type':str,'write':self.set_global_state,'help':'Global state of the shutters : "0x1" = Close shutter 1 and open shutter 3'})
        model.append({'element':'action','name':'safe_state','do':self.safe_state,'help':'Close every shutters'})
        model.append({'element':'action','name':'invert','do':self.invert,'help':'Invert every shutter state'})
        model.append({'element':'action','name':'danse','do':self.danse,'help':'Random danse then safe state'})
        return model
  
    
    
    
    
    
    
class Shutter :
    
    def __init__(self,master,num,angles):
        
        self.master = master
        self.num = num
        self.angles = angles
        self.state = True
        
        
        
    def set_angle(self,angle,execute=True):
        
        ''' Set the angle of the shutter '''
        
        self.master.append_instruction(f'SRV{self.num}={angle}')
        if execute is True : self.master.execute_queue()
        
        
        
    def set_state(self,state,**kwargs):
        
        ''' Set the state of the shutter '''
        
        self.set_angle(self.angles[state],**kwargs)
        self.state = state
        
        
                
    def get_state(self):
        
        ''' Return the current state of the shutter '''
        
        return self.state
    
    
    
    def invert(self,**kwargs):
        
        ''' Invert the current state of the shutter '''
        
        self.set_state(not(self.state),**kwargs)
        
        
        
    def get_driver_model(self):
        
        model = []
        model.append({'element':'variable','name':'state','type':bool,'read':self.get_state,'write':self.set_state,'help':'State of the shutter (True: beam blocked)'})
        model.append({'element':'action','name':'invert','do':self.invert,'help':'Invert the shutter state'})
        return model
        
    
    


#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='ASRL::2::INSTR', **kwargs):
        import visa 
        
        self.BAUDRATE = 115200 

        # Instantiation
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(address)
        self.inst.timeout = 5000 #ms
        self.inst.baud_rate = self.BAUDRATE
        
        Driver.__init__(self)
        
        
    def close(self):
        try : self.inst.close()
        except : pass

    def query(self,command):
        return self.inst.query(command).strip('\n')
    
    def write(self,command):
        self.inst.write(command)

############################## Connections classes ##############################
#################################################################################
        

        
