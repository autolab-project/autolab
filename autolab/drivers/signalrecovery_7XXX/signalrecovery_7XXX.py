#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- signal recovery 7124 
- signal recovery 7280 (VISA only)
"""

import time

class Driver():
    
    category = 'Lock-in amplifier'

    def __init__(self):
        pass 

    def getID(self):
        return str(self.query('ID'))+' VER '+str(self.query('VER'))

    def waitFourTimeConstant(self): # see manual why
        time.sleep(4*self.getTimeConstant())

    def getMagnitude(self):
        return float(self.query("MAG."))

    def getPhase(self):
        return float(self.query("PHA."))
    
    def getRefFrequency(self):
        return float(self.query('FRQ.'))

    def getTimeConstant(self):
        return float(self.query('TC.'))
    
    def getSensitivity(self):
        return float(self.query('SEN.'))
    
    
    def getDriverConfig(self):
        
        config = []
        config.append({'element':'variable','name':'timeConstant','type':float,'read':self.getTimeConstant, 'help':'Filter time constant control.'})        
        config.append({'element':'variable','name':'sensitivity','type':float,'read':self.getSensitivity, 'help':'Full-scale sensitivity control.'})        
        config.append({'element':'variable','name':'refFrequency','type':float,'read':self.getRefFrequency, 'unit':'Hz', 'help':'Reads reference frequency in Hertz.'})        
        config.append({'element':'variable','name':'magnitude','type':float,'read':self.getMagnitude, 'unit':'V', 'help':'Reads magnitude in volts.'})        
        config.append({'element':'variable','name':'phase','type':float,'read':self.getPhase, 'unit':'degrees', 'phase':'Reads Phase in degrees.'})
        config.append({'element':'action','name':'waitFourTimeConstant','do':self.waitFourTimeConstant,
                       'help':'Wait four time constants. See manual.'})
        return config
    
    
    
    
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
        if '=' in result : result = result.split('=')[1]
        try : result = float(result)
        except: pass
        return result
    
    def write(self,command):
        self.controller.write(command)
        
        
class Driver_SOCKET(Driver):
    def __init__(self, address='192.168.0.9', **kwargs):
        import socket
        
        self.BUFFER_SIZE = 40000
        
        self.controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controller.connect((address,50000))    
        Driver.__init__(self)
        
    def write(self,command):
        self.controller.send(command.encode())
        self.controller.recv(self.BUFFER_SIZE)
        

    def query(self,command):
        self.controller.send(command.encode())
        result = self.controller.recv(self.BUFFER_SIZE).decode()
        result = result.strip('\n\x00)\x00')
        if '=' in result : result = result.split('=')[1]
        try : result = float(result)
        except: pass
        return result
    
    def close(self):
        try :
            self.controller.close()
        except :
            pass
        self.controller = None  


############################## Connections classes ##############################
#################################################################################    
    
    
