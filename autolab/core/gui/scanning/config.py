# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:16:09 2019

@author: qchat
"""
import configparser
import datetime
import os

import numpy as np
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon

from ... import paths, devices, config
from .... import __version__


class ConfigHistory:

    def __init__(self):
        self.list = []
        self.index = -1
        # Note: it's normal to have the first data unchangeable by append method
        # use pop if need to remove first data

    def __repr__(self):
        return object.__repr__(self)+"\n\t"+self.list.__repr__()+f"\n\tCurrent data: {self.get_data()}"

    def __len__(self):
        return len(self.list)

    def append(self, data):

        if data is not None:
            if self.index != len(self)-1:  # if in middle remove right indexes
                self.list = self.list[:self.index+1]

            self.index += 1
            self.list.append(data)

    def pop(self):  # OBSOLETE
        if len(self) != 0:
            if self.index == len(self)-1:
                self.index -= 1
            self.list.pop()

    def go_up(self):
        if (self.index+1) <= (len(self)-1):
            self.index += 1

    def go_down(self):
        if self.index-1 >= 0:
            self.index -= 1

    def get_data(self):
        if self.index >= 0:
            return self.list[self.index]


class ConfigManager :

    def __init__(self,gui):

        self.gui = gui

        # Import Autolab config
        scanner_config = config.get_scanner_config()
        self.precision = scanner_config['precision']

        # Configuration menu
        configMenu = self.gui.menuBar.addMenu('Configuration')
        self.importAction = configMenu.addAction('Import configuration')
        self.importAction.setIcon(QIcon.fromTheme("folder-open"))
        self.importAction.triggered.connect(self.importActionClicked)
        exportAction = configMenu.addAction('Export current configuration')
        exportAction.triggered.connect(self.exportActionClicked)
        exportAction.setIcon(QIcon.fromTheme("document-save-as"))

        # Edition menu
        editMenu = self.gui.menuBar.addMenu('Edit')
        self.undo = editMenu.addAction('Undo')
        self.undo.setIcon(QIcon.fromTheme("edit-undo"))
        self.undo.triggered.connect(self.undoClicked)
        self.undo.setEnabled(False)
        self.redo = editMenu.addAction('Redo')
        self.redo.setIcon(QIcon.fromTheme("edit-redo"))
        self.redo.triggered.connect(self.redoClicked)
        self.redo.setEnabled(False)

        # Initializing configuration values
        self.config = {}
        self.config['parameter'] = {'element':None,'name':None}
        self.config['nbpts'] = 11
        self.config['range'] = (0,10)
        self.config['step'] = 1

        self.config['log'] = False
        self.config['recipe'] = []

        self.historic = ConfigHistory()
        self._activate_historic = True


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

    def addNewConfig(self):

        """ Add new config to historic list """

        if self._activate_historic:
            self.historic.append(self.create_configPars())  # BUG: small issue if add recipe or scanrange change without any parameter set

            self.undo.setEnabled(True)
            self.redo.setEnabled(False)


    def setParameter(self,element,name=None):

        """ This function set the element provided as the new parameter of the scan """

        if self.gui.scanManager.isStarted() is False :
            self.config['parameter']['element'] = element
            if name is None : name = self.getUniqueName(element.name)
            self.config['parameter']['name'] = name
            self.gui.parameterManager.refresh()
            self.gui.dataManager.clear()
            self.addNewConfig()


    def setParameterName(self,name):

        """ This function set the name of the current parameter of the scan """

        if self.gui.scanManager.isStarted() is False :
            if name != self.config['parameter']['name']:
                name = self.getUniqueName(name)
                self.config['parameter']['name'] = name
                self.gui.dataManager.clear()
                self.addNewConfig()
        self.gui.parameterManager.refresh()


    def addRecipeStep(self,stepType,element,name=None,value=None):

        """ This function add a step to the scan recipe """

        if self.gui.scanManager.isStarted() is False :

            if name is None : name = self.getUniqueName(element.name)
            step = {'stepType':stepType,'element':element,'name':name,'value':None}

            # Value
            if stepType == 'set' : setValue = True
            elif stepType == 'action' and element.type in [int,float,str,pd.DataFrame,np.ndarray] : setValue = True
            else : setValue = False

            if setValue is True :
                if value is None :
                    if element.type in [int,float] :
                        value = 0
                    elif element.type in [str,pd.DataFrame,np.ndarray] :
                        value = ''
                    elif element.type in [bool]:
                        value = False
                step['value'] = value

            self.config['recipe'].append(step)
            self.gui.recipeManager.refresh()
            self.gui.dataManager.clear()
            self.addNewConfig()


    def delRecipeStep(self,name):

        """ This function removes a step from the scan recipe """

        if self.gui.scanManager.isStarted() is False :
            pos = self.getRecipeStepPosition(name)
            self.config['recipe'].pop(pos)
            self.gui.recipeManager.refresh()
            self.gui.dataManager.clear()
            self.addNewConfig()


    def renameRecipeStep(self,name,newName):

        """ This function rename a step in the scan recipe """

        if self.gui.scanManager.isStarted() is False :
            if newName != name :
                pos = self.getRecipeStepPosition(name)
                newName = self.getUniqueName(newName)
                self.config['recipe'][pos]['name'] = newName
                self.gui.recipeManager.refresh()
                self.gui.dataManager.clear()
                self.addNewConfig()


    def setRecipeStepValue(self,name,value):

        """ This function set the value of a step in the scan recipe """

        if self.gui.scanManager.isStarted() is False :
            pos = self.getRecipeStepPosition(name)
            if value != self.config['recipe'][pos]['value'] :
                self.config['recipe'][pos]['value'] = value
                self.gui.recipeManager.refresh()
                self.gui.dataManager.clear()
                self.addNewConfig()


    def setRecipeOrder(self,stepOrder):

        """ This function reorder the recipe as a function of the list of step names provided """

        if self.gui.scanManager.isStarted() is False :
            newOrder = [self.getRecipeStepPosition(name) for name in stepOrder]
            recipe = self.config['recipe']
            self.config['recipe'] = [recipe[i] for i in newOrder]
            self.gui.dataManager.clear()
            self.addNewConfig()
        self.gui.recipeManager.refresh()


    def setNbPts(self,value):

        """ This function set the value of the number of points of the scan """

        if self.gui.scanManager.isStarted() is False :

            self.config['nbpts'] = value

            if value == 1:
                self.config['step'] = 0
            else:
                xrange = tuple(self.getRange())
                width = abs(xrange[1]-xrange[0])
                self.config['step'] = width / (value-1)
            self.addNewConfig()

        self.gui.rangeManager.refresh()



    def setStep(self,value):

        """ This function set the value of the step between points of the scan """

        if self.gui.scanManager.isStarted() is False :

            self.config['step'] = value

            if value == 0:
                self.config['nbpts'] = 1
                self.config['step'] = 0
            else:
                xrange = tuple(self.getRange())
                width = abs(xrange[1]-xrange[0])
                self.config['nbpts'] = int(round(width/value)+1)
                if width != 0:
                    self.config['step'] = width / (self.config['nbpts']-1)
            self.addNewConfig()

        self.gui.rangeManager.refresh()


    def setRange(self,lim):

        """ This function set the range (start and end value) of the scan """

        if self.gui.scanManager.isStarted() is False :
            if lim != self.config['range'] :
                self.config['range'] = tuple(lim)

            width = abs(lim[1]-lim[0])

            if self.gui.rangeManager.point_or_step == "point":
                self.config['step'] = width / (self.getNbPts()-1)

            elif self.gui.rangeManager.point_or_step == "step":
                self.config['nbpts'] = int(round(width/self.getStep())+1)
                self.config['step'] = width / (self.getNbPts()-1)
            self.addNewConfig()

        self.gui.rangeManager.refresh()


    def setLog(self,state):

        """ This function set the log state of the scan """

        if self.gui.scanManager.isStarted() is False :
            if state != self.config['log']:
                self.config['log'] = state
            self.addNewConfig()
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

        pos = self.getRecipeStepPosition(name)
        return self.config['recipe'][pos]['element']



    def getRecipeStepType(self,name):

        """ This function returns the type a recipe step """

        pos = self.getRecipeStepPosition(name)
        return self.config['recipe'][pos]['stepType']



    def getRecipeStepValue(self,name):

        """ This function returns the value of a recipe step """

        pos = self.getRecipeStepPosition(name)
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



    def getStep(self):

        """ This function returns the value of the step between points of the scan """

        return self.config['step']



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

        filename = QtWidgets.QFileDialog.getSaveFileName(self.gui, "Export AUTOLAB configuration file",
                                                     os.path.join(paths.USER_LAST_CUSTOM_FOLDER,'config.conf'),
                                                     "AUTOLAB configuration file (*.conf);;All Files (*)")[0]

        if filename != '' :
            path = os.path.dirname(filename)
            paths.USER_LAST_CUSTOM_FOLDER = path

            try :
                self.export(filename)
                self.gui.setStatus(f"Current configuration successfully saved at {filename}",5000)
            except Exception as e :
                self.gui.setStatus(f"An error occured: {str(e)}",10000, False)



    def export(self,filename):

        """ This function exports the current scan configuration in the provided file """

        configPars = self.create_configPars()

        with open(filename, 'w') as configfile:
            configPars.write(configfile)


    def create_configPars(self):

        """ This function create the current scan configuration parser """

        configPars = configparser.ConfigParser()
        configPars['autolab'] = {'version':__version__,
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
            if stepType == 'set' or (stepType == 'action' and self.config['recipe'][i]['element'].type in [int,float,str,pd.DataFrame,np.ndarray]) :
                value = self.config['recipe'][i]['value']
                try:
                    valueStr = f'{value:.{self.precision}g}'
                except:
                    valueStr = f'{value}'
                configPars['recipe'][f'{i+1}_value'] = valueStr

        return configPars


    def importActionClicked(self):

        """ This function prompts the user for a configuration filename,
        and import the current scan configuration from it """

        filename = QtWidgets.QFileDialog.getOpenFileName(self.gui, "Import AUTOLAB configuration file",
                                                     paths.USER_LAST_CUSTOM_FOLDER,
                                                     "AUTOLAB configuration file (*.conf);;All Files (*)")[0]
        if filename != '':
            self.import_configPars(filename)

    def import_configPars(self, filename):

        configPars = configparser.ConfigParser()
        try:
            configPars.read(filename)
        except Exception as error:
            self.gui.setStatus(f"Impossible to load configuration file: {error}",10000, False)
            return

        path = os.path.dirname(filename)
        paths.USER_LAST_CUSTOM_FOLDER = path

        self.load_configPars(configPars)

        if self._got_error is False:
            self.addNewConfig()


    def load_configPars(self, configPars):

        self._got_error = False
        self._activate_historic = False
        previous_config = self.config.copy()  # used to recover old config if error in loading new one

        try :

            assert 'parameter' in configPars
            config = {}

            if 'address' in configPars['parameter'] :
                element = devices.get_element_by_address(configPars['parameter']['address'])
                assert element is not None, f"Parameter {configPars['parameter']['address']} not found."
                assert 'name' in configPars['parameter'], "Parameter name not found."
                config['parameter'] = {'element':element,'name':configPars['parameter']['name']}


            assert 'recipe' in configPars
            for key in ['nbpts','start_value','end_value','log'] :
                assert key in configPars['parameter'], "Missing parameter key {key}."
                config['nbpts'] = int(configPars['parameter']['nbpts'])
                start = float(configPars['parameter']['start_value'])
                end = float(configPars['parameter']['end_value'])
                config['range'] = (start,end)
                config['log'] = bool(int(configPars['parameter']['log']))
                if config['nbpts'] > 1:
                    config['step'] = abs(end-start)/(config['nbpts']-1)
                else:
                    config['step'] = 0


            config['recipe'] = []

            while True:
                step = {}

                i = len(config['recipe'])+1

                if f'{i}_name' in configPars['recipe']:

                    step['name'] = configPars['recipe'][f'{i}_name']
                    name = step['name']

                    assert f'{i}_stepType' in configPars['recipe'], f"Missing stepType in step {i} ({name})."
                    step['stepType'] = configPars['recipe'][f'{i}_stepType']

                    assert f'{i}_address' in configPars['recipe'], f"Missing address in step {i} ({name})."
                    address = configPars['recipe'][f'{i}_address']
                    element = devices.get_element_by_address(address)
                    assert element is not None, f"Address {address} not found for step {i} ({name})."
                    step['element'] = element

                    if step['stepType']=='set' or (step['stepType'] == 'action' and element.type in [int,float,str,pd.DataFrame,np.ndarray]) :
                        assert f'{i}_value' in configPars['recipe'], f"Missing value in step {i} ({name})."
                        value = configPars['recipe'][f'{i}_value']

                        try:
                            try:
                                assert self.checkVariable(value) == 0, "Need $eval: to evaluate the given string"
                            except:
                                # Type conversions
                                if element.type in [int]:
                                    value = int(value)
                                elif element.type in [float] :
                                    value = float(value)
                                elif element.type in [str] :
                                    value = str(value)
                                elif element.type in [bool]:
                                    if value == "False": value = False
                                    elif value == "True": value = True
                                    value = int(value)
                                    assert value in [0,1]
                                    value = bool(value)
                                else:
                                    assert self.checkVariable(value) == 0, "Need $eval: to evaluate the given string"
                        except:
                            raise ValueError(f"Error with {i}_value = {value}. Expect either {element.type} or device address. Check address or open device first.")
                        step['value'] = value
                    else:
                        step['value'] = None

                    config['recipe'].append(step)


                else:
                    break


            self.config = config
            self.gui.dataManager.clear()
            self.gui.parameterManager.refresh()
            self.gui.recipeManager.refresh()
            self.gui.rangeManager.refresh()


            self.gui.setStatus("Configuration file loaded successfully",5000)

        except Exception as error:
            self._got_error = True
            self.gui.setStatus(f"Impossible to load configuration file: {error}",10000, False)
            self.config = previous_config

        self._activate_historic = True


    def checkVariable(self, value):

        """ Check if value start with '$eval:'. Will not try to check if variables exists"""

        if str(value).startswith("$eval:"):
            return 0
        else:
            return -1

    # UNDO REDO ACTIONS
    ###########################################################################

    def undoClicked(self):

        """ Undo an action from parameter, recipe or range """

        self.historic.go_down()
        self.changeConfig()


    def redoClicked(self):

        """ Redo an action from parameter, recipe or range """

        self.historic.go_up()
        self.changeConfig()


    def changeConfig(self):

        """ Get config from historic and enable/disable undo/redo button accordingly """

        configPars = self.historic.get_data()

        if configPars is not None:
            self.load_configPars(configPars)

        self.updateUndoRedoButtons()


    def updateUndoRedoButtons(self):

        """ enable/disable undo/redo button depending on historic """

        if self.historic.index == 0:
            self.undo.setEnabled(False)
        else:
            self.undo.setEnabled(True)

        if self.historic.index == len(self.historic)-1:
            self.redo.setEnabled(False)
        else:  # implicit <
            self.redo.setEnabled(True)
