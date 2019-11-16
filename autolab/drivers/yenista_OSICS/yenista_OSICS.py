#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver():
    
    slot_config = '<MODULE_NAME>'

    def __init__(self,**kwargs):
        
        self.write('*RST') # The input buffer is cleared. The command interpreter is reset and a reset instruction is sent to every module. The status and event registers are cleared. Sets the OPC bit to 1.
        self.write('*CLS') # Clears the Event Status Register and the output queue. Sets the OPC bit to 1.
        
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
                print(self.slot_names)


    def get_id(self):
        return self.query('*IDN?')


    def get_driver_model(self):
        config = []
        for name in self.slot_names.values() :
            config.append({'element':'module','name':name,'object':getattr(self,name)})
        return config


#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::2::INSTR',**kwargs):
        
        import visa
        
        
        self.TIMEOUT = 60000 #ms
        
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.timeout = self.TIMEOUT
        
        Driver.__init__(self,**kwargs)
        

    def close(self):
        try : self.controller.close()
        except : pass


    def write(self,command):
        self.controller.write(command)
        
    def read(self):
        result = self.controller.read()
        result = result.strip('\n')
        return result
    
    def query(self,command):
        result = self.controller.query(command)
        result = result.strip('\n')
        return result
        
############################## Connections classes ##############################
#################################################################################


class Module_T100():   
    
    category = 'Optical source'
    
    def __init__(self,dev,slot):
        
        self.dev = dev
        self.SLOT = slot
        self.prefix = f'CH{int(slot)}:'
        
        self.write(self.prefix+'NM')
        self.write(self.prefix+'MW')


    def write(self,command):
        self.dev.write(command)
        
    def read(self):
        return self.dev.read()
    
    def query(self,command):
        return self.dev.query(command)
    
    #--------------------------------------------------------------------------
    # Optional functions
    #--------------------------------------------------------------------------
    
    def safe_state(self):
        self.set_output_state(False)
        if self.get_output_state() is False :
            return True
            

    def get_id(self):
        result = self.query(self.prefix+'*IDN?')
        result = self.clean_result(result)
        return result
        
        
    #--------------------------------------------------------------------------
    # Instrument variables
    #--------------------------------------------------------------------------
        
    def clean_result(self,result):
        try:
            result=result.split(':')[1]
            result=result.split('=')[1]
            result=float(result)
        except:
            pass
        return result
    
    


    def set_wavelength(self,value):
        self.write(self.prefix+f"L={value}")
        self.query('*OPC?')
        
    def get_wavelength(self):
        result = self.query(self.prefix+'L?')
        result = self.clean_result(result)
        return result
    
    
    
    
    
    def set_frequency(self,value):
        self.write(self.prefix+f"F={value}")
        self.query('*OPC?')
        
    def get_frequency(self):
        result = self.query(self.prefix+'F?')
        result = self.clean_result(result)
        return result
    
    
    
    
    
    
    def set_power(self,value):
        if value == 0 :
            self.set_output_state(False)
        else :
            if self.get_output_state() is False :
                self.set_output_state(True)
            self.write(self.prefix+f"P={value}")
            self.query('*OPC?')
            
    def get_power(self):
        result = self.query(self.prefix+'P?')
        result = self.clean_result(result)
        if result == 'Disabled':
            return 0
        else :
            return result
    




    
    def set_intensity(self,value):
        if value == 0 :
            self.set_output_state(False)
        else :
            if self.get_output_state() is False :
                self.set_output_state(True)
            self.write(self.prefix+f"I={value}")
            self.query('*OPC?')
        
    def get_intensity(self):
        result = self.query(self.prefix+'I?')
        result = self.clean_result(result)
        if result == 'Disabled':
            return 0
        else :
            return result
        
        
    
    
    
    def set_coherence_control_state(self,state):
        if state is True :
            self.write(self.prefix+'CTRL ON')
        else :
            self.write(self.prefix+'CTRL OFF')
        self.query('*OPC?')
        
    def get_coherence_control_state(self):
        result = self.query(self.prefix+'CTRL?')
        result = self.clean_result(result)
        return bool(int(result))
    
    
    
    
    def set_auto_peak_find_control_state(self,state):
        if state is True :
            self.write(self.prefix+'APF ON')
        else :
            self.write(self.prefix+'APF OFF')
        self.query('*OPC?')
        
    def get_auto_peak_find_control_state(self):
        result = self.query(self.prefix+'APF?')
        result = self.clean_result(result)
        return bool(int(result))
    
    
    
    
    
    def set_output_state(self,state):
        if state is True :
            self.write(self.prefix+"ENABLE")
        else :
            self.write(self.prefix+"DISABLE")
        self.query('*OPC?')
        
    def get_output_state(self):
        result = self.query(self.prefix+'ENABLE?')
        result = self.clean_result(result)
        return result == 'ENABLED'
    
    
    
    def get_driver_model(self):
        
        model = []
        model.append({'element':'variable','name':'wavelength','type':float,'unit':'nm','read':self.get_wavelength,'write':self.set_wavelength,'help':'Wavelength'})
        model.append({'element':'variable','name':'frequency','type':float,'unit':'GHz','read':self.get_frequency,'write':self.set_frequency,'help':'Frequency'})
        model.append({'element':'variable','name':'power','type':float,'unit':'mW','read':self.get_power,'write':self.set_power,'help':'Output power'})
        model.append({'element':'variable','name':'intensity','type':float,'unit':'mA','read':self.get_intensity,'write':self.set_intensity,'help':'Current intensity'})
        model.append({'element':'variable','name':'output','type':bool,'read':self.get_output_state,'write':self.set_output_state,'help':'Output state'})
        model.append({'element':'variable','name':'coherence_control','type':bool,'read':self.get_coherence_control_state,'write':self.set_coherence_control_state,'help':'Coherence control mode'})
        model.append({'element':'variable','name':'auto_peak_find_control','type':bool,'read':self.get_auto_peak_find_control_state,'write':self.set_auto_peak_find_control_state,'help':'Auto peak find control'})
        return model





class Module_SLD():   
    
    category = 'Broadband optical source'
    
    def __init__(self,dev,slot):
        
        self.dev = dev
        self.SLOT = slot
        self.prefix = f'CH{int(slot)}:'
        
        self.write(self.prefix+'NM')
        self.write(self.prefix+'MW')
        
    def write(self,command):
        self.dev.write(command)
        
    def read(self):
        return self.dev.read()
    
    def query(self,command):
        return self.dev.query(command)
    
    #--------------------------------------------------------------------------
    # Optional functions
    #--------------------------------------------------------------------------
        
    def safe_state(self):
        self.set_output_state(False)
        if self.get_output_state() is False :
            return True
            
        
    def get_id(self):
        return self.dev.query(self.prefix+'*IDN?')
        
        
    #--------------------------------------------------------------------------
    # Instrument variables
    #--------------------------------------------------------------------------

        
    def clean_result(self,result):
        try:
            result=result.split(':')[1]
            result=result.split('=')[1]
            result=float(result)
        except:
            pass
        return result
    
    

        
    def get_wavelength(self):
        result = self.query(self.prefix+'L?')
        result = self.clean_result(result)
        return result
    
    
   
    
    
    def set_power(self,value):
        if value < 5:
            self.set_output_state(False)
        elif 5<=value<10 :
            if self.get_output_state() is False :
                self.set_output_state(True)
            self.write(self.prefix+'P=LOW')
            self.query('*OPC?')
        else :
            if self.get_output_state() is False :
                self.set_output_state(True)
            self.write(self.prefix+'P=HIGH')
            self.query('*OPC?')   
            
            
        
    def get_power(self):
        result = self.query(self.prefix+'P?')
        result = self.clean_result(result)
        if result == 'Disabled':
            return 0
        elif result == 'HIGH':
            return 10
        elif result == 'LOW' :
            return 5
    
    
  
    
    
    def set_output_state(self,state):
        if state is True :
            self.write(self.prefix+"ENABLE")
        else :
            self.write(self.prefix+"DISABLE")
        self.query('*OPC?')
        
    def get_output_state(self):
        result = self.query(self.prefix+'ENABLE?')
        result = self.clean_result(result)
        return result == 'ENABLED'
    



    def get_driver_model(self):
        
        model = []
        model.append({'element':'variable','name':'power','type':float,'unit':'mW','read':self.get_power,'write':self.set_power,'help':'Output power'})
        model.append({'element':'variable','name':'output','type':bool,'read':self.get_output_state,'write':self.set_output_state,'help':'Output state'})
        return model
    
    
