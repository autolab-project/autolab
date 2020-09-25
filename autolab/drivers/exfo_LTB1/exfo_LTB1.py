#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver():

    slot_config = '<MODULE_NAME>'
    
    def __init__(self,**kwargs):
        
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
        for name in self.slot_names.values() :
            model.append({'element':'module','name':name,'object':getattr(self,name)})
        return model
    
#################################################################################
############################## Connections classes ##############################
class Driver_TELNET(Driver):
    
    def __init__(self, address='192.168.0.1', **kwargs):
        from telnetlib import Telnet
        
        # Instantiation
        self.controller = Telnet(address,5024)
        while True : 
            ans = self.read(timeout=0.1)
            if ans is not None and 'Connected' in ans :
                break

        Driver.__init__(self, **kwargs)
        
    def write(self,command):
        self.controller.write(f'{command}\r\n'.encode())
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
    
    
    
class Module_FTB1750():
    
    def __init__(self,dev,slot):
        
        self.dev = dev
        self.SLOT = slot
        
        # Initialisation
        self.dev.write(f"LINS1:UNIT{self.SLOT}:POW W")                # Unité = Watts
        self.dev.write(f"LINS1:SENS{self.SLOT}:POW:RANG:AUTO 1")      # Ajuster la gamme de mesure automatiquement
        self.dev.write(f"LINS1:SENS{self.SLOT}:POW:REF:STAT 0")       # Set Absolute power measurment mode (dBm or W)
        self.dev.write('*OPC?')
    



    
    def set_averaging_state(self,state):
        assert isinstance(state,bool)
        self.dev.write(f"LINS1:SENS{self.SLOT}:AVER:STAT {int(state)}")
        self.dev.write('*OPC?')
    
    def get_averaging_state(self):
        ans = self.dev.write(f"LINS1:SENS{self.SLOT}:AVER:STAT?")
        return bool(int(ans))



    
    
    def get_buffer_size(self):
        ans = self.dev.write(f"LINS1:SENS{self.SLOT}:AVER:COUN?")
        return int(ans)
    
    def set_buffer_size(self, value):
        self.dev.write(f"LINS1:SENS{self.SLOT}:AVER:COUN {value}")
        self.dev.write('*OPC?')


 
       

    
    def get_power(self):
        ans = self.dev.write(f"LINS1:READ{self.SLOT}:SCAL:POW:DC?")
        return float(ans)
    

    
        
    
    
    def set_wavelength(self,wavelength):
        self.dev.write(f"LINS1:SENS{self.SLOT}:POW:WAV {wavelength} nm")
        self.dev.write('*OPC?')
    
    def get_wavelength(self):
        ans = self.dev.write(f"LINS1:SENS{self.SLOT}:POW:WAV?")
        return float(ans)*1e9
    
    
    
    
    
    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'averaging','type':bool,'read':self.get_averaging_state,'write':self.set_averaging_state,'help':'Average or not the measure'})
        model.append({'element':'variable','name':'buffer_size','type':int,'read':self.get_buffer_size,'write':self.set_buffer_size,'help':'Buffer size for the average'})
        model.append({'element':'variable','name':'wavelength','type':float,'unit':'nm','read':self.get_wavelength,'write':self.set_wavelength,'help':'Wavelength of the measure'})
        model.append({'element':'variable','name':'power','type':float,'unit':'W','read':self.get_power,'help':'Current power'})
        return model
        
