# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 21:03:46 2019

@author: qchat
"""
from threading import Thread, Event
from autolab.core import elements
import collections
import itertools
import os
import time
import h5py

class Scanner :
    
    def __init__(self):
        
        self._parameters = collections.OrderedDict()
        self._recipe = collections.OrderedDict()
        self._initrecipe = collections.OrderedDict()
        self._endrecipe = collections.OrderedDict()
    
        self._name = 'scan'
        self._datapath = os.path.realpath('./')
        
        self._thread = None
        self.verbose = False
        
        
    # Utilities
    # =========================================================================
    
    def _check_item_name(self,name):
        try : 
            assert name not in self._parameters.keys()
            assert name not in self._initrecipe.keys()
            assert name not in self._recipe.keys()
            assert name not in self._endrecipe.keys()
        except :
            raise ValueError(f"Item '{name}' already exists.")
            
    
    def _check_modif_allowed(self):
        assert self._thread is None, f"Scan is running, stop it first to modify it."

            
    def clear(self):
        for obj_name in ['parameters','initrecipe','recipe','endrecipe']:
            self._clear_object(obj_name)

    def _add_item(self,obj_name,item_name,item):
        self._check_modif_allowed()
        self._check_item_name(item_name)
        getattr(self, f'_{obj_name}')[item_name] = item
        
    def _clear_object(self,obj_name):
        self._check_modif_allowed()
        setattr(self, f'_{obj_name}', collections.OrderedDict())
            
        
        
    # Paths
    # =========================================================================
    
    def set_datapath(self,path):
        self._check_modif_allowed()
        path = os.path.realpath(path)
        assert os.path.exists(path), "This path doesn't exists."
        self._datapath = path
        
    def get_datapath(self):
        return self._datapath
    
    
    
    
    # Scan name
    # =========================================================================
    
    def set_name(self,name):
        self._check_modif_allowed()
        self._name = name
        
    def get_name(self,name):
        return self._name


        
    # Parameters and recipe
    # =========================================================================
        
    def add_parameter(self, param_name, parameter):
        assert isinstance(parameter,Parameter), "Wrong object type"
        self._add_item('parameters', param_name, parameter)
        
    def add_recipe_step(self, step_name, step):
        assert isinstance(step,(Measure,Set,Execute,Wait)), "Wrong object type"
        self._add_item('recipe', step_name, step)
    
    def add_init_recipe_step(self, step_name, step):
        assert isinstance(step,(Measure,Set,Execute,Wait)), "Wrong object type"
        self._add_item('initrecipe', step_name, step)
     
    def add_end_recipe_step(self, step_name, step):
        assert isinstance(step,(Measure,Set,Execute,Wait)), "Wrong object type"
        self._add_item('endrecipe', step_name, step)
        
    
    def clear_parameters(self):
        self._clear_object('parameters')

    def clear_recipe(self):
        self._clear_object('recipe')

    def clear_init_recipe(self):
        self._clear_object('intirecipe')

    def clear_end_recipe(self):
        self._clear_object('endrecipe')
    
    
    
    
    
    # Structure
    # =========================================================================
    
    def show_configuration(self):
        
        ''' Prints the current configuration of the scan '''
        
        # Init recipe
        print()
        if len(self._initrecipe) == 0 : print("No init recipe\n"+'='*len('No init recipe'))
        else : 
            print('Init recipe:\n'+'='*len('Init recipe:'))
            i = 1
            for name in self._initrecipe.keys() :
                print(f' {i}) {name}: {self._initrecipe[name].info()}')
                i += 1
                
        # Parameters
        indent = 0
        print()
        if len(self._parameters) == 0 : print("No parameters\n"+'='*len('No parameters'))
        else : 
            print('Parameters:\n'+'='*len('Parameters:'))
            for name in self._parameters.keys() :
                print("   "*indent+f' - {name}: {self._parameters[name].info()}')
                indent += 1
        
        # Recipe
        indent += 1
        print()
        if len(self._recipe) == 0 : print("   "*indent+"No recipe\n"+"   "*indent+'='*len('No recipe'))
        else : 
            print("   "*indent+'Recipe:\n'+"   "*indent+'='*len('Recipe:'))
            i = 1
            for name in self._recipe.keys() :
                print("   "*indent+f' {i}) {name}: {self._recipe[name].info()}')
                i += 1
                
        # End recipe
        print()
        if len(self._endrecipe) == 0 : print("No end recipe\n"+'='*len('No end recipe'))
        else : 
            print('End recipe:\n'+'='*len('End recipe:'))
            i = 1
            for name in self._endrecipe.keys() :
                print(f' {i}) {name}: {self._endrecipe[name].info()}')
                i += 1
        
        
       
        
        
        
    # Scan state
    # =========================================================================
        
    def start(self):
        
        ''' Start a new scan '''
        
        assert self._thread is None, f'The scan is already running'
        self._thread = ScanThread(self)
        self._thread.start()
        if self.verbose : print('Scan started')
        
        
        
    def stop(self):
        
        ''' Stop the ongoing scan '''
        
        assert self._thread is not None, f'The scan is not running.'
        self._thread.stop_event.set()
        self._thread.join()
        self._thread = None
        if self.verbose : print('Scan stopped')
        
        
        
    def pause(self):
        
        ''' Pause the ongoing scan '''
        
        assert self._thread is not None, f'The scan is not running.'
        self._thread.pause_event.set()
        print('Scan paused')
        
        
        
    def resume(self):
        
        ''' Resume the ongoing scan '''
        
        assert self._thread is not None, f'The scan is not running.'
        self._thread.pause_event.clear()
        print('Scan resumed')
        
        
        
        
        
        
        
class ScanThread(Thread):
    
    def __init__(self,scanner):
        
        self.scanner = scanner
        Thread.__init__(self)
        
        # Itertools product on parameters
        self.param_sets = list(dict(zip(self.scanner._parameters.keys(),x)) for x in itertools.product(*[a.values for a in self.scanner._parameters.values()]) )
            
        # Pause and stop events
        self.stop_event = Event()
        self.pause_event = Event()
        
        # Current data
        self.data = collections.OrderedDict()
        
        # Prepare datafile
        self.prepare_datafile()
        
        
        
    def prepare_datafile(self):
        
        ''' Find a unique name for the datafile and initialize it size and name 
        of parameters and step names '''
        
         # Create a unique name for the datafile
        suffix = ''
        count = 0
        while os.path.exists(os.path.join(self.scanner._datapath,self.scanner._name+suffix+'.hdf5')) :
            count += 1
            suffix = f'_{count}'
        self.datapath = os.path.join(self.scanner._datapath,self.scanner._name+suffix+'.hdf5')

        # Prepare structure
        def configure(file,obj,data_length):
            for key in obj.keys(): 
                if isinstance(obj[key],(Parameter,Measure)) :
                    file.create_dataset(key, (data_length,))     
        with h5py.File(self.datapath, "a") as file :
            configure(file,self.scanner._initrecipe,1)
            configure(file,self.scanner._parameters,len(self.param_sets))
            configure(file,self.scanner._recipe,len(self.param_sets))
            configure(file,self.scanner._endrecipe,1)



    def run(self):
        
        ''' Start the execution of the scan '''
        
        # Init recipe
        self.reset_data()
        self.execute_recipe(self.scanner._initrecipe)
        
        # Main recipe of each set of parameter
        self.reset_data()
        for i in range(len(self.param_sets)) :
            self.set_parameters(i)
            self.execute_recipe(self.scanner._recipe,i)
            
        # End recipe
        self.reset_data()
        self.execute_recipe(self.scanner._endrecipe)
        
        
        
    def reset_data(self):
        
        ''' Reset the self.data dictionnary '''
        
        self.data = collections.OrderedDict()
        
        
        
    def execute_recipe(self,recipe,i=0):
        
        """ Execute the given recipe for the i-th time """
        
        for key in recipe.keys() :
            
            # If the scan has not been stopped
            if self.stop_event.is_set() is False :
                
                # Execute step
                step = recipe[key]
                ans = step.execute()
                if ans is not None :
                    self.data[key] = ans
                if self.scanner.verbose : print(key, step.info(), ans)
                
                # If scan is paused, wait for resume
                while self.pause_event.is_set() :
                    time.sleep(0.1)
              
            # If the scan has been stopped
            else :
                break
        
        # Save data
        if self.stop_event.is_set() is False :
            self.save_data(i)
        
        
        
    def set_parameters(self,i):
        
        """ Apply the i-th set of parameters """
        
        param_set = self.param_sets[i]
        
        for key in param_set.keys() :
            
            # If the scan has not been stopped
            if self.stop_event.is_set() is False :
                
                value = param_set[key]
                if key not in self.data.keys() or value != self.data[key] : 
                    parameter = self.scanner._parameters[key]
                    parameter.element(param_set[key])
                    self.data[key] = value
                    if self.scanner.verbose : print(key, parameter.info(), value)
                    
                # If scan is paused, wait for resume
                while self.pause_event.is_set() :
                    time.sleep(0.1)
        
            # If the scan has been stopped
            else :
                break
            
        # Save data
        if self.stop_event.is_set() is False :
            self.save_data(i)
        
        
    
    def save_data(self,i=0):
        
        """ Save in the whole content of the current self.data dictionnary 
        in the hdf5 datafile """
        
        with h5py.File(self.datapath, "a") as file :
            for key in self.data.keys():
                file[key][i] = self.data[key]
        if self.scanner.verbose : print('Saving data')
            
        
        
        
        
        
        
        
        
        
        
        
        
# PARAMETERS AND STEPS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        
class Parameter:
    
    ''' Class dedicated to parameter declaration '''
    
    def __init__(self,element,values):
        assert isinstance(element,elements.Variable), "A parameter must be a Variable"
        assert element.writable is True, f"SET step: Variable {element.address()} is not writable."
        self.element = element
        assert hasattr(values, '__iter__'), "Parameter values must be iterable"
        self.values = values  
        
    def info(self):
        return f"Sweep parameter {self.element.address()} with {len(self.values)} values."
        
        
        
        
class Execute:
    
    ''' Scan step dedicated to execute an Action '''
    
    def __init__(self,element,value=None):
        assert isinstance(element,elements.Action), "EXECUTE step element must be an Action."
        self.element = element
        self.value = None
        if value is not None :
            assert element.has_parameter is True, f"EXECUTE step: element {element.address()} has no parameter."
            try : value = element.type(value)
            except : raise ValueError(f'EXECUTE step: value must be of type {element.type}.')
            self.value = value
    
    def info(self):
        if self.value is None : return f'Execute action {self.element.address()}.'
        else : return f'Execute action {self.element.address()} with value {self.value}.'
        
    def execute(self):
        if self.value is None : self.element()
        else : self.element(self.value)






class Set:
    
    ''' Scan step dedicated to set the value of a Variable '''
    
    def __init__(self,element,value):
        assert isinstance(element,elements.Variable), "SET step element must be a Variable."
        assert element.writable is True, f"SET step: Variable {element.address()} is not writable."
        self.element = element
        try : value = element.type(value)
        except : raise ValueError(f'SET step: value must be of type {element.type}.')
        self.value = value
        
    def info(self):
        return f'Set variable {self.element.address()} with value {self.value}.'
        
    def execute(self):
        self.element(self.value)
        
        
        
        
        
class Measure:
    
    ''' Scan step dedicated to measure a Variable '''

    def __init__(self,element):
        assert isinstance(element,elements.Variable), "MEASURE step element must be a Variable."
        assert element.readable is True, f"MEASURE step: Variable {element.address()} is not readable."
        self.element = element
        
    def info(self):
        return f'Measure variable {self.element.address()}.'
        
    def execute(self):
        return self.element()





class Wait:
    
    ''' Scan step dedicated to pause the scan from a certain amount of time '''
    
    def __init__(self,delay):
        try : delay = float(delay)
        except : raise ValueError('WAIT step delay must be numerical.')
        self.delay = delay
        
    def info(self):
        return f'Wait {self.value} seconds.'
        
    def execute(self):
        time.sleep(self.delay)
 
    
    
# Futures classes, to be defined
 
#class WaitUser:
#    
#    def __init__(self):
#        
#        
#    
#class SendEmail:
#    
#    def __init__(self, address, message):
#        
#        
#       
#class While:
#    
#    def __init__(self, element, '<', value):
#        
#    def execute():
#        while()
#        
        

