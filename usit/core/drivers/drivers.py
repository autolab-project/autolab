# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 10:25:49 2019

@author: quentin.chateiller
"""

import os
import importlib

from usit import _DRIVERS_PATH

class DriverManager() :
    
    def __init__(self):
        self._drivers = {}
            
    def __dir__(self):
        return self.list()
        
    def list(self):
        return [name for name in os.listdir(_DRIVERS_PATH) if os.path.isdir(os.path.join(_DRIVERS_PATH,name)) and
                                                                f'{name}.py' in os.listdir(os.path.join(_DRIVERS_PATH,name))]
    
    def _loadDriver(self,name):
        assert name in self.list(), f"Impossible to find driver '{name}'"
        driver_path = os.path.join(_DRIVERS_PATH,name,f'{name}.py')
        spec = importlib.util.spec_from_file_location(name, driver_path)
        lib = importlib.util.module_from_spec(spec)
        
        currDir = os.getcwd()
        os.chdir(os.path.dirname(driver_path))
        
        try : 
            spec.loader.exec_module(lib)
            self._drivers[name] = lib            
        except Exception as e :
            print(e)
            print(f'Impossible to load {driver_path}')
            
        os.chdir(currDir)
        
    def __getattr__(self,name):
        if name in self._drivers.keys() : return self._drivers[name]
        else : 
            self._loadDriver(name)
            return self._drivers[name]

            
driverManager = DriverManager()