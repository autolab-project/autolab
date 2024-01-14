# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:13:45 2019

@author: qchat
"""

from qtpy import QtWidgets

from . import main


class ParameterManager:
    """ Manage the parameter from a recipe in a scan """

    def __init__(self, gui: QtWidgets.QMainWindow, recipe_name: str):

        self.gui = gui
        self.recipe_name = recipe_name

        # TODO: now should be list for parameters
        self.unit_label = self.gui.recipeDict[self.recipe_name]['recipeManager'].unit_label
        self.parameterName_lineEdit = self.gui.recipeDict[self.recipe_name]['recipeManager'].parameterName_lineEdit
        self.parameterAddress_label = self.gui.recipeDict[self.recipe_name]['recipeManager'].parameterAddress_label

        self.displayParameter = self.gui.recipeDict[self.recipe_name]['rangeManager'].displayParameter  # TODO: move displayParameter to main (should do it when moving tree creation from recipe to main)
        self.parameterName_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.parameterName_lineEdit,'edited'))
        self.parameterName_lineEdit.returnPressed.connect(self.nameChanged)
        self.parameterName_lineEdit.setEnabled(False)

        self.refresh()

    def refresh(self):
        """ This functions refreshes all the values of the name and address of the scan parameter,
        from the configuration center """
        for parameter in self.gui.configManager.parameterList(self.recipe_name):
            # Paramater name, address and unit
            param_name = parameter['name']
            element = self.gui.configManager.getParameterElement(self.recipe_name, param_name)

            if element is not None:
                address = element.address()
                unit = element.unit
            else:
                address = 'None'
                unit = ''

            self.parameterName_lineEdit.setEnabled(True)
            self.parameterName_lineEdit.setText(param_name)
            self.gui.setLineEditBackground(self.parameterName_lineEdit, 'synced')
            self.parameterAddress_label.setText(address)
            if unit in ('', None):
                self.unit_label.setText('')
            else:
                self.unit_label.setText(f'({unit})')

            if self.displayParameter.active:
                self.displayParameter.refresh(
                    self.gui.configManager.getParamDataFrame(self.recipe_name, param_name))

    def nameChanged(self):
        """ This function changes the name of the scan parameter """
        newName = self.parameterName_lineEdit.text()
        newName = main.cleanString(newName)

        if newName != '':
            param_name = self.gui.configManager.TEMPgetParameterName(self.recipe_name)
            self.gui.configManager.renameParameter(self.recipe_name, param_name, newName)

    # PROCESSING STATE BACKGROUND
    ###########################################################################

    def setProcessingState(self, state: str):
        """ This function set the background color of the parameter address during the scan """
        if state == 'idle':
            self.parameterAddress_label.setStyleSheet("font-size: 9pt;")
        else :
            if state == 'started': color = '#ff8c1a'
            if state == 'finished': color = '#70db70'
            self.parameterAddress_label.setStyleSheet(f"background-color: {color}; font-size: 9pt;")
