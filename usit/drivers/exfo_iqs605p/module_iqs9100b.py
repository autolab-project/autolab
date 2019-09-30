# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 16:39:47 2019

@author: qchat
"""

class IQS9100B():
    
    
    def __init__(self,dev,slot):
        
        self.dev = dev
        self.SLOT = slot
        self.prefix = f'LINS1{self.SLOT}:'
        
        # Initialisation
        self.dev.write(self.prefix+f'STAT?')
        self.dev.write('*OPC?')
        
    def setSafeState(self):
        self.setShutter(True)
        if self.isShuttered() is True :
            return True
   

    def getID(self):
        return self.dev.write(self.prefix+f'SNUM?')
        
        
    def setRoute(self,routeID):
        currRoute = self.getRoute()
        if currRoute != routeID :
            self.dev.write(self.prefix+f"ROUT1:SCAN {int(routeID)}")
            self.dev.write(self.prefix+f'ROUT1:SCAN:ADJ')
            self.dev.write('*OPC?')

    def getRoute(self):
        ans=self.dev.write(self.prefix+f'ROUT1:SCAN?')
        return int(ans)



    def isShuttered(self):
        ans=self.dev.write(self.prefix+f'ROUT1:OPEN:STAT?')
        return not bool(int(ans))
        
    def setShuttered(self,value):
        assert isinstance(value,bool)
        if value is False :
            self.dev.write(self.prefix+f"ROUT1:OPEN")
        else :
            self.dev.write(self.prefix+f"ROUT1:CLOS")
        self.dev.write('*OPC?')
        
    def getDriverConfig(self):
        
        config = []
        config.append({'element':'variable','name':'route','type':int,'read':self.getRoute,'write':self.setRoute,'help':'Current route of the switch'})
        config.append({'element':'variable','name':'shuttered','type':bool,'read':self.isShuttered,'write':self.setShuttered,'help':'State of the shutter'})
        config.append({'element':'action','name':'safestate','do':self.setSafeState,'help':'Set the shutter'})
        return config
        