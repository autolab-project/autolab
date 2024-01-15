# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:13:45 2019

@author: qchat
"""

from qtpy import QtCore, QtWidgets

from . import main
from .display import DisplayValues
from .customWidgets import parameterQFrame


class ParameterManager:
    """ Manage the parameter from a recipe in a scan """

    def __init__(self, gui: QtWidgets.QMainWindow, recipe_name: str, param_name: str):

        self.gui = gui
        self.recipe_name = recipe_name
        self.param_name = param_name

        # Parameter frame
        frameParameter = parameterQFrame(self.gui, self.recipe_name, self.param_name)
        # frameParameter.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frameParameter.setMinimumSize(0, 32)
        frameParameter.setMaximumSize(16777215, 32)
        frameParameter.setToolTip(f"Drag and drop a variable or use the right click option of a variable from the control panel to add a recipe to the tree: {self.recipe_name}")
        self.frameParameter = frameParameter

        parameterName_lineEdit = QtWidgets.QLineEdit('', frameParameter)
        parameterName_lineEdit.setMinimumSize(0, 20)
        parameterName_lineEdit.setMaximumSize(16777215, 20)
        parameterName_lineEdit.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        parameterName_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        parameterName_lineEdit.setToolTip('Name of the parameter, as it will displayed in the data')
        self.parameterName_lineEdit = parameterName_lineEdit

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

        unit_label = QtWidgets.QLabel("uA", frameParameter)
        unit_label.setMinimumSize(0, 20)
        unit_label.setMaximumSize(16777215, 20)
        unit_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.unit_label = unit_label

        self.displayParameter = DisplayValues(self.gui, "Parameter", size=(250, 400))

        displayParameter_pushButton = QtWidgets.QPushButton("Parameter")
        displayParameter_pushButton.setMinimumSize(0, 23)
        displayParameter_pushButton.setMaximumSize(16777215, 23)
        self.displayParameter_pushButton = displayParameter_pushButton

        # Push button
        self.displayParameter_pushButton.clicked.connect(self.displayParameterButtonClicked)

        self.parameterName_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.parameterName_lineEdit,'edited'))
        self.parameterName_lineEdit.returnPressed.connect(self.nameChanged)
        self.parameterName_lineEdit.setEnabled(False)

        layoutParameter = QtWidgets.QHBoxLayout(frameParameter)
        layoutParameter.addWidget(parameterName_lineEdit)
        layoutParameter.addWidget(unit_label)
        layoutParameter.addWidget(parameterAddressIndicator_label)
        layoutParameter.addWidget(parameterAddress_label)
        layoutParameter.addWidget(displayParameter_pushButton)

        # Do refresh at start
        self.refresh()

    def _removeWidget(self):
        if hasattr(self, 'frameParameter'):
            try:
                self.frameParameter.hide()
                self.frameParameter.deleteLater()
                del self.frameParameter
            except: pass

    def refresh(self):
        """ Refreshes all the values of the name and address of the scan parameter,
        from the configuration center """
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
        newName = main.cleanString(newName)

        if newName != '':
            self.gui.configManager.renameParameter(self.recipe_name, self.param_name, newName)

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
