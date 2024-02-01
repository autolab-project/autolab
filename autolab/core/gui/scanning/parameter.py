# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:13:45 2019

@author: qchat
"""

import math as m

from qtpy import QtCore, QtWidgets

from .display import DisplayValues
from .customWidgets import parameterQFrame
from ...utilities import clean_string


class ParameterManager:
    """ Manage the parameter from a recipe in a scan """

    def __init__(self, gui: QtWidgets.QMainWindow, recipe_name: str, param_name: str):

        self.gui = gui
        self.recipe_name = recipe_name
        self.param_name = param_name

        self.point_or_step = "point"

        # Parameter frame
        mainFrame = parameterQFrame(self.gui, self.recipe_name, self.param_name)
        mainFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        mainFrame.setMinimumSize(0, 32+60)
        mainFrame.setMaximumSize(16777215, 32+60)
        self.mainFrame = mainFrame

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
        parameterName_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        parameterName_lineEdit.setToolTip('Name of the parameter, as it will displayed in the data')
        parameterName_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(parameterName_lineEdit,'edited'))
        parameterName_lineEdit.returnPressed.connect(self.nameChanged)
        parameterName_lineEdit.setEnabled(False)
        self.parameterName_lineEdit = parameterName_lineEdit

        ### Address
        parameterAddressIndicator_label = QtWidgets.QLabel("Address:", frameParameter)
        parameterAddressIndicator_label.setMinimumSize(0, 20)
        parameterAddressIndicator_label.setMaximumSize(16777215, 20)
        parameterAddressIndicator_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        parameterAddress_label = QtWidgets.QLabel("<variable>", frameParameter)
        parameterAddress_label.setMinimumSize(0, 20)
        parameterAddress_label.setMaximumSize(16777215, 20)
        parameterAddress_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        parameterAddress_label.setToolTip('Address of the parameter')
        self.parameterAddress_label = parameterAddress_label

        ### Unit
        unit_label = QtWidgets.QLabel("uA", frameParameter)
        unit_label.setMinimumSize(0, 20)
        unit_label.setMaximumSize(16777215, 20)
        unit_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.unit_label = unit_label

        ### displayParameter button
        self.displayParameter = DisplayValues("Parameter", size=(250, 400))
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

        ## 2nd row frame: Range
        frameScanRange = QtWidgets.QFrame(mainFrame)
        frameScanRange.setMinimumSize(0, 60)
        frameScanRange.setMaximumSize(16777215, 60)
        frameScanRange = frameScanRange

        ### first grid widgets: start, stop
        labelStart = QtWidgets.QLabel("Start", frameScanRange)
        start_lineEdit = QtWidgets.QLineEdit('0', frameScanRange)
        start_lineEdit.setToolTip('Start value of the scan')
        start_lineEdit.setMinimumSize(0, 20)
        start_lineEdit.setMaximumSize(16777215, 20)
        start_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.start_lineEdit = start_lineEdit

        labelEnd = QtWidgets.QLabel("End", frameScanRange)
        end_lineEdit = QtWidgets.QLineEdit('10', frameScanRange)
        end_lineEdit.setMinimumSize(0, 20)
        end_lineEdit.setMaximumSize(16777215, 20)
        end_lineEdit.setToolTip('End value of the scan')
        end_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.end_lineEdit = end_lineEdit

        ### first grid layout: start, stop
        startEndGridLayout = QtWidgets.QGridLayout(frameScanRange)
        startEndGridLayout.addWidget(labelStart, 0, 0)
        startEndGridLayout.addWidget(start_lineEdit, 0, 1)
        startEndGridLayout.addWidget(labelEnd, 1, 0)
        startEndGridLayout.addWidget(end_lineEdit, 1, 1)

        startEndGridWidget = QtWidgets.QWidget(frameScanRange)
        startEndGridWidget.setLayout(startEndGridLayout)

        ### second grid widgets: mean, width
        labelMean = QtWidgets.QLabel("Mean", frameScanRange)
        mean_lineEdit = QtWidgets.QLineEdit('5', frameScanRange)
        mean_lineEdit.setMinimumSize(0, 20)
        mean_lineEdit.setMaximumSize(16777215, 20)
        mean_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.mean_lineEdit = mean_lineEdit

        labelWidth = QtWidgets.QLabel("Width", frameScanRange)
        width_lineEdit = QtWidgets.QLineEdit('10', frameScanRange)
        width_lineEdit.setMinimumSize(0, 20)
        width_lineEdit.setMaximumSize(16777215, 20)
        width_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.width_lineEdit = width_lineEdit

        ### second grid layout: mean, width
        meanWidthGridLayout = QtWidgets.QGridLayout(frameScanRange)
        meanWidthGridWidget = QtWidgets.QWidget(frameScanRange)
        meanWidthGridWidget.setLayout(meanWidthGridLayout)
        meanWidthGridLayout.addWidget(labelMean, 0, 0)
        meanWidthGridLayout.addWidget(mean_lineEdit, 0, 1)
        meanWidthGridLayout.addWidget(labelWidth, 1, 0)
        meanWidthGridLayout.addWidget(width_lineEdit, 1, 1)

        ### third grid widgets: npts, step, log
        labelNbpts = QtWidgets.QLabel("Nb points", frameScanRange)
        nbpts_lineEdit = QtWidgets.QLineEdit('11', frameScanRange)
        nbpts_lineEdit.setMinimumSize(0, 20)
        nbpts_lineEdit.setMaximumSize(16777215, 20)
        nbpts_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.nbpts_lineEdit = nbpts_lineEdit

        labelStep = QtWidgets.QLabel("Step", frameScanRange)
        step_lineEdit = QtWidgets.QLineEdit('1', frameScanRange)
        step_lineEdit.setMinimumSize(0, 20)
        step_lineEdit.setMaximumSize(16777215, 20)
        step_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.step_lineEdit = step_lineEdit
        scanLog_checkBox = QtWidgets.QCheckBox("Log")
        self.scanLog_checkBox = scanLog_checkBox

        ### third grid layout: npts, step, log
        nptsStepGridLayout = QtWidgets.QGridLayout(frameScanRange)
        nptsStepGridWidget = QtWidgets.QWidget(frameScanRange)
        nptsStepGridWidget.setLayout(nptsStepGridLayout)
        nptsStepGridLayout.addWidget(labelNbpts, 0, 0)
        nptsStepGridLayout.addWidget(nbpts_lineEdit, 0, 1)
        nptsStepGridLayout.addWidget(labelStep, 1, 0)
        nptsStepGridLayout.addWidget(step_lineEdit, 1, 1)
        nptsStepGridLayout.addWidget(scanLog_checkBox, 1, 2)

        ## 2nd row layout: Range
        layoutScanRange = QtWidgets.QHBoxLayout(frameScanRange)
        layoutScanRange.setContentsMargins(0,0,0,0)
        layoutScanRange.setSpacing(0)
        layoutScanRange.addWidget(startEndGridWidget)
        layoutScanRange.addStretch()
        layoutScanRange.addWidget(meanWidthGridWidget)
        layoutScanRange.addStretch()
        layoutScanRange.addWidget(nptsStepGridWidget)

        # Parameter layout
        parameterLayout = QtWidgets.QVBoxLayout(mainFrame)
        parameterLayout.setContentsMargins(0,0,0,0)
        parameterLayout.setSpacing(0)
        parameterLayout.addWidget(frameParameter)
        parameterLayout.addWidget(frameScanRange)

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
        self.gui.setLineEditBackground(self.parameterName_lineEdit, 'synced')
        self.parameterAddress_label.setText(address)
        if unit in ('', None):
            self.unit_label.setText('')
        else:
            self.unit_label.setText(f'({unit})')

        # Range
        xrange = self.gui.configManager.getRange(self.recipe_name, self.param_name)

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
        nbpts = self.gui.configManager.getNbPts(self.recipe_name, self.param_name)
        step = self.gui.configManager.getStep(self.recipe_name, self.param_name)

        self.nbpts_lineEdit.setText(f'{nbpts:g}')
        self.gui.setLineEditBackground(self.nbpts_lineEdit, 'synced')

        # Log
        log: bool = self.gui.configManager.getLog(self.recipe_name, self.param_name)
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
                self.gui.configManager.getParamDataFrame(self.recipe_name, self.param_name))

    def displayParameterButtonClicked(self):
        """ Opens a table widget with the array of the corresponding parameter """
        if not self.displayParameter.active:
            self.displayParameter.refresh(
                self.gui.configManager.getParamDataFrame(self.recipe_name, self.param_name))

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

    def scanLogChanged(self):
        """ Changes the log state of the parameter """
        state: bool = self.scanLog_checkBox.isChecked()
        if state:
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

        self.gui.configManager.setLog(self.recipe_name, self.param_name, state)


    # PROCESSING STATE BACKGROUND
    ###########################################################################

    def setProcessingState(self, state: str):
        """ Sets the background color of the parameter address during the scan """
        if state == 'idle':
            self.parameterAddress_label.setStyleSheet("font-size: 9pt;")
        else :
            if state == 'started': color = '#ff8c1a'
            if state == 'finished': color = '#70db70'
            self.parameterAddress_label.setStyleSheet(f"background-color: {color}; font-size: 9pt;")

    def close(self):
        """ Called by scanner on closing """
        self.displayParameter.close()
