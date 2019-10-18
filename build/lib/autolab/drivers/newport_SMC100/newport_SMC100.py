#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- Newport smc100
"""



class Driver():
    
    category = 'Motion controller'
    slotNaming = 'slot<NUM> = <MODULE_NAME>,<SLOT_NAME>'
    
    def __init__(self,**kwargs):
        
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


    def getDriverConfig(self):
        
        config = []
        for name in self.slotnames:
            config.append({'element':'module','name':name,'object':getattr(self,name)})
        return config
    
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
    

    def query(self,command,unwrap=True) :
        result = self.controller.query(command)
        if unwrap is True :
            try:
                prefix=self.SLOT+command[0:2]
                result = result.replace(prefix,'')
                result = result.strip()
                result = float(result)
            except:
                pass
        return result
        
    def write(self,command) :
        self.controller.write(command)

############################## Connections classes ##############################
#################################################################################


import time 

class Module_ILS100CC() :
    
    def __init__(self,dev,slot):
        
        self.dev = dev
        self.SLOT = str(slot)        
        
    def query(self,command):
        return self.dev.query(self.SLOT+command)
    
    
    def write(self,command):
        self.dev.write(self.SLOT+command)
        
    def getState(self):
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
        
    def getReady(self):
        
        # On vérifie que l'on est pas dans le mode REF
        state=self.getState()
        if state == 'JOGGING' : 
            self.write('JD') # Sortie du mode Jogging   
        elif state == 'DISABLED' : 
            self.write('MM1') # Sortie du mode disabled  
        self.waitReady()

    def waitReady(self):
        while self.getState() != 'READY' :
            time.sleep(0.1)
            

    def getID(self):
        return self.query('ID?')


    def getPosition(self):
        return self.query('PA?')
    
    def setPosition(self,value):
        self.getReady()
        self.write('PA'+str(value))
        self.waitReady()


    def setAcceleration(self,value):
        self.getReady()
        self.write('AC'+str(value))


    def getAcceleration(self):
        return self.query('AC?')
    
    def getDriverConfig(self):
        config = []
        config.append({'element':'variable','name':'position','type':str,
                       'read':self.getPosition,'write':self.setPosition, 'help':'Initiates an absolute move.'})
        return config
            

