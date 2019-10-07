# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:38:15 2019

@author: qchat
"""
from .paths import Paths
import os 
import inspect
import importlib

class DriverWrapper() :
    
    def __init__(self, name):
        
        self._name = name
        
        # Loading preparation
        paths = Paths()
        driver_path = os.path.join(paths.DRIVERS_PATH,name,f'{name}.py')
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
        
        assert hasattr(self._module,'Driver'), f"Driver {self._name}: Missing class Driver"
        assert inspect.isclass(self._module.Driver), f"Driver {self._name}: Driver is not a class"
        #assert len([attr for attr in self._module.__dir__() if attr.startswith('Driver_')]), f"Driver {self._name}: Require at least one connection class Driver_XXX"
    
    def __getattr__(self,attr) :
        
        return getattr(self._module,attr)
    
    def __dir__(self):
        
        return ['help'] + self._module.__dir__()
        
        
        
    def help(self) :
        
        mess = '\n'
        
        # Name and category if available
        submess = f'Driver "{self._name}"'
        if hasattr(self._module.Driver,'category') : submess += f' ({self._module.Driver.category})'
        mess += '='*len(submess)+'\n'+submess+'\n'+'='*len(submess)+'\n\n'

        
        # Connections types
        mess += 'Available connection(s):\n'
        connections = self._getConnectionNames()
        for connection in connections : 
            mess += f' - {connection}\n'
        mess += '\n'
        
        # Modules
        if hasattr(self._module.Driver,'slotNaming') :
            mess += 'Available modules(s):\n'
            modules = self._getModuleNames()
            for module in modules : 
                moduleClass = self._getModuleClass(module)
                mess += f' - {module}'
                if hasattr(moduleClass,'category') : mess += f' ({moduleClass.category})'
                mess += '\n'
            mess += '\n'
        
        
        mess += f'Configuration example(s) for devices_index.ini:\n\n'
        
        # Arguments of Driver class
        DriverClassArgs = ''
        defaults_args = self._getClassArgs(self._module.Driver)
        for key,value in defaults_args.items() :
            DriverClassArgs += f'{key} = {value}\n'
        if hasattr(self._module.Driver,'slotNaming') : 
            DriverClassArgs += self._module.Driver.slotNaming+'\n'
            
        # Arguments of Driver_XXX classes
        for connection in connections :
            
            mess += '[myDeviceName]\n'
            mess += f'driver = {self._name}\n'
            mess += f'connection = {connection}\n'
            
            # get all optional parameters and default values of __init__ method of Driver_ class
            defaults_args = self._getClassArgs(self._getConnectionClass(connection))
            for key,value in defaults_args.items() :
                mess += f'{key} = {value}\n'
    
            mess += DriverClassArgs + '\n'
            
                
        print(mess)
    
    
    def _getModuleNames(self):
        return [name.split('_')[1] for name, obj in inspect.getmembers(self._module, inspect.isclass) 
                        if obj.__module__ is self._module.__name__ and name.startswith('Module_') ]
            
    def _getConnectionNames(self):
        return [name.split('_')[1] for name, obj in inspect.getmembers(self._module, inspect.isclass) 
                    if obj.__module__ is self._module.__name__ and name.startswith('Driver_') ]
        
    def _getDriverCategory(self):
        if hasattr(self._module.Driver,'category'):
            return self._module.Driver.category
        
    def _getConnectionClass(self,connection):
        assert connection in self._getConnectionNames()
        return getattr(self._module,f'Driver_{connection}')
    
    def _getModuleClass(self,module):
        assert module in self._getModuleNames()
        return getattr(self._module,f'Module_{module}')
    
    def _getClassArgs(self,c):
        signature = inspect.signature(c)
        return {k: v.default for k, v in signature.parameters.items() if v.default is not inspect.Parameter.empty}
            
        

class DriverManager() :
    
    def __init__(self):
        self._drivers = {}
            
    def __dir__(self):
        return self.list() + ['list','help']
    
    def list(self):
        paths = Paths()
        return [name for name in os.listdir(paths.DRIVERS_PATH) 
                if os.path.isdir(os.path.join(paths.DRIVERS_PATH,name)) and
                 f'{name}.py' in os.listdir(os.path.join(paths.DRIVERS_PATH,name))]
        
    def help(self):
        d = {}
        for driver in self.list() :
            
            # REMOVE TRY EXCEPT WHEN DRIVERS WILL BE FINISHED
            
            try : 
                category = getattr(self,driver)._getDriverCategory()
                if category is None :
                    category = 'Other'
                if category not in d.keys() :
                    d[category] = []
                d[category].append(driver)
            except :
                pass


        
        mess = '\n'
        for category in d.keys() :
            mess += f'[{category.upper()}]\n'
            mess += ", ".join([driver for driver in d[category]])+'\n\n'
        
        
        print(mess[:-2])

        
    def __getattr__(self,name):
        
        assert name in self.list(), f"Driver {name} doesn't exist"
        return DriverWrapper(name)
        

