#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""    
    
class Driver():

    slot_config = '<MODULE_NAME>'
    
    def __init__(self, **kwargs):
        
        self.write('*CLS')
        
        # Submodules loading
        self.slot_names = {}
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix) and not '_name' in key :
                slot_num = key[len(prefix):]
                module_name = kwargs[key].strip()
                module_class = globals()[f'Module_{module_name}']
                if f'{key}_name' in kwargs.keys() : name = kwargs[f'{key}_name']
                else : name = f'{key}_{module_name}'
                setattr(self,name,module_class(self,slot_num))
                self.slot_names[slot_num] = name

    def get_id(self):
        return self.write('*IDN?')
    
    def get_driver_model(self):
        
        model = []
        for name in self.slot_names :
            model.append({'element':'module','name':name,'object':getattr(self,name)})
        return model
    
    
    
#################################################################################
############################## Connections classes ##############################
class Driver_TELNET(Driver):
    
    def __init__(self, address='192.168.0.12', **kwargs):
        from telnetlib import Telnet
                
        # Instantiation
        self.controller = Telnet(address,5024)
        while True : 
            ans = self.read(timeout=0.1)
            if ans is not None and 'Connected' in ans :
                break

        
        Driver.__init__(self,**kwargs)
        
        
    def write(self,command):
        try : self.controller.write(f'{command}\r\n'.encode())
        except : pass
        return self.read()
        
        
    def read(self,timeout=1):
        try :
            ans = self.controller.read_until('READY>'.encode(),timeout=timeout)
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
        
    def safe_state(self):
        self.set_shutter(True)
        if self.is_shuttered() is True :
            return True
   

    def get_id(self):
        return self.dev.write(self.prefix+f'SNUM?')
        
        
    def set_route(self,route_id):
        curr_route = self.get_route()
        if curr_route != route_id :
            self.dev.write(self.prefix+f"ROUT1:SCAN {int(route_id)}")
            self.dev.write(self.prefix+f'ROUT1:SCAN:ADJ')
            self.dev.write('*OPC?')

    def get_route(self):
        ans=self.dev.write(self.prefix+f'ROUT1:SCAN?')
        return int(ans)



    def is_shuttered(self):
        ans=self.dev.write(self.prefix+f'ROUT1:OPEN:STAT?')
        return not bool(int(ans))
        
    def set_shuttered(self,value):
        assert isinstance(value,bool)
        if value is False :
            self.dev.write(self.prefix+f"ROUT1:OPEN")
        else :
            self.dev.write(self.prefix+f"ROUT1:CLOS")
        self.dev.write('*OPC?')
        
    def get_driver_model(self):
        
        model = []
        model.append({'element':'variable','name':'route','type':int,'read':self.get_route,'write':self.set_route,'help':'Current route of the switch'})
        model.append({'element':'variable','name':'shuttered','type':bool,'read':self.is_shuttered,'write':self.set_shuttered,'help':'State of the shutter'})
        model.append({'element':'action','name':'safe_state','do':self.safe_state,'help':'Set the shutter'})
        return model
        
