#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- signal recovery 7124 
- signal recovery 7280 (VISA only)
"""

import time

class Driver():

    def __init__(self):
        pass 

    def get_id(self):
        return str(self.query('ID'))+' VER '+str(self.query('VER'))

    def wait_four_time_constant(self): # see manual why
        time.sleep(4*self.get_time_constant())

    def get_magnitude(self):
        return float(self.query("MAG.").split('=')[1])

    def get_phase(self):
        return float(self.query("PHA.").split('=')[1])
    
    def get_ref_frequency(self):
        return float(self.query('FRQ.').split('=')[1])

    def get_time_constant(self):
        return float(self.query('TC.').split('=')[1])
    
    def get_sensitivity(self):
        return float(self.query('SEN.').split('=')[1])
    
    
    def get_driver_model(self):
        
        model = []
        model.append({'element':'variable','name':'time_constant','type':float,'read':self.get_time_constant, 'help':'Filter time constant control.'})        
        model.append({'element':'variable','name':'sensitivity','type':float,'read':self.get_sensitivity, 'help':'Full-scale sensitivity control.'})        
        model.append({'element':'variable','name':'ref_frequency','type':float,'read':self.get_ref_frequency, 'unit':'Hz', 'help':'Reads reference frequency in Hertz.'})        
        model.append({'element':'variable','name':'magnitude','type':float,'read':self.get_magnitude, 'unit':'V', 'help':'Reads magnitude in volts.'})        
        model.append({'element':'variable','name':'phase','type':float,'read':self.get_phase, 'unit':'degrees', 'phase':'Reads Phase in degrees.'})
        model.append({'element':'action','name':'wait_four_time_constant','do':self.wait_four_time_constant,
                       'help':'Wait four time constants. See manual.'})
        return model
    
    
    
    
#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::2::INSTR', **kwargs):
        import visa
        
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
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
        
        
class Driver_SOCKET(Driver):
    def __init__(self, address='192.168.0.9', **kwargs):
        import socket
        
        self.BUFFER_SIZE = 40000
        
        self.controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controller.connect((address,int(50000)))    
        Driver.__init__(self)
        
    def write(self,command):
        self.controller.send(command.encode())
        self.controller.recv(self.BUFFER_SIZE)
        

    def query(self,command):
        self.controller.send(command.encode())
        result = self.controller.recv(self.BUFFER_SIZE).decode()
        result = result.strip('\n\x00)\x00')
        return result
    
    def close(self):
        try :
            self.controller.close()
        except :
            pass
        self.controller = None  


############################## Connections classes ##############################
#################################################################################    
    
    
