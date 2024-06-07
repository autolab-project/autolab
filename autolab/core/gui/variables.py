# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 14:54:41 2024

@author: Jonathan
"""

import sys
import re
# import ast
from typing import Any, List, Tuple, Union

import numpy as np
import pandas as pd
from qtpy import QtCore, QtWidgets, QtGui

from .GUI_utilities import setLineEditBackground
from .icons import icons
from ..devices import DEVICES
from ..utilities import (str_to_array, str_to_dataframe, str_to_value,
                         array_to_str, dataframe_to_str, clean_string)

from .monitoring.main import Monitor
from .slider import Slider


# class AddVarSignal(QtCore.QObject):
#     add = QtCore.Signal(object, object)
#     def emit_add(self, name, value):
#         self.add.emit(name, value)


# class RemoveVarSignal(QtCore.QObject):
#     remove = QtCore.Signal(object)
#     def emit_remove(self, name):
#         self.remove.emit(name)


# class MyDict(dict):

#     def __init__(self):
#         self.addVarSignal = AddVarSignal()
#         self.removeVarSignal = RemoveVarSignal()

#     def __setitem__(self, item, value):
#         super(MyDict, self).__setitem__(item, value)
#         self.addVarSignal.emit_add(item, value)

#     def pop(self, item):
#         super(MyDict, self).pop(item)
#         self.removeVarSignal.emit_remove(item)


# VARIABLES = MyDict()
VARIABLES = {}

EVAL = "$eval:"


def update_allowed_dict() -> dict:
    global allowed_dict  # needed to remove variables instead of just adding new one
    allowed_dict = {"np": np, "pd": pd}
    allowed_dict.update(DEVICES)
    allowed_dict.update(VARIABLES)
    return allowed_dict


allowed_dict = update_allowed_dict()

# TODO: replace refresh by (value)?
# OPTIMIZE: Variable becomes closer and closer to core.elements.Variable, could envision a merge
# TODO: refresh menu display by looking if has eval (no -> can refresh)
# TODO add read signal to update gui (seperate class for event and use it on itemwidget creation to change setText with new value)
class Variable():

    def __init__(self, name: str, var: Any):

        self.refresh(name, var)

    def refresh(self, name: str, var: Any):
        if isinstance(var, Variable):
            self.raw = var.raw
            self.value = var.value
        else:
            self.raw = var
            self.value = 'Need update' if has_eval(self.raw) else self.raw

        if not has_variable(self.raw):
            try: self.value = self.evaluate()  # If no devices or variables found in name, can evaluate value safely
            except Exception as e: self.value = str(e)

        self.name = name
        self.unit = None
        self.address = lambda: name
        self.type = type(self.raw)  # For slider

    def __call__(self, value: Any = None) -> Any:
        if value is None:
            return self.evaluate()

        self.refresh(self.name, value)
        return None


    def evaluate(self):
        if has_eval(self.raw):
            value = str(self.raw)[len(EVAL): ]
            call = eval(str(value), {}, allowed_dict)
            self.value = call
        else:
            call = self.value

        return call

    def __repr__(self) -> str:
        if isinstance(self.raw, np.ndarray):
            raw_value_str = array_to_str(self.raw, threshold=1000000, max_line_width=9000000)
        elif isinstance(self.raw, pd.DataFrame):
            raw_value_str = dataframe_to_str(self.raw, threshold=1000000)
        else:
            raw_value_str = str(self.raw)
        return raw_value_str


def rename_variable(name, new_name):
    var = remove_variable(name)
    assert var is not None
    set_variable(new_name, var)


def set_variable(name: str, value: Any):
    ''' Create or modify a Variable with provided name and value '''
    name = clean_string(name)

    if is_Variable(value):
        var = value
        var.refresh(name, value)
    else:
        var = get_variable(name)
        if var is None:
            var = Variable(name, value)
        else:
            assert is_Variable(var)
            var.refresh(name, value)

    VARIABLES[name] = var
    update_allowed_dict()


def get_variable(name: str) -> Union[Variable, None]:
    ''' Return Variable with provided name if exists else None '''
    return VARIABLES.get(name)


def remove_variable(name: str) -> Any:
    value = VARIABLES.pop(name) if name in VARIABLES else None
    update_allowed_dict()
    return value


def remove_from_config(listVariable: List[Tuple[str, Any]]):
    for var in listVariable:
        remove_variable(var[0])


def update_from_config(listVariable: List[Tuple[str, Any]]):
    for var in listVariable:
        set_variable(var[0], var[1])


def convert_str_to_data(raw_value: str) -> Any:
    """ Convert data in str format to proper format """
    if not has_eval(raw_value):
        if '\t' in raw_value and '\n' in raw_value:
            try: raw_value = str_to_dataframe(raw_value)
            except: pass
        elif '[' in raw_value:
            try: raw_value = str_to_array(raw_value)
            except: pass
        else:
            try: raw_value = str_to_value(raw_value)
            except: pass
    return raw_value


def has_variable(value: str) -> bool:
    pattern = r'[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?'

    for key in (list(DEVICES) + list(VARIABLES)):
        if key in [var.split('.')[0] for var in re.findall(pattern, str(value))]:
            return True
    return False


def has_eval(value: Any) -> bool:
    """ Checks if value is a string starting with '$eval:'"""
    return True if isinstance(value, str) and value.startswith(EVAL) else False


def is_Variable(value: Any):
    """ Returns True if value of type Variable """
    return isinstance(value, Variable)


def eval_variable(value: Any) -> Any:
    """ Evaluate the given python string. String can contain variables,
    devices, numpy arrays and pandas dataframes."""
    if has_eval(value): value = Variable('temp', value)

    if is_Variable(value): return value()
    return value


def eval_safely(value: Any) -> Any:
    """ Same as eval_variable but do not evaluate if contains devices or variables """
    if has_eval(value): value = Variable('temp', value)

    if is_Variable(value): return value.value
    return value


class VariablesDialog(QtWidgets.QDialog):

    def __init__(self, parent: QtWidgets.QMainWindow, name: str, defaultValue: str):

        super().__init__(parent)
        self.setWindowTitle(name)
        self.setWindowModality(QtCore.Qt.ApplicationModal)  # block GUI interaction

        self.variablesMenu = None
        # ORDER of creation mater to have button OK selected instead of Variables
        variablesButton = QtWidgets.QPushButton('Variables', self)
        variablesButton.clicked.connect(self.variablesButtonClicked)

        hbox = QtWidgets.QHBoxLayout(self)
        hbox.addStretch()
        hbox.addWidget(variablesButton)
        hbox.setContentsMargins(10,0,10,10)

        widget = QtWidgets.QWidget(self)
        widget.setLayout(hbox)

        dialog = QtWidgets.QInputDialog(self)
        dialog.setLabelText(f"Set {name} value")
        dialog.setInputMode(QtWidgets.QInputDialog.TextInput)
        dialog.setWindowFlags(dialog.windowFlags() & ~QtCore.Qt.Dialog)

        lineEdit = dialog.findChild(QtWidgets.QLineEdit)
        lineEdit.setMaxLength(10000000)
        dialog.setTextValue(defaultValue)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(dialog)
        layout.addWidget(widget)
        layout.addStretch()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        self.exec_ = dialog.exec_
        self.textValue = dialog.textValue
        self.setTextValue = dialog.setTextValue

    def variablesButtonClicked(self):
        if self.variablesMenu is None:
            self.variablesMenu = VariablesMenu(self)
            self.variablesMenu.setWindowTitle(
                self.windowTitle()+": "+self.variablesMenu.windowTitle())

            self.variablesMenu.variableSignal.connect(self.toggleVariableName)
            self.variablesMenu.deviceSignal.connect(self.toggleDeviceName)
            self.variablesMenu.show()
        else:
            self.variablesMenu.refresh()

    def clearVariablesMenu(self):
        """ This clear the variables menu instance reference when quitted """
        self.variablesMenu = None

    def toggleVariableName(self, name):
        value = self.textValue()
        if is_Variable(get_variable(name)): name += '()'

        if value in ('0', "''"): value = ''
        if not has_eval(value): value = EVAL + value

        if value.endswith(name): value = value[:-len(name)]
        else: value += name

        if value == EVAL: value = ''

        self.setTextValue(value)

    def toggleDeviceName(self, name):
        name += '()'
        self.toggleVariableName(name)

    def closeEvent(self, event):
        for children in self.findChildren(QtWidgets.QWidget):
            children.deleteLater()
        super().closeEvent(event)


class VariablesMenu(QtWidgets.QMainWindow):

    variableSignal = QtCore.Signal(object)
    deviceSignal = QtCore.Signal(object)

    def __init__(self, parent: QtWidgets.QMainWindow = None):

        super().__init__(parent)
        self.gui = parent
        self.setWindowTitle('Variables manager')

        self.statusBar = self.statusBar()

        # Main widgets creation
        self.variablesWidget = QtWidgets.QTreeWidget(self)
        self.variablesWidget.setHeaderLabels(
            ['', 'Name', 'Value', 'Evaluated value', 'Type', 'Action'])
        self.variablesWidget.setAlternatingRowColors(True)
        self.variablesWidget.setIndentation(0)
        self.variablesWidget.setStyleSheet(
            "QHeaderView::section { background-color: lightgray; }")
        header = self.variablesWidget.header()
        header.setMinimumSectionSize(20)
        header.resizeSection(0, 20)
        header.resizeSection(1, 90)
        header.resizeSection(2, 120)
        header.resizeSection(3, 120)
        header.resizeSection(4, 50)
        header.resizeSection(5, 100)
        self.variablesWidget.itemDoubleClicked.connect(self.variableActivated)
        self.variablesWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.variablesWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.variablesWidget.customContextMenuRequested.connect(self.rightClick)

        addButton = QtWidgets.QPushButton('Add')
        addButton.clicked.connect(self.addVariableAction)

        removeButton = QtWidgets.QPushButton('Remove')
        removeButton.clicked.connect(self.removeVariableAction)

        self.devicesWidget = QtWidgets.QTreeWidget(self)
        self.devicesWidget.setHeaderLabels(['Name'])
        self.devicesWidget.setAlternatingRowColors(True)
        self.devicesWidget.setIndentation(10)
        self.devicesWidget.setStyleSheet("QHeaderView::section { background-color: lightgray; }")
        self.devicesWidget.itemDoubleClicked.connect(self.deviceActivated)

        # Main layout creation
        layoutWindow = QtWidgets.QVBoxLayout()
        layoutTab = QtWidgets.QHBoxLayout()
        layoutWindow.addLayout(layoutTab)

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(layoutWindow)
        self.setCentralWidget(centralWidget)

        refreshButtonWidget = QtWidgets.QPushButton()
        refreshButtonWidget.setText('Refresh Manager')
        refreshButtonWidget.clicked.connect(self.refresh)

        # Main layout definition
        layoutButton = QtWidgets.QHBoxLayout()
        layoutButton.addWidget(addButton)
        layoutButton.addWidget(removeButton)
        layoutButton.addWidget(refreshButtonWidget)
        layoutButton.addStretch()

        frameVariables = QtWidgets.QFrame()
        layoutVariables = QtWidgets.QVBoxLayout(frameVariables)
        layoutVariables.addWidget(self.variablesWidget)
        layoutVariables.addLayout(layoutButton)

        frameDevices = QtWidgets.QFrame()
        layoutDevices = QtWidgets.QVBoxLayout(frameDevices)
        layoutDevices.addWidget(self.devicesWidget)

        tab = QtWidgets.QTabWidget(self)
        tab.addTab(frameVariables, 'Variables')
        tab.addTab(frameDevices, 'Devices')

        layoutTab.addWidget(tab)

        self.resize(550, 300)
        self.refresh()

        self.monitors = {}
        self.sliders = {}
        # self.timer = QtCore.QTimer(self)
        # self.timer.setInterval(400) # ms
        # self.timer.timeout.connect(self.refresh_new)
        # self.timer.start()
        # VARIABLES.removeVarSignal.remove.connect(self.removeVarSignalChanged)
        # VARIABLES.addVarSignal.add.connect(self.addVarSignalChanged)

    def variableActivated(self, item: QtWidgets.QTreeWidgetItem):
        self.variableSignal.emit(item.name)

    def rightClick(self, position: QtCore.QPoint):
        """ Provides a menu where the user right clicked to manage a variable """
        item = self.variablesWidget.itemAt(position)
        if hasattr(item, 'menu'): item.menu(position)

    def deviceActivated(self, item: QtWidgets.QTreeWidgetItem):
        if hasattr(item, 'name'): self.deviceSignal.emit(item.name)

    def removeVariableAction(self):
        for variableItem in self.variablesWidget.selectedItems():
            remove_variable(variableItem.name)
            self.removeVariableItem(variableItem)

    # def addVariableItem(self, name):
    #     MyQTreeWidgetItem(self.variablesWidget, name, self)

    def removeVariableItem(self, item: QtWidgets.QTreeWidgetItem):
        index = self.variablesWidget.indexFromItem(item)
        self.variablesWidget.takeTopLevelItem(index.row())

    def addVariableAction(self):
        basename = 'var'
        name = basename
        names = list(VARIABLES)

        compt = 0
        while True:
            if name in names:
                compt += 1
                name = basename + str(compt)
            else:
                break

        set_variable(name, 0)

        variable = get_variable(name)
        MyQTreeWidgetItem(self.variablesWidget, name, variable, self)  # not catched by VARIABLES signal

    # def addVarSignalChanged(self, key, value):
    #     print('got add signal', key, value)
    #     all_items = [self.variablesWidget.topLevelItem(i) for i in range(
    #         self.variablesWidget.topLevelItemCount())]

    #     for variableItem in all_items:
    #         if variableItem.name == key:
    #             variableItem.raw_value = get_variable(variableItem.name)
    #             variableItem.refresh_rawValue()
    #             variableItem.refresh_value()
    #             break
    #     else:
    #         self.addVariableItem(key)
    #     # self.refresh()  # TODO: check if item exists, create if not, update if yes

    # def removeVarSignalChanged(self, key):
    #     print('got remove signal', key)
    #     all_items = [self.variablesWidget.topLevelItem(i) for i in range(
    #         self.variablesWidget.topLevelItemCount())]

    #     for variableItem in all_items:
    #         if variableItem.name == key:
    #             self.removeVariableItem(variableItem)

    #     # self.refresh()  # TODO: check if exists, remove if yes

    def refresh(self):
        self.variablesWidget.clear()
        for var_name in VARIABLES:
            variable = get_variable(var_name)
            MyQTreeWidgetItem(self.variablesWidget, var_name, variable, self)

        self.devicesWidget.clear()
        for device_name in DEVICES:
            device = DEVICES[device_name]
            deviceItem = QtWidgets.QTreeWidgetItem(
                self.devicesWidget, [device_name])
            deviceItem.setBackground(0, QtGui.QColor('#9EB7F5'))  # blue
            deviceItem.setExpanded(True)
            for elements in device.get_structure():
                deviceItem2 = QtWidgets.QTreeWidgetItem(
                    deviceItem, [elements[0]])
                deviceItem2.name = elements[0]

    def setStatus(self, message: str, timeout: int = 0, stdout: bool = True):
        """ Modify the message displayed in the status bar and add error message to logger """
        self.statusBar.showMessage(message, timeout)
        if not stdout: print(message, file=sys.stderr)

    def closeEvent(self, event):
        # self.timer.stop()
        if self.gui is not None and hasattr(self.gui, 'clearVariablesMenu'):
            self.gui.clearVariablesMenu()

        for monitor in list(self.monitors.values()):
            monitor.close()

        for slider in list(self.sliders.values()):
            slider.close()

        for children in self.findChildren(QtWidgets.QWidget):
            children.deleteLater()

        super().closeEvent(event)


class MyQTreeWidgetItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, itemParent, name, variable, gui):

        super().__init__(itemParent, ['', name])

        self.itemParent = itemParent
        self.gui = gui
        self.name = name
        self.variable = variable

        nameWidget = QtWidgets.QLineEdit()
        nameWidget.setText(name)
        nameWidget.setAlignment(QtCore.Qt.AlignCenter)
        nameWidget.returnPressed.connect(self.renameVariable)
        nameWidget.textEdited.connect(lambda: setLineEditBackground(
            nameWidget, 'edited'))
        setLineEditBackground(nameWidget, 'synced')
        self.gui.variablesWidget.setItemWidget(self, 1, nameWidget)
        self.nameWidget = nameWidget

        rawValueWidget = QtWidgets.QLineEdit()
        rawValueWidget.setMaxLength(10000000)
        rawValueWidget.setAlignment(QtCore.Qt.AlignCenter)
        rawValueWidget.returnPressed.connect(self.changeRawValue)
        rawValueWidget.textEdited.connect(lambda: setLineEditBackground(
            rawValueWidget, 'edited'))
        self.gui.variablesWidget.setItemWidget(self, 2, rawValueWidget)
        self.rawValueWidget = rawValueWidget

        valueWidget = QtWidgets.QLineEdit()
        valueWidget.setMaxLength(10000000)
        valueWidget.setReadOnly(True)
        valueWidget.setStyleSheet(
            "QLineEdit {border: 1px solid #a4a4a4; background-color: #f4f4f4}")
        valueWidget.setAlignment(QtCore.Qt.AlignCenter)
        self.gui.variablesWidget.setItemWidget(self, 3, valueWidget)
        self.valueWidget = valueWidget

        typeWidget = QtWidgets.QLabel()
        typeWidget.setAlignment(QtCore.Qt.AlignCenter)
        self.gui.variablesWidget.setItemWidget(self, 4, typeWidget)
        self.typeWidget = typeWidget

        self.actionButtonWidget = None

        self.refresh_rawValue()
        self.refresh_value()

    def menu(self, position: QtCore.QPoint):
        """ This function provides the menu when the user right click on an item """
        menu = QtWidgets.QMenu()
        monitoringAction = menu.addAction("Start monitoring")
        monitoringAction.setIcon(QtGui.QIcon(icons['monitor']))
        monitoringAction.setEnabled(has_eval(self.variable.raw) or isinstance(
            self.variable.value, (int, float, np.ndarray, pd.DataFrame)))

        menu.addSeparator()
        sliderAction = menu.addAction("Create a slider")
        sliderAction.setIcon(QtGui.QIcon(icons['slider']))
        sliderAction.setEnabled(self.variable.type in (int, float))

        choice = menu.exec_(self.gui.variablesWidget.viewport().mapToGlobal(position))
        if choice == monitoringAction: self.openMonitor()
        elif choice == sliderAction: self.openSlider()

    def openMonitor(self):
        """ This function open the monitor associated to this variable. """
        # If the monitor is not already running, create one
        if id(self) not in self.gui.monitors:
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
        if id(self) not in self.gui.sliders:
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
        if id(self) in self.gui.monitors:
            self.gui.monitors.pop(id(self))

    def clearSlider(self):
        """ This clear the slider instances reference when quitted """
        if id(self) in self.gui.sliders:
            self.gui.sliders.pop(id(self))

    def renameVariable(self):
        new_name = self.nameWidget.text()
        if new_name == self.name:
            setLineEditBackground(self.nameWidget, 'synced')
            return None

        if new_name in VARIABLES:
            self.gui.setStatus(
                f"Error: {new_name} already exist!", 10000, False)
            return None

        for character in r'$*."/\[]:;|, -(){}^=':
            new_name = new_name.replace(character, '')

        try:
            rename_variable(self.name, new_name)
        except Exception as e:
            self.gui.setStatus(f'Error: {e}', 10000, False)
        else:
            self.name = new_name
            new_name = self.nameWidget.setText(self.name)
            setLineEditBackground(self.nameWidget, 'synced')
            self.gui.setStatus('')

    def refresh_rawValue(self):
        raw_value = self.variable.raw

        if isinstance(raw_value, np.ndarray):
            raw_value_str = array_to_str(raw_value)
        elif isinstance(raw_value, pd.DataFrame):
            raw_value_str = dataframe_to_str(raw_value)
        else:
            raw_value_str = str(raw_value)

        self.rawValueWidget.setText(raw_value_str)
        setLineEditBackground(self.rawValueWidget, 'synced')

        if has_variable(self.variable):  # OPTIMIZE: use hide and show instead but doesn't hide on instantiation
            if self.actionButtonWidget is None:
                actionButtonWidget = QtWidgets.QPushButton()
                actionButtonWidget.setText('Update value')
                actionButtonWidget.setMinimumSize(0, 23)
                actionButtonWidget.setMaximumSize(85, 23)
                actionButtonWidget.clicked.connect(self.convertVariableClicked)
                self.gui.variablesWidget.setItemWidget(self, 5, actionButtonWidget)
                self.actionButtonWidget = actionButtonWidget
        else:
            self.gui.variablesWidget.removeItemWidget(self, 5)
            self.actionButtonWidget = None

    def refresh_value(self):
        value = self.variable.value

        if isinstance(value, np.ndarray):
            value_str = array_to_str(value)
        elif isinstance(value, pd.DataFrame):
            value_str = dataframe_to_str(value)
        else:
            value_str = str(value)

        self.valueWidget.setText(value_str)
        self.typeWidget.setText(str(type(value).__name__))

    def changeRawValue(self):
        name = self.name
        raw_value = self.rawValueWidget.text()
        try:
            if not has_eval(raw_value):
                raw_value = convert_str_to_data(raw_value)
            else:
                # get all variables
                pattern1 = r'[a-zA-Z][a-zA-Z0-9._]*'
                matches1 = re.findall(pattern1, raw_value)
                # get variables not unclosed by ' or " (gives bad name so needs to check with all variables)
                pattern2 = r'(?<!["\'])([a-zA-Z][a-zA-Z0-9._]*)(?!["\'])'
                matches2 = re.findall(pattern2, raw_value)
                matches = list(set(matches1) & set(matches2))
                assert name not in matches, f"Variable '{name}' name can't be used in eval to avoid circular definition"
        except Exception as e:
            self.gui.setStatus(f'Error: {e}', 10000, False)
        else:
            try: set_variable(name, raw_value)
            except Exception as e:
                self.gui.setStatus(f'Error: {e}', 10000)
            else:
                self.refresh_rawValue()
                self.refresh_value()

    def convertVariableClicked(self):
        try: value = eval_variable(self.variable)
        except Exception as e:
            self.gui.setStatus(f'Error: {e}', 10000, False)
        else:
            if isinstance(value, np.ndarray):
                value_str = array_to_str(value)
            elif isinstance(value, pd.DataFrame):
                value_str = dataframe_to_str(value)
            else:
                value_str = str(value)

            self.valueWidget.setText(value_str)
            self.typeWidget.setText(str(type(value).__name__))
            # self.gui.refresh()  # OPTIMIZE replace by each variable send update signal
