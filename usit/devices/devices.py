# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 10:25:49 2019

@author: quentin.chateiller
"""

import threading
import inspect

from . import drivers




    

class DeviceManager() :
    
    """ This class manage the different devices """
    
    def __init__(self):
        
        self._dev = {}

        for name in list(drivers.get_devices()) :
            self._dev[name] = Device(self,name)
        
    def get_available_devices(self):
        return list(self._dev.keys())
    
    def get_loaded_devices(self):
        return [ name for name in self.get_available_devices() if self._isLoaded(name) ]
    
    def _isLoaded(self,name):
        return self._dev[name]._instance is not None
        
        
    
    # REPRESENTATION
    # =========================================================================
    
    def _getDetails(self):
        txt = "Availables devices:\n"
        for name in self.get_available_devices():
            txt += f" - {name}"
            if self._isLoaded(name) : txt += ' [loaded]'
            txt += "\n"
        return txt
    
    def __str__(self):
        return self._getDetails()
    
    def __repr__(self):
        return self._getDetails()
    
    
    
    # GET AND CLOSE DEVICE
    # =========================================================================

    def __getattr__(self,name):
        assert name in self.get_available_devices(), f"No device with name {name} in the index"
        if self._isLoaded(name) is False :
            self._load(name)
        return self._dev[name]
       
    def close_all(self):
        for devName in self.get_loaded_devices() :
            self._dev[devName].close()
        
    def _load(self,name):
        instance,configFunc = drivers.getDeviceMaterial(name)
        configFunc(instance,self._dev[name])
        self._dev[name]._setInstance(instance)


        
        


        
class Module():
    
    def __init__(self,parent,name):
        
        self._name = name
        self._parent = parent   
        self._mod = {}
        self._var = {}
        self._act = {}

    def _reset(self):
        for mod in self._mod.values() : mod._reset()
        for var in self._var.values() : var._reset()
        for act in self._act.values() : act._reset()
        self._mod = {}
        self._var = {}
        self._act = {}
        

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
    
    
    
    def addVariable(self,name,**kwargs):
        assert name not in self._var.keys(), f"The variable '{name}' already exists in module {self._name}"
        var = Variable(self,name,**kwargs)
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
        assert any(attr in x for x in [self._var.keys(),self._act.keys(),self._mod.keys()]), f"'{attr}' not found in module '{self._name}'"
        if attr in self._var.keys() : return self._var[attr]
        elif attr in self._act.keys() : return self._act[attr]
        elif attr in self._mod.keys() : return self._mod[attr]
        
    def __repr__(self):        
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
    
    def __init__(self,manager,name):
        
        Module.__init__(self,None,name)
        self._name = name
        self._manager = manager
        self._instance = None
        self._lock = threading.Lock()
        
    def _setInstance(self,instance):
        self._instance = instance
                
    def close(self):
        try : self._instance.close()
        except : pass
        self._instance = None
        self._reset()
        
    def _acquire(self):
        self._lock.acquire()
        
    def _release(self):
        self._lock.release()   
        
    def reload(self):
        self.close()
        self._manager._load(self._name)

          
        
 
        
        
class Variable:
    
    def __init__(self,module,name,**kwargs):
        
        self._module = module
        
        assert isinstance(name,str), f"Variable names have to be str values"        
        self._name = name
        
        self._pty = {}
        
        for key,value in kwargs.items() :
            if key == 'setFunction' :
                assert inspect.ismethod(value), f"The SET function provided for the variable {self._name} is not a function"
            elif key == 'getFunction' :
                assert inspect.ismethod(value), f"The GET function provided for the variable {self._name} is not a function"
            elif key == 'unit' :
                assert isinstance(value,str), f"The UNIT value has to be a str object"
            self._pty[key] = value
            
        self._lock = threading.Lock()
        
    def _reset(self):
        self._pty = {}
        
    def __repr__(self):
        display = f'Variable {self._name}\n'
        for key,value in self._pty.items() :
            display+=f'{key} : {value}\n'
        return display
    
    def _getType(self):
        if 'type' in self._pty.keys() :
            return self._pty['type']
    
    def _getName(self):
        return self._name


    def __call__(self,value=None):
        if value is None:
            return self.get()
        else : 
            self.set(value)

    def get(self):
        assert 'getFunction' in self._pty.keys(), f"The variable {self._name} is not configured to be measurable"
        self._module._acquire()
        result = self._pty['getFunction']()
        self._module._release()
        if 'type' not in self._pty.keys() : self._pty['type'] = type(result)
        return result
    
    
    def set(self,value):
        assert 'setFunction' in self._pty.keys(), f"The variable {self._name} is not configured to be set"
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
        
    def _reset(self):
        self._pty = {}
        
    def __repr__(self):
        display = f'Action {self._name}\n'
        for key,value in self._pty.items() :
            display+=f'{key} : {value}\n'
        return display
    
    def __call__(self):
        self.do()

    def do(self):
        assert 'function' in self._pty.keys(), f"The action {self._name} is not configured to be actionable"
        self._module._acquire()
        self._pty['function']()
        self._module._release()
    

deviceManager = DeviceManager()