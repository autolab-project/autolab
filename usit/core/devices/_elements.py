# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 15:52:04 2019

@author: qchat
"""
import threading
import inspect
import numpy as np
import pandas as pd


def getAddress(item):
    
    address = [item.name]
    parent = item._parent
    while parent is not None : 
        address.append(parent.name)
        parent = parent._parent
    return '.'.join(address[::-1])
    


class Module():
    
    _elementType = 'Module'
    getAddress = getAddress
    
    def __init__(self,parent,name):
        
        self.name = name
        self._parent = parent   
        self._mod = {}
        self._var = {}
        self._act = {}
        
        
        

    def addModule(self,name):
        assert name not in self._mod.keys(), f"The submodule '{name}' already exists in module {self.name}"
        mod = Module(self,name)
        self._mod[name] = mod
        return mod
    
    def getModule(self,name):
        assert name in self._mod.keys(), f"The submodule '{name}' does not exist in module {self.name}"
        return self._mod[name]
    
    def getModuleList(self):
        return list(self._mod.keys())
    
    
    
    def addVariable(self,name,varType,**kwargs):
        assert name not in self._var.keys(), f"The variable '{name}' already exists in module {self.name}"
        var = Variable(self,name,varType,**kwargs)
        self._var[name] = var
        return var
    
    def getVariable(self,name):
        assert name in self._var.keys(), f"The variable '{name}' does not exist in module {self.name}"
        return self._var[name]
    
    def getVariableList(self):
        return list(self._var.keys())
    
    
    
    
    def addAction(self,name,**kwargs):
        assert name not in self._act.keys(), f"The action '{name}' already exists in device {self.name}"
        act = Action(self,name,**kwargs)
        self._act[name] = act
        return act
    
    def getAction(self,name):
        assert name in self._dev.keys(), f"The action '{name}' does not exist in device {self.name}"
        return self._dev[name]
    
    def getActionList(self):
        return list(self._act.keys())
    
    

    def __getattr__(self,attr):
        assert any(attr in x for x in [self._var.keys(),self._act.keys(),self._mod.keys()]), f"'{attr}' not found in module '{self.name}'"
        if attr in self._var.keys() : return self._var[attr]
        elif attr in self._act.keys() : return self._act[attr]
        elif attr in self._mod.keys() : return self._mod[attr]
        
        
    def info(self):
        
        display = f'Module {self.name}\n'
        display += '-'*(len(display)-1)+'\n'
        
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
        
        print(display)
        
        
    def __dir__(self):
        """ For auto-completion """
        return self.getModuleList() + self.getVariableList() + self.getActionList() + ['info']
    
    def _acquire(self):
        self._parent._acquire()
        
    def _release(self):
        self._parent._release()


        



class Device(Module):
    
    def __init__(self,manager,name):
        
        Module.__init__(self,None,name)

        self._manager = manager
        self._instance = None
        self._lock = threading.Lock()
        
        

        
    def _setInstance(self,instance):
        self._instance = instance
                
    def close(self):
        try : self._instance.close()
        except : pass
        self._instance = None
        
        
    def _acquire(self):
        self._lock.acquire()
        
    def _release(self):
        self._lock.release()   
        
    def reload(self):
        self.close()
        self._manager._load(self.name)
        
    def __dir__(self):
        """ For auto-completion """
        return  self.getModuleList() + self.getVariableList() + self.getActionList() + ['reload','close','info']
 
        
    

        
        
class Variable:
    
    _elementType = 'Variable'
    getAddress = getAddress
    
    def __init__(self,parent,name,varType,**kwargs):
        
        self._parent = parent
        
        assert isinstance(name,str), f"Variable names have to be str values"        
        self.name = name
        
        self.type = varType
        
        self.readFunction = None
        self.writeFunction = None
        self.unit = None
                
        for key,value in kwargs.items() :
            if key == 'setFunction' :
                assert inspect.ismethod(value), f"The SET function provided for the variable {self.name} is not a function"
                self.writeFunction = value
            elif key == 'getFunction' :
                assert inspect.ismethod(value), f"The GET function provided for the variable {self.name} is not a function"
                self.readFunction = value
            elif key == 'unit' :
                assert isinstance(value,str), f"The UNIT value has to be a str object"
                self.unit = value
                
        # Properties
        self.writable = self.writeFunction is not None
        self.readable = self.readFunction is not None
        self.numerical = self.type in [int,float]
        self.parameterAllowed = self.writable and self.numerical
            
        # Lock    
        self._lock = threading.Lock()
        
        # Signals for GUI
        self._readSignal = None
        self._writeSignal = None
        
        
    def save(self,path):
        assert self.readable, f"The variable {self.name} is not configured to be measurable"
        result = self()
        save(self,result,path)
        
        
        
    def info(self):
        display = f'Variable {self.name}\n'
        display += '-'*(len(display)-1)+'\n'
        if self.readable is True : display+=f'Readable ({self.readFunction.__name__})\n'
        else : display+=f'Not readable\n'
        if self.writable is True : display+=f'Writable ({self.writeFunction.__name__})\n'
        else : display+=f'Not writable\n'
        if self.unit is not None : display+=f'Unit : {self.unit}\n'
        else : display+=f'No unit\n'
        print(display)
    



    def __call__(self,value=None):
                
        self._parent._acquire()
        # GET FUNCTION
        if value is None:
            try : 
                assert self.readable, f"The variable {self.name} is not configured to be measurable"
                answer = self.readFunction()
                if self._readSignal is not None : self._readSignal.emit(answer)
                self._parent._release()
                return answer
            except Exception as e :
                self._parent._release()
                raise ValueError(f'An error occured while reading variable {self.name} : {str(e)}')
            
        # SET FUNCTION
        else : 
            try : 
                assert self.readable, f"The variable {self.name} is not configured to be set"
                self.writeFunction(value)
                if self._writeSignal is not None : self._writeSignal.emit()
                self._parent._release()
            except Exception as e :
                self._parent._release()
                raise ValueError(f'An error occured while writing variable {self.name} : {str(e)}')
  
        
def save(variable,result,path):
    
    if variable.type in [int,float,bool,str]:
        with open(path,'w') as f : f.write(str(result))
    elif isinstance(result,np.ndarray) :
        np.savetxt(path,result)
    elif isinstance(result, pd.DataFrame):
        result.to_csv(path,index=False)
    else :
        raise ValueError("The variable {variable.name} of type {variable.type} cannot be saved.")        
        
        
class Action:
    
    _elementType = 'Action'
    getAddress = getAddress
    
    def __init__(self,parent,name,**kwargs):
        
        self._parent = parent
        
        assert isinstance(name,str), f"Action names have to be str values"        
        self.name = name
        
        self.function = None
        
        for key,value in kwargs.items() :
            if key == 'function' :
                assert inspect.ismethod(value), f"The function provided for the variable {self.name} is not a function"
                self.function = value

        # Lock            
        self._lock = threading.Lock()
        
        

        
        
    def info(self):
        display = f'Action {self.name}\n'        
        display += '-'*(len(display)-1)+'\n'
        if self.function is not None : display+=f'Function : {self.function.__name__}\n'
        print(display)
        
    
    def __call__(self):
        # DO FUNCTION
        try : 
            assert self.function is not None, f"The action {self.name} is not configured to be actionable"
            self._parent._acquire()
            self.function()
            self._parent._release()
        except Exception as e :
            self._parent._release()
            raise ValueError(f'An error occured while executing action {self.name} : {str(e)}')
            
    
