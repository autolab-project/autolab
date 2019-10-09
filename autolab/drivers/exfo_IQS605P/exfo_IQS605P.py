#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""    
    
class Driver():
    
    category = 'Optical frame'
    slotNaming = 'slot<NUM> = <MODULE_NAME>,<SLOT_NAME>'
    
    def __init__(self, **kwargs):
        
        self.write('*CLS')
        
        # Submodules
        self.slotnames = []
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix):
                slot_num = key[len(prefix):]
                module = globals()[ 'Module_'+kwargs[key].split(',')[0].strip() ]
                name = kwargs[key].split(',')[1].strip()
                setattr(self,name,module(self,slot_num))
                self.slotnames.append(name)

    def getID(self):
        return self.write('*IDN?')
    
    def getDriverConfig(self):
        
        config = []
        for name in self.slotnames :
            config.append({'element':'module','name':name,'object':getattr(self,name)})
        return config
    
    
    
#################################################################################
############################## Connections classes ##############################
class Driver_TELNET(Driver):
    
    def __init__(self, address='192.168.0.12', **kwargs):
        from telnetlib import Telnet
        
        self.TIMEOUT = 1
        
        # Instantiation
        self.controller = Telnet(address,5024)
        self.read()
        self.read()
        
        Driver.__init__(self,**kwargs)
        
        
    def write(self,command):
        try : self.controller.write(f'{command}\r\n'.encode())
        except : pass
        return self.read()
        
        
    def read(self):
        try :
            ans = self.controller.read_until('READY>'.encode(),timeout=self.TIMEOUT)
            ans = ans.decode().replace('READY>','').strip() 
            assert ans != ''
            return ans
        except :
            pass
        
    def close(self):
        try : self.controller.close()
        except : pass
    
############################## Connections classes ##############################
#################################################################################
        
    
    
class Module_IQS9100B():
    
    
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
        
    
    
if __name__ == '__main__' :
    ADDRESS = '192.168.0.99'
    PORT = 5024




