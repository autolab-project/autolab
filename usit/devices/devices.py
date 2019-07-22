# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 10:25:49 2019

@author: quentin.chateiller
"""

import threading
import inspect
import pandas as pd
import numpy as np

from . import drivers




    

class DeviceManager() :
    
    """ This class manage the different devices """
    
    def __init__(self):

        self._dev = {}
        
    def get_available_devices(self):
        return list(drivers.get_devices())
    
    def get_loaded_devices(self):
        return list(self._dev.keys())
    
    
    # REPRESENTATION
    # =========================================================================
    
    def _getDetails(self):
        txt = "Availables devices:\n"
        for name in self.get_available_devices():
            txt += f" - {name}"
            if name in self.get_loaded_devices() : txt += ' [loaded]'
            txt += "\n"
        return txt
    
    def __str__(self):
        return self._getDetails()
    
    def __repr__(self):
        return self._getDetails()
    
    
    
    # GET AND CLOSE DEVICE
    # =========================================================================

    def __getattr__(self,name):
        if name in self._dev.keys(): # The device is already loaded
            return self._dev[name]
        else : # Loading of the device
            assert name in self.get_available_devices(), f"No device with name {name} in the index"
            instance,configFunc = drivers.getDeviceMaterial(name)
            device = Device(name,instance,self)
            configFunc(instance,device)
            self._dev[name] = device
            return self._dev[name]
       
    def close_all(self):
        for devName in self.get_loaded_devices() :
            self._dev[devName].close()
        
        
        
        


        
class Module():
    
    def __init__(self,name,parent=None):
        
        self._name = name
        self._parent = parent   
        self._deleted = False
        self._mod = {}
        self._var = {}
        self._act = {}

    def _delete(self):
        for mod in self._mod.values() : mod._delete()
        for var in self._var.values() : var._delete()
        for act in self._act.values() : act._delete()
        self._mod = {}
        self._var = {}
        self._act = {}
        self._deleted = True
        

    def addModule(self,name):
        assert name not in self._mod.keys(), f"The submodule '{name}' already exists in module {self._name}"
        mod = Module(name,self)
        self._mod[name] = mod
        return mod
    
    def getModule(self,name):
        assert name in self._mod.keys(), f"The submodule '{name}' does not exist in module {self._name}"
        return self._mod[name]
    
    def getModuleList(self):
        return tuple(self._mod.keys())
    
    
    
    def addVariable(self,name,valueType,**kwargs):
        assert name not in self._var.keys(), f"The variable '{name}' already exists in module {self._name}"
        var = Variable(self,name,valueType,**kwargs)
        self._var[name] = var
        return var
    
    def getVariable(self,name):
        assert name in self._var.keys(), f"The variable '{name}' does not exist in module {self._name}"
        return self._var[name]
    
    def getVariableList(self):
        return tuple(self._var.keys())
    
    
    
    
    def addAction(self,name,**kwargs):
        assert name not in self._act.keys(), f"The action '{name}' already exists in device {self._name}"
        act = Action(self,name,**kwargs)
        self._act[name] = act
        return act
    
    def getAction(self,name):
        assert name in self._dev.keys(), f"The action '{name}' does not exist in device {self._name}"
        return self._dev[name]
    
    def getActionList(self):
        return tuple(self._act.keys())
    
    

    def __getattr__(self,attr):
        assert self._deleted is False, f"This object cannot be used anymore"
        assert any(attr in x for x in [self._var.keys(),self._act.keys(),self._mod.keys()]), f"'{attr}' not found in module '{self._name}'"
        if attr in self._var.keys() : return self._var[attr]
        elif attr in self._act.keys() : return self._act[attr]
        elif attr in self._mod.keys() : return self._mod[attr]
        
    def __repr__(self):
        
        assert self._deleted is False, f"This object cannot be used anymore"
        
        display = f'Module {self._name}\n'
        
        devList = self.getModuleList()
        if len(devList)>0 :
            display+='Submodule(s):\n'
            for key in devList :
                display+=f' - {key}\n'
        else : display+='No submodule(s)\n'
        
        varList = self.getVariableList()
        if len(varList)>0 :
            display+='Variable(s):\n'
            for key in varList :
                display+=f' - {key}\n'
        else : display+='No variable(s)\n'
        
        actList = self.getActionList()
        if len(actList)>0 :
            display+='Action(s):\n'
            for key in actList :
                display+=f' - {key}\n'
        else : display+='No action(s)\n'
        
        return display
        
        
    def _acquire(self):
        self._parent._acquire()
        
    def _release(self):
        self._parent._release()


        



class Device(Module):
    
    def __init__(self,name,instance,manager):
        
        Module.__init__(self,name)
        self._name = name
        self._manager = manager
        self._instance = instance
        self._lock = threading.Lock()
        
    def close(self):
        try : self._instance.close()
        except : pass
        self._delete()
        del self._manager._dev[self._name]
        
        
    def _acquire(self):
        self._lock.acquire()
    def _release(self):
        self._lock.release()          

          
        
 
        
        
class Variable:
    
    def __init__(self,module,name,valueType,**kwargs):
        
        self._module = module
        
        assert isinstance(name,str), f"Variable names have to be str values"        
        self._name = name
        
        if valueType == 'dataframe' : valueType = pd.DataFrame
        elif valueType == 'numpy_array' : valueType = type(np.array(0))
        types = [int,float,bool,pd.DataFrame,type(np.array(0))]
        assert valueType in types, f"Variable {self._name} : {valueType} is not supported. Please use one of the following class: {types}"
        self._pty = {'type':valueType}
        
        for key,value in kwargs.items() :
            if key == 'setFunction' :
                assert inspect.ismethod(value), f"The SET function provided for the variable {self._name} is not a function"
            elif key == 'getFunction' :
                assert inspect.ismethod(value), f"The GET function provided for the variable {self._name} is not a function"
            elif key == 'unit' :
                assert isinstance(value,str), f"The UNIT value has to be a str object"
            self._pty[key] = value
            
        self._lock = threading.Lock()
        self._deleted = False
        
    def _delete(self):
        self._deleted = True
        
    def __repr__(self):
        assert self._deleted is False, f"This object cannot be used anymore"
        display = f'Variable {self._name}\n'
        for key,value in self._pty.items() :
            display+=f'{key} : {value}\n'
        return display
    
    def _getType(self):
        return self._pty['type']
    
    def _getName(self):
        return self._name


    def get(self):
        assert self._deleted is False, f"This object cannot be used anymore"
        assert 'getFunction' in self._pty.keys(), f"The variable {self._name} is not configured to be measurable"
        self._module._acquire()
        result = self._pty['getFunction']()
        self._module._release()
        return result
    
    
    def set(self,value):
        assert self._deleted is False, f"This object cannot be used anymore"
        assert 'getFunction' in self._pty.keys(), f"The variable {self._name} is not configured to be set"
        if isinstance(value,int) and self._pty['type']==float :
            value = float(value)
        assert isinstance(value,self._pty['type']), f"The variable {self._name} is configured to be of type {self._pty['type']}, not {type(value)}"
        self._module._acquire()
        self._pty['setFunction'](value)
        self._module._release()

        
        
        
        
        
class Action:
    
    def __init__(self,module,name,**kwargs):
        
        self._module = module
        
        assert isinstance(name,str), f"Action names have to be str values"        
        self._name = name
        
        self._pty = {}
        
        for key,value in kwargs.items() :
            if key == 'function' :
                assert inspect.ismethod(value), f"The function provided for the variable {self._name} is not a function"
            self._pty[key] = value
            
        self._lock = threading.Lock()
        self._deleted = False
        
    def _delete(self):
        self._deleted = True
        
    def __repr__(self):
        assert self._deleted is False, f"This object cannot be used anymore"
        display = f'Action {self._name}\n'
        for key,value in self._pty.items() :
            display+=f'{key} : {value}\n'
        return display
    

    def do(self):
        assert self._deleted is False, f"This object cannot be used anymore"
        assert 'function' in self._pty.keys(), f"The action {self._name} is not configured to be actionable"
        self._module._acquire()
        self._pty['function']()
        self._module._release()
    

deviceManager = DeviceManager()