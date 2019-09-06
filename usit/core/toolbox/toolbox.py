# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 19:34:31 2019

@author: qchat
"""

import usit






_elements = []

def getElement(elementName):
    elementList = [ e for e in _elements if e._name == elementName]
    assert len(elementList) == 1, f"Element {elementName} not found"
    return elementList[0]

def getElementNames():
    return [ e._name for e in _elements ]

def _register(element):
    assert element._name not in getElementNames()
    _elements.append(element)







class Experiment :
    
    def __init__(self):
        
        self._recipe = None
        
        self._running = False
        self._paused = False
    
    
    
    
    def isRunning(self):
        return self._running
    
    def run(self):
        assert self._recipe is not None, "Set recipe first"
        assert not self.isRunning(), "Experiment already running"
        
    def stop(self):
        assert self.isRunning(), "Experiment not running"
        

        
    
    def isPaused(self):
        return self._paused
        
    def pause(self):
        assert self.isRunning(), "Experiment not running"
        assert not self.isPaused(), "Experiment already paused"
        self._paused = True
        
    def resume(self):
        assert self.isRunning(), "Experiment not running"
        assert self.isPaused(), "Experiment not paused"
        self._paused = False
        


    
    def setRecipe(self,recipe):
        assert isinstance(recipe,Recipe), "Recipe object required"
        assert not self.isRunning(), "Stop the experiment first"
        self._recipe = recipe
        
        
        
# ELEMENTS
# =============================================================================
        
        
class Recipe :
    
    def __init__(self,name=None):
        
        self._name = _getUniqueName(self,name)
        _register(self)
        
        self._elements = []
        
        
    def addElement(self,element):
        assert any([isinstance(element,elementType) for elementType in [Recipe,Scan,Measure,Set,Do,Loop]]), "Wrong element type"
        self._elements.append(element)
        
    def getElementNames(self):
        return [ e._name for e in self._elements ]
    
    def getElement(self,elementName):
        assert elementName in self.getElementNames(), f"Element {elementName} not found"
        return [ e for e in self._elements if e._name == elementNames ][0]
    
    def delElement(self,elementName):
        element = self.getElement(elementName)
        del self._elements.remove(element)
        
    def moveElementUp(self,elementName):
        element = self.getElement(elementName)
        i = self._elements.index(element)
        if i>0:
            self._elements[i-1],self._elements[i]=self._elements[i],self._elements[i-1]
        
    def moveElementDown(self,elementName):
        element = self.getElement(elementName)
        i = self._elements.index(element)
        if i<(len(self._elements)-1):
            self._elements[i+1],self._elements[i]=self._elements[i],self._elements[i+1]
        
    def _execute(self,elementName):
        pass
        
        
class Scan :
    
    def __init__(self,parameter,recipe,name=None):
        pass
        
    def setStopCondition(self,condtion,value):
        pass
        
    def _execute(self):
        pass
        

class Loop :
    
    def __init__(recipe,name=None):
        pass
        
    def _execute():
        pass
    
    def setStopCondition(self,condtion,value):
        pass
        
        
        
        
class Measure :
    
    def __init__(self,variable,name=None):
        pass
        
    def _execute(self):
        pass
        

class Set :
    
    def __init__(self,variable,name=None):
        pass
        
    def _execute(self):
        pass
        
        
        
class Do :
    
    def __init__(self,action,name=None):
        pass
        
    def _execute(self):
        pass
        
        
        
class Parameter :
    
    def __init__(self,variable,name=None):
        pass
        
    def setInitValue(self,value):
        pass
        
    def getInitValue(self):
        pass
        
    def setEndValue(self,value):
        pass
        
    def getEndValue(self):
        pass
        
    def setNbPoints(self,value):
        pass
        
    def getNbPoints(self):
        pass
        
    def setStep(self,value):
        pass
        
    def getStep(self):
        pass
        
    def setScale(self,scale):
        pass
        
    def getScale(self):
        pass
        
    def setValues(self,values):
        pass
        
    def getValues(self):
        pass
        
    def _execute(self):
        pass
        
    def _reset(self):
        pass
        
    def _setStopFlag(self):
        pass
        
        
def _getUniqueName(obj,basename):
    
    # BASENAME GENERATION
    if basename is None :
        if isinstance(obj,Recipe):
            basename = 'recipe'
    
    # UNIQUE NAME GENERATION
    elementNames = getElementNames()
    if basename not in elementNames : 
        name = basename
    else :
        count = 1
        while True :
            name = basename+'_'+str(count)
            if name not in elementNames : break
            else : count += 1
        
    return name
    
    