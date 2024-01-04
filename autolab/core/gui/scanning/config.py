# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:16:09 2019

@author: qchat
"""
import configparser
import json
import datetime
import os
import math as m
from typing import Tuple, Any
import collections

import numpy as np
import pandas as pd
from qtpy import QtWidgets, QtCore
from qtpy.QtGui import QIcon

from ... import paths, devices, config
from .... import __version__


class ConfigHistory:
    """ Manage config history: store each change made to a config """

    def __init__(self):
        self.active = True
        self.list = []
        self.index = -1
        # Note: it's normal to have the first data unchangeable by append method
        # use pop if need to remove first data

    def __repr__(self):
        return object.__repr__(self) + "\n\t" + self.list.__repr__() + f"\n\tCurrent data: {self.get_data()}"

    def __len__(self):
        return len(self.list)

    def append(self, data):

        if data is not None:
            # if in middle remove right indexes
            if (self.index != len(self)-1): self.list = self.list[: self.index+1]
            self.index += 1
            self.list.append(data)

    def pop(self):  # OBSOLETE
        if len(self) != 0:
            if (self.index == len(self) - 1): self.index -= 1
            self.list.pop()

    def go_up(self):
        if (self.index + 1) <= (len(self) - 1): self.index += 1

    def go_down(self):
        if (self.index-1 >= 0): self.index -= 1

    def get_data(self):
        return self.list[self.index] if self.index >= 0 else None


class ConfigManager:
    """ Manage a config, storing recipes of a scan """

    def __init__(self, gui):

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
        self.config = collections.OrderedDict()

        self.configHistory = ConfigHistory()
        self.configHistory.active = True

        self._append = False  # option for import config


    # NAMES
    ###########################################################################

    def getNames(self, recipe_name: str, option: str = None) -> list:
        """ This function returns a list of the names of the recipe step and of the parameter """
        names = [step['name'] for step in self.config[recipe_name]['recipe']]

        if option != 'recipe':
            names.append(self.config[recipe_name]['parameter']['name'])

        return names

    def getUniqueName(self, recipe_name: str, basename: str) -> str:
        """ This function adds a number next to basename in case this basename
        is already taken for the given recipe with recipe_name name """
        name = basename
        names = []

        if recipe_name in self.config.keys():
            names += self.getNames(recipe_name)

        compt = 0
        while True:
            if name in names:
                compt += 1
                name = basename+'_'+str(compt)
            else:
                break

        return name

    def getUniqueNameRecipe(self, basename: str) -> str:
        """ This function adds a number next to basename in case this basename
        is already taken by a recipe """
        name = basename
        names = []

        names.append('recipe')  # don't want 'recipe' as name but only 'recipe_i'
        names.append('autolab')  # don't want 'autolab' as name
        names += self.config.keys()

        compt = 0
        while True:
            if name in names:
                compt += 1
                name = basename+'_'+str(compt)
            else:
                break

        return name

    # CONFIG MODIFICATIONS
    ###########################################################################

    def addNewConfig(self):
        """ Add new config to history list """
        if self.configHistory.active:
            self.configHistory.append(self.create_configPars())
            self.undo.setEnabled(True)
            self.redo.setEnabled(False)

    def addRecipe(self, recipe_name: str):
        """ Add new recipe to config """
        if not self.gui.scanManager.isStarted():
            recipe_name = self.getUniqueNameRecipe(recipe_name)
            parameter_name = self.getUniqueName(recipe_name, 'parameter')

            self.config[recipe_name] = {}
            self.config[recipe_name]['parameter'] = {'element':None,
                                                     'name':parameter_name}
            self.config[recipe_name]['nbpts'] = 11
            self.config[recipe_name]['range'] = (0, 10)
            self.config[recipe_name]['step'] = 1
            self.config[recipe_name]['log'] = False
            self.config[recipe_name]['recipe'] = []

            self.gui._addRecipe(recipe_name)
            self.gui.dataManager.clear()
            self.addNewConfig()

    def removeRecipe(self, recipe_name: str):
        """ Remove recipe with recipe_name from config """
        if not self.gui.scanManager.isStarted():
            self.config.pop(recipe_name)
            self.gui._removeRecipe(recipe_name)
            self.gui.dataManager.clear()
            self.addNewConfig()

    def lastRecipeName(self) -> str:
        return list(self.config.keys())[-1] if len(self.config.keys()) != 0 else ""

    def _defaultParameterPars(self) -> dict:
        return {'name': 'parameter',
                'address': 'None',
                'nbpts': 1,
                'start_value': 0,
                'end_value': 0,
                'log': False}

    def setParameter(self, recipe_name: str, element: devices.Device,
                     name: str = None):
        """ This function set the element provided as the new parameter of the scan """
        if not self.gui.scanManager.isStarted():
            self.config[recipe_name]['parameter']['element'] = element
            if name is None: name = self.getUniqueName(recipe_name, element.name)
            self.config[recipe_name]['parameter']['name'] = name
            self.gui.recipeDict[recipe_name]['parameterManager'].refresh()
            self.gui.dataManager.clear()
            self.addNewConfig()

    def setParameterName(self, recipe_name: str, name: str):
        """ This function set the name of the current parameter of the scan """
        if not self.gui.scanManager.isStarted():
            if name != self.config[recipe_name]['parameter']['name']:
                name = self.getUniqueName(recipe_name, name)
                self.config[recipe_name]['parameter']['name'] = name
                self.gui.dataManager.clear()
                self.addNewConfig()

        self.gui.recipeDict[recipe_name]['parameterManager'].refresh()

    def addRecipeStep(self, recipe_name: str, stepType: str, element,
                      name: str = None, value = None):
        """ This function add a step to the scan recipe """
        if recipe_name == "":
            self.addRecipe("recipe")
            recipe_name = self.lastRecipeName()

        if not self.gui.scanManager.isStarted():
            assert recipe_name in self.config.keys(), f'{recipe_name} not in {list(self.config.keys())}'

            if name is None:
                name = self.getUniqueName(recipe_name, element.name)
            else:
                name = self.getUniqueName(recipe_name, name)

            step = {'stepType': stepType, 'element': element,
                    'name': name,'value': None}

            # Value
            if stepType == 'set': setValue = True
            elif stepType == 'action' and element.type in [
                    int, float, str, pd.DataFrame,np.ndarray]: setValue = True
            else: setValue = False

            if setValue:
                if value is None:
                    if element.type in [int, float]: value = 0
                    elif element.type in [
                            str, pd.DataFrame, np.ndarray]: value = ''
                    elif element.type in [bool]: value = False
                step['value'] = value

            self.config[recipe_name]['recipe'].append(step)
            self.refreshRecipe(recipe_name)
            self.gui.dataManager.clear()
            self.addNewConfig()

    def refreshRecipe(self, recipe_name: str):
        self.gui.recipeDict[recipe_name]['recipeManager'].refresh()

    def delRecipeStep(self, recipe_name: str, name: str):
        """ This function removes a step from the scan recipe """
        if not self.gui.scanManager.isStarted():
            pos = self.getRecipeStepPosition(recipe_name, name)
            self.config[recipe_name]['recipe'].pop(pos)
            self.refreshRecipe(recipe_name)
            self.gui.dataManager.clear()
            self.addNewConfig()

    def renameRecipeStep(self, recipe_name: str, name: str, newName: str):
        """ This function rename a step in the scan recipe """
        if not self.gui.scanManager.isStarted():
            if newName != name :
                pos = self.getRecipeStepPosition(recipe_name, name)
                newName = self.getUniqueName(recipe_name, newName)
                self.config[recipe_name]['recipe'][pos]['name'] = newName
                self.refreshRecipe(recipe_name)
                self.gui.dataManager.clear()
                self.addNewConfig()

    def setRecipeStepValue(self, recipe_name: str, name: str, value: Any):
        """ This function set the value of a step in the scan recipe """
        if not self.gui.scanManager.isStarted():
            pos = self.getRecipeStepPosition(recipe_name, name)

            if value != self.config[recipe_name]['recipe'][pos]['value']:
                self.config[recipe_name]['recipe'][pos]['value'] = value
                self.refreshRecipe(recipe_name)
                self.gui.dataManager.clear()
                self.addNewConfig()

    def setRecipeOrder(self, recipe_name: str, stepOrder: list):
        """ This function reorder the recipe as a function of the list of step names provided """
        if not self.gui.scanManager.isStarted():
            newOrder = [self.getRecipeStepPosition(recipe_name, name) for name in stepOrder]
            recipe = self.config[recipe_name]['recipe']
            self.config[recipe_name]['recipe'] = [recipe[i] for i in newOrder]
            self.gui.dataManager.clear()
            self.addNewConfig()

        self.refreshRecipe(recipe_name)

    def setNbPts(self, recipe_name: str, value: int):
        """ This function set the value of the number of points of the scan """
        if not self.gui.scanManager.isStarted():
            self.config[recipe_name]['nbpts'] = value

            if value == 1:
                self.config[recipe_name]['step'] = 0
            else:
                xrange = tuple(self.getRange(recipe_name))
                width = abs(xrange[1] - xrange[0])
                self.config[recipe_name]['step'] = width / (value - 1)
            self.addNewConfig()

        self.gui.recipeDict[recipe_name]['rangeManager'].refresh()

    def setStep(self, recipe_name: str, value: float):

        """ This function set the value of the step between points of the scan """
        if not self.gui.scanManager.isStarted():

            if value == 0:
                self.config[recipe_name]['nbpts'] = 1
                self.config[recipe_name]['step'] = 0
            else:
                self.config[recipe_name]['step'] = value
                xrange = tuple(self.getRange(recipe_name))
                width = abs(xrange[1] - xrange[0])
                self.config[recipe_name]['nbpts'] = int(round(width / value) + 1)
                if width != 0:
                    self.config[recipe_name]['step'] = width / (self.config[recipe_name]['nbpts'] - 1)
            self.addNewConfig()

        self.gui.recipeDict[recipe_name]['rangeManager'].refresh()

    def setRange(self, recipe_name: str, lim: Tuple[float, float]):

        """ This function set the range (start and end value) of the scan """

        if not self.gui.scanManager.isStarted():
            if lim != self.config[recipe_name]['range']:
                self.config[recipe_name]['range'] = tuple(lim)

            width = abs(lim[1] - lim[0])

            if self.gui.recipeDict[recipe_name]['rangeManager'].point_or_step == "point":
                self.config[recipe_name]['step'] = width / (self.getNbPts(recipe_name) - 1)

            elif self.gui.recipeDict[recipe_name]['rangeManager'].point_or_step == "step":
                self.config[recipe_name]['nbpts'] = int(round(width / self.getStep(recipe_name)) + 1)
                self.config[recipe_name]['step'] = width / (self.getNbPts(recipe_name) - 1)
            self.addNewConfig()

        self.gui.recipeDict[recipe_name]['rangeManager'].refresh()

    def setLog(self, recipe_name: str, state: bool):
        """ This function set the log state of the scan """
        if not self.gui.scanManager.isStarted():
            if state != self.config[recipe_name]['log']:
                self.config[recipe_name]['log'] = state
            self.addNewConfig()

        self.gui.recipeDict[recipe_name]['rangeManager'].refresh()


    # CONFIG READING
    ###########################################################################

    def getParameter(self, recipe_name: str) -> devices.Device:
        """ This function returns the element of the current parameter of the scan """
        return self.config[recipe_name]['parameter']['element']

    def getParameterName(self, recipe_name: str) -> str:
        """ This function returns the name of the current parameter of the scan """
        return self.config[recipe_name]['parameter']['name']

    def getRecipeStepElement(self, recipe_name: str, name: str) -> devices.Device:
        """ This function returns the element of a recipe step """
        pos = self.getRecipeStepPosition(recipe_name, name)
        return self.config[recipe_name]['recipe'][pos]['element']

    def getRecipeStepType(self, recipe_name: str, name: str) -> str:
        """ This function returns the type a recipe step """
        pos = self.getRecipeStepPosition(recipe_name, name)
        return self.config[recipe_name]['recipe'][pos]['stepType']

    def getRecipeStepValue(self, recipe_name: str, name: str) -> Any:
        """ This function returns the value of a recipe step """
        pos = self.getRecipeStepPosition(recipe_name, name)
        return self.config[recipe_name]['recipe'][pos]['value']

    def getRecipeStepPosition(self, recipe_name: str, name: str) -> int:
        """ This function returns the position of a recipe step in the recipe """
        return [i for i, step in enumerate(self.config[recipe_name]['recipe']) if step['name'] == name][0]

    def getLog(self, recipe_name: str) -> bool:
        """ This function returns the log state of the scan """
        return self.config[recipe_name]['log']

    def getNbPts(self, recipe_name: str) -> int:
        """ This function returns the number of points of the scan """
        return self.config[recipe_name]['nbpts']

    def getStep(self, recipe_name: str) -> float:
        """ This function returns the value of the step between points of the scan """
        return self.config[recipe_name]['step']

    def getRange(self, recipe_name: str) -> Tuple[float, float]:
        """ This function returns the range (start and end value) of the scan """
        return self.config[recipe_name]['range']

    def getParamDataFrame(self, recipe_name: str) -> pd.DataFrame:
        """ This function returns a DataFrame with 'id' and '<parameterName>' columns \
            containing the parameter array """
        startValue, endValue = self.getRange(recipe_name)
        nbpts = self.getNbPts(recipe_name)
        logScale: bool = self.getLog(recipe_name)
        parameterName = self.getParameterName(recipe_name)

        if logScale:
            paramValues = np.logspace(m.log10(startValue), m.log10(endValue),
                                      nbpts, endpoint=True)
        else:
            paramValues = np.linspace(startValue, endValue, nbpts, endpoint=True)

        data = pd.DataFrame()
        data["id"] = 1 + np.arange(len(paramValues))
        data[parameterName] = paramValues

        return data

    def getRecipe(self, recipe_name: str) -> list:
        """ This function returns the whole recipe of the scan """
        return self.config[recipe_name]['recipe']


    # EXPORT IMPORT ACTIONS
    ###########################################################################

    def exportActionClicked(self):
        """ This function prompts the user for a configuration file path,
        and export the current scan configuration in it """
        filename = QtWidgets.QFileDialog.getSaveFileName(
            self.gui, "Export AUTOLAB configuration file",
            os.path.join(paths.USER_LAST_CUSTOM_FOLDER,'config.conf'),
            "AUTOLAB configuration file (*.conf);;All Files (*)")[0]

        if filename != '':
            path = os.path.dirname(filename)
            paths.USER_LAST_CUSTOM_FOLDER = path

            try :
                self.export(filename)
                self.gui.setStatus(f"Current configuration successfully saved at {filename}", 5000)
            except Exception as e:
                self.gui.setStatus(f"An error occured: {str(e)}", 10000, False)

    def export(self, filename: str):
        """ This function exports the current scan configuration in the provided file """
        configPars = self.create_configPars()

        with open(filename, "w") as configfile:
            json.dump(configPars, configfile, indent=4)

    def create_configPars(self) -> dict:

        """ This function create the current scan configuration parser """
        configPars = {}
        configPars['autolab'] = {'version':__version__,
                                 'timestamp':str(datetime.datetime.now())}

        for recipe_name, recipe_i in zip(self.config.keys(), self.config.values()):
            pars_recipe_i = {}
            pars_recipe_i['parameter'] = {}
            pars_recipe_i['parameter']['name'] = recipe_i['parameter']['name']
            if recipe_i['parameter']['element'] is not None:
                pars_recipe_i['parameter']['address'] = recipe_i['parameter']['element'].address()
            else:
                pars_recipe_i['parameter']['address'] = "None"
            pars_recipe_i['parameter']['nbpts'] = str(recipe_i['nbpts'])
            pars_recipe_i['parameter']['start_value'] = str(recipe_i['range'][0])
            pars_recipe_i['parameter']['end_value'] = str(recipe_i['range'][1])
            pars_recipe_i['parameter']['log'] = str(int(recipe_i['log']))

            pars_recipe_i['recipe'] = {}
            for i, config_step in enumerate(recipe_i['recipe']):
                pars_recipe_i['recipe'][f'{i+1}_name'] = config_step['name']
                pars_recipe_i['recipe'][f'{i+1}_steptype'] = config_step['stepType']
                pars_recipe_i['recipe'][f'{i+1}_address'] = config_step['element'].address()
                stepType = config_step['stepType']
                if stepType == 'set' or (stepType == 'action'
                                         and config_step['element'].type in [
                                             int,float,str,
                                             pd.DataFrame,np.ndarray]):
                    value = config_step['value']
                    try:
                        valueStr = f'{value:.{self.precision}g}'
                    except:
                        valueStr = f'{value}'
                    pars_recipe_i['recipe'][f'{i+1}_value'] = valueStr
            configPars[recipe_name] = pars_recipe_i
        return configPars


    def importActionClicked(self):
        """ This function prompts the user for a configuration filename,
        and import the current scan configuration from it """
        main_dialog = QtWidgets.QDialog(self.gui)
        main_dialog.setWindowTitle("Import AUTOLAB configuration file")
        layout = QtWidgets.QVBoxLayout(main_dialog)

        file_dialog = QtWidgets.QFileDialog(main_dialog, QtCore.Qt.Widget)
        file_dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog)
        file_dialog.setWindowFlags(file_dialog.windowFlags() & ~QtCore.Qt.Dialog)
        file_dialog.setDirectory(paths.USER_LAST_CUSTOM_FOLDER)
        file_dialog.setNameFilters(["AUTOLAB configuration file (*.conf)", "All Files (*)"])
        layout.addWidget(file_dialog)

        appendCheck = QtWidgets.QCheckBox('Append', main_dialog)
        appendCheck.setChecked(self._append)
        layout.addWidget(appendCheck)

        main_dialog.show()

        once_or_append = True
        while once_or_append:
            filenames = file_dialog.selectedFiles() if file_dialog.exec_() else []

            self._append = appendCheck.isChecked()
            once_or_append = self._append and len(filenames) != 0

            for filename in filenames:
                if filename != '': self.import_configPars(filename, append=self._append)

        main_dialog.close()

    def import_configPars(self, filename: str, append: bool = False):

        try:
            legacy_configPars = configparser.ConfigParser()
            legacy_configPars.read(filename)
        except:
            try:
                with open(filename, "r") as read_file:
                    configPars = json.load(read_file)
            except Exception as error:
                self.gui.setStatus(f"Impossible to load configuration file: {error}", 10000, False)
                return None
        else:
            print("ConfigParser depreciated, now use json. Will convert this config to json if save it.")
            configPars = {s: dict(legacy_configPars.items(s)) for s in legacy_configPars.sections()}

        path = os.path.dirname(filename)
        paths.USER_LAST_CUSTOM_FOLDER = path

        self.load_configPars(configPars, append=append)

        if not self._got_error:
            self.addNewConfig()


    def load_configPars(self, configPars: dict, append: bool = False):

        self._got_error = False
        self.configHistory.active = False
        previous_config = self.config.copy()  # used to recover old config if error in loading new one
        already_loaded_devices = devices.list_loaded_devices()

        try :
            # Legacy config
            if 'parameter' in configPars:
                new_configPars = collections.OrderedDict()
                new_configPars["autolab"] = configPars["autolab"]

                if 'initrecipe' in configPars:
                    new_configPars["init"] = {}
                    new_configPars["init"]['parameter'] = self._defaultParameterPars()
                    new_configPars["init"]['parameter']['name'] = 'init'
                    new_configPars["init"]['recipe'] = configPars['initrecipe']

                new_configPars["recipe"] = {}
                new_configPars["recipe"]['parameter'] = configPars['parameter']
                new_configPars["recipe"]['recipe'] = configPars['recipe']

                if 'endrecipe' in configPars:
                    new_configPars["end"] = {}
                    new_configPars["end"]['parameter'] = self._defaultParameterPars()
                    new_configPars["end"]['parameter']['name'] = 'end'
                    new_configPars["end"]['recipe'] = configPars['endrecipe']
                configPars = new_configPars

            # Config
            config = collections.OrderedDict()
            recipeNameList = [i for i in list(configPars.keys()) if i != 'autolab']  # to remove 'autolab' from recipe list

            for recipe_name in recipeNameList:
                config[recipe_name] = collections.OrderedDict()
                recipe_i = config[recipe_name]
                pars_recipe_i = configPars[recipe_name]
                assert 'parameter' in pars_recipe_i, f'Missing parameter in {recipe_name}:{pars_recipe_i}'
                assert 'address' in pars_recipe_i['parameter'], f"Missing address to {pars_recipe_i['parameter']}"
                if pars_recipe_i['parameter']['address'] == "None":
                    element = None
                else:
                    element = devices.get_element_by_address(pars_recipe_i['parameter']['address'])
                    assert element is not None, f"Parameter {pars_recipe_i['parameter']['address']} not found."

                assert 'name' in pars_recipe_i['parameter'], "Missing name to {pars_recipe_i['parameter']}"
                recipe_i['parameter'] = {'element':element,'name':pars_recipe_i['parameter']['name']}

                for key in ['nbpts', 'start_value', 'end_value', 'log'] :
                    assert key in pars_recipe_i['parameter'], "Missing parameter key {key}."
                    recipe_i['nbpts'] = int(pars_recipe_i['parameter']['nbpts'])
                    start = float(pars_recipe_i['parameter']['start_value'])
                    end = float(pars_recipe_i['parameter']['end_value'])
                    recipe_i['range'] = (start,end)
                    recipe_i['log'] = bool(int(pars_recipe_i['parameter']['log']))
                    if recipe_i['nbpts'] > 1:
                        recipe_i['step'] = abs(end-start)/(recipe_i['nbpts']-1)
                    else:
                        recipe_i['step'] = 0

                recipe_i['recipe'] = []
                recipe = recipe_i['recipe']
                pars_recipe = pars_recipe_i['recipe']

                while True:
                    step = {}
                    i = len(recipe) + 1

                    if f'{i}_name' in pars_recipe:
                        step['name'] = pars_recipe[f'{i}_name']
                        name = step['name']

                        assert f'{i}_steptype' in pars_recipe, f"Missing stepType in step {i} ({name})."
                        step['stepType'] = pars_recipe[f'{i}_steptype']

                        assert f'{i}_address' in pars_recipe, f"Missing address in step {i} ({name})."
                        address = pars_recipe[f'{i}_address']
                        element = devices.get_element_by_address(address)
                        assert element is not None, f"Address {address} not found for step {i} ({name})."
                        step['element'] = element

                        if (step['stepType'] == 'set')  or (
                                step['stepType'] == 'action' and element.type in [
                                    int, float, str, pd.DataFrame, np.ndarray]):
                            assert f'{i}_value' in pars_recipe, f"Missing value in step {i} ({name})."
                            value = pars_recipe[f'{i}_value']

                            try:
                                try:
                                    assert self.checkVariable(value), "Need $eval: to evaluate the given string"
                                except:
                                    # Type conversions
                                    if element.type in [int]:
                                        value = int(value)
                                    elif element.type in [float]:
                                        value = float(value)
                                    elif element.type in [str]:
                                        value = str(value)
                                    elif element.type in [bool]:
                                        if value == "False": value = False
                                        elif value == "True": value = True
                                        value = int(value)
                                        assert value in [0, 1]
                                        value = bool(value)
                                    else:
                                        assert self.checkVariable(value), "Need $eval: to evaluate the given string"
                            except:
                                raise ValueError(f"Error with {i}_value = {value}. Expect either {element.type} or device address. Check address or open device first.")

                            step['value'] = value
                        else:
                            step['value'] = None

                        recipe.append(step)
                    else:
                        break

            if append:
                for recipe_name in config.keys():

                    if recipe_name in self.config.keys():
                        new_recipe_name = self.getUniqueNameRecipe('recipe')
                    else:
                        new_recipe_name = recipe_name

                    self.config[new_recipe_name] = config[recipe_name]
            else:
                self.config = config

        except Exception as error:
            self._got_error = True
            self.gui.setStatus(f"Impossible to load configuration file: {error}", 10000, False)
            self.config = previous_config
        else:
            self.resetRecipe()
            self.gui.setStatus("Configuration file loaded successfully", 5000)

            for device in (set(devices.list_loaded_devices()) - set(already_loaded_devices)):
                item_list = self.gui.mainGui.tree.findItems(device, QtCore.Qt.MatchExactly, 0)

                if len(item_list) == 1:
                    item = item_list[0]
                    self.gui.mainGui.itemClicked(item)

        self.configHistory.active = True

    def resetRecipe(self):
        self.gui._clearRecipe()  # before everything to have access to recipe and del it
        self.gui.dataManager.clear()

        for recipe_name in self.config.keys():
            self.gui._addRecipe(recipe_name)
            self.gui.recipeDict[recipe_name]['parameterManager'].refresh()
            self.refreshRecipe(recipe_name)
            self.gui.recipeDict[recipe_name]['rangeManager'].refresh()

    def renameRecipe(self, existing_recipe_name: str, new_recipe_name: str):
        if existing_recipe_name not in self.config.keys():
            raise ValueError(f'should not be possible to select a non existing recipe_name: {existing_recipe_name} not in {self.config.keys()}')

        new_recipe_name = self.getUniqueNameRecipe(new_recipe_name)
        old_config = self.config
        new_config = {}

        for recipe_name in old_config.keys():
            if recipe_name == existing_recipe_name:
                new_config[new_recipe_name] = old_config[recipe_name]
            else:
                new_config[recipe_name] = old_config[recipe_name]

        self.config = new_config
        self.resetRecipe()

    def checkVariable(self, value) -> bool:
        """ Check if value start with '$eval:'. \
            Will not try to check if variables exists """
        return True if str(value).startswith("$eval:") else False


    # UNDO REDO ACTIONS
    ###########################################################################

    def undoClicked(self):
        """ Undo an action from parameter, recipe or range """
        self.configHistory.go_down()
        self.changeConfig()


    def redoClicked(self):
        """ Redo an action from parameter, recipe or range """
        self.configHistory.go_up()
        self.changeConfig()


    def changeConfig(self):
        """ Get config from history and enable/disable undo/redo button accordingly """
        configPars = self.configHistory.get_data()

        if configPars is not None:
            self.load_configPars(configPars)

        self.updateUndoRedoButtons()


    def updateUndoRedoButtons(self):
        """ enable/disable undo/redo button depending on history """
        if self.configHistory.index == 0:
            self.undo.setEnabled(False)
        else:
            self.undo.setEnabled(True)

        if self.configHistory.index == len(self.configHistory)-1:
            self.redo.setEnabled(False)
        else:  # implicit <
            self.redo.setEnabled(True)
