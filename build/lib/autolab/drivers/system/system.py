#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


import time 

class Driver():
        
    def __init__(self):
        pass
        self.chronometer_startTime = time.time()
    
    def chronometer(self):
        return time.time() - self.chronometer_startTime
    
    def reset_chronometer(self):
        self.chronometer_startTime = time.time()
        
    def parameter_buffer(self,value):
        pass
    
    def getDriverConfig(self):
        
        config = []
        config.append({'element':'variable','name':'chronometer','type':float,'read':self.chronometer,'unit':'s','help':'Elapsed time since chronometer reset'})
        config.append({'element':'action','name':'reset_chronometer','do':self.reset_chronometer,'help':'Reset the chronometer time'})
        config.append({'element':'variable','name':'parameter_buffer','type':float,'write':self.parameter_buffer,'help':'Parameter buffer for monitoring in the scanning panel. Does nothing with the input value'})
        
        return config
        
        
    
#################################################################################
############################## Connections classes ##############################
class Driver_DEFAULT(Driver):
    def __init__(self):
        
        Driver.__init__(self)
        

############################## Connections classes ##############################
#################################################################################
