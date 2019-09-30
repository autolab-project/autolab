#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


from module_line import Line


class Device():
    
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
class Device_VISA(Device):
    def __init__(self, address=None):
        import visa

        self.TIMEOUT = 1000 #ms
        
        # Instantiation
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(self.address)
        self.controller.timeout = self.TIMEOUT
        
        Device.__init__(self)
    
        
   
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

        
#ADDRESS = 'GPIB0::10::INSTR'
