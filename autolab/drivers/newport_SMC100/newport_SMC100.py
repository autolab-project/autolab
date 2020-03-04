#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- Newport smc100
"""



class Driver():

    slot_naming = 'slot<NUM> = <MODULE_NAME>'
    
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

    def get_driver_model(self):
        
        model = []
        for name in self.slot_names.values():
            model.append({'element':'module','name':name,'object':getattr(self,name)})
        return model
    
#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::2::INSTR', **kwargs):
        import visa
        
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.baud_rate = 57600
        self.controller.flow_control = visa.constants.VI_ASRL_FLOW_XON_XOFF
        self.controller.read_termination = '\r\n'
        
        Driver.__init__(self, **kwargs)
    

    def query(self,command) :
        return self.controller.query(command)
        
    def write(self,command) :
        self.controller.write(command)

############################## Connections classes ##############################
#################################################################################


import time 

class Module_ILS100CC() :
    
    def __init__(self,dev,slot):
        
        self.dev = dev
        self.SLOT = str(slot)        
        
    def query(self,command,unwrap=True):
        result = self.dev.query(self.SLOT+command)
        if unwrap is True :
            try:
                prefix=self.SLOT+command[0:2]
                result = result.replace(prefix,'')
                result = result.strip()
                result = float(result)
            except:
                pass
            
        return result
    
    
    def write(self,command):
        self.dev.write(self.SLOT+command)
        
    def get_state(self):
        ans = self.query('TS?',unwrap=False)[-2:]
        if ans[0] == '0' :
            return 'NOTREF'
        elif ans == '14' :
            return 'CONF'
        elif ans in ['1E','1F'] :
            return 'HOMING'
        elif ans == '28' :
            return 'MOVING'
        elif ans[0] == '3' and ( ans[1].isalpha() is False)  :
            return 'READY'
        elif ans[0] == '3' and ( ans[1].isalpha() is True)  :
            return 'DISABLED'
        elif ans in ['46','47']:
            return 'JOGGING'
        else :
            return 'UNKNOWN'
        
    def set_ready_state(self):
        
        # On vérifie que l'on est pas dans le mode REF
        state=self.get_state()
        if state == 'JOGGING' : 
            self.write('JD') # Sortie du mode Jogging   
        elif state == 'DISABLED' : 
            self.write('MM1') # Sortie du mode disabled  
        self.wait_ready_state()

    def wait_ready_state(self):
        while self.get_state() != 'READY' :
            time.sleep(0.1)
            

    def get_id(self):
        return self.query('ID?')


    def get_position(self):
        return self.query('PA?')
    
    def set_position(self,value):
        self.set_ready_state()
        self.write('PA'+str(value))
        self.wait_ready_state()


    def set_acceleration(self,value):
        self.set_ready_state()
        self.write('AC'+str(value))


    def get_acceleration(self):
        return self.query('AC?')
    
    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'position','type':float,
                       'read':self.get_position,'write':self.set_position, 'help':'Initiates an absolute move.'})
        return model
            

