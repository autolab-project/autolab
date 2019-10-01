# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:38:15 2019

@author: qchat
"""
import usit
import os 
import inspect
import importlib

class DriverWrapper() :
    
    def __init__(self, name):
        
        self._name = name
        
        # Loading preparation
        driver_path = os.path.join(usit.core.DRIVERS_PATH,name,f'{name}.py')
        spec = importlib.util.spec_from_file_location(name, driver_path)
        lib = importlib.util.module_from_spec(spec)
        
        # Current working directory
        currDir = os.getcwd()
        
        # Go to driver's directory, in case there are absolute imports
        os.chdir(os.path.dirname(driver_path))
    
        # Load the module
        spec.loader.exec_module(lib)
        self._module = lib       
        
        # Come back to previous working directory
        os.chdir(currDir)
    
    def __getattr__(self,attr) :
        
        return getattr(self._module,attr)
    
    def __dir__(self):
        
        return ['help'] + self._module.__dir__()
        
        
        
    def help(self) :
        
        mess = f'\nExample(s) of configuration in file devices_index.ini for driver "{self._name}"\n\n'
        
        classes = [name for name, obj in inspect.getmembers(self._module, inspect.isclass) 
                    if obj.__module__ is self._module.__name__ and name.startswith('Device_') ]

        for className in classes :
            
            mess += '[myDeviceName]\n'
            mess += f'driver = {self._name}\n'
            mess += f'class = {className}\n'
            
            signature = inspect.signature(getattr(self._module,className))
            defaults_args = {k: v.default for k, v in signature.parameters.items() if v.default is not inspect.Parameter.empty}
            for key,value in defaults_args.items() :
                mess += f'{key} = {value}\n'
                
            if hasattr(self._module,'Device') :
                signature = inspect.signature(getattr(self._module,'Device'))
                defaults_args = {k: v.default for k, v in signature.parameters.items() if v.default is not inspect.Parameter.empty}
                for key,value in defaults_args.items() :
                    mess += f'{key} = {value}\n'
                if hasattr(self._module.Device,'slotNaming') and isinstance(self._module.Device.slotNaming,str) : 
                    mess += self._module.Device.slotNaming
                    if hasattr(self._module,'modules') and isinstance(self._module.modules,dict) : 
                        mess += '\t;(modules:'+','.join(self._module.modules.keys())+')'
                
        print(mess)
    
#    assert 'Device_'+options.link in classes , "Not in " + str([a for a in classes if a.startwith('Device_')])
#    Device_LINK = getattr(sys.modules[__name__],'Device_'+options.link)
#    I = Device_LINK(address=options.address)

        


class DriverManager() :
    
    def __init__(self):
        self._drivers = {}
            
    def __dir__(self):
        return self.list() + ['list']
    
    def list(self):
        return [name for name in os.listdir(usit.core.DRIVERS_PATH) 
                if os.path.isdir(os.path.join(usit.core.DRIVERS_PATH,name)) and
                 f'{name}.py' in os.listdir(os.path.join(usit.core.DRIVERS_PATH,name))]
        
    def __getattr__(self,name):
        
        assert name in self.list(), f"Driver {name} doesn't exist"
        return DriverWrapper(name)
        
