# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 14:54:41 2024

@author: Jonathan
"""

import sys
import re
# import ast
from typing import Any, List, Tuple

import numpy as np
import pandas as pd
from qtpy import QtCore, QtWidgets, QtGui

from .GUI_utilities import setLineEditBackground
from ..devices import DEVICES
from ..utilities import (str_to_array, str_to_dataframe, str_to_value,
                         array_to_str, dataframe_to_str)



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


# TODO add read signal to update gui (seperate class for event and use it on itemwidget creation to change setText with new value)
class Variable():

    def __init__(self, var: Any):
        if isinstance(var, Variable):
            self.raw = var.raw
            self.value = var.value
        else:
            self.raw = var
            self.value = 'Need update' if has_eval(self.raw) else self.raw

        if not has_variable(self.raw):
            try: self.value = self.evaluate()  # If no devices or variables found in name, can evaluate value safely
            except Exception as e: self.value = str(e)

    def __call__(self) -> Any:
        return self.evaluate()

    def evaluate(self):
        if has_eval(self.raw):
            value = str(self.raw)[len(EVAL): ]
            call = eval(str(value), {}, allowed_dict)
            self.value = call
        else:
            call = self.raw

        return call

    def __repr__(self) -> str:
        if type(self.raw) in [np.ndarray]:
            raw_value_str = array_to_str(self.raw, threshold=1000000, max_line_width=9000000)
        elif type(self.raw) in [pd.DataFrame]:
            raw_value_str = dataframe_to_str(self.raw, threshold=1000000)
        else:
            raw_value_str = str(self.raw)
        return raw_value_str


def set_variable(name: str, value: Any):
    # for character in r'$*."/\[]:;|, ': name = name.replace(character, '')
    assert re.match('^[a-zA-Z_][a-zA-Z0-9_]*$', name) is not None, f"Wrong format for variable '{name}'"
    var = Variable(value) if has_eval(value) else value
    VARIABLES[name] = var
    update_allowed_dict()


def get_variable(name: str) -> Any:
    return VARIABLES.get(name)


def list_variable() -> List[str]:
    return list(VARIABLES.keys())


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

    for key in list(DEVICES.keys())+list(VARIABLES.keys()):
        if key in re.findall(pattern, str(value)): return True
    else: return False


def has_eval(value: Any) -> bool:
    """ Checks if value is a string starting with '$eval:'"""
    return True if isinstance(value, str) and value.startswith(EVAL) else False


def is_Variable(value: Any):
    """ Returns True if value of type Variable """
    return isinstance(value, Variable)


def eval_variable(value: Any) -> Any:
    """ Evaluate the given python string. String can contain variables,
    devices, numpy arrays and pandas dataframes."""
    if has_eval(value): value = Variable(value)

    if is_Variable(value): return value()
    else: return value


def eval_safely(value: Any) -> Any:
    """ Same as eval_variable but do not evaluate if contains devices or variables """
    if has_eval(value): value = Variable(value)

    if is_Variable(value): return value.value
    else: return value


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

        self.show()

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
        for children in self.findChildren(
                QtWidgets.QWidget, options=QtCore.Qt.FindDirectChildrenOnly):
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
        self.show()

        # self.timer = QtCore.QTimer(self)
        # self.timer.setInterval(400) # ms
        # self.timer.timeout.connect(self.refresh_new)
        # self.timer.start()
        # VARIABLES.removeVarSignal.remove.connect(self.removeVarSignalChanged)
        # VARIABLES.addVarSignal.add.connect(self.addVarSignalChanged)

    def variableActivated(self, item: QtWidgets.QTreeWidgetItem):
        self.variableSignal.emit(item.name)

    def deviceActivated(self, item: QtWidgets.QTreeWidgetItem):
        if hasattr(item, 'name'):
            self.deviceSignal.emit(item.name)

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
        names = list_variable()

        compt = 0
        while True:
            if name in names:
                compt += 1
                name = basename + str(compt)
            else:
                break

        set_variable(name, 0)
        MyQTreeWidgetItem(self.variablesWidget, name, self)  # not catched by VARIABLES signal

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
        for i, var_name in enumerate(list_variable()):
            MyQTreeWidgetItem(self.variablesWidget, var_name, self)

        self.devicesWidget.clear()
        for i, device_name in enumerate(DEVICES):
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

        for children in self.findChildren(
                QtWidgets.QWidget, options=QtCore.Qt.FindDirectChildrenOnly):
            children.deleteLater()

        super().closeEvent(event)


class MyQTreeWidgetItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, itemParent, name, gui):

        super().__init__(itemParent, ['', name])

        self.itemParent = itemParent
        self.gui = gui
        self.name = name

        raw_value = get_variable(name)
        self.raw_value = raw_value

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

    def renameVariable(self):
        new_name = self.nameWidget.text()
        if new_name == self.name:
            setLineEditBackground(self.nameWidget, 'synced')
            return None

        if new_name in list_variable():
            self.gui.setStatus(
                f"Error: {new_name} already exist!", 10000, False)
            return None

        for character in r'$*."/\[]:;|, -(){}^=':
            new_name = new_name.replace(character, '')

        try:
            set_variable(new_name, get_variable(self.name))
        except Exception as e:
            self.gui.setStatus(f'Error: {e}', 10000, False)
        else:
            remove_variable(self.name)
            self.name = new_name
            new_name = self.nameWidget.setText(self.name)
            setLineEditBackground(self.nameWidget, 'synced')
            self.gui.setStatus('')

    def refresh_rawValue(self):
        raw_value = self.raw_value

        if type(raw_value) in [np.ndarray]:
            raw_value_str = array_to_str(raw_value)
        elif type(raw_value) in [pd.DataFrame]:
            raw_value_str = dataframe_to_str(raw_value)
        else:
            raw_value_str = str(raw_value)

        self.rawValueWidget.setText(raw_value_str)
        setLineEditBackground(self.rawValueWidget, 'synced')

        if isinstance(raw_value, Variable) and has_variable(raw_value):  # OPTIMIZE: use hide and show instead but doesn't hide on instantiation
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
        raw_value = self.raw_value

        value = eval_safely(raw_value)

        if type(value) in [np.ndarray]:
            value_str = array_to_str(value)
        elif type(value) in [pd.DataFrame]:
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
                self.raw_value = get_variable(name)
                self.refresh_rawValue()
                self.refresh_value()

    def convertVariableClicked(self):
        try: value = eval_variable(self.raw_value)
        except Exception as e:
            self.gui.setStatus(f'Error: {e}', 10000, False)
        else:
            if type(value) in [np.ndarray]:
                value_str = array_to_str(value)
            elif type(value) in [pd.DataFrame]:
                value_str = dataframe_to_str(value)
            else:
                value_str = str(value)

            self.valueWidget.setText(value_str)
            self.typeWidget.setText(str(type(value).__name__))
            # self.gui.refresh()  # OPTIMIZE replace by each variable send update signal
