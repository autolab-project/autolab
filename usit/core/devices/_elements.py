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
    
    """ Returns the address of the given element """

    address = [item.name]
    parent = item._parent
    while parent is not None : 
        address.append(parent.name)
        parent = parent._parent
    return '.'.join(address[::-1])
    


class Module():
    
    _elementType = 'Module'
    getAddress = getAddress
    
    def __init__(self,parent):
        
        self.name = None
        self._parent = parent   
        self.instance = None
        self._mod = {}
        self._var = {}
        self._act = {}
        self._help = None


    def cleanString(self,name):
    
        """ This function clears the given name from special characters """
        
        for character in '*."/\[]:;|, ' :
            name = name.replace(character,'')
        return name   
    
    
    def load(self,instance):
        
        self.instance = instance
        config = self.instance.getDriverConfig()
        assert isinstance(config,list), f"Module {self.name} configuration: 'getUsitConfig' output must be a list of dictionnaries"
        for configPart in config : 
            
            # General check
            assert isinstance(configPart,dict), f"Module {self.name} configuration: 'getUsitConfig' output must be a list of dictionnaries"
            
            # Name check
            assert 'name' in configPart.keys(), f"Module {self.name} configuration: missing 'name' key in one dictionnary"
            assert isinstance(configPart['name'],str), f"Module {self.name} configuration: elements names must be a string"
            name = self.cleanString(configPart['name'])
            assert name != '', f"Module {self.name}: elements names cannot be empty"
        
            # Element type check
            assert 'element' in configPart.keys(), f"Module {self.name}, Element {name} configuration: missing 'element' key in the dictionnary"
            assert isinstance(configPart['element'],str), f"Module {self.name}, Element {name} configuration: element type must be a string"
            elementType = configPart['element']
            assert elementType in ['module','variable','action'], f"Module {self.name}, Element {name} configuration: Element type has to be either 'module','variable' or 'action'"
            
            if elementType == 'module' :
                
                # Check name uniqueness
                assert name not in self.getNames(), f"Module {self.name}, Submodule {name} configuration: '{name}' already exists"
                
                # Check object
                assert 'object' in configPart.keys(), f"Module {self.name}, Submodule {name} configuration: Missing module object"
            
                mod = Module(self)
                mod.name = name
                
                # Help
                if 'help' in configPart.keys():
                    assert isinstance(configPart['help'],str), f"Module {self.getAddress()} configuration: Info parameter must be a string"
                    mod._help = configPart['help']
                
                mod.load(configPart['object'])
                self._mod[name] = mod
                
            elif elementType == 'variable':
                
                # Check name uniqueness
                assert name not in self.getNames(), f"Module {self.name}, Variable {name} configuration: '{name}' already exists"
                
                var = Variable(self,configPart)
                self._var[name] = var
                
            elif elementType == 'action' :
                
                # Check name uniqueness
                assert name not in self.getNames(), f"Module {self.name}, Action {name} configuration: '{name}' already exists"
                
                act = Action(self,configPart)
                self._act[name] = act



    def getModule(self,name):
        
        """ Returns the submodule of the given name """
        
        assert name in self._mod.keys(), f"The submodule '{name}' does not exist in module {self.name}"
        return self._mod[name]
    
    
    
    def getModuleList(self):
        
        """ Returns a list with the names of all existing submodules """
        
        return list(self._mod.keys())
    
    
    
    def getVariable(self,name):
        
        """ Returns the variable with the given name """
        
        assert name in self._var.keys(), f"The variable '{name}' does not exist in module {self.name}"
        return self._var[name]
    
    
    
    def getVariableList(self):
        
        """ Returns a list with the names of all existing variables attached to this module """
        
        return list(self._var.keys())
    
    
    
    def getAction(self,name):
        
        """ Returns the action with the given name """
        
        assert name in self._dev.keys(), f"The action '{name}' does not exist in device {self.name}"
        return self._dev[name]
    
    
    
    def getActionList(self):
        
        """ Returns a list with the names of all existing actions attached to this module """
        
        return list(self._act.keys())
    
    
    def getNames(self):
        return list(self._mod.keys()) + list(self._var.keys()) + list(self._act.keys())

    def __getattr__(self,attr):
        assert any(attr in x for x in [self._var.keys(),self._act.keys(),self._mod.keys()]), f"'{attr}' not found in module '{self.name}'"
        if attr in self._var.keys() : return self._var[attr]
        elif attr in self._act.keys() : return self._act[attr]
        elif attr in self._mod.keys() : return self._mod[attr]
        
        
        
    def help(self):
        
        """ This function prints informations for the user about the availables 
        submodules, variables and action attached to the current module """
        
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
        
        if self._help is not None : display+=f'Help: {self._help}\n'
        
        print(display)
        
        
        
    def __dir__(self):
        
        """ For auto-completion """
        
        return self.getModuleList() + self.getVariableList() + self.getActionList() + ['info','instance']
    
    
    
    def _acquire(self):
        
        """ Acquire the lock of the device """
        
        self._parent._acquire()
        
    def _release(self):
        
        """ Release the lock of the device """

        self._parent._release()


        
        
        



class Device(Module):
    
    def __init__(self,manager,name):
        
        Module.__init__(self,None)

        self._manager = manager
        self.name = name
        self._lock = threading.Lock()
        
        
        
    def close(self):
        
        """ This function close the connection of the current physical device """
        
        try : self.instance.close()
        except : pass
        self.instance = None
        
        
        
    def _acquire(self):
        
        """ Acquire the lock of the device """
        
        self._lock.acquire()
        
        
        
    def _release(self):
        
        """ Release the lock of the device """
        
        self._lock.release()   
        
        
        
    def reload(self):
        
        """ Close and setup a new connection to the physical device """
        
        self.close()
        self._manager._load(self.name)
        
        
        
    def __dir__(self):
        
        """ For auto-completion """
        
        return  self.getModuleList() + self.getVariableList() + self.getActionList() + ['reload','close','info']
 
        
    



        
        
class Variable:
    
    _elementType = 'Variable'
    getAddress = getAddress
    
    def __init__(self,parent,config):
        
        self._parent = parent
        self.name = config['name']
        
        # Type
        assert 'type' in config.keys(), f"Variable {self.getAddress()}: Missing variable type"
        assert config['type'] in [int,float,bool,str,bytes,pd.DataFrame,np.ndarray], f"Variable {self.getAddress()} configuration: Variable type not supported in usit"
        self.type = config['type']
        
        # Read and write function
        assert 'read' in config.keys() or 'write' in config.keys(), f"Variable {self.getAddress()} configuration: no 'read' nor 'write' functions provided"
        
        # Read function
        self.readFunction = None
        if 'read' in config.keys():
            assert inspect.ismethod(config['read']), f"Variable {self.getAddress()} configuration: Read parameter must be a function"
            self.readFunction = config['read']
            
        # Write function
        self.writeFunction = None
        if 'write' in config.keys():
            assert inspect.ismethod(config['write']), f"Variable {self.getAddress()} configuration: Write parameter must be a function"
            self.writeFunction = config['write']
        
        # Unit
        self.unit = None
        if 'unit' in config.keys():
            assert isinstance(config['unit'],str), f"Variable {self.getAddress()} configuration: Unit parameter must be a string"
            self.unit = config['unit']
            
        # Help
        self._help = None
        if 'help' in config.keys():
            assert isinstance(config['help'],str), f"Variable {self.getAddress()} configuration: Info parameter must be a string"
            self._help = config['help']
                
        # Properties
        self.writable = self.writeFunction is not None
        self.readable = self.readFunction is not None
        self.numerical = self.type in [int,float]
        self.parameterAllowed = self.writable and self.numerical
                
        # Signals for GUI
        self._readSignal = None
        self._writeSignal = None
        
        
        
    def save(self,path):
        
        """ This function measure the variable and saves its value in the provided path """
        
        assert self.readable, f"The variable {self.name} is not configured to be measurable"
        result = self()
        save(self,result,path)
        
        
        
    def help(self):
        
        """ This function prints informations for the user about the current variable """
        
        display = f'Variable {self.name}\n'
        display += '-'*(len(display)-1)+'\n'
        if self.readable is True : display+=f'Readable ({self.readFunction.__name__})\n'
        else : display+=f'Not readable\n'
        if self.writable is True : display+=f'Writable ({self.writeFunction.__name__})\n'
        else : display+=f'Not writable\n'
        if self.unit is not None : display+=f'Unit: {self.unit}\n'
        else : display+=f'No unit\n'
        if self._help is not None : display+=f'Help: {self._help}\n'
        print(display)
    


    def __call__(self,value=None):
        
        """ Measure or set the value of the variable """
                
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
                assert self.writable, f"The variable {self.name} is not configured to be set"
                self.writeFunction(value)
                if self._writeSignal is not None : self._writeSignal.emit()
                self._parent._release()
            except Exception as e :
                self._parent._release()
                raise ValueError(f'An error occured while writing variable {self.name} : {str(e)}')
  
        
        

   
    
    
    
        
class Action:
    
    _elementType = 'Action'
    getAddress = getAddress
    
    def __init__(self,parent,config):
        
        self._parent = parent
        self.name = config['name']
        
        # Do function
        assert 'do' in config.keys(), f"Action {self.getAddress()}: Missing 'do' function"
        assert inspect.ismethod(config['do']), f"Action {self.getAddress()} configuration: Do parameter must be a function"
        self.function = config['do'] 
        
        # Help
        self._help = None
        if 'help' in config.keys():
            assert isinstance(config['help'],str), f"Action {self.getAddress()} configuration: Info parameter must be a string"
            self._help = config['help']
        
        
    def help(self):
        
        """ This function prints informations for the user about the current variable """
        
        display = f'Action {self.name}\n'        
        display += '-'*(len(display)-1)+'\n'
        display+=f'Function : {self.function.__name__}\n'
        if self._help is not None : display+=f'Help: {self._help}\n'
        print(display)
        
    
    
    def __call__(self):
        
        """ Executes the action """
        
        # DO FUNCTION
        try : 
            assert self.function is not None, f"The action {self.name} is not configured to be actionable"
            self._parent._acquire()
            self.function()
            self._parent._release()
        except Exception as e :
            self._parent._release()
            raise ValueError(f'An error occured while executing action {self.name} : {str(e)}')
            
    
        
        
        
        
        
def save(variable,result,path):
    
    """ This function saves the value of a variable in the provided path """
    
    if variable.type in [int,float,bool,str]:
        with open(path,'w') as f : f.write(str(result))
    elif variable.type == bytes :
        with open(path,'wb') as f : f.write(result)
    elif variable.type == np.ndarray :
        np.savetxt(path,result)
    elif variable.type == pd.DataFrame :
        result.to_csv(path,index=False)
    else :
        raise ValueError("The variable {variable.name} of type {variable.type} cannot be saved.")        
        
        