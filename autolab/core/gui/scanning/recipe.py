# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:15:26 2019

@author: qchat
"""

import numpy as np
import pandas as pd
from qtpy import QtCore, QtWidgets, QtGui

from .customWidgets import MyQTreeWidget, MyQTabWidget, MyQTreeWidgetItem
from ..icons import icons
from ..GUI_utilities import MyInputDialog, qt_object_exists
from ...config import get_scanner_config
from ...variables import has_eval
from ...utilities import (clean_string, str_to_array, array_to_str,
                          str_to_dataframe, dataframe_to_str, str_to_tuple)


class RecipeManager:
    """ Manage a recipe from a scan """

    def __init__(self, gui: QtWidgets.QMainWindow, recipe_name: str):

        self.gui = gui  # gui is scanner
        self.recipe_name = recipe_name

        # Import Autolab config
        scanner_config = get_scanner_config()
        self.precision = scanner_config['precision']

        self.defaultItemBackground = None

        # Recipe frame
        frameRecipe = QtWidgets.QFrame()

        # Tree configuration
        self.tree = MyQTreeWidget(frameRecipe, self.gui, self.recipe_name)
        self.tree.setHeaderLabels(['Step name', 'Action', 'Element address',
                                   'Type', 'Value', 'Unit'])
        header = self.tree.header()
        header.setMinimumSectionSize(20)
        header.setStretchLastSection(False)
        header.resizeSection(0, 95)
        header.resizeSection(1, 55)
        header.resizeSection(2, 115)
        header.resizeSection(3, 35)
        header.resizeSection(4, 110)
        header.resizeSection(5, 32)
        header.setMaximumSize(16777215, 16777215)
        self.tree.itemDoubleClicked.connect(self.itemDoubleClicked)
        self.tree.reorderSignal.connect(self.orderChanged)
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.tree.setDropIndicatorShown(True)
        self.tree.setAlternatingRowColors(True)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.tree.customContextMenuRequested.connect(self.rightClick)
        self.tree.setMinimumSize(0, 200)
        self.tree.setMaximumSize(16777215, 16777215)
        self.tree.setIndentation(0)

        layoutRecipe = QtWidgets.QVBoxLayout(frameRecipe)
        layoutRecipe.addWidget(self.tree)

        # Qframe and QTab for close+parameter+scanrange+recipe
        frameAll = QtWidgets.QFrame()
        layoutAll = QtWidgets.QVBoxLayout(frameAll)
        layoutAll.setContentsMargins(0,0,0,0)
        layoutAll.setSpacing(0)

        layoutAll.addWidget(frameRecipe, stretch=1)

        frameAll2 = MyQTabWidget(frameAll, self.gui, self.recipe_name)
        self._frame = frameAll2
        self._layoutAll = layoutAll
        self.gui.verticalLayout_recipe.addWidget(self._frame)

    def __del__(self):
        self._removeWidget()

    def _removeWidget(self):
        if hasattr(self, '_frame'):
            try:
                self._frame.hide()
                self._frame.deleteLater()
                del self._frame
            except: pass

    def _activateTree(self, active: bool):
        self._frame.setTabEnabled(0, bool(active))

    def orderChanged(self, event):
        newOrder = [self.tree.topLevelItem(i).text(0)
                    for i in range(self.tree.topLevelItemCount())]
        self.gui.configManager.setRecipeStepOrder(self.recipe_name, newOrder)

    def refresh(self):
        """ Refreshs the whole scan recipe displayed from the configuration center """
        self.tree.clear()

        for step in self.gui.configManager.stepList(self.recipe_name):
            # Loading step informations
            item = MyQTreeWidgetItem(self.tree, step, self)
            self.defaultItemBackground = item.background(0)

        self.tree.setFocus()  # needed for ctrl+z ctrl+y on recipe
        # toggle recipe
        active = bool(self.gui.configManager.getActive(self.recipe_name))
        self.gui._activateRecipe(self.recipe_name, active)

    def rightClick(self, position: QtCore.QPoint):
        """ Provides a menu where the user right clicked to manage a recipe """
        if not self.gui.scanManager.isStarted():
            item = self.tree.itemAt(position)

            if item is not None:
                name = item.text(0)
                stepType = self.gui.configManager.getRecipeStepType(
                    self.recipe_name, name)
                element = self.gui.configManager.getRecipeStepElement(
                    self.recipe_name, name)

                menuActions = {}
                menu = QtWidgets.QMenu()
                menuActions['copy'] = menu.addAction("Copy")
                menuActions['copy'].setIcon(icons['copy'])
                menuActions['copy'].setShortcut(QtGui.QKeySequence("Ctrl+C"))
                menu.addSeparator()

                if stepType == 'set' or (stepType == 'action' and element.type in [
                        int, float, bool, str, tuple, np.ndarray, pd.DataFrame]):
                    menuActions['setvalue'] = menu.addAction("Set value")
                    menuActions['setvalue'].setIcon(icons['write'])

                menuActions['remove'] = menu.addAction("Remove")
                menuActions['remove'].setIcon(icons['remove'])
                menuActions['remove'].setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete))

                menuActions['rename'] = menu.addAction("Rename")
                menuActions['rename'].setIcon(icons['rename'])
                menuActions['rename'].setShortcut(QtGui.QKeySequence("Ctrl+R"))

                choice = menu.exec_(self.tree.viewport().mapToGlobal(position))

                if choice == menuActions['copy']:
                    self.copyStep(name)
                elif choice == menuActions['rename']:
                    self.renameStep(name)
                elif choice == menuActions['remove']:
                    self.removeStep(name)
                elif 'setvalue' in menuActions and choice == menuActions['setvalue']:
                    self.setStepValue(name)
            else:
                menuActions = {}
                menu = QtWidgets.QMenu()
                menuActions['paste'] = menu.addAction("Paste")
                menuActions['paste'].setIcon(icons['paste'])
                menuActions['paste'].setShortcut(QtGui.QKeySequence("Ctrl+V"))
                menuActions['paste'].setEnabled(self.gui._copy_step_info is not None)
                choice = menu.exec_(self.tree.viewport().mapToGlobal(position))

                if choice == menuActions['paste']:
                    self.pasteStep()

            # TODO: disabled this feature has it is not good in its current state
            #     config = self.gui.configManager.config
            #     if len(config) > 1:

            #         recipe_name_list = self.gui.configManager.getAllowedRecipe(self.recipe_name)

            #         menuActions = {}
            #         menu = QtWidgets.QMenu()
            #         for recipe_name in recipe_name_list:
            #             menuActions[recipe_name] = menu.addAction(f'Add {recipe_name}')
            #             menuActions[recipe_name].setIcon(icons['recipe'])

            #         if len(recipe_name_list) != 0:
            #             choice = menu.exec_(self.tree.viewport().mapToGlobal(position))

            #         for recipe_name in recipe_name_list:
            #             if choice == menuActions[recipe_name]:
            #                 self.gui.configManager.configHistory.active = False
            #                 active = self.gui.configManager.getActive(recipe_name)

            #                 if active: self.gui.configManager.activateRecipe(
            #                         recipe_name, not active)  # disable

            #                 for param in self.gui.configManager.parameterList(recipe_name):
            #                     newName = self.gui.configManager.getUniqueName(self.recipe_name, param['name'])
            #                     self.gui.configManager.renameParameter(
            #                         recipe_name, param['name'], newName)

            #                 for step in self.gui.configManager.stepList(recipe_name):
            #                     newName = self.gui.configManager.getUniqueName(self.recipe_name, step['name'])
            #                     self.gui.configManager.renameRecipeStep(
            #                         recipe_name, step['name'], newName)

            #                 self.gui.configManager.configHistory.active = True

            #                 self.gui.configManager.addRecipeStep(
            #                     self.recipe_name, 'recipe',
            #                     recipe_name,  f'do_{recipe_name}')

            #                 break

    def copyStep(self, name: str):
        """ Copy step information """
        self.gui._copy_step_info = self.gui.configManager.getRecipeStep(
            self.recipe_name, name)

    def pasteStep(self):
        """ Paste step information """
        step_info = self.gui._copy_step_info
        if step_info is not None:
            self.gui.configManager.addRecipeStep(
                self.recipe_name, step_info['stepType'],
                step_info['element'], step_info['name'],
                value=step_info['value'])

    def renameStep(self, name: str):
        """ Prompts the user for a new step name and apply it to the selected step """
        newName, state = QtWidgets.QInputDialog.getText(
            self.gui, name, f"Set {name} new name",
            QtWidgets.QLineEdit.Normal, name)

        newName = clean_string(newName)
        if newName != '':
            self.gui.configManager.renameRecipeStep(
                self.recipe_name, name, newName)

    def removeStep(self, name: str):
        self.gui.configManager.delRecipeStep(self.recipe_name, name)

    def setStepValue(self, name: str):
        """ Prompts the user for a new step value and apply it to the selected step """
        element = self.gui.configManager.getRecipeStepElement(
            self.recipe_name, name)
        value = self.gui.configManager.getRecipeStepValue(
            self.recipe_name, name)
        # Default value displayed in the QInputDialog
        if has_eval(value):
            defaultValue = f'{value}'
        else:
            if element.type in [np.ndarray]:
                defaultValue = array_to_str(value, threshold=1000000, max_line_width=100)
            elif element.type in [pd.DataFrame]:
                defaultValue = dataframe_to_str(value, threshold=1000000)
            if element.type in [bytes] and isinstance(value, bytes):
                defaultValue = f'{value.decode()}'
            else:
                try:
                    defaultValue = f'{value:.{self.precision}g}'
                except (ValueError, TypeError):
                    defaultValue = f'{value}'

        main_dialog = MyInputDialog(self.gui, name)
        main_dialog.setWindowModality(QtCore.Qt.ApplicationModal)  # block GUI interaction
        main_dialog.setTextValue(defaultValue)
        main_dialog.show()

        if main_dialog.exec_() == QtWidgets.QInputDialog.Accepted:
            value = main_dialog.textValue()

            try:
                try:
                    assert has_eval(value), "Need $eval: to evaluate the given string"
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
                        if value == "False": value = False
                        elif value == "True": value = True
                        value = int(value)
                        assert value in [0, 1]
                        value = bool(value)
                    elif element.type in [tuple]:
                        value = str_to_tuple(value)
                    # OPTIMIZE: bad with large data (truncate), but nobody will use it for large data right?
                    elif element.type in [np.ndarray]:
                        value = str_to_array(value)
                    elif element.type in [pd.DataFrame]:
                        value = str_to_dataframe(value)
                    else:
                        assert has_eval(value), "Need $eval: to evaluate the given string"
                # Apply modification
                self.gui.configManager.setRecipeStepValue(
                    self.recipe_name, name, value)
            except Exception as er:
                self.gui.setStatus(f"Can't set step: {er}", 10000, False)
                pass

        main_dialog.deleteLater()

    def itemDoubleClicked(self, item: QtWidgets.QTreeWidgetItem, column: int):
        """ Executes an action depending where the user double clicked """
        if not self.gui.scanManager.isStarted():
            name = item.text(0)
            stepType = self.gui.configManager.getRecipeStepType(self.recipe_name, name)
            element = self.gui.configManager.getRecipeStepElement(self.recipe_name, name)

            if column == 0:
                self.renameStep(name)
            elif column == 4:
                if stepType == 'set' or (stepType == 'action' and element.type in [
                        int, float, bool, str, bytes, tuple, np.ndarray, pd.DataFrame]):
                    self.setStepValue(name)

    def setStepProcessingState(self, name: str, state: str):
        """ Sets the background color of a recipe step during the scan """
        if not qt_object_exists(self.tree):
            return None
        item = self.tree.findItems(name, QtCore.Qt.MatchExactly, 0)[0]

        if state is None:
            item.setBackground(0, self.defaultItemBackground)
        elif state == 'started':
            item.setBackground(0, QtGui.QColor('#ff8c1a'))
        elif state == 'finished':
            item.setBackground(0, QtGui.QColor('#70db70'))

    def resetStepsProcessingState(self):
        """ Resets the background color of a recipe once the scan is finished """
        for name in self.gui.configManager.getNames(self.recipe_name, option='recipe'):
            self.setStepProcessingState(name, None)


#
#class Step:
#
#    def __init__(self,name):
#        self.name = None
#
#    def set_name(self,name):
#        self.name = name
#
#    def message(self,mess):
#        return f'Step {self.name} (self.step_type): {mess}'
#
#
#class ExecuteActionStep(Step):
#    step_type = 'execute_action'
#
#    def __init__(self,name,element,value=None):
#        Step.__init__(self,name)
#
#        # Element
#        assert element._element_type == 'action', self.message('The element has to be an Action')
#        self.action = element
#
#        # Value
#        if self.action.has_parameter :
#            assert value is not None, self.message('Parameter value required')
#            self.set_value(value)
#        else :
#            assert value is None, self.message('This action has no parameter')
#
#    def set_value(self,value):
#        assert self.action.has_parameter, self.message('This action has no parameter')
#        try :
#            self.value = self.action.type(value)
#        except :
#            raise ValueError(self.message(f'Impossible to convert {value} in type {self.element.type.__name__}'))
#
#    def get_value(self):
#        return self.value
#
#    def run(self):
#        if self.element.has_parameter :
#            assert self.value is not None
#            self.action(self.value)
#        else :
#            self.action()
#
#
#
#class ScanVariableStep:
#    step_type = 'scan_variable'
#
#    def __init__(self,name,element):
#
#        Step.__init__(self,name)
#
#        # Element
#        assert element._element_type == 'variable', self.message('The element has to be a Variable')
#        assert element.writable is True, self.message('The Variable has to be writable')
#        self.variable = element
#
#
#class ScanVariableEndStep:
#    step_type = 'scan_variable_end'
#
#    def __init__(self,name):
#
#
#    def run(self):
#
#
#
#class MeasureVariableStep:
#    step_type = 'measure_variable'
#
#    def __init__(self,name,element):
#        Step.__init__(self,name)
#
#        # Element
#        assert element._element_type == 'variable', self.message('The element has to be a Variable')
#        assert element.readable is True, self.message('The Variable has to be readable')
#        self.variable = element
#
#
#    def run(self):
#        return self.variable()
#
#
#
#
#class SetVariableStep:
#    step_type = 'set_variable'
#
#    def __init__(self,name,element,value):
#        Step.__init__(self,name)
#
#        # Element
#        assert element._element_type == 'variable', self.message('The element has to be a Variable')
#        assert element.writable is True, self.message('The Variable has to be writable')
#        self.variable = element
#
#        # Value
#        self.set_value(value)
#
#
#    def set_value(self,value):
#        try :
#            self.value = self.variable.type(value)
#        except :
#            raise ValueError(self.message(f'Impossible to convert {value} in type {self.element.type.__name__}'))
#
#    def get_value(self):
#        return self.value
#
#    def run(self):
#        self.variable(self.value)
#
#
#    def prompt_value(self):
#
#        # Default value displayed in the QInputDialog
#        if self.variable.type == str :
#            defaultValue = f'{self.value}'
#        else :
#            defaultValue = f'{self.value:g}'
#
#        value,state = QtWidgets.QInputDialog.getText(self.gui,
#                                                     name,
#                                                     f"Set {name} value",
#                                                     QtWidgets.QLineEdit.Normal, defaultValue)
#
#        if value != '' :
#
#            try :
#
#                # Type conversions
#                if element.type in [int]:
#                    value = int(value)
#                elif element.type in [float] :
#                    value = float(value)
#                elif element.type in [str] :
#                    value = str(value)
#                elif element.type in [bool]:
#                    value = int(value)
#                    assert value in [0,1]
#                    value = bool(value)
#
#                # Apply modification
#                self.gui.configManager.setRecipeStepValue(name,value)
#
#            except :
#                pass
#
