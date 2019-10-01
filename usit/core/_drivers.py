# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:38:15 2019

@author: qchat
"""
import usit
import os 
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
        
        print(f'Auto help for the configuration of driver {self._name}')
        


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
        
