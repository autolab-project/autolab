# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:14:28 2019

@author: qchat
"""
import math as m

from qtpy import QtWidgets

from .display import DisplayValues


class RangeManager:
    """ Manage the range of a parameter """

    def __init__(self, gui: QtWidgets.QMainWindow, recipe_name: str):

        self.gui = gui
        self.recipe_name = recipe_name

        self.scanLog_checkBox = self.gui.recipeDict[self.recipe_name]['recipeManager'].scanLog_checkBox
        self.nbpts_lineEdit = self.gui.recipeDict[self.recipe_name]['recipeManager'].nbpts_lineEdit
        self.step_lineEdit = self.gui.recipeDict[self.recipe_name]['recipeManager'].step_lineEdit
        self.start_lineEdit = self.gui.recipeDict[self.recipe_name]['recipeManager'].start_lineEdit
        self.end_lineEdit = self.gui.recipeDict[self.recipe_name]['recipeManager'].end_lineEdit
        self.mean_lineEdit = self.gui.recipeDict[self.recipe_name]['recipeManager'].mean_lineEdit
        self.width_lineEdit = self.gui.recipeDict[self.recipe_name]['recipeManager'].width_lineEdit
        self.displayParameter_pushButton = self.gui.recipeDict[self.recipe_name]['recipeManager'].displayParameter_pushButton

        # Widget 'return pressed' signal connections
        self.scanLog_checkBox.stateChanged.connect(self.scanLogChanged)
        self.nbpts_lineEdit.returnPressed.connect(self.nbptsChanged)
        self.step_lineEdit.returnPressed.connect(self.stepChanged)
        self.start_lineEdit.returnPressed.connect(self.startChanged)
        self.end_lineEdit.returnPressed.connect(self.endChanged)
        self.mean_lineEdit.returnPressed.connect(self.meanChanged)
        self.width_lineEdit.returnPressed.connect(self.widthChanged)

        # Widget 'text edited' signal connections
        self.nbpts_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.nbpts_lineEdit,'edited'))
        self.step_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.step_lineEdit,'edited'))
        self.start_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.start_lineEdit,'edited'))
        self.end_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.end_lineEdit,'edited'))
        self.mean_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.mean_lineEdit,'edited'))
        self.width_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.width_lineEdit,'edited'))

        # Push button
        self.displayParameter_pushButton.clicked.connect(self.displayParameterButtonClicked)

        self.displayParameter = DisplayValues(self.gui, "Parameter", size=(250, 400))

        self.point_or_step = "point"
        self.refresh()

    def displayParameterButtonClicked(self):
        """ This function opens a window showing the parameter array that will
            be used in the scan """
        if not self.displayParameter.active:
            self.displayParameter.refresh(
                self.gui.configManager.getParamDataFrame(self.recipe_name))

        self.displayParameter.show()

    def refresh(self):
        """ This function refreshes all the values displayed of the scan
            configuration from the configuration center """

        xrange = self.gui.configManager.getRange(self.recipe_name)

        # Start
        start = xrange[0]
        self.start_lineEdit.setText(f'{start:g}')
        self.gui.setLineEditBackground(self.start_lineEdit, 'synced')

        # End
        end = xrange[1]
        self.end_lineEdit.setText(f'{end:g}')
        self.gui.setLineEditBackground(self.end_lineEdit, 'synced')

        # Mean
        mean = (start + end) / 2
        self.mean_lineEdit.setText(f'{mean:g}')
        self.gui.setLineEditBackground(self.mean_lineEdit, 'synced')

        # Width
        width = abs(end - start)
        self.width_lineEdit.setText(f'{width:g}')
        self.gui.setLineEditBackground(self.width_lineEdit, 'synced')

        # Nbpts
        nbpts = self.gui.configManager.getNbPts(self.recipe_name)
        step = self.gui.configManager.getStep(self.recipe_name)

        self.nbpts_lineEdit.setText(f'{nbpts:g}')
        self.gui.setLineEditBackground(self.nbpts_lineEdit, 'synced')

        # Log
        log: bool = self.gui.configManager.getLog(self.recipe_name)
        self.scanLog_checkBox.setChecked(log)

        # Step
        if log:
            self.step_lineEdit.setEnabled(False)
            self.step_lineEdit.setText('')
        else:
            self.step_lineEdit.setText(f'{step:g}')
            self.step_lineEdit.setEnabled(True)

        self.gui.setLineEditBackground(self.step_lineEdit, 'synced')

        if self.displayParameter.active:
            self.displayParameter.refresh(
                self.gui.configManager.getParamDataFrame(self.recipe_name))

    def nbptsChanged(self):
        """ This function changes the number of point of the scan """
        value = self.nbpts_lineEdit.text()

        try:
            value = int(float(value))
            assert value > 0
            self.gui.configManager.setNbPts(self.recipe_name, value)
            self.point_or_step = "point"
        except:
            self.refresh()

    def stepChanged(self):
        """ This function changes the step size of the scan """
        value = self.step_lineEdit.text()

        try:
            if value == "inf" or float(value) == 0:
                self.nbpts_lineEdit.setText('1')
                self.nbptsChanged()
                return

            value = float(value)
            assert value > 0

            self.gui.configManager.setStep(self.recipe_name, value)

            self.point_or_step = "step"
        except:
            self.refresh()

    def startChanged(self):
        """ This function changes the start value of the scan """
        value = self.start_lineEdit.text()

        try:
            value=float(value)
            log: bool = self.gui.configManager.getLog(self.recipe_name)
            if log: assert value > 0

            xrange = list(self.gui.configManager.getRange(self.recipe_name))
            xrange[0] = value
            self.gui.configManager.setRange(self.recipe_name, xrange)
        except:
            self.refresh()

    def endChanged(self):
        """ This function changes the end value of the scan """
        value = self.end_lineEdit.text()

        try:
            value = float(value)
            log:bool = self.gui.configManager.getLog(self.recipe_name)
            if log: assert value > 0
            xrange = list(self.gui.configManager.getRange(self.recipe_name))
            xrange[1] = value
            self.gui.configManager.setRange(self.recipe_name, xrange)
        except :
            self.refresh()

    def meanChanged(self):
        """ This function changes the mean value of the scan """
        value = self.mean_lineEdit.text()

        try:
            value = float(value)
            log: bool = self.gui.configManager.getLog(self.recipe_name)
            if log: assert value > 0
            xrange = list(self.gui.configManager.getRange(self.recipe_name))
            xrange_new = xrange.copy()
            xrange_new[0] = value - (xrange[1] - xrange[0])/2
            xrange_new[1] = value + (xrange[1] - xrange[0])/2
            assert xrange_new[0] > 0
            assert xrange_new[1] > 0
            self.gui.configManager.setRange(self.recipe_name, xrange_new)
        except:
            self.refresh()

    def widthChanged(self):
        """ This function changes the width of the scan """
        value = self.width_lineEdit.text()

        try:
            value = float(value)
            log: bool = self.gui.configManager.getLog(self.recipe_name)
            if log: assert value > 0
            xrange = list(self.gui.configManager.getRange(self.recipe_name))
            xrange_new = xrange.copy()
            xrange_new[0] = (xrange[1]+xrange[0])/2 - value/2
            xrange_new[1] = (xrange[1]+xrange[0])/2 + value/2
            assert xrange_new[0] > 0
            assert xrange_new[1] > 0
            self.gui.configManager.setRange(self.recipe_name, xrange_new)
        except:
            self.refresh()

    def scanLogChanged(self):
        """ This function changes the log state of the scan """
        state: bool = self.scanLog_checkBox.isChecked()

        if state:
            self.point_or_step = "point"
            xrange = list(self.gui.configManager.getRange(self.recipe_name))
            change = False

            if xrange[1] <= 0:
                xrange[1] = 1
                change = True

            if xrange[0] <= 0:
                xrange[0] = 10**(m.log10(xrange[1]) - 1)
                change = True

            if change: self.gui.configManager.setRange(self.recipe_name, xrange)

        self.gui.configManager.setLog(self.recipe_name, state)
