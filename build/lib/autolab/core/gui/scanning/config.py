# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:16:09 2019

@author: qchat
"""
from PyQt5 import QtWidgets
import autolab
from autolab import paths
import configparser
import datetime
import os
        
class ConfigManager :
    
    def __init__(self,gui):
        
        self.gui = gui
        
        # Configuration menu
        configMenu = self.gui.menuBar.addMenu('&Configuration')
        self.importAction = configMenu.addAction('Import configuration')
        self.importAction.triggered.connect(self.importActionClicked)
        exportAction = configMenu.addAction('Export current configuration')
        exportAction.triggered.connect(self.exportActionClicked)

        # Initializing configuration values
        self.config = {}
        self.config['parameter'] = {'element':None,'name':None}
        self.config['nbpts'] = 11
        self.config['range'] = (0,10)
        self.config['log'] = False
        self.config['recipe'] = []
        
        
       
    # NAMES
    ###########################################################################
        
    def getNames(self,option=None):
        
        """ This function returns a list of the names of the recipe step and of the parameter """
        
        names = [step['name'] for step in self.config['recipe']]
        if self.config['parameter']['element'] is not None and option != 'recipe': 
            names.append(self.config['parameter']['name'])
        return names
        
    
    
    def getUniqueName(self,basename):
        
        """ This function adds a number next to basename in case this basename is already taken """
        
        names = self.getNames()
        name = basename
        
        compt = 0
        while True :
            if name in names :
                compt += 1
                name = basename+'_'+str(compt)
            else :
                break
        return name
    
    
        
    # CONFIG MODIFICATIONS
    ###########################################################################   
    
    def setParameter(self,element,name=None):
        
        """ This function set the element provided as the new parameter of the scan """
        
        if self.gui.scanManager.isStarted() is False :
            self.config['parameter']['element'] = element
            if name is None : name = self.getUniqueName(element.name)
            self.config['parameter']['name'] = name
            self.gui.parameterManager.refresh()
            self.gui.dataManager.clear()
            
            
            
    def setParameterName(self,name):
        
        """ This function set the name of the current parameter of the scan """
        
        if self.gui.scanManager.isStarted() is False :
            if name != self.config['parameter']['name']:
                name = self.getUniqueName(name)
                self.config['parameter']['name'] = name
                self.gui.dataManager.clear()
        self.gui.parameterManager.refresh()
        
        
        
    def addRecipeStep(self,stepType,element,name=None,value=None):
        
        """ This function add a step to the scan recipe """
        
        if self.gui.scanManager.isStarted() is False :
            
            if name is None : name = self.getUniqueName(element.name)
            step = {'stepType':stepType,'element':element,'name':name,'value':None}
            
            # Value
            if stepType == 'set' : setValue = True
            elif stepType == 'action' and element.type in [int,float,str] : setValue = True
            else : setValue = False
            
            if setValue is True :
                if value is None : 
                    if element.type in [int,float] :
                        value = 0
                    elif element.type in [str] :
                        value = ''
                    elif element.type in [bool]:
                        value = False
                step['value'] = value
            
            self.config['recipe'].append(step)
            self.gui.recipeManager.refresh()
            self.gui.dataManager.clear()
            
            
            
    def delRecipeStep(self,name):
        
        """ This function removes a step from the scan recipe """
        
        if self.gui.scanManager.isStarted() is False :
            pos = self.getRecipeStepPosition(name)
            self.config['recipe'].pop(pos)
            self.gui.recipeManager.refresh()
            self.gui.dataManager.clear()
            
            
    
    def renameRecipeStep(self,name,newName):
        
        """ This function rename a step in the scan recipe """
        
        if self.gui.scanManager.isStarted() is False :
            if newName != name :
                pos = self.getRecipeStepPosition(name)
                newName = self.getUniqueName(newName)
                self.config['recipe'][pos]['name'] = newName
                self.gui.recipeManager.refresh()
                self.gui.dataManager.clear()
                
                
                
    def setRecipeStepValue(self,name,value):
        
        """ This function set the value of a step in the scan recipe """
        
        if self.gui.scanManager.isStarted() is False :
            pos = self.getRecipeStepPosition(name)
            if value != self.config['recipe'][pos]['value'] :
                self.config['recipe'][pos]['value'] = value
                self.gui.recipeManager.refresh()
                self.gui.dataManager.clear()    
                
                
                
    def setRecipeOrder(self,stepOrder):
        
        """ This function reorder the recipe as a function of the list of step names provided """
        
        newOrder = [self.getRecipeStepPosition(name) for name in stepOrder]
        recipe = self.config['recipe']
        self.config['recipe'] = [recipe[i] for i in newOrder]
        self.gui.recipeManager.refresh()
        self.gui.dataManager.clear()  
                
        
                
    def setNbPts(self,value):
        
        """ This function set the value of the number of points of the scan """
        
        if self.gui.scanManager.isStarted() is False :
            self.config['nbpts'] = value
        self.gui.rangeManager.refresh()
        
        
        
    def setRange(self,lim):
        
        """ This function set the range (start and end value) of the scan """
        
        if self.gui.scanManager.isStarted() is False :
            if lim != self.config['range'] :
                self.config['range'] = tuple(lim)
        self.gui.rangeManager.refresh()
        
        
        
    def setLog(self,state):
        
        """ This function set the log state of the scan """
        
        if self.gui.scanManager.isStarted() is False :
            if state != self.config['log']:
                self.config['log'] = state
        self.gui.rangeManager.refresh()
                
            
            
            
    # CONFIG READING
    ###########################################################################

    def getParameter(self):
        
        """ This function returns the element of the current parameter of the scan """
        
        return self.config['parameter']['element']
    
    
    
    def getParameterName(self):
        
        """ This function returns the name of the current parameter of the scan """
        
        return self.config['parameter']['name']
    
    
    
    def getRecipeStepElement(self,name):
        
        """ This function returns the element of a recipe step """
        
        pos =  self.getRecipeStepPosition(name)
        return self.config['recipe'][pos]['element']
            
    
    
    def getRecipeStepType(self,name):
        
        """ This function returns the type a recipe step """

        pos =  self.getRecipeStepPosition(name)
        return self.config['recipe'][pos]['stepType']
    
    
    
    def getRecipeStepValue(self,name):
        
        """ This function returns the value of a recipe step """
        
        pos =  self.getRecipeStepPosition(name)
        return self.config['recipe'][pos]['value']
    
    
    
    def getRecipeStepPosition(self,name):
        
        """ This function returns the position of a recipe step in the recipe """
        
        return [i for i, step in enumerate(self.config['recipe']) if step['name'] == name][0]     
    
    
        
    def getLog(self):
        
        """ This function returns the log state of the scan """
        
        return self.config['log']
    
    
    
    def getNbPts(self):
        
        """ This function returns the number of points of the scan """
        
        return self.config['nbpts']
    
    
    
    def getRange(self):
        
        """ This function returns the range (start and end value) of the scan """
        
        return self.config['range']
    
    
    
    def getRecipe(self):
        
        """ This function returns the whole recipe of the scan """
        
        return self.config['recipe']
    
    
                        
    def getConfig(self):
        
        """ This function returns the whole configuration of the scan """
        
        return self.config
  
    
    
    

    # EXPORT IMPORT ACTIONS
    ###########################################################################

    def exportActionClicked(self):
        
        """ This function prompts the user for a configuration file path, 
        and export the current scan configuration in it """

        path = QtWidgets.QFileDialog.getSaveFileName(self.gui, "Export AUTOLAB configuration file", 
                                                     os.path.join(paths.USER_LAST_CUSTOM_FOLDER,'config.conf'), 
                                                     "AUTOLAB configuration file (*.conf)")[0]

        if path != '' :
            paths.USER_LAST_CUSTOM_FOLDER = path
            
            try : 
                self.export(path)
                self.gui.statusBar.showMessage(f"Current configuration successfully saved at {path}",5000)
            except Exception as e :
                self.gui.statusBar.showMessage(f"An error occured: {str(e)}",10000)
                
                
         
    
    
    def export(self,path):
        
        """ This function exports the curr scan configuration in the provided path """
        
        configPars = configparser.ConfigParser()
        configPars['autolab'] = {'version':autolab.__version__,
                                  'timestamp':str(datetime.datetime.now())}
                
        configPars['parameter'] = {}
        if self.config['parameter']['element'] is not None :
            configPars['parameter']['name'] = self.config['parameter']['name']
            configPars['parameter']['address'] = self.config['parameter']['element'].address()
        configPars['parameter']['nbpts'] = str(self.config['nbpts'])
        configPars['parameter']['start_value'] = str(self.config['range'][0])
        configPars['parameter']['end_value'] = str(self.config['range'][1])
        configPars['parameter']['log'] = str(int(self.config['log']))
        
        configPars['recipe'] = {}
        for i in range(len(self.config['recipe'])) :
            configPars['recipe'][f'{i+1}_name'] = self.config['recipe'][i]['name']
            configPars['recipe'][f'{i+1}_stepType'] = self.config['recipe'][i]['stepType']
            configPars['recipe'][f'{i+1}_address'] = self.config['recipe'][i]['element'].address()
            stepType = self.config['recipe'][i]['stepType']
            if stepType == 'set' or (stepType == 'action' and self.config['recipe'][i]['element'].type in [int,float,str]) :
                value = self.config['recipe'][i]['value']
                if self.config['recipe'][i]['element'].type in [str] :
                    valueStr = f'{value}'
                else :
                    valueStr = f'{value:g}'
                configPars['recipe'][f'{i+1}_value'] = valueStr
                
        with open(path, 'w') as configfile:
            configPars.write(configfile)
            
            
        
    def importActionClicked(self):
        
        """ This function prompts the user for a configuration file path, 
        and import the current scan configuration from it """
        
        path = QtWidgets.QFileDialog.getOpenFileName(self.gui, "Import AUTOLAB configuration file", 
                                                     paths.USER_LAST_CUSTOM_FOLDER,
                                                     "AUTOLAB configuration file (*.conf)")[0]
        if path != '' :
            
            configPars = configparser.ConfigParser()
            configPars.read(path)
            
            try :
            
                assert 'parameter' in configPars
                config = {}
                
                if 'address' in configPars['parameter'] :
                    element = autolab.get_element_by_address(configPars['parameter']['address'])
                    assert element is not None, f"Parameter {configPars['parameter']['address']} not found."
                    assert 'name' in configPars['parameter'], f"Parameter name not found."
                    config['parameter'] = {'element':element,'name':configPars['parameter']['name']}
                    
                
                assert 'recipe' in configPars
                for key in ['nbpts','start_value','end_value','log'] :
                    assert key in configPars['parameter'], "Missing parameter key {key}."
                    config['nbpts'] = int(configPars['parameter']['nbpts'])
                    start = float(configPars['parameter']['start_value'])
                    end = float(configPars['parameter']['end_value'])
                    config['range'] = (start,end)
                    config['log'] = bool(int(configPars['parameter']['log']))                    
                
                
                config['recipe'] = []

                while True :
                    step = {}
                    
                    i = len(config['recipe'])+1
    
                    if f'{i}_name' in configPars['recipe']:
                        
                        step['name'] = configPars['recipe'][f'{i}_name']
                        name = step['name']
                        
                        assert f'{i}_stepType' in configPars['recipe'], f"Missing stepType in step {i} ({name})."
                        step['stepType'] = configPars['recipe'][f'{i}_stepType']
                        
                        assert f'{i}_address' in configPars['recipe'], f"Missing address in step {i} ({name})."
                        address = configPars['recipe'][f'{i}_address']
                        element = autolab.get_element_by_address(address)
                        assert element is not None, f"Address {address} not found for step {i} ({name})."
                        step['element'] = element
                        
                        if step['stepType']=='set' or (step['stepType'] == 'action' and element.type in [int,float,str]) :
                            assert f'{i}_value' in configPars['recipe'], f"Missing value in step {i} ({name})."
                            value = configPars['recipe'][f'{i}_value']
                            if element.type in [int]:
                                value = int(value)
                            elif element.type in [float] :
                                value = float(value)
                            elif element.type in [str] :
                                value = str(value)
                            elif element.type in [bool]:
                                value = int(value)
                                assert value in [0,1]
                                value = bool(value)
                            step['value'] = value
                        else :
                            step['value'] = None
                                                        
                        config['recipe'].append(step)
                        
    
                    else :
                        break
                
                
                self.config = config
                
                self.gui.dataManager.clear()
                self.gui.parameterManager.refresh()
                self.gui.recipeManager.refresh()
                self.gui.rangeManager.refresh()
                
                self.gui.statusBar.showMessage(f"Configuration file loaded successfully",5000)
            
            except Exception as e :
                
                self.gui.statusBar.showMessage(f"Impossible to load configuration file: "+str(e),10000)
            