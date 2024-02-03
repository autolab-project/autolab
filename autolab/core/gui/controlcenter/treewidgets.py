# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:29:07 2019

@author: qchat
"""


import os
from typing import Any

import pandas as pd
import numpy as np
from qtpy import QtCore, QtWidgets, QtGui

from .slider import Slider
from ..monitoring.main import Monitor
from ..icons import icons
from ... import paths, config
from ...devices import close, DEVICES
from ...utilities import (qt_object_exists, SUPPORTED_EXTENSION,
                          array_from_txt, array_to_txt,
                          dataframe_to_txt, dataframe_from_txt)


class TreeWidgetItemModule(QtWidgets.QTreeWidgetItem):
    """ This class represents a module in an item of the tree """

    def __init__(self, itemParent, name, gui):

        self.name = name
        self.module = None
        self.loaded = False
        self.gui = gui
        self.is_not_submodule = type(gui.tree) is type(itemParent)

        if self.is_not_submodule:
            QtWidgets.QTreeWidgetItem.__init__(self, itemParent, [name, 'Device'])
        else:
            QtWidgets.QTreeWidgetItem.__init__(self, itemParent, [name, 'Module'])

        self.setTextAlignment(1, QtCore.Qt.AlignHCenter)

    def load(self, module):
        """ This function loads the entire module (submodules, variables, actions) """
        self.module = module

        # Submodules
        subModuleNames = self.module.list_modules()
        for subModuleName in subModuleNames:
            subModule = getattr(self.module, subModuleName)
            item = TreeWidgetItemModule(self, subModuleName, self.gui)
            item.load(subModule)

        # Variables
        varNames = self.module.list_variables()
        for varName in varNames:
            variable = getattr(self.module,varName)
            TreeWidgetItemVariable(self, variable, self.gui)

        # Actions
        actNames = self.module.list_actions()
        for actName in actNames:
            action = getattr(self.module, actName)
            TreeWidgetItemAction(self, action, self.gui)

        # Change loaded status
        self.loaded = True

        # Tooltip
        if self.module._help is not None: self.setToolTip(0, self.module._help)

    def menu(self, position: QtCore.QPoint):
        """ This function provides the menu when the user right click on an item """
        if self.is_not_submodule and self.loaded:
            menu = QtWidgets.QMenu()
            disconnectDevice = menu.addAction(f"Disconnect {self.name}")
            disconnectDevice.setIcon(QtGui.QIcon(icons['disconnect']))

            choice = menu.exec_(self.gui.tree.viewport().mapToGlobal(position))

            if choice == disconnectDevice:
                close(self.name)

                for i in range(self.childCount()):
                    self.removeChild(self.child(0))

                self.loaded = False


class TreeWidgetItemAction(QtWidgets.QTreeWidgetItem):
    """ This class represents an action in an item of the tree """

    def __init__(self, itemParent, action, gui):

        displayName = f'{action.name}'
        if action.unit is not None:
            displayName += f' ({action.unit})'

        QtWidgets.QTreeWidgetItem.__init__(self, itemParent, [displayName, 'Action'])
        self.setTextAlignment(1, QtCore.Qt.AlignHCenter)

        self.gui = gui
        self.action = action

        if self.action.has_parameter:
            if self.action.type in [int, float, str, pd.DataFrame, np.ndarray]:
                self.executable = True
                self.has_value = True
            else:
                self.executable = False
                self.has_value = False
        else:
            self.executable = True
            self.has_value = False

        # Main - Column 2 : actionread button
        if self.executable:
            self.execButton = QtWidgets.QPushButton()
            self.execButton.setText("Execute")
            self.execButton.clicked.connect(self.execute)
            self.gui.tree.setItemWidget(self, 2, self.execButton)

        # Main - Column 3 : QlineEdit if the action has a parameter
        if self.has_value:
            self.valueWidget = QtWidgets.QLineEdit()
            self.valueWidget.setAlignment(QtCore.Qt.AlignCenter)
            self.gui.tree.setItemWidget(self, 3, self.valueWidget)
            self.valueWidget.returnPressed.connect(self.execute)

        # Tooltip
        if self.action._help is None: tooltip = 'No help available for this action'
        else: tooltip = self.action._help
        self.setToolTip(0, tooltip)

    def readGui(self) -> Any:
        """ This function returns the value in good format of the value in the GUI """
        value = self.valueWidget.text()

        if value == '':
            if self.action.unit in ('open-file', 'save-file', 'filename'):
                if self.action.unit == "filename":  # LEGACY (may be removed later)
                    self.gui.setStatus("Using 'filename' as unit is depreciated in favor of 'open-file' and 'save-file'" \
                                       f"\nUpdate driver {self.action.name} to remove this warning",
                                       10000, False)
                    self.action.unit = "open-file"

                if self.action.unit == "open-file":
                    filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                        self.gui, caption="Open file",
                        directory=paths.USER_LAST_CUSTOM_FOLDER,
                        filter=SUPPORTED_EXTENSION)
                elif self.action.unit == "save-file":
                    filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                        self.gui, caption="Save file",
                        directory=paths.USER_LAST_CUSTOM_FOLDER,
                        filter=SUPPORTED_EXTENSION)

                if filename != '':
                    path = os.path.dirname(filename)
                    paths.USER_LAST_CUSTOM_FOLDER = path
                    return filename
                else:
                    self.gui.setStatus(
                        f"Action {self.action.name} cancel filename selection",
                        10000)
            else:
                self.gui.setStatus(
                    f"Action {self.action.name} requires a value for its parameter",
                    10000, False)
        else:
            try:
                value = self.checkVariable(value)
                if self.action.type in [np.ndarray]:
                    if type(value) is str: value = array_from_txt(value)
                elif self.action.type in [pd.DataFrame]:
                    if type(value) is str: value = dataframe_from_txt(value)
                else:
                    value = self.action.type(value)
                return value
            except:
                self.gui.setStatus(
                    f"Action {self.action.name}: Impossible to convert {value} to {self.action.type.__name__}",
                    10000, False)

    def checkVariable(self, value):
        """ Try to execute the given command line (meant to contain device variables) and return the result """
        if str(value).startswith("$eval:"):
            value = str(value)[len("$eval:"): ]
            try:
                allowed_dict = {"np": np, "pd": pd}
                allowed_dict.update(DEVICES)
                value = eval(str(value), {}, allowed_dict)
            except: pass
        return value

    def execute(self):
        """ Start a new thread to execute the associated action """
        if not self.isDisabled():
            if self.has_value:
                value = self.readGui()
                if value is not None: self.gui.threadManager.start(
                        self, 'execute', value=value)
            else:
                self.gui.threadManager.start(self, 'execute')

    def menu(self, position: QtCore.QPoint):
        """ This function provides the menu when the user right click on an item """
        if not self.isDisabled():
            menu = QtWidgets.QMenu()
            scanRecipe = menu.addAction("Do in scan recipe")
            scanRecipe.setIcon(QtGui.QIcon(icons['action']))

            choice = menu.exec_(self.gui.tree.viewport().mapToGlobal(position))
            if choice == scanRecipe:
                recipe_name = self.gui.getRecipeName()
                self.gui.addStepToScanRecipe(recipe_name, 'action', self.action)


class TreeWidgetItemVariable(QtWidgets.QTreeWidgetItem):
    """ This class represents a variable in an item of the tree """

    def __init__(self, itemParent, variable ,gui):

        self.displayName = f'{variable.name}'
        if variable.unit is not None:
            self.displayName += f' ({variable.unit})'

        QtWidgets.QTreeWidgetItem.__init__(
            self, itemParent, [self.displayName, 'Variable'])
        self.setTextAlignment(1, QtCore.Qt.AlignHCenter)

        self.gui = gui
        self.variable = variable

        # Import Autolab config
        control_center_config = config.get_control_center_config()
        self.precision = int(control_center_config['precision'])

        # Signal creation and associations in autolab devices instances
        self.readSignal = ReadSignal()
        self.readSignal.read.connect(self.writeGui)
        self.variable._read_signal = self.readSignal
        self.writeSignal = WriteSignal()
        self.writeSignal.writed.connect(self.valueEdited)
        self.variable._write_signal = self.writeSignal

        # Main - Column 2 : Creation of a READ button if the variable is readable
        if self.variable.readable and self.variable.type in [
                int, float, bool, str, tuple, np.ndarray, pd.DataFrame]:
            self.readButton = QtWidgets.QPushButton()
            self.readButton.setText("Read")
            self.readButton.clicked.connect(self.read)

            if not self.variable.writable and self.variable.type in [
                    np.ndarray, pd.DataFrame]:
                self.readButtonCheck = QtWidgets.QCheckBox()
                self.readButtonCheck.stateChanged.connect(self.readButtonCheckEdited)
                self.readButtonCheck.setToolTip('Toggle reading in text, careful can truncate data and impact performance')
                self.readButtonCheck.setMaximumWidth(15)

                frameReadButton = QtWidgets.QFrame()
                hbox = QtWidgets.QHBoxLayout(frameReadButton)
                hbox.setSpacing(0)
                hbox.setContentsMargins(0,0,0,0)
                hbox.addWidget(self.readButtonCheck)
                hbox.addWidget(self.readButton)
                self.gui.tree.setItemWidget(self, 2, frameReadButton)
            else:
                self.gui.tree.setItemWidget(self, 2, self.readButton)

        # Main - column 3 : Creation of a VALUE widget, depending on the type

        ## QLineEdit or QLabel
        if self.variable.type in [int, float, str, np.ndarray, pd.DataFrame]:
            if self.variable.writable:
                self.valueWidget = QtWidgets.QLineEdit()
                self.valueWidget.setAlignment(QtCore.Qt.AlignCenter)
                self.valueWidget.returnPressed.connect(self.write)
                self.valueWidget.textEdited.connect(self.valueEdited)
                self.valueWidget.setMaxLength(1000000)  # default is 32767, not enought for array and dataframe
                # self.valueWidget.setPlaceholderText(self.variable._help)  # Could be nice but take too much place. Maybe add it as option
            elif self.variable.readable:
                self.valueWidget = QtWidgets.QLineEdit()
                self.valueWidget.setMaxLength(1000000)
                self.valueWidget.setReadOnly(True)
                self.valueWidget.setStyleSheet(
                    "QLineEdit {border: 1px solid #a4a4a4; background-color: #f4f4f4}")
                self.valueWidget.setAlignment(QtCore.Qt.AlignCenter)
            else:
                self.valueWidget = QtWidgets.QLabel()
                self.valueWidget.setAlignment(QtCore.Qt.AlignCenter)

            self.gui.tree.setItemWidget(self, 3, self.valueWidget)

        ## QCheckbox for boolean variables
        elif self.variable.type in [bool]:

            class MyQCheckBox(QtWidgets.QCheckBox):

                def __init__(self, parent):
                    self.parent = parent
                    QtWidgets.QCheckBox.__init__(self)

                def mouseReleaseEvent(self, event):
                    super(MyQCheckBox, self).mouseReleaseEvent(event)
                    self.parent.valueEdited()
                    self.parent.write()

            self.valueWidget = MyQCheckBox(self)
            # self.valueWidget = QtWidgets.QCheckBox()
            # self.valueWidget.stateChanged.connect(self.valueEdited)
            # self.valueWidget.stateChanged.connect(self.write)  # removed this to avoid setting a second time when reading a change
            hbox = QtWidgets.QHBoxLayout()
            hbox.addWidget(self.valueWidget)
            hbox.setAlignment(QtCore.Qt.AlignCenter)
            hbox.setSpacing(0)
            hbox.setContentsMargins(0,0,0,0)
            widget = QtWidgets.QWidget()
            widget.setLayout(hbox)
            if not self.variable.writable:  # Disable interaction is not writable
                self.valueWidget.setEnabled(False)

            self.gui.tree.setItemWidget(self, 3, widget)

        ## Combobox for tuples: Tuple[List[str], int]
        elif self.variable.type in [tuple]:

            class MyQComboBox(QtWidgets.QComboBox):
                def __init__(self):
                    QtWidgets.QComboBox.__init__(self)
                    self.readonly = False
                    self.wheel = True
                    self.key = True

                def mousePressEvent(self, event):
                    if not self.readonly:
                        QtWidgets.QComboBox.mousePressEvent(self, event)

                def keyPressEvent(self, event):
                    if not self.readonly and self.key:
                        QtWidgets.QComboBox.keyPressEvent(self, event)

                def wheelEvent(self, event):
                    if not self.readonly and self.wheel:
                        QtWidgets.QComboBox.wheelEvent(self, event)

            if self.variable.writable:
                self.valueWidget = MyQComboBox()
                self.valueWidget.wheel = False  # prevent changing value by mistake
                self.valueWidget.key = False
                self.valueWidget.activated.connect(self.write)
            elif self.variable.readable:
                self.valueWidget = MyQComboBox()
                self.valueWidget.readonly = True
            else:
                self.valueWidget = QtWidgets.QLabel()
                self.valueWidget.setAlignment(QtCore.Qt.AlignCenter)

            self.gui.tree.setItemWidget(self, 3, self.valueWidget)

        # Main - column 4 : indicator (status of the actual value : known or not known)
        if self.variable.type in [int, float, str, bool, tuple, np.ndarray, pd.DataFrame]:
            self.indicator = QtWidgets.QLabel()
            self.gui.tree.setItemWidget(self, 4, self.indicator)

        # Tooltip
        if self.variable._help is None: tooltip = 'No help available for this variable'
        else: tooltip = self.variable._help
        if hasattr(self.variable, "type"):
            variable_type = str(self.variable.type).split("'")[1]
            tooltip += f" ({variable_type})"
        self.setToolTip(0, tooltip)

        # disable read button if array/dataframe
        if hasattr(self, 'readButtonCheck'): self.readButtonCheckEdited()

    def writeGui(self, value):
        """ This function displays a new value in the GUI """
        if qt_object_exists(self.valueWidget):  # avoid crash if device closed and try to write gui (if close device before reading finished)
            # Update value
            if self.variable.numerical:
                self.valueWidget.setText(f'{value:.{self.precision}g}') # default is .6g
            elif self.variable.type in [str]:
                self.valueWidget.setText(value)
            elif self.variable.type in [bool]:
                self.valueWidget.setChecked(value)
            elif self.variable.type in [tuple]:
                AllItems = [self.valueWidget.itemText(i) for i in range(self.valueWidget.count())]
                if value[0] != AllItems:
                    self.valueWidget.clear()
                    self.valueWidget.addItems(value[0])
                self.valueWidget.setCurrentIndex(value[1])
            elif self.variable.type in [np.ndarray, pd.DataFrame]:

                if self.variable.writable or self.readButtonCheck.isChecked():
                    if self.variable.type in [np.ndarray]:
                        self.valueWidget.setText(array_to_txt(value))
                    if self.variable.type in [pd.DataFrame]:
                        self.valueWidget.setText(dataframe_to_txt(value))
                # else:
                #     self.valueWidget.setText('')

            # Change indicator light to green
            if self.variable.type in [int, float, bool, str, tuple, np.ndarray, pd.DataFrame]:
                self.setValueKnownState(True)

    def readGui(self):
        """ This function returns the value in good format of the value in the GUI """
        if self.variable.type in [int, float, str, np.ndarray, pd.DataFrame]:
            value = self.valueWidget.text()
            if value == '':
                self.gui.setStatus(
                    f"Variable {self.variable.name} requires a value to be set",
                    10000, False)
            else:
                try:
                    value = self.checkVariable(value)
                    if self.variable.type in [np.ndarray]:
                        if type(value) is str: value = array_from_txt(value)
                    elif self.variable.type in [pd.DataFrame]:
                        if type(value) is str: value = dataframe_from_txt(value)
                    else:
                        value = self.variable.type(value)
                    return value
                except:
                    self.gui.setStatus(
                        f"Variable {self.variable.name}: Impossible to convert {value} to {self.variable.type.__name__}",
                        10000, False)

        elif self.variable.type in [bool]:
            value = self.valueWidget.isChecked()
            return value
        elif self.variable.type in [tuple]:
            AllItems = [self.valueWidget.itemText(i) for i in range(self.valueWidget.count())]
            value = (AllItems, self.valueWidget.currentIndex())
            return value

    def checkVariable(self, value):
        """ Check if value is a device variable address and if is it, return its value """
        if str(value).startswith("$eval:"):
            value = str(value)[len("$eval:"): ]
            try:
                allowed_dict = {"np": np, "pd": pd}
                allowed_dict.update(DEVICES)
                value = eval(str(value), {}, allowed_dict)
            except: pass
        return value

    def setValueKnownState(self, state: bool):
        """ Turn the color of the indicator depending of the known state of the value """
        if state: self.indicator.setStyleSheet("background-color:#70db70")  # green
        else: self.indicator.setStyleSheet("background-color:#ff8c1a")  # orange

    def read(self):
        """ Start a new thread to READ the associated variable """
        if not self.isDisabled():
            self.setValueKnownState(False)
            self.gui.threadManager.start(self, 'read')

    def write(self):
        """ Start a new thread to WRITE the associated variable """
        if not self.isDisabled():
            value = self.readGui()
            if value is not None:
                self.gui.threadManager.start(self, 'write', value=value)

    def valueEdited(self):
        """ Function call when the value displayed in not sure anymore.
            The value has been modified either in the GUI (but not sent) or by command line """
        self.setValueKnownState(False)

    def readButtonCheckEdited(self):
        state = bool(self.readButtonCheck.isChecked())

        self.readButton.setEnabled(state)

        # if not self.variable.writable:
        #     self.valueWidget.setVisible(state) # doesn't work on instantiation, but not problem if start with visible

            # if not state: self.valueWidget.setText('')

    def menu(self, position: QtCore.QPoint):
        """ This function provides the menu when the user right click on an item """
        if not self.isDisabled():
            # TODO: could be used to select which recipe and parameter the step should go
            # But, seems not ergonomic (not finish to implement it if want it)
            # if self.gui.scanner is None:
            #     pass
            # else:
            #     recipe_name = self.gui.getRecipeName()
            #     recipe_name_list = self.gui.scanner.configManager.recipeNameList()
            #     param_name = self.gui.getParameterName()
            #     param_name_list = self.gui.scanner.configManager.parameterNameList(recipe_name)
            #     print(recipe_name, recipe_name_list,
            #           param_name, param_name_list)

            menu = QtWidgets.QMenu()
            monitoringAction = menu.addAction("Start monitoring")
            monitoringAction.setIcon(QtGui.QIcon(icons['monitor']))
            menu.addSeparator()
            sliderAction = menu.addAction("Create a slider")
            sliderAction.setIcon(QtGui.QIcon(icons['slider']))
            menu.addSeparator()
            # sub_menu = QtWidgets.QMenu("Set as parameter", menu)
            # sub_menu.setIcon(QtGui.QIcon(icons['parameter']))
            # menu.addMenu(sub_menu)
            # scanParameterAction = sub_menu.addAction(f"in {recipe_name}")
            # scanParameterAction.setIcon(QtGui.QIcon(icons['recipe']))
            scanParameterAction = menu.addAction("Set as scan parameter")
            scanParameterAction.setIcon(QtGui.QIcon(icons['parameter']))
            scanMeasureStepAction = menu.addAction("Measure in scan recipe")
            scanMeasureStepAction.setIcon(QtGui.QIcon(icons['measure']))
            scanSetStepAction = menu.addAction("Set value in scan recipe")
            scanSetStepAction.setIcon(QtGui.QIcon(icons['write']))
            menu.addSeparator()
            saveAction = menu.addAction("Read and save as...")
            saveAction.setIcon(QtGui.QIcon(icons['read-save']))

            monitoringAction.setEnabled(
                self.variable.readable and self.variable.type in [
                    int, float, np.ndarray, pd.DataFrame])
            sliderAction.setEnabled((self.variable.writable
                                     and self.variable.readable
                                     and self.variable.type in [int, float]))
            scanParameterAction.setEnabled(self.variable.parameter_allowed)
            scanMeasureStepAction.setEnabled(self.variable.readable)
            saveAction.setEnabled(self.variable.readable)
            scanSetStepAction.setEnabled(
                self.variable.writable if self.variable.type not in [
                    tuple] else False)  # OPTIMIZE: forbid setting tuple to scanner

            choice = menu.exec_(self.gui.tree.viewport().mapToGlobal(position))
            if choice == monitoringAction: self.openMonitor()
            elif choice == sliderAction: self.openSlider()
            elif choice == scanParameterAction:
                recipe_name = self.gui.getRecipeName()
                param_name = self.gui.getParameterName()
                self.gui.setScanParameter(recipe_name, param_name, self.variable)
            elif choice == scanMeasureStepAction:
                recipe_name = self.gui.getRecipeName()
                self.gui.addStepToScanRecipe(recipe_name, 'measure', self.variable)
            elif choice == scanSetStepAction:
                recipe_name = self.gui.getRecipeName()
                self.gui.addStepToScanRecipe(recipe_name, 'set', self.variable)
            elif choice == saveAction: self.saveValue()

    def saveValue(self):
        """ Prompt user for filename to save data of the variable """
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.gui, f"Save {self.variable.name} value", os.path.join(
                paths.USER_LAST_CUSTOM_FOLDER, f'{self.variable.address()}.txt'),
            filter=SUPPORTED_EXTENSION)

        path = os.path.dirname(filename)
        if path != '':
            paths.USER_LAST_CUSTOM_FOLDER = path
            try:
                self.gui.setStatus(f"Saving value of {self.variable.name}...",
                                   5000)
                self.variable.save(filename)
                self.gui.setStatus(
                    f"Value of {self.variable.name} successfully read and save at {filename}",
                    5000)
            except Exception as e:
                self.gui.setStatus(f"An error occured: {str(e)}", 10000, False)

    def openMonitor(self):
        """ This function open the monitor associated to this variable. """
        # If the monitor is not already running, create one
        if id(self) not in self.gui.monitors.keys():
            self.gui.monitors[id(self)] = Monitor(self)
            self.gui.monitors[id(self)].show()
        # If the monitor is already running, just make as the front window
        else:
            monitor = self.gui.monitors[id(self)]
            monitor.setWindowState(
                monitor.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            monitor.activateWindow()

    def openSlider(self):
        """ This function open the slider associated to this variable. """
        # If the slider is not already running, create one
        if id(self) not in self.gui.sliders.keys():
            self.gui.sliders[id(self)] = Slider(self)
            self.gui.sliders[id(self)].show()
        # If the slider is already running, just make as the front window
        else:
            slider = self.gui.sliders[id(self)]
            slider.setWindowState(
                slider.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            slider.activateWindow()

    def clearMonitor(self):
        """ This clear monitor instances reference when quitted """
        if id(self) in self.gui.monitors.keys():
            self.gui.monitors.pop(id(self))

    def clearSlider(self):
        """ This clear the slider instances reference when quitted """
        if id(self) in self.gui.sliders.keys():
            self.gui.sliders.pop(id(self))


# Signals can be emitted only from QObjects
# These class provides convenient ways to use signals
class ReadSignal(QtCore.QObject):
    read = QtCore.Signal(object)
    def emit_read(self, value):
        self.read.emit(value)

class WriteSignal(QtCore.QObject):
    writed = QtCore.Signal()
    def emit_write(self):
        self.writed.emit()
