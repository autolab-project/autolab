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
from typing import Any, Tuple, List, Dict, Union
from collections import OrderedDict

import numpy as np
import pandas as pd
from qtpy import QtWidgets, QtCore

from ...config import get_scanner_config
from ...elements import Variable as Variable_og
from ...elements import Action
from ...devices import DEVICES, list_loaded_devices, get_element_by_address
from ...utilities import (boolean, str_to_array, array_to_str, create_array,
                          str_to_dataframe, dataframe_to_str, str_to_data,
                          str_to_tuple)
from ...variables import (get_variable, has_eval, is_Variable, eval_variable,
                          remove_from_config, update_from_config, VARIABLES)
from ...paths import PATHS
from .... import __version__


class ConfigHistory:
    """ Manage config history: store each change made to a config """

    def __init__(self):
        self.active = True
        self.list = []
        self.index = -1
        # Note: it's normal to have the first data unchangeable by append method
        # use pop if need to remove first data

    def __repr__(self) -> str:
        return (object.__repr__(self) + "\n\t" + self.list.__repr__()
                + f"\n\tCurrent data: {self.get_data()}")

    def __len__(self) -> int:
        return len(self.list)

    def append(self, data: dict):

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

    def get_data(self) -> dict:
        return self.list[self.index] if self.index >= 0 else None


class ConfigManager:
    """ Manage a config, storing recipes of a scan """

    def __init__(self, gui: QtWidgets.QMainWindow):

        self.gui = gui

        # Import Autolab config
        scanner_config = get_scanner_config()
        self.precision = scanner_config['precision']

        # Initializing configuration values
        self.config = OrderedDict()

        self.configHistory = ConfigHistory()
        self.configHistory.active = True

        self._old_variables = []  # To update variable menu

    def ask_get_element_by_address(self, device_name: str, address: str):
        """ Wrap of :meth:`get_element_by_address` to ask user if want to
        instantiate device if not already instantiated.
        Returns the element at the given address. """
        if device_name not in DEVICES:
            msg_box = QtWidgets.QMessageBox(self.gui)
            msg_box.setWindowTitle(f"Device {device_name}")
            msg_box.setText(f"Instantiate device {device_name}?")
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok
                                       | QtWidgets.QMessageBox.Cancel)
            msg_box.show()
            if msg_box.exec_() == QtWidgets.QMessageBox.Cancel:
                raise ValueError(f'Refused {device_name} instantiation')

        element = get_element_by_address(address)

        return element

    def update_loaded_devices(self, already_loaded_devices: list):
        """ Refresh GUI with the new loaded devices """
        for device in (set(list_loaded_devices()) - set(already_loaded_devices)):
            item_list = self.gui.mainGui.tree.findItems(
                device, QtCore.Qt.MatchExactly, 0)

            if len(item_list) == 1:
                item = item_list[0]
                self.gui.mainGui.itemClicked(item)

    # NAMES
    ###########################################################################

    def getNames(self, recipe_name: str, option: str = None) -> List[str]:
        """ Returns a list of step names and parameter names of a recipe """
        names = [step['name'] for step in self.stepList(recipe_name)]

        if option != 'recipe':
            for parameter in self.parameterList(recipe_name):
                names.append(parameter['name'])

        return names

    def getUniqueName(self, recipe_name: str, basename: str,
                      ignore: List[str] = []) -> str:
        """ Returns unique name: Adds a number next to basename in case this
        basename is already taken for the given recipe """
        name = basename
        names = []

        for recipe_name in self.getRecipeLink(recipe_name):
            if recipe_name in self.recipeNameList():
                names += self.getNames(recipe_name)

        names = [name for name in names if name not in ignore]
        compt = 0
        while True:
            if name in names:
                compt += 1
                name = basename + '_' + str(compt)
            else:
                break

        return name

    def getUniqueNameRecipe(self, basename: str, ignore: List[str] = []) -> str:
        """ Returns unique name for recipe: Adds a number next to basename in
        case this basename is already taken by a recipe """
        name = basename
        names = []

        names += self.recipeNameList()
        names = [name for name in names if name not in ignore]

        compt = 0
        while True:
            if name in names:
                compt += 1
                name = basename + '_' + str(compt)
            else:
                break

        return name

    # CONFIG MODIFICATIONS
    ###########################################################################
    def updateVariableConfig(self, new_variables: List[Tuple[str, Any]] = None):
        if new_variables is None:
            new_variables = self.getConfigVariables()
        remove_variables = list(set(self._old_variables) - set(new_variables))
        remove_from_config(remove_variables)
        update_from_config(new_variables)
        self._old_variables = new_variables

    def addNewConfig(self):
        """ Adds new config to history list """
        if self.configHistory.active:
            self.updateVariableConfig()  # before create_configPars
            self.configHistory.append(self.create_configPars())
            self.gui.undo.setEnabled(True)
            self.gui.redo.setEnabled(False)

    def addRecipe(self, recipe_name: str):
        """ Adds new recipe to config """
        if not self.gui.scanManager.isStarted():
            recipe_name = self.getUniqueNameRecipe(recipe_name)

            self.config[recipe_name] = {}
            self.config[recipe_name]['parameter'] = []
            self.config[recipe_name]['recipe'] = []
            self.config[recipe_name]['active'] = True
            self._addDefaultParameter(recipe_name)

            self.gui._addRecipe(recipe_name)
            self.addNewConfig()

    def removeRecipe(self, recipe_name: str):
        """ Removes recipe from config """
        if not self.gui.scanManager.isStarted():
            self.config.pop(recipe_name)
            self.gui._removeRecipe(recipe_name)
            self.addNewConfig()

    def activateRecipe(self, recipe_name: str, state: bool):
        """ Activates/Deactivates a recipe """
        if not self.gui.scanManager.isStarted():
            self.config[recipe_name]['active'] = bool(state)

            self.gui._activateRecipe(recipe_name, self.config[recipe_name]['active'])
            self.addNewConfig()

    def setRecipeOrder(self, keys: List[str]):
        """ Reorders recipes according to the list of recipe names 'keys' """
        if not self.gui.scanManager.isStarted():
            self.config = OrderedDict((key, self.config[key]) for key in keys)
            self.gui._resetRecipe()
            self.addNewConfig()

    def renameRecipe(self, existing_recipe_name: str, new_recipe_name: str):
        """ Renames recipe """
        if not self.gui.scanManager.isStarted():
            if new_recipe_name == existing_recipe_name:
                return None
            if existing_recipe_name not in self.recipeNameList():
                raise ValueError(
                    'should not be possible to select a non existing recipe_name: ' \
                        f'{existing_recipe_name} not in {self.recipeNameList()}')

            new_recipe_name = self.getUniqueNameRecipe(
                new_recipe_name, ignore=[existing_recipe_name])

            if new_recipe_name == existing_recipe_name:
                return None
            old_config = self.config
            new_config = {}

            for recipe_name in old_config:
                if recipe_name == existing_recipe_name:
                    new_config[new_recipe_name] = old_config[recipe_name]
                else:
                    new_config[recipe_name] = old_config[recipe_name]

            self.config = new_config

            prev_index_recipe = self.gui.selectRecipe_comboBox.currentIndex()
            prev_index_param = self.gui.selectParameter_comboBox.currentIndex()
            self.gui._resetRecipe()
            self.gui.selectRecipe_comboBox.setCurrentIndex(prev_index_recipe)
            self.gui._updateSelectParameter()
            self.gui.selectParameter_comboBox.setCurrentIndex(prev_index_param)

    def checkConfig(self):
        """ Checks validity of a config. Used before a scan start or after a scan pause. """
        assert len(self.recipeNameList()) != 0, 'Need a recipe to start a scan!'

        one_recipe_active = False
        for recipe_name in self.recipeNameList():
            recipe = self.config[recipe_name]
            if recipe['active']:
                one_recipe_active = True
                assert len(recipe['recipe']) > 0, f"Recipe {recipe_name} is empty!"

            list_recipe_new = [recipe]
            has_sub_recipe = True

            while has_sub_recipe:  # OBSOLETE
                has_sub_recipe = False
                recipe_list = list_recipe_new

                for recipe_i in recipe_list:

                    for step in recipe_i['recipe']:
                        if step['stepType'] == 'recipe':
                            has_sub_recipe = True
                            assert step['element'] in self.config, (
                                f"Recipe {step['element']} doesn't exist in {recipe_name}!")
                            other_recipe = self.config[step['element']]
                            assert len(other_recipe['recipe']) > 0, (
                                f"Recipe {step['element']} is empty!")
                            list_recipe_new.append(other_recipe)

                    list_recipe_new.remove(recipe_i)

        assert one_recipe_active, "Need at least one active recipe!"

        already_loaded_devices = list_loaded_devices()
        try:
            # Replace closed devices by reopened one
            for recipe_name in self.recipeNameList():
                for step in (self.stepList(recipe_name)
                              + self.parameterList(recipe_name)):
                    if step['element']:
                        device_name = step['element'].address().split('.')[0]
                        element = self.ask_get_element_by_address(
                            device_name, step['element'].address())
                        step['element'] = element
        finally:
            self.update_loaded_devices(already_loaded_devices)

    def lastRecipeName(self) -> str:
        """ Returns last recipe name """
        return self.recipeNameList()[-1] if len(self.recipeNameList()) != 0 else ""

    # set Param
    def _defaultParameterPars(self) -> dict:
        return {'name': 'parameter',
                'address': 'None',
                'nbpts': 1,
                'start_value': 0,
                'end_value': 0,
                'log': False}

    def _addDefaultParameter(self, recipe_name: str):
        """ Adds a default parameter to the config"""
        parameter_name = self.getUniqueName(recipe_name, 'parameter')

        parameter = {'name': parameter_name,
                     'element': None,
                     'nbpts': 11,
                     'range': (0, 10),
                     'step': 1,
                     'log': False,
                     }

        self.parameterList(recipe_name).append(parameter)

    def addParameter(self, recipe_name: str):
        """ Adds a parameter to the recipe """
        if not self.gui.scanManager.isStarted():
            self._addDefaultParameter(recipe_name)
            param_name = self.parameterList(recipe_name)[-1]['name']
            self.gui._addParameter(recipe_name, param_name)

            self.addNewConfig()

    def removeParameter(self, recipe_name: str, param_name: str):
        """ Removes the parameter from the recipe """
        if not self.gui.scanManager.isStarted():
            pos = self.getParameterPosition(recipe_name, param_name)
            self.parameterList(recipe_name).pop(pos)
            self.gui._removeParameter(recipe_name, param_name)

            self.addNewConfig()

    def setParameter(self, recipe_name: str, param_name: str,
                     element: Variable_og, newName: str = None):
        """ Sets the element provided as the new parameter of the scan.
        Add a parameter is no existing parameter """
        if not self.gui.scanManager.isStarted():
            if recipe_name == "":
                self.configHistory.active = False
                self.addRecipe("recipe")
                self.configHistory.active = True
                recipe_name = self.lastRecipeName()
                param_name = self.parameterNameList(recipe_name)[-1]
            if len(self.parameterList(recipe_name)) == 0:
                self.configHistory.active = False
                self.addParameter(recipe_name)
                self.configHistory.active = True
                param_name = self.parameterList(recipe_name)[-1]['name']

            param = self.getParameter(recipe_name, param_name)

            param['element'] = element
            if newName is None:
                if param_name == element.name:
                    newName = param_name
                else:
                    newName = self.getUniqueName(
                        recipe_name, element.name)
            param['name'] = newName
            self.gui._refreshParameterRange(recipe_name, param_name, newName)
            self.addNewConfig()

    def renameParameter(self, recipe_name: str, param_name: str, newName: str):
        """ Renames a parameter of a recipe """
        if not self.gui.scanManager.isStarted():
            if newName != param_name:
                param = self.getParameter(recipe_name, param_name)

                newName = self.getUniqueName(
                    recipe_name, newName, ignore=[param_name])
                if newName != param_name:
                    param['name'] = newName
                    self.addNewConfig()
        else:
            newName = param_name

        self.gui._refreshParameterRange(recipe_name, param_name, newName)

    def setNbPts(self, recipe_name: str, param_name: str, value: int):
        """ Sets the number of points of a parameter """
        if not self.gui.scanManager.isStarted():
            param = self.getParameter(recipe_name, param_name)

            param['nbpts'] = value

            if value == 1:
                param['step'] = 0
            else:
                xrange = tuple(self.getRange(recipe_name, param_name))
                width = abs(xrange[1] - xrange[0])
                param['step'] = width / (value - 1)
            self.addNewConfig()

        self.gui._refreshParameterRange(recipe_name, param_name)

    def setStep(self, recipe_name: str, param_name: str, value: float):
        """ Sets the step between points of a parameter """
        if not self.gui.scanManager.isStarted():
            param = self.getParameter(recipe_name, param_name)

            if value == 0:
                param['nbpts'] = 1
                param['step'] = 0
            else:
                param['step'] = value
                xrange = tuple(self.getRange(recipe_name, param_name))
                width = abs(xrange[1] - xrange[0])
                param['nbpts'] = int(round(width / value) + 1)
                if width != 0:
                    param['step'] = width / (param['nbpts'] - 1)
            self.addNewConfig()

        self.gui._refreshParameterRange(recipe_name, param_name)

    def setRange(self, recipe_name: str, param_name: str,
                 lim: Tuple[float, float]):
        """ Sets the range values (start and end value) of a parameter """
        if not self.gui.scanManager.isStarted():
            param = self.getParameter(recipe_name, param_name)

            if lim != param['range']: param['range'] = tuple(lim)

            width = abs(lim[1] - lim[0])

            recipeDictRange = self.gui.recipeDict[recipe_name]['parameterManager']

            if recipeDictRange[param_name].point_or_step == "point":
                param['step'] = float(
                    width / (self.getNbPts(recipe_name, param_name) - 1))

            elif recipeDictRange[param_name].point_or_step == "step":
                param['nbpts'] = int(
                    round(width / self.getStep(recipe_name, param_name)) + 1)
                param['step'] = float(
                    width / (self.getNbPts(recipe_name, param_name) - 1))
            self.addNewConfig()

        self.gui._refreshParameterRange(recipe_name, param_name)

    def setLog(self, recipe_name: str, param_name: str, state: bool):
        """ Sets the log state of a parameter """
        if not self.gui.scanManager.isStarted():
            param = self.getParameter(recipe_name, param_name)

            if state != param['log']: param['log'] = state
            self.addNewConfig()

        self.gui._refreshParameterRange(recipe_name, param_name)

    def setValues(self, recipe_name: str, param_name: str, values: List[float]):
        """ Sets custom values to a parameter """
        if not self.gui.scanManager.isStarted():
            param = self.getParameter(recipe_name, param_name)

            if has_eval(values) or np.ndim(values) == 1:
                param['values'] = values
                self.addNewConfig()

        self.gui._refreshParameterRange(recipe_name, param_name)

    # set step
    def addRecipeStep(self, recipe_name: str, stepType: str, element,
                      name: str = None, value = None):
        """ Adds a step to the scan recipe """
        if recipe_name == "":
            self.addRecipe("recipe")
            recipe_name = self.lastRecipeName()

        if not self.gui.scanManager.isStarted():
            assert recipe_name in self.recipeNameList(), (
                f'{recipe_name} not in {self.recipeNameList()}')

            if name is None:
                name = self.getUniqueName(recipe_name, element.name)
            else:
                name = self.getUniqueName(recipe_name, name)

            step = {'name': name, 'element': element,
                    'stepType': stepType, 'value': None}

            # Value
            if stepType == 'recipe':
                assert element != recipe_name, "Can't have a recipe in itself: {element}"  # safeguard but should be stopped before arriving here
            if stepType == 'set': setValue = True
            elif stepType == 'action' and element.type in [
                    int, float, bool, str, bytes, tuple, np.ndarray, pd.DataFrame]:
                setValue = True
            else: setValue = False

            if setValue:
                if value is None:
                    if element.type in [int, float]: value = 0
                    elif element.type in [str]: value = ''
                    elif element.type in [bytes]: value = b''
                    elif element.type in [pd.DataFrame]: value = pd.DataFrame()
                    elif element.type in [np.ndarray]: value = np.array([])
                    elif element.type in [bool]: value = False
                    elif element.type in [tuple]: value = ([], -1)
                step['value'] = value

            self.stepList(recipe_name).append(step)
            self.gui._refreshRecipe(recipe_name)
            self.addNewConfig()

    def delRecipeStep(self, recipe_name: str, name: str):
        """ Removes a step from the scan recipe """
        if not self.gui.scanManager.isStarted():
            pos = self.getRecipeStepPosition(recipe_name, name)
            self.stepList(recipe_name).pop(pos)
            self.gui._refreshRecipe(recipe_name)
            self.addNewConfig()

    def renameRecipeStep(self, recipe_name: str, name: str, newName: str):
        """ Renames a step in the scan recipe """
        if not self.gui.scanManager.isStarted():
            if newName != name:
                step_info = self.getRecipeStep(recipe_name, name)
                newName = self.getUniqueName(recipe_name, newName)
                step_info['name'] = newName
                self.gui._refreshRecipe(recipe_name)
                self.addNewConfig()

    def setRecipeStepValue(self, recipe_name: str, name: str, value: Any):
        """ Sets the value of a step in the scan recipe """
        if not self.gui.scanManager.isStarted():
            step_info = self.getRecipeStep(recipe_name, name)
            if value is not step_info['value']:
                step_info['value'] = value
                self.gui._refreshRecipe(recipe_name)
                self.addNewConfig()

    def setRecipeStepOrder(self, recipe_name: str, stepOrder: list):
        """ Reorders steps of a recipe according to the list of step names 'stepOrder' """
        if not self.gui.scanManager.isStarted():
            newOrder = [self.getRecipeStepPosition(
                recipe_name, name) for name in stepOrder]
            recipe = self.stepList(recipe_name)
            self.config[recipe_name]['recipe'] = [recipe[i] for i in newOrder]
            self.addNewConfig()

        self.gui._refreshRecipe(recipe_name)

    # CONFIG READING
    ###########################################################################
    def recipeNameList(self):
        """ Returns the list of recipe names """
        return list(self.config.keys())

    def getLinkedRecipe(self) -> Dict[str, list]:  # OBSOLETE
        """ Returns a dict with recipe_name key and list of recipes linked to recipe_name recipe.
        Example: {'recipe_1': ['recipe_1', 'recipe_2', 'recipe_3', 'recipe_2'], 'recipe_3': ['recipe_3', 'recipe_2'], 'recipe_2': ['recipe_2']}"""
        linkedRecipe = {}

        for recipe_name in self.recipeNameList():
            recipe = self.config[recipe_name]
            recipe_name_link = []
            list_recipe_new = [recipe]
            has_sub_recipe = True

            i = 0
            while has_sub_recipe:
                i +=1
                if i > 100:  # safeguard, condition: "step['element'] in recipe_name_link" should be enough
                    raise ValueError('ERROR: stopped recursive function to prevent crash')
                has_sub_recipe = False
                recipe_list = list_recipe_new
                for recipe_i in recipe_list:

                    for step in recipe_i['recipe']:
                        if step['stepType'] == 'recipe':
                            if step['element'] in recipe_name_link:
                                raise ValueError(f"ERROR: cycle detected for recipe {step['element']}!")
                            has_sub_recipe = True
                            if step['element'] in self.config:
                                other_recipe = self.config[step['element']]
                                list_recipe_new.append(other_recipe)
                                recipe_name_link.append(step['element'])

                    list_recipe_new.remove(recipe_i)

            recipe_name_link.append(recipe_name)
            linkedRecipe[recipe_name] = recipe_name_link

        return linkedRecipe

    def getRecipeLink(self, recipe_name: str) -> List[str]:  # OBSOLETE
        """ Returns a list of unique recipe names for which recipes are linked to recipe_name
        Example: for 'recipe_1': ['recipe_1', 'recipe_2', 'recipe_3'] """
        linkedRecipe = self.getLinkedRecipe()
        uniqueLinkedRecipe = []

        for key, val in linkedRecipe.items():
            if recipe_name in val:
                uniqueLinkedRecipe.append(val)

        return list(set(sum(uniqueLinkedRecipe, [])))

    def getAllowedRecipe(self, recipe_name: str) -> List[str]:  # OBSOLETE
        """ Returns a list of recipe that can be added to recipe_name without
        risk of cycle or twice same recipe """
        recipe_name_list = self.recipeNameList()
        linked_recipes = self.getLinkedRecipe()

        for recipe_name_i, recipe_i in linked_recipes.items():
            # remove recipe that are in recipe_name
            if recipe_name_i in linked_recipes[recipe_name]:
                if recipe_name_i in recipe_name_list:
                    recipe_name_list.remove(recipe_name_i)

            # remove recipe that contains recipe_name
            if recipe_name in recipe_i:
                if recipe_name_i in recipe_name_list:
                    recipe_name_list.remove(recipe_name_i)

                # remove all recipes that are in recipe_name_i
                for recipe_name_j in recipe_i:
                    if recipe_name_j in recipe_name_list:
                        recipe_name_list.remove(recipe_name_j)

        return recipe_name_list

    def getActive(self, recipe_name: str) -> bool:
        """ Returns whether the recipe is active """
        return self.config[recipe_name]['active']

    def getRecipeActive(self) -> List[str]:
        """ Returns list of active recipes """
        return [i for i in self.recipeNameList() if self.getActive(i)]

    # get Param
    def getParameter(self, recipe_name: str, param_name: str) -> dict:
        pos = self.getParameterPosition(recipe_name, param_name)
        return self.parameterList(recipe_name)[pos]

    def getParameterPosition(self, recipe_name: str, param_name: str) -> int:
        """ Returns the position of a parameter """
        return [i for i, param in enumerate(self.parameterList(recipe_name))
                if param['name'] == param_name][0]

    def parameterList(self, recipe_name: str) -> List[dict]:
        """ Returns the list of parameters in the recipe """
        return self.config[recipe_name]['parameter']

    def parameterNameList(self, recipe_name: str) -> List[str]:
        """ Returns the list of parameter names in the recipe """
        return [param['name'] for param in self.parameterList(recipe_name)] if (
            recipe_name in self.config) else []

    def getParameterElement(
            self, recipe_name: str, param_name: str) -> Union[None, Variable_og]:
        """ Returns the element of a parameter """
        param = self.getParameter(recipe_name, param_name)
        return param['element']

    def getLog(self, recipe_name: str, param_name: str) -> bool:
        """ Returns the log state of a parameter """
        param = self.getParameter(recipe_name, param_name)
        return param['log']

    def getNbPts(self, recipe_name: str, param_name: str) -> int:
        """ Returns the number of points of a parameter """
        param = self.getParameter(recipe_name, param_name)
        return param['nbpts']

    def getStep(self, recipe_name: str, param_name: str) -> float:
        """ Returns the step between points of a parameter """
        param = self.getParameter(recipe_name, param_name)
        return param['step']

    def getRange(self, recipe_name: str, param_name: str) -> Tuple[float, float]:
        """ Returns the range (start and end value) of a parameter """
        param = self.getParameter(recipe_name, param_name)
        return param['range']

    def getValues(self, recipe_name: str, param_name: str) -> List[float]:
        """ Returns the values of a parameter """
        param = self.getParameter(recipe_name, param_name)
        if 'values' in param:
            return param['values']
        else:
            startValue, endValue = param['range']
            nbpts = param['nbpts']
            logScale = param['log']

            # Creates the array of values for the parameter
            if logScale:
                paramValues = np.logspace(
                    m.log10(startValue), m.log10(endValue), nbpts, endpoint=True)
            else:
                paramValues = np.linspace(startValue, endValue, nbpts, endpoint=True)

            return paramValues

    def hasCustomValues(self, recipe_name: str, param_name: str) -> bool:
        """ Boolean to know if parameter has custom array """
        param = self.getParameter(recipe_name, param_name)
        return 'values' in param

    # get Step
    def stepList(self, recipe_name: str) -> List[dict]:
        """ Returns the list of steps in the recipe """
        return self.config[recipe_name]['recipe']

    def getRecipeStep(self, recipe_name: str, name: str) -> dict:
        """ Returns a dictionnary with recipe step information """
        pos = self.getRecipeStepPosition(recipe_name, name)
        return self.stepList(recipe_name)[pos]

    def getRecipeStepElement(
            self, recipe_name: str, name: str) -> Union[Variable_og, Action]:
        """ Returns the element of a recipe step """
        step_info = self.getRecipeStep(recipe_name, name)
        return step_info['element']

    def getRecipeStepType(self, recipe_name: str, name: str) -> str:
        """ Returns the type a recipe step """
        step_info = self.getRecipeStep(recipe_name, name)
        return step_info['stepType']

    def getRecipeStepValue(self, recipe_name: str, name: str) -> Any:
        """ Returns the value of a recipe step """
        step_info = self.getRecipeStep(recipe_name, name)
        return step_info['value']

    def getRecipeStepPosition(self, recipe_name: str, name: str) -> int:
        """ Returns the position of a recipe step in the recipe """
        return [i for i, step in enumerate(self.stepList(recipe_name)) if step['name'] == name][0]

    def getParamDataFrame(self, recipe_name: str, param_name: str) -> pd.DataFrame:
        """ Returns a pd.DataFrame with 'id' and 'param_name'
        columns containing the parameter array """
        paramValues = self.getValues(recipe_name, param_name)
        paramValues = eval_variable(paramValues)
        paramValues = create_array(paramValues)
        assert isinstance(paramValues, np.ndarray)
        data = pd.DataFrame()
        data["id"] = 1 + np.arange(len(paramValues))
        data[param_name] = paramValues

        return data

    def getConfigVariables(self) -> List[Tuple[str, Any]]:
        """ Returns a (key, value) list of parameters and measured step """
        listVariable = []
        listVariable.append(('ID', 1))

        for recipe_name in reversed(self.recipeNameList()):
            for param_name in self.parameterNameList(recipe_name):
                values = self.getValues(recipe_name, param_name)
                value = values if has_eval(values) else float(values[0])
                listVariable.append((param_name, value))
            for step in self.stepList(recipe_name):
                if step['stepType'] == 'measure':
                    listVariable.append((step['name'], step['value']))

        return listVariable

    # EXPORT IMPORT ACTIONS
    ###########################################################################

    def export(self, filename: str):
        """ Exports the current scan configuration in the provided file """
        configPars = self.create_configPars()

        with open(filename, "w") as configfile:
            json.dump(configPars, configfile, indent=4)

    def create_configPars(self) -> dict:
        """ Creates the current scan configuration parser """
        configPars = {}
        configPars['autolab'] = {'version': __version__,
                                 'timestamp': str(datetime.datetime.now())}

        for recipe_num, recipe_name in enumerate(self.recipeNameList()):
            recipe_i = self.config[recipe_name]
            pars_recipe_i = {}

            pars_recipe_i['name'] = str(recipe_name)
            pars_recipe_i['active'] = str(bool(recipe_i['active']))
            pars_recipe_i['parameter'] = {}

            for i, param in enumerate(recipe_i['parameter']):
                param_name = f"parameter_{i+1}"

                param_pars = {}

                param_pars['name'] = param['name']

                if param['element'] is not None:
                    param_pars['address'] = param['element'].address()
                else:
                    param_pars['address'] = "None"

                if 'values' in param:
                    if has_eval(param['values']):
                        param_pars['values'] = param['values']
                    else:
                        param_pars['values'] = array_to_str(
                            param['values'], threshold=1000000, max_line_width=9000000)
                else:
                    param_pars['nbpts'] = str(param['nbpts'])
                    param_pars['start_value'] = str(param['range'][0])
                    param_pars['end_value'] = str(param['range'][1])
                    param_pars['log'] = str(int(param['log']))

                pars_recipe_i['parameter'][param_name] = param_pars

            pars_recipe_i['recipe'] = {}

            for i, config_step in enumerate(recipe_i['recipe']):
                pars_recipe_i['recipe'][f'{i+1}_name'] = config_step['name']
                pars_recipe_i['recipe'][f'{i+1}_steptype'] = config_step['stepType']

                if config_step['stepType'] == 'recipe':
                    pars_recipe_i['recipe'][f'{i+1}_address'] = config_step['element']
                else:
                    pars_recipe_i['recipe'][f'{i+1}_address'] = config_step['element'].address()

                stepType = config_step['stepType']

                if stepType == 'set' or (stepType == 'action'
                                         and config_step['element'].type in [
                                             int, float, bool, str, bytes, tuple,
                                             np.ndarray, pd.DataFrame]):
                    value = config_step['value']

                    if has_eval(value):
                        valueStr = value
                    else:
                        if config_step['element'].type in [np.ndarray]:
                            valueStr = array_to_str(
                                value, threshold=1000000, max_line_width=9000000)
                        elif config_step['element'].type in [pd.DataFrame]:
                            valueStr = dataframe_to_str(value, threshold=1000000)
                        elif config_step['element'].type in [int, float, str]:
                            try:
                                valueStr = f'{value:.{self.precision}g}'
                            except:
                                valueStr = f'{value}'
                        elif config_step['element'].type in [bytes]:
                            valueStr = f'{value.decode()}'
                        else:  # for tuple and safety
                            valueStr = f'{value}'

                    pars_recipe_i['recipe'][f'{i+1}_value'] = valueStr

            configPars[f"recipe_{recipe_num+1}"] = pars_recipe_i

        # Add variables to config
        name_var_config = [var[0] for var in self.getConfigVariables()]
        names_var_user = list(VARIABLES)
        names_var_to_save = list(set(names_var_user) - set(name_var_config))

        var_to_save = {}
        for var_name in names_var_to_save:
            var = get_variable(var_name)

            if var is not None:
                assert is_Variable(var)
                value_raw = var.raw
                if isinstance(value_raw, np.ndarray):
                    valueStr = array_to_str(
                        value_raw, threshold=1000000, max_line_width=9000000)
                elif isinstance(value_raw, pd.DataFrame):
                    valueStr = dataframe_to_str(value_raw, threshold=1000000)
                elif isinstance(value_raw, (int, float, str)):
                    try: valueStr = f'{value_raw:.{self.precision}g}'
                    except: valueStr = f'{value_raw}'

                var_to_save[var_name] = valueStr

        if len(var_to_save) != 0: configPars['variables'] = var_to_save

        return configPars

    def import_configPars(self, filename: str, append: bool = False):
        """ Import a scan configuration from file with filename name """
        if not self.gui.scanManager.isStarted():
            if os.path.exists(filename):
                try:
                    legacy_configPars = configparser.ConfigParser()
                    legacy_configPars.read(filename)
                except:
                    try:
                        with open(filename, "r") as read_file:
                            configPars = json.load(read_file)
                    except Exception as e:
                        self.gui.setStatus(
                            f"Impossible to load configuration file: {e}",
                            10000, False)
                        return None
                else:
                    print("ConfigParser depreciated, now use json. " \
                          "Will convert this config to json if save it.")
                    configPars = {s: dict(legacy_configPars.items(s))
                                  for s in legacy_configPars.sections()}

                path = os.path.dirname(filename)
                PATHS['last_folder'] = path

                self.load_configPars(configPars, append=append)

                if not self._got_error: self.addNewConfig()
            else:
                self.gui.setStatus(
                    f"Configuration file {filename} doesn't exists", 5000)

    def load_configPars(self, configPars: dict, append: bool = False):
        """ Creates a config representing a scan form a configPars """
        self._got_error = False
        self.configHistory.active = False
        previous_config = self.config.copy()  # used to recover old config if error in loading new one
        already_loaded_devices = list_loaded_devices()

        try:
            # LEGACY <= 1.2
            try:
                LEGACY = (configPars["autolab"]["version"].startswith("1.0")
                          or configPars["autolab"]["version"].startswith("1.1.")
                          or configPars["autolab"]["version"] == "1.2")
                if LEGACY:
                    new_configPars = OrderedDict()
                    new_configPars["autolab"] = configPars["autolab"]

                    if 'initrecipe' in configPars:
                        new_configPars["recipe_1"] = {}
                        new_configPars["recipe_1"]['name'] = "init"
                        new_configPars["recipe_1"]['active'] = "True"
                        new_configPars["recipe_1"]['parameter'] = {}
                        new_configPars["recipe_1"]['parameter']["parameter_1"] = self._defaultParameterPars()
                        new_configPars["recipe_1"]['parameter']["parameter_1"]['name'] = 'init'
                        new_configPars["recipe_1"]['recipe'] = configPars['initrecipe']

                    new_configPars["recipe_2"] = {}
                    new_configPars["recipe_2"]['name'] = "recipe_1"
                    new_configPars["recipe_2"]['active'] = "True"
                    new_configPars["recipe_2"]['parameter'] = {}
                    new_configPars["recipe_2"]['parameter']["parameter_1"] = configPars['parameter']
                    new_configPars["recipe_2"]['recipe'] = configPars['recipe']

                    if 'endrecipe' in configPars:
                        new_configPars["recipe_3"] = {}
                        new_configPars["recipe_3"]['name'] = "end"
                        new_configPars["recipe_3"]['active'] = "True"
                        new_configPars["recipe_3"]['parameter'] = {}
                        new_configPars["recipe_3"]['parameter']["parameter_1"] = self._defaultParameterPars()
                        new_configPars["recipe_3"]['parameter']['name'] = 'end'
                        new_configPars["recipe_3"]['recipe'] = configPars['endrecipe']

                    configPars = new_configPars
            except: pass

            # Config
            config = OrderedDict()
            # to remove 'autolab' and 'variables' from recipe list
            recipeNameList = [i for i in list(configPars)
                              if i not in ('autolab', 'variables')]

            for recipe_num_name in recipeNameList:

                pars_recipe_i = configPars[recipe_num_name]

                if 'name' in pars_recipe_i:
                    recipe_name = pars_recipe_i['name']
                else:
                    recipe_name = recipe_num_name  # LEGACY <= 2.0b1

                config[recipe_name] = OrderedDict()
                recipe_i = config[recipe_name]

                recipe_i['name'] = recipe_name

                if 'active' in pars_recipe_i:
                    recipe_i['active'] = boolean(pars_recipe_i['active'])
                else:
                    recipe_i['active'] = True  # LEGACY <= 1.2.1

                assert 'parameter' in pars_recipe_i, (
                    f'Missing parameter in {recipe_name}')

                param_list = recipe_i['parameter'] = []

                # LEGACY <= 1.2.1
                if len(pars_recipe_i['parameter']) != 0:
                    if not isinstance(
                            list(pars_recipe_i['parameter'].values())[0],
                            dict):
                        pars_recipe_i['parameter'] = {
                            'parameter_1': pars_recipe_i['parameter']}

                for param_pars_name in pars_recipe_i['parameter']:
                    param_pars = pars_recipe_i['parameter'][param_pars_name]

                    param = {}

                    assert 'name' in param_pars, (
                        f"Missing name to {param_pars}")
                    param['name'] = param_pars['name']

                    assert 'address' in param_pars, (
                        f"Missing address to {param_pars}")
                    if param_pars['address'] == "None": element = None
                    else:
                        device_name = param_pars['address'].split('.')[0]
                        element = self.ask_get_element_by_address(device_name, param_pars['address'])

                    param['element'] = element

                    if 'values' in param_pars:
                        if has_eval(param_pars['values']):
                            values = param_pars['values']
                        else:
                            values = str_to_array(param_pars['values'])
                        if not has_eval(values):
                            assert np.ndim(values) == 1, (
                                f"Values must be one dimension array in parameter: {param['name']}")
                        param['values'] = values
                    else:
                        for key in ['nbpts', 'start_value', 'end_value', 'log']:
                            assert key in param_pars, "Missing parameter key {key}."

                        param['nbpts'] = int(param_pars['nbpts'])
                        start = float(param_pars['start_value'])
                        end = float(param_pars['end_value'])
                        param['range'] = (start, end)
                        param['log'] = bool(int(param_pars['log']))

                        if param['nbpts'] > 1:
                            param['step'] = abs(end - start) / (param['nbpts'] - 1)
                        else:
                            param['step'] = 0

                    param_list.append(param)

                recipe_i['recipe'] = []
                recipe = recipe_i['recipe']
                pars_recipe = pars_recipe_i['recipe']

                while True:
                    step = {}
                    i = len(recipe) + 1

                    if f'{i}_name' in pars_recipe:
                        step['name'] = pars_recipe[f'{i}_name']
                        name = step['name']

                        assert f'{i}_steptype' in pars_recipe, (
                            f"Missing stepType in step {i} ({name}).")
                        step['stepType'] = pars_recipe[f'{i}_steptype']

                        assert f'{i}_address' in pars_recipe, (
                            f"Missing address in step {i} ({name}).")
                        address = pars_recipe[f'{i}_address']

                        if step['stepType'] == 'recipe':
                            assert step['stepType'] != 'recipe', (
                                "Removed the recipe in recipe feature!")
                            element = address
                        else:
                            device_name = address.split('.')[0]
                            element = self.ask_get_element_by_address(device_name, address)

                        step['element'] = element

                        if (step['stepType'] == 'set') or (
                                step['stepType'] == 'action' and element.type in [
                                    int, float, bool, str, bytes, tuple,
                                    np.ndarray, pd.DataFrame]):
                            assert f'{i}_value' in pars_recipe, (
                                f"Missing value in step {i} ({name}).")
                            value = pars_recipe[f'{i}_value']

                            try:
                                try:
                                    assert has_eval(value), (
                                        "Need $eval: to evaluate the given string")
                                except:
                                    # Type conversions
                                    if element.type in [int]:
                                        value = int(value)
                                    elif element.type in [float]:
                                        value = float(value)
                                    elif element.type in [str]:
                                        value = str(value)
                                    elif element.type in [bytes]:
                                        value = value.encode()
                                    elif element.type in [bool]:
                                        value = boolean(value)
                                    elif element.type in [tuple]:
                                        value = str_to_tuple(value)
                                    elif element.type in [np.ndarray]:
                                        value = str_to_array(value)
                                    elif element.type in [pd.DataFrame]:
                                        value = str_to_dataframe(value)
                                    else:
                                        assert has_eval(value), (
                                            "Need $eval: to evaluate the given string")
                            except:
                                raise ValueError(f"Error with {i}_value = {value}. Expect either {element.type} or device address. Check address or open device first.")

                            step['value'] = value
                        else:
                            step['value'] = None

                        recipe.append(step)
                    else:
                        break
            if append:
                for conf in config.values():
                    recipe_name = conf['name']
                    if recipe_name in self.recipeNameList():
                        new_recipe_name = self.getUniqueNameRecipe('recipe')
                    else:
                        new_recipe_name = recipe_name

                    self.config[new_recipe_name] = conf
            else:
                self.config = config

            if 'variables' in configPars:
                var_dict = configPars['variables']

                add_vars = []
                for var_name, raw_value in var_dict.items():
                    if not has_eval(raw_value):
                        raw_value = str_to_data(raw_value)
                    add_vars.append((var_name, raw_value))

                update_from_config(add_vars)

        except Exception as error:
            self._got_error = True
            self.gui.setStatus(
                f"Impossible to load configuration file: {error}", 10000, False)
            self.config = previous_config
        else:
            self.gui._resetRecipe()
            self.gui.setStatus("Configuration file loaded successfully", 5000)
        finally:
            self.configHistory.active = True
            self.update_loaded_devices(already_loaded_devices)

    # UNDO REDO ACTIONS
    ###########################################################################

    def undoClicked(self):
        """ Undos an action from parameter, recipe or range """
        if not self.gui.scanManager.isStarted():
            self.configHistory.go_down()
            self.changeConfig()

    def redoClicked(self):
        """ Redos an action from parameter, recipe or range """
        if not self.gui.scanManager.isStarted():
            self.configHistory.go_up()
            self.changeConfig()

    def changeConfig(self):
        """ Gets config from history and enables/disables undo/redo button accordingly """
        configPars = self.configHistory.get_data()

        if configPars is not None:
            self.load_configPars(configPars)

        self.updateUndoRedoButtons()
        self.updateVariableConfig()
        self.gui.setStatus('')

    def updateUndoRedoButtons(self):
        """ enables/disables undo/redo button depending on history """
        if self.configHistory.index == 0:
            self.gui.undo.setEnabled(False)
        else:
            self.gui.undo.setEnabled(True)

        if self.configHistory.index == len(self.configHistory)-1:
            self.gui.redo.setEnabled(False)
        else:  # implicit <
            self.gui.redo.setEnabled(True)
