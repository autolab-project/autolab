# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:13:45 2019

@author: qchat
"""

import math as m

import numpy as np
from qtpy import QtCore, QtWidgets, QtGui

from .display import DisplayValues
from .customWidgets import parameterQFrame
from .. import variables
from ..GUI_utilities import get_font_size, setLineEditBackground
from ..icons import icons
from ...utilities import clean_string, str_to_array, array_to_str, create_array


class ParameterManager:
    """ Manage the parameter from a recipe in a scan """

    def __init__(self, gui: QtWidgets.QMainWindow,
                 recipe_name: str, param_name: str):

        self.gui = gui
        self.recipe_name = recipe_name
        self.param_name = param_name

        self.point_or_step = "point"

        self._font_size = get_font_size() + 1

        # Parameter frame
        mainFrame = parameterQFrame(self.gui, self.recipe_name, self.param_name)
        mainFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        mainFrame.setMinimumSize(0, 32+60)
        mainFrame.setMaximumSize(16777215, 32+60)
        self.mainFrame = mainFrame

        self.mainFrame.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mainFrame.customContextMenuRequested.connect(self.rightClick)

        ## 1st row frame: Parameter
        frameParameter = QtWidgets.QFrame(mainFrame)
        frameParameter.setMinimumSize(0, 32)
        frameParameter.setMaximumSize(16777215, 32)
        frameParameter.setToolTip(f"Drag and drop a variable or use the right click option of a variable from the control panel to add a recipe to the tree: {self.recipe_name}")

        ### Name
        parameterName_lineEdit = QtWidgets.QLineEdit('', frameParameter)
        parameterName_lineEdit.setMinimumSize(0, 20)
        parameterName_lineEdit.setMaximumSize(16777215, 20)
        parameterName_lineEdit.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        parameterName_lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        parameterName_lineEdit.setToolTip('Name of the parameter, as it will displayed in the data')
        parameterName_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(parameterName_lineEdit,'edited'))
        parameterName_lineEdit.returnPressed.connect(self.nameChanged)
        parameterName_lineEdit.setEnabled(False)
        self.parameterName_lineEdit = parameterName_lineEdit

        ### Address
        parameterAddressIndicator_label = QtWidgets.QLabel("Address:", frameParameter)
        parameterAddressIndicator_label.setMinimumSize(0, 20)
        parameterAddressIndicator_label.setMaximumSize(16777215, 20)
        parameterAddressIndicator_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        parameterAddress_label = QtWidgets.QLabel("<variable>", frameParameter)
        parameterAddress_label.setMinimumSize(0, 20)
        parameterAddress_label.setMaximumSize(16777215, 20)
        parameterAddress_label.setAlignment(QtCore.Qt.AlignCenter)
        parameterAddress_label.setToolTip('Address of the parameter')
        self.parameterAddress_label = parameterAddress_label

        ### Unit
        unit_label = QtWidgets.QLabel("uA", frameParameter)
        unit_label.setMinimumSize(0, 20)
        unit_label.setMaximumSize(16777215, 20)
        unit_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.unit_label = unit_label

        ### displayParameter button
        self.displayParameter = DisplayValues("Parameter", size=(250, 400))
        self.displayParameter.setWindowIcon(QtGui.QIcon(icons['ndarray']))
        displayParameter_pushButton = QtWidgets.QPushButton("Parameter", frameParameter)
        displayParameter_pushButton.setMinimumSize(0, 23)
        displayParameter_pushButton.setMaximumSize(16777215, 23)
        self.displayParameter_pushButton = displayParameter_pushButton
        self.displayParameter_pushButton.clicked.connect(self.displayParameterButtonClicked)

        ## 1sr row layout: Parameter
        layoutParameter = QtWidgets.QHBoxLayout(frameParameter)
        layoutParameter.addWidget(parameterName_lineEdit)
        layoutParameter.addWidget(unit_label)
        layoutParameter.addWidget(parameterAddressIndicator_label)
        layoutParameter.addWidget(parameterAddress_label)
        layoutParameter.addWidget(displayParameter_pushButton)

        frameScanRange = QtWidgets.QFrame(mainFrame)
        frameScanRange.setMinimumSize(0, 60)
        frameScanRange.setMaximumSize(16777215, 60)
        self.frameScanRange = frameScanRange

        ## 2nd row frame: Range
        frameScanRange_linLog = QtWidgets.QFrame(frameScanRange)
        frameScanRange_linLog.setMinimumSize(0, 60)
        frameScanRange_linLog.setMaximumSize(16777215, 60)
        self.frameScanRange_linLog = frameScanRange_linLog

        ### first grid widgets: start, stop
        labelStart = QtWidgets.QLabel("Start", frameScanRange_linLog)
        start_lineEdit = QtWidgets.QLineEdit('0', frameScanRange_linLog)
        start_lineEdit.setToolTip('Start value of the scan')
        start_lineEdit.setMinimumSize(0, 20)
        start_lineEdit.setMaximumSize(16777215, 20)
        start_lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.start_lineEdit = start_lineEdit

        labelEnd = QtWidgets.QLabel("End", frameScanRange_linLog)
        end_lineEdit = QtWidgets.QLineEdit('10', frameScanRange_linLog)
        end_lineEdit.setMinimumSize(0, 20)
        end_lineEdit.setMaximumSize(16777215, 20)
        end_lineEdit.setToolTip('End value of the scan')
        end_lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.end_lineEdit = end_lineEdit

        ### first grid layout: start, stop
        startEndGridLayout = QtWidgets.QGridLayout(frameScanRange_linLog)
        startEndGridLayout.addWidget(labelStart, 0, 0)
        startEndGridLayout.addWidget(start_lineEdit, 0, 1)
        startEndGridLayout.addWidget(labelEnd, 1, 0)
        startEndGridLayout.addWidget(end_lineEdit, 1, 1)

        startEndGridWidget = QtWidgets.QWidget(frameScanRange_linLog)
        startEndGridWidget.setLayout(startEndGridLayout)

        ### second grid widgets: mean, width
        labelMean = QtWidgets.QLabel("Mean", frameScanRange_linLog)
        mean_lineEdit = QtWidgets.QLineEdit('5', frameScanRange_linLog)
        mean_lineEdit.setMinimumSize(0, 20)
        mean_lineEdit.setMaximumSize(16777215, 20)
        mean_lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.mean_lineEdit = mean_lineEdit

        labelWidth = QtWidgets.QLabel("Width", frameScanRange_linLog)
        width_lineEdit = QtWidgets.QLineEdit('10', frameScanRange_linLog)
        width_lineEdit.setMinimumSize(0, 20)
        width_lineEdit.setMaximumSize(16777215, 20)
        width_lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.width_lineEdit = width_lineEdit

        ### second grid layout: mean, width
        meanWidthGridLayout = QtWidgets.QGridLayout(frameScanRange_linLog)
        meanWidthGridWidget = QtWidgets.QWidget(frameScanRange_linLog)
        meanWidthGridWidget.setLayout(meanWidthGridLayout)
        meanWidthGridLayout.addWidget(labelMean, 0, 0)
        meanWidthGridLayout.addWidget(mean_lineEdit, 0, 1)
        meanWidthGridLayout.addWidget(labelWidth, 1, 0)
        meanWidthGridLayout.addWidget(width_lineEdit, 1, 1)

        ### third grid widgets: npts, step, log
        labelNbpts = QtWidgets.QLabel("Nb points", frameScanRange_linLog)
        nbpts_lineEdit = QtWidgets.QLineEdit('11', frameScanRange_linLog)
        nbpts_lineEdit.setMinimumSize(0, 20)
        nbpts_lineEdit.setMaximumSize(16777215, 20)
        nbpts_lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.nbpts_lineEdit = nbpts_lineEdit

        labelStep = QtWidgets.QLabel("Step", frameScanRange_linLog)
        self.labelStep = labelStep
        step_lineEdit = QtWidgets.QLineEdit('1', frameScanRange_linLog)
        step_lineEdit.setMinimumSize(0, 20)
        step_lineEdit.setMaximumSize(16777215, 20)
        step_lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.step_lineEdit = step_lineEdit

        ### third grid layout: npts, step, log
        nptsStepGridLayout = QtWidgets.QGridLayout(frameScanRange_linLog)
        nptsStepGridWidget = QtWidgets.QWidget(frameScanRange_linLog)
        nptsStepGridWidget.setLayout(nptsStepGridLayout)
        nptsStepGridLayout.addWidget(labelNbpts, 0, 0)
        nptsStepGridLayout.addWidget(nbpts_lineEdit, 0, 1)
        nptsStepGridLayout.addWidget(labelStep, 1, 0)
        nptsStepGridLayout.addWidget(step_lineEdit, 1, 1)

        ## 2nd row layout: Range
        layoutScanRange = QtWidgets.QHBoxLayout(frameScanRange_linLog)
        layoutScanRange.setContentsMargins(0,0,0,0)
        layoutScanRange.setSpacing(0)
        layoutScanRange.addWidget(startEndGridWidget)
        layoutScanRange.addStretch()
        layoutScanRange.addWidget(meanWidthGridWidget)
        layoutScanRange.addStretch()
        layoutScanRange.addWidget(nptsStepGridWidget)

        ## 2nd row bis frame: Values (hidden at start)
        frameScanRange_values = QtWidgets.QFrame(frameScanRange)
        frameScanRange_values.setMinimumSize(0, 60)
        frameScanRange_values.setMaximumSize(16777215, 60)
        self.frameScanRange_values = frameScanRange_values

        ### first grid widgets: values (hidden at start)
        labelValues = QtWidgets.QLabel("Values", frameScanRange_values)
        values_lineEdit = QtWidgets.QLineEdit('[0,1,2,3]', frameScanRange_values)
        values_lineEdit.setToolTip('Values of the scan')
        values_lineEdit.setMinimumSize(0, 20)
        values_lineEdit.setMaximumSize(16777215, 20)
        values_lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        values_lineEdit.setMaxLength(10000000)
        self.values_lineEdit = values_lineEdit
        # TODO: keep eval in values, show evaluated in evaluated
        labelEvaluatedValues = QtWidgets.QLabel("Evaluated values", frameScanRange_values)
        self.labelEvaluatedValues = labelEvaluatedValues
        evaluatedValues_lineEdit = QtWidgets.QLineEdit('[0,1,2,3]', frameScanRange_values)
        evaluatedValues_lineEdit.setToolTip('Evaluated values of the scan')
        evaluatedValues_lineEdit.setMinimumSize(0, 20)
        evaluatedValues_lineEdit.setMaximumSize(16777215, 20)
        evaluatedValues_lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        evaluatedValues_lineEdit.setMaxLength(10000000)
        evaluatedValues_lineEdit.setReadOnly(True)
        evaluatedValues_lineEdit.setStyleSheet(
            "QLineEdit {border: 1px solid #a4a4a4; background-color: #f4f4f4}")
        self.evaluatedValues_lineEdit = evaluatedValues_lineEdit

        ### first grid layout: values (hidden at start)
        valuesGridLayout = QtWidgets.QGridLayout(frameScanRange_values)
        valuesGridLayout.addWidget(labelValues, 0, 0)
        valuesGridLayout.addWidget(values_lineEdit, 0, 1)
        valuesGridLayout.addWidget(labelEvaluatedValues, 1, 0)
        valuesGridLayout.addWidget(evaluatedValues_lineEdit, 1, 1)

        valuesGridWidget = QtWidgets.QWidget(frameScanRange_values)
        valuesGridWidget.setLayout(valuesGridLayout)

        ## 2nd row bis layout: Values (hidden at start)
        layoutScanRange_values = QtWidgets.QHBoxLayout(frameScanRange_values)
        layoutScanRange_values.setContentsMargins(0,0,0,0)
        layoutScanRange_values.setSpacing(0)
        layoutScanRange_values.addWidget(valuesGridWidget)

        ## 3rd row frame: choice
        frameScanRange_choice = QtWidgets.QFrame(frameScanRange)
        frameScanRange_choice.setMinimumSize(0, 60)
        frameScanRange_choice.setMaximumSize(16777215, 60)
        self.frameScanRange_choice = frameScanRange_choice

        ### first grid widgets: choice
        comboBoxChoice = QtWidgets.QComboBox(frameScanRange_choice)
        comboBoxChoice.addItems(['Linear', 'Log', 'Custom'])
        self.comboBoxChoice = comboBoxChoice

        ### first grid layout: choice
        choiceGridLayout = QtWidgets.QGridLayout(frameScanRange_choice)
        choiceGridLayout.addWidget(comboBoxChoice, 0, 0)

        choiceGridWidget = QtWidgets.QWidget(frameScanRange_choice)
        choiceGridWidget.setLayout(choiceGridLayout)

        ## 3rd row layout: choice
        layoutScanRange_choice = QtWidgets.QHBoxLayout(frameScanRange_choice)
        layoutScanRange_choice.setContentsMargins(0,0,0,0)
        layoutScanRange_choice.setSpacing(0)
        layoutScanRange_choice.addWidget(choiceGridWidget)

        scanRangeLayout = QtWidgets.QHBoxLayout(frameScanRange)
        scanRangeLayout.setContentsMargins(0,0,0,0)
        scanRangeLayout.setSpacing(0)
        scanRangeLayout.addWidget(frameScanRange_linLog)
        scanRangeLayout.addWidget(frameScanRange_values)  # hidden at start
        scanRangeLayout.addWidget(frameScanRange_choice)

        # Parameter layout
        parameterLayout = QtWidgets.QVBoxLayout(mainFrame)
        parameterLayout.setContentsMargins(0,0,0,0)
        parameterLayout.setSpacing(0)
        parameterLayout.addWidget(frameParameter)
        parameterLayout.addWidget(frameScanRange)

        # Widget 'return pressed' signal connections
        self.comboBoxChoice.activated.connect(self.scanRangeComboBoxChanged)
        self.nbpts_lineEdit.returnPressed.connect(self.nbptsChanged)
        self.step_lineEdit.returnPressed.connect(self.stepChanged)
        self.start_lineEdit.returnPressed.connect(self.startChanged)
        self.end_lineEdit.returnPressed.connect(self.endChanged)
        self.mean_lineEdit.returnPressed.connect(self.meanChanged)
        self.width_lineEdit.returnPressed.connect(self.widthChanged)
        self.values_lineEdit.returnPressed.connect(self.valuesChanged)

        # Widget 'text edited' signal connections
        self.nbpts_lineEdit.textEdited.connect(lambda: setLineEditBackground(
            self.nbpts_lineEdit,'edited', self._font_size))
        self.step_lineEdit.textEdited.connect(lambda: setLineEditBackground(
            self.step_lineEdit,'edited', self._font_size))
        self.start_lineEdit.textEdited.connect(lambda: setLineEditBackground(
            self.start_lineEdit,'edited', self._font_size))
        self.end_lineEdit.textEdited.connect(lambda: setLineEditBackground(
            self.end_lineEdit,'edited', self._font_size))
        self.mean_lineEdit.textEdited.connect(lambda: setLineEditBackground(
            self.mean_lineEdit,'edited', self._font_size))
        self.width_lineEdit.textEdited.connect(lambda: setLineEditBackground(
            self.width_lineEdit,'edited', self._font_size))
        self.values_lineEdit.textEdited.connect(lambda: setLineEditBackground(
            self.values_lineEdit,'edited', self._font_size))

        # Do refresh at start
        self.refresh()

    def _removeWidget(self):
        if hasattr(self, 'mainFrame'):
            try:
                self.mainFrame.hide()
                self.mainFrame.deleteLater()
                del self.mainFrame
            except: pass

    def changeName(self, newName):
        self.param_name = newName
        self.mainFrame.param_name = newName

    def refresh(self):
        """ Refreshes all the values of the name and address of the scan parameter,
        from the configuration center """
        # Parameter
        element = self.gui.configManager.getParameterElement(self.recipe_name, self.param_name)

        if element is not None:
            address = element.address()
            unit = element.unit
        else:
            address = 'None'
            unit = ''

        self.parameterName_lineEdit.setEnabled(True)
        self.parameterName_lineEdit.setText(self.param_name)
        setLineEditBackground(self.parameterName_lineEdit, 'synced', self._font_size)
        self.parameterAddress_label.setText(address)
        if unit in ('', None):
            self.unit_label.setText('')
        else:
            self.unit_label.setText(f'({unit})')

        # Values if defined
        if self.gui.configManager.hasCustomValues(self.recipe_name, self.param_name):
            raw_values = self.gui.configManager.getValues(self.recipe_name, self.param_name)

            str_raw_values = raw_values if variables.has_eval(
                raw_values) else array_to_str(raw_values)

            if not variables.has_eval(raw_values):
                str_values = str_raw_values
                self.evaluatedValues_lineEdit.hide()
                self.labelEvaluatedValues.hide()
            else:
                values = variables.eval_safely(raw_values)
                try: values = create_array(values)
                except: str_values = values
                else: str_values = variables.array_to_str(values)
                self.evaluatedValues_lineEdit.show()
                self.labelEvaluatedValues.show()

            self.frameScanRange_linLog.hide()
            self.frameScanRange_values.show()
            self.values_lineEdit.setText(f'{str_raw_values}')
            self.evaluatedValues_lineEdit.setText(f'{str_values}')
            setLineEditBackground(self.values_lineEdit, 'synced', self._font_size)
            self.comboBoxChoice.setCurrentIndex(2)  # Custom
        else:
            self.frameScanRange_linLog.show()
            self.frameScanRange_values.hide()

            # Range
            xrange = self.gui.configManager.getRange(self.recipe_name, self.param_name)

            # Start
            start = xrange[0]
            self.start_lineEdit.setText(f'{start:g}')
            setLineEditBackground(self.start_lineEdit, 'synced', self._font_size)

            # End
            end = xrange[1]
            self.end_lineEdit.setText(f'{end:g}')
            setLineEditBackground(self.end_lineEdit, 'synced', self._font_size)

            # Mean
            mean = (start + end) / 2
            self.mean_lineEdit.setText(f'{mean:g}')
            setLineEditBackground(self.mean_lineEdit, 'synced', self._font_size)

            # Width
            width = abs(end - start)
            self.width_lineEdit.setText(f'{width:g}')
            setLineEditBackground(self.width_lineEdit, 'synced', self._font_size)

            # Nbpts
            nbpts = self.gui.configManager.getNbPts(self.recipe_name, self.param_name)
            step = self.gui.configManager.getStep(self.recipe_name, self.param_name)

            self.nbpts_lineEdit.setText(f'{nbpts:g}')
            setLineEditBackground(self.nbpts_lineEdit, 'synced', self._font_size)

            # Log
            log: bool = self.gui.configManager.getLog(self.recipe_name, self.param_name)

            # Step
            if log:
                self.comboBoxChoice.setCurrentIndex(1)  # Log
                self.labelStep.hide()
                self.step_lineEdit.hide()
                self.step_lineEdit.setText('')
            else:
                self.comboBoxChoice.setCurrentIndex(0)  # Linear
                self.step_lineEdit.setText(f'{step:g}')
                self.labelStep.show()
                self.step_lineEdit.show()

            setLineEditBackground(self.step_lineEdit, 'synced', self._font_size)

        if self.displayParameter.active:
            try: paramValues = self.gui.configManager.getParamDataFrame(
                self.recipe_name, self.param_name)
            except:
                self.gui.setStatus(
                    f"Wrong format for parameter '{self.param_name}'", 10000, False)
                return None

            str_values = variables.array_to_str(paramValues[self.param_name].values)
            self.evaluatedValues_lineEdit.setText(f'{str_values}')
            self.displayParameter.refresh(paramValues)

    def displayParameterButtonClicked(self):
        """ Opens a table widget with the array of the corresponding parameter """
        if not self.displayParameter.active:
            try: paramValues = self.gui.configManager.getParamDataFrame(
                self.recipe_name, self.param_name)
            except Exception as e:
                self.gui.setStatus(f"Wrong format for parameter '{self.param_name}': {e}", 10000)
                return None
            str_values = variables.array_to_str(paramValues[self.param_name].values)
            self.evaluatedValues_lineEdit.setText(f'{str_values}')
            self.displayParameter.refresh(paramValues)

        self.displayParameter.show()

    def nameChanged(self):
        """ Changes the name of the scan parameter """
        newName = self.parameterName_lineEdit.text()
        newName = clean_string(newName)

        if newName != '':
            self.gui.configManager.renameParameter(self.recipe_name, self.param_name, newName)

    def nbptsChanged(self):
        """ Changes the number of points of the parameter """
        value = self.nbpts_lineEdit.text()

        try:
            value = int(float(value))
            assert value > 0

            self.gui.configManager.setNbPts(self.recipe_name, self.param_name, value)
            self.point_or_step = "point"
        except:
            self.refresh()

    def stepChanged(self):
        """ Changes the step size of the parameter """
        value = self.step_lineEdit.text()

        try:
            if value == "inf" or float(value) == 0:
                self.nbpts_lineEdit.setText('1')
                self.nbptsChanged()
                return

            value = float(value)
            assert value > 0

            self.gui.configManager.setStep(self.recipe_name, self.param_name, value)

            self.point_or_step = "step"
        except:
            self.refresh()

    def startChanged(self):
        """ Changes the start value of the parameter """
        value = self.start_lineEdit.text()

        try:
            value = float(value)
            log: bool = self.gui.configManager.getLog(self.recipe_name, self.param_name)
            if log: assert value > 0

            xrange = list(self.gui.configManager.getRange(self.recipe_name, self.param_name))
            xrange[0] = value

            self.gui.configManager.setRange(self.recipe_name, self.param_name, xrange)
        except:
            self.refresh()

    def endChanged(self):
        """ Changes the end value of the parameter """
        value = self.end_lineEdit.text()

        try:
            value = float(value)
            log:bool = self.gui.configManager.getLog(self.recipe_name, self.param_name)
            if log: assert value > 0
            xrange = list(self.gui.configManager.getRange(self.recipe_name, self.param_name))
            xrange[1] = value

            self.gui.configManager.setRange(self.recipe_name, self.param_name, xrange)
        except :
            self.refresh()

    def meanChanged(self):
        """ Changes the mean value of the parameter """
        value = self.mean_lineEdit.text()

        try:
            value = float(value)
            log: bool = self.gui.configManager.getLog(self.recipe_name, self.param_name)
            if log: assert value > 0
            xrange = list(self.gui.configManager.getRange(self.recipe_name, self.param_name))
            xrange_new = xrange.copy()
            xrange_new[0] = value - (xrange[1] - xrange[0])/2
            xrange_new[1] = value + (xrange[1] - xrange[0])/2
            assert xrange_new[0] > 0
            assert xrange_new[1] > 0

            self.gui.configManager.setRange(self.recipe_name, self.param_name, xrange_new)
        except:
            self.refresh()

    def widthChanged(self):
        """ Changes the width of the parameter """
        value = self.width_lineEdit.text()

        try:
            value = float(value)
            log: bool = self.gui.configManager.getLog(self.recipe_name, self.param_name)
            if log: assert value > 0
            xrange = list(self.gui.configManager.getRange(self.recipe_name, self.param_name))
            xrange_new = xrange.copy()
            xrange_new[0] = (xrange[1]+xrange[0])/2 - value/2
            xrange_new[1] = (xrange[1]+xrange[0])/2 + value/2
            assert xrange_new[0] > 0
            assert xrange_new[1] > 0

            self.gui.configManager.setRange(self.recipe_name, self.param_name, xrange_new)
        except:
            self.refresh()

    def scanRangeComboBoxChanged(self):
        choice = self.comboBoxChoice.currentText()

        raw_values = self.gui.configManager.getValues(
            self.recipe_name, self.param_name)

        if choice == "Custom":
            self.gui.configManager.setValues(
                self.recipe_name, self.param_name, raw_values)
        else:
            CUSTOM_VALUES = self.gui.configManager.hasCustomValues(
                self.recipe_name, self.param_name)
            if CUSTOM_VALUES:
                param = self.gui.configManager.getParameter(
                    self.recipe_name, self.param_name)
                # OPTIMIZE: would be cleaner in configManager but easier that way
                param.pop('values')

                if isinstance(raw_values, np.ndarray): values = raw_values
                else:
                    try: values = str_to_array(self.evaluatedValues_lineEdit.text())
                    except: values = np.linspace(0, 10, 11)  # OPTIMIZE: should know last values when start scan (need to update values)

                param['range'] = (values[0], values[-1])

                if 'log' not in param: param['log'] = False

                self.gui.configManager.setNbPts(
                    self.recipe_name, self.param_name, len(values))

            if choice == "Linear": self.setLog(False)
            elif choice == "Log": self.setLog(True)

    def setLog(self, log: bool):
        """ Changes the log state of the parameter """
        if log:
            self.point_or_step = "point"
            xrange = list(self.gui.configManager.getRange(self.recipe_name, self.param_name))
            change = False

            if xrange[1] <= 0:
                xrange[1] = 1
                change = True

            if xrange[0] <= 0:
                xrange[0] = 10**(m.log10(xrange[1]) - 1)
                change = True

            if change: self.gui.configManager.setRange(self.recipe_name, self.param_name, xrange)

        self.gui.configManager.setLog(self.recipe_name, self.param_name, log)

    def valuesChanged(self):
        """ Changes values of the parameter """
        raw_values = self.values_lineEdit.text()

        try:
            if not variables.has_eval(raw_values):
                raw_values = str_to_array(raw_values)
                assert len(raw_values) != 0, "Cannot have empty array"
                values = raw_values
            elif not variables.has_variable(raw_values):
                values = variables.eval_safely(raw_values)
                values = create_array(values)
                assert len(values) != 0, "Cannot have empty array"

            self.gui.configManager.setValues(self.recipe_name, self.param_name, raw_values)
        except Exception as e:
            self.gui.setStatus(f"Wrong format for parameter '{self.param_name}': {e}", 10000)

    def rightClick(self, position: QtCore.QPoint):
        """ Provides the menu when the user right click on a parameter """
        menu = QtWidgets.QMenu()

        removeActions = menu.addAction(f"Remove {self.param_name}")
        removeActions.setIcon(QtGui.QIcon(icons['remove']))

        choice = menu.exec_(self.mainFrame.mapToGlobal(position))

        if choice == removeActions:
            self.gui.configManager.removeParameter(self.recipe_name, self.param_name)

    # PROCESSING STATE BACKGROUND
    ###########################################################################

    def setProcessingState(self, state: str):
        """ Sets the background color of the parameter address during the scan """
        if state == 'idle':
            self.parameterAddress_label.setStyleSheet(
                f"font-size: {self._font_size+1}pt;")
        else :
            if state == 'started': color = '#ff8c1a'
            if state == 'finished': color = '#70db70'
            self.parameterAddress_label.setStyleSheet(
                f"background-color: {color}; font-size: {self._font_size+1}pt;")

    def close(self):
        """ Called by scanner on closing """
        self.displayParameter.close()
