# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""

from usit import devices
from ..devices.devices import Action,Variable
from threading import Thread,Event
import time
import numpy as np
import pandas as pd
import pickle
import os






        
        
_scanMaster = None
_scanRunningFlag = Event()
_scanRunningFlag = Event()
_scanNotPausedFlag = Event()

_scanStopping = Event()
        


def getUniqueName(self,basename,existList):
    if basename not in existList() :
        return basename
    else :
        compt = 1
        while basename+'_'+str(compt) in existList :
            compt+=1
        return basename+'_'+str(compt)       
        





class Scan():
    def __init__(self,name=None):
        
        self.data = ScanDatasetManager()
        
        # Naming 
        assert name is None or isinstance(name,str)
        if name is None : name = 'scan'
        self.name=name
        
        self.recipe_init = Recipe(self)
        self.parameter = Parameter(self) 
        self.recipe_loop = Recipe(self)
        self.recipe_end = Recipe(self)
        
        self._thread = None
        
        self.error = None

            
    # State and details
    # =========================================================================
    
    def rename(self,name):
        assert isinstance(name,str)
        self.name = name
        
    
    def _getDetails(self):
        txt = ''
        for i in range(len(self._recipe)) :
            item = self._recipe[i]
            if type(item['obj']) is Action : 
                txt += f"{i+1}) {item['name']} : Do {item['obj']._name} from module {item['obj']._module._name}\n"
            elif type(item['obj']) is Variable :
                txt += f"{i+1}) {item['name']} : Measure {item['obj']._name} from module {item['obj']._module._name}\n"
        return txt
    
    def __str__(self):
        return self._getDetails()
        
    def __repr__(self):
        return self._getDetails()
    
    def _isReady(self):
        if not self.recipe_init._isReady(): self.error="Init recipe not ready"
        elif not self.parameter._isReady(): self.error="Parameter not ready"
        elif not self.recipe_loop._isReady(): self.error="Loop recipe not ready"
        elif not self.recipe_end._isReady(): self.error="End recipe not ready"
        else: self.error = None
        return self.error is None
            
                
                
    # Scan
    # =========================================================================
    
    def start(self):
        """ Manually start this scan """
        try : assert not _scanRunningFlag.is_set()
        except :
            if _scanMaster == self : raise ValueError("Scan already started")
            else : raise ValueError("Stop the master scan first")
        assert self._isReady(), self.error
        _scanMaster = self
        _scanRunningFlag.set()
        self._startThread()
         
        
    def pause(self):
        """ Manually pause this scan """
        assert _scanMaster == self, "Stop the master scan first"
        assert _scanRunningFlag.is_set(), 'The scan is not started'
        assert not _scanStopping.is_set(), 'The scan is finishing'
        assert _scanNotPausedFlag.is_set(), 'The scan is already paused'
        _scanNotPausedFlag.clear()
        
        
    def resume(self):
        assert _scanMaster == self, "Stop the master scan first"
        assert _scanRunningFlag.is_set(), 'The scan is not started'
        assert not _scanStopping.is_set(), 'The scan is finishing'
        assert not _scanNotPausedFlag.is_set(), 'The scan is already running'
        _scanNotPausedFlag.set()
        
    def stop(self):
        """ Manually stop this scan """
        assert _scanMaster == self, "Stop the master scan first"
        assert _scanRunningFlag.is_set(), 'The scan is not started'
        assert not _scanStopping.is_set(), 'The scan is already finishing'
        _scanNotPausedFlag.set() # In case the scan is paused
        _scanStopping.set()
        
    def _startThread(self,wait=False):
        self._thread = ScanWorker(self)
        self._thread.start()
        if wait is True : 
            self._thread.join()
            return self.data.getLast()  
        
    # Access data
    # =========================================================================        
    
  # Step 3
    
    
    


class Parameter:
    
    def __init__(self):
        
        self.__dict__['_config'] = {'var':None,
                                    'name':'',
                                    'init':None,
                                    'end':None,
                                    'span':None,
                                    'step':None,
                                    'pts':None,                        
                                    'log':False,
                                    'range':None}
        
        
        self.__dict__['error'] = None
        self.__dict__['_control'] = 'pts'
        
        self._updateConfig()
        
    def __getattr__(self,attr):
        assert attr in self._config.keys(), "Incorrect parameter"
        return self._config[attr]
        
    def __setattr__(self,attr,value):
        if attr in self.__dict__.keys() :
            self.__dict__[attr] = value
        else :
            if attr == 'var' :
                assert type(value) is Variable, "You have to provide a Variable instance"
                self._config['var'] = value
                self._config['name'] = value._name
                self._updateConfig()
            elif attr in ['init','end','step'] :
                assert any([isinstance(value,t) for t in [int,float]]), "Incorrect value type"
                self._config[attr] = value
                if attr == 'step' : self._control='step'
                self._updateConfig()
            elif attr == 'span' :
                assert any([isinstance(value,t) for t in [int,float]]), "Incorrect value type"
                self._config['span'] = value
                if all([self._config[att] is not None for att in ['init','end']]) and self._config['log'] is False :
                    mean = ( self._config['init'] + self._config['end'] ) / 2
                    self._config['init'] = mean - value / 2
                    self._config['end'] = mean + value / 2
                self._updateConfig()                
            elif attr == 'pts' :
                assert isinstance(int(value),int), "Incorrect value type"
                value = int(value)
                assert value > 0, "The number of point has to be positive"
                self._config['pts'] = value
                self._control = 'pts'
                self._updateConfig()
            elif attr == 'log' :
                assert isinstance(value,bool), "Incorrect value type"  
                self._config['log'] = value
                self._updateConfig()
            elif attr == 'name' :
                assert isinstance(value,str), "Incorrect value type"  
                self._config['name'] = value
            elif attr == 'range' :
                assert isinstance(value, np.ndarray), "Custom range has to be a 1D numpy array"
                assert value.ndim == 1, "Custom range has to be a 1D numpy array"
                self._config['range'] = value
                self._control = 'custom'
                self._updateConfig()
            
    def _updateConfig(self):
            
        try :
            
            if self._control == 'custom' : 
                self._config['init'] = None
                self._config['end'] = None
                self._config['span'] = None
                self._config['step'] = None
                self._config['pts'] = None
                return True
            else :            
                assert self._config['init'] is not None, "The init value is not configured"
                assert self._config['end'] is not None, "The end value is not configured"
                if self._config['log'] is True : 
                    assert self._control == 'pts', "In log mode, only the number of points can be changed"
                    assert self._config['init'] > 0, "In log mode, the init value has to be positive"
                    assert self._config['end'] > 0, "In log mode, the end value has to be positive"
                    self._config['range'] = np.logspace(np.log10(self._config['init']),np.log10(self._config['end']),self._config['pts'])
                    self._config['step'] = None
                else : 
                    if self._control == 'pts': #pts
                        assert self._config['pts'] is not None, "The number of point is not configured"
                        self._config['range'],self._config['step'] = np.linspace(self._config['init'],
                                                                                       self._config['end'],
                                                                                       self._config['pts'],
                                                                                       retstep=True)
                    elif self._control == 'step' :
                        assert self._config['step'] is not None, "The step size is not configured"
                        self._config['range'] = np.arange(self._config['init'],
                                                           self._config['end'],
                                                           self._config['step'])
                        self._config['pts'] = len(self._config['range'])
                        
            assert self._config['var'] is not None, "The parameter variable is not configured"
            
            self.error = None            
        
        except Exception as e:
            self.error = str(e)
            
    # Infos 
    #==========================================================================
    def _getDetails(self):
        if self.error is not None : return self.error
        else : 
            txt = "Tuned variable: {self._config['var']}\n"
            
            if self._control == 'custom' : txt += 'Range: custom' 
            for i in range(len(self._recipe)) :
                step = self._recipe[i]
                if type(step.obj) is Action : 
                    txt += f"{i+1}) {step.name} : Do {step.obj._name} from module {step.obj._module._name}\n"
                elif type(step.obj) is Variable :
                    txt += f"{i+1}) {step.name} : Measure {step.obj._name} from module {step.obj._module._name}\n"
            return txt
        
    def __str__(self):
        return self._getDetails()
    
    def __repr__(self):
        return self._getDetails()
    
    def _isReady(self):
        return self.__dict__['error'] is None

    
    
    
    
class Recipe:
    
    def __init__(self):
        
        self._recipe = []
        
    # Infos
    # =========================================================================
        
    def _getNames(self):
        return [step.name for step in self._recipe]
    
    def _getDetails(self):
        txt = ''
        for i in range(len(self._recipe)) :
            step = self._recipe[i]
            if type(step.obj) is Action : 
                txt += f"{i+1}) {step.name} : Do {step.obj._name} from module {step.obj._module._name}\n"
            elif type(step.obj) is Variable :
                txt += f"{i+1}) {step.name} : Measure {step.obj._name} from module {step.obj._module._name}\n"
        return txt
        
    def __str__(self):
        return self._getDetails()
        
    def __repr__(self):
        return self._getDetails()
        
    def _getStep(self,name):
        return [step for step in self._recipe if step.name==name][0]
    
        
    def _isReady(self):
        for step in self._recipe :
            if type(step) is Scan and not step._isReady() : 
                self.error=f"Step {self._recipe.index(step)} (Scan {step.name}) not ready"
                break
            elif type(step) is Recipe and not step._isReady() : 
                self.error=f"Step {self._recipe.index(step)} (Recipe {step.name}) not ready"
                break
            else: self.error = None
        return self.error is None
        
    # Modifications
    # =========================================================================
        
    def append(self,obj,name=None,value=None):
        assert any([type(obj) is t for t in [Variable,Action,Recipe,Scan]]), f"Recipe step has to be a Variable, an Action, another Recipe, or another Scan"    
        if name is None : name = obj._name
        assert name not in self.getNames(), f"Name '{name}' already exists"
        if value is not None : 
            assert isinstance(obj,Variable), "You can provide a value only to set a variable"
            assert isinstance(value,obj._pty['type']), f"The type of the value for variable {obj._getName()} has to be {obj._getType()}"
            self._recipe.append(RecipeStep(name,obj,value=value))
        else :
            self._recipe.append(RecipeStep(name,obj))
        
    def remove(self,name):
        assert name in self.getNames(), f"Recipe step with name '{name}' does not exist"
        step = self._getStep(name)
        self._recipe.remove(step)
        
    def rename(self,name,newName):
        assert name in self.getNames(), f"Recipe step with name '{name}' does not exist"
        assert newName not in self.getNames(), f"Name '{name}' already exists"
        self._getStep(name).rename(newName)
        

        
    




class RecipeStep:
    
    def __init__(self,name,obj,value=None):
        self.name = name 
        self.obj = obj
        self.value = value

    def rename(self,name):
        self.name = name








        
class ScanWorker(Thread):
    
    def __init__(self,scan):
        Thread.__init__(self)
        self.scan = scan
        self.dataset = None
        self.paramValue = None
        
    def runRecipe(self,recipe,recipeType):
        for step in recipe :
            
            # Pause and stop
            _scanNotPausedFlag.wait()
            if _scanStopping.is_set() : break
        
            # Measure
            if isinstance(step.obj,Action) : step.obj.start()
            elif isinstance(step.obj,Variable) : 
                if step.value is None : 
                    step.obj.set(step.value)
                else : ans = step.obj.get()
            elif isinstance(step.obj,Scan) : ans = step.obj._startThread(wait=True)
            
            # Saving
            if isinstance(step.obj,Scan) or (isinstance(step.obj,Variable) and step.value is not None) :
                if recipeType in ('init','end') :
                    getattr(self.dataset,recipeType)[step.name] = ans
                elif recipeType == 'loop' :
                    self.dataset.loop.loc[self.paramValue,step.name] = ans
                    
                
        
    def run(self):
        
        _scanNotPausedFlag.set()
        
        # Dataframe creation
        self.dataset = ScanDataset()
        self.scan.data.append(self.dataset)
        
        # Initialisation
        self.runRecipe(self.scan.recipe_init,'init')
        
        # Scan
        for paramValue in self.scan._parameter['range'] :
            
            # Pause and stop
            _scanNotPausedFlag.wait()
            if _scanStopping.is_set() : break
        
            # Set parameter
            self.scan._parameter['var'].set(paramValue)
            self.paramValue = paramValue
        
            # Execute recipe
            self.runRecipe(self.scan.recipe_loop,'loop')
            
        # Finalisation
        self.runRecipe(self.scan.recipe_end,'end')
                    
        # Auto delete
        self.scan._thread = None
        
        # Scan ending
        if _scanMaster == self.scan :
            _scanStopping.clear()
            _scanNotPausedFlag.clear()
        
        
        
        
        
class ScanDataset :
    
    def __init__(self):
        
        self.ID = time.time()
        self.init = {}
        self.loop = pd.DataFrame()
        self.loop.index.name = self.scan._parameter['name']
        self.end = {}
        

        
        
class ScanDatasetManager :
    
    def __init__(self):
        
        self._data = {}
        
    def append(self,dataset):
        assert isinstance(dataset,ScanDataset)
        self._data[dataset.ID] = dataset
        
    def reset(self):
        self._data = {}
        
    def getListID(self):
        return self._data.keys()
        
    def getLastID(self):
        assert len(self._data)>0, "There is no dataset"
        return max(self.getListID)
    
    def getLast(self):
        return self.get(self.getLastID())
    
    def get(self,ID):
        assert ID in self.getListID(), "ID {ID} not existing"
    
    def save_pickle(self,filePath,ID=None):
        folderPath = os.path.dirname(filePath)
        assert os.path.exists(folderPath), "Folder path doesn't exist"
        if ID is None : ID = self.getLastID()
        dataset = self.get(ID)
        with open(filePath, 'wb') as fileHandle : pickle.dump(dataset, fileHandle)
        
    def save_files(self,filePath,ID=None):
        pass # To be written
        
        
        
        
        
        