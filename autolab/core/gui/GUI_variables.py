# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 14:54:41 2024

@author: Jonathan
"""

from typing import Union
import sys
import re

import numpy as np
import pandas as pd
from qtpy import QtCore, QtWidgets, QtGui

from .GUI_utilities import setLineEditBackground, MyLineEdit
from .icons import icons
from ..devices import DEVICES
from ..utilities import data_to_str, str_to_data, clean_string
from ..variables import (VARIABLES, get_variable, set_variable, Variable,
                         rename_variable, remove_variable, is_Variable,
                         has_variable, has_eval, eval_variable, EVAL)
from ..elements import Variable as Variable_og
from ..devices import get_element_by_address
from .GUI_instances import (openMonitor, openSlider, openPlotter,
                            closeMonitors, closeSliders, closePlotter,
                            clearVariablesMenu)


class VariablesMenu(QtWidgets.QMainWindow):

    variableSignal = QtCore.Signal(object)
    deviceSignal = QtCore.Signal(object)

    def __init__(self, has_parent: bool = False):

        super().__init__()
        self.has_parent = has_parent  # Only for closeEvent
        self.setWindowTitle('AUTOLAB - Variables Menu')
        self.setWindowIcon(icons['variables'])

        self.statusBar = self.statusBar()

        # Main widgets creation
        self.variablesWidget = QtWidgets.QTreeWidget(self)
        self.variablesWidget.setHeaderLabels(
            ['', 'Name', 'Value', 'Evaluated value', 'Type', 'Action'])
        self.variablesWidget.setAlternatingRowColors(True)
        self.variablesWidget.setIndentation(0)
        header = self.variablesWidget.header()
        header.setMinimumSectionSize(20)
        header.resizeSection(0, 20)
        header.resizeSection(1, 90)
        header.resizeSection(2, 120)
        header.resizeSection(3, 120)
        header.resizeSection(4, 50)
        header.resizeSection(5, 100)
        self.variablesWidget.itemDoubleClicked.connect(self.variableActivated)
        self.variablesWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
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
        self.devicesWidget.itemDoubleClicked.connect(self.deviceActivated)
        self.devicesWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.devicesWidget.customContextMenuRequested.connect(self.rightClickDevice)

        # Main layout creation
        layoutWindow = QtWidgets.QVBoxLayout()
        layoutWindow.setContentsMargins(0,0,0,0)
        layoutWindow.setSpacing(0)
        layoutTab = QtWidgets.QVBoxLayout()
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
        layoutTab.addWidget(refreshButtonWidget)

        self.resize(550, 300)
        self.refresh()

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

    def rightClickDevice(self, position: QtCore.QPoint):
        """ Provides a menu where the user right clicked to manage a variable """
        item = self.devicesWidget.itemAt(position)
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

        variable = set_variable(name, 0)

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
        for device_name, device in DEVICES.items():
            deviceItem = QtWidgets.QTreeWidgetItem(
                self.devicesWidget, [device_name])
            deviceItem.setBackground(0, QtGui.QColor('#9EB7F5'))  # blue
            deviceItem.setExpanded(True)
            for elements in device.get_structure():
                var = get_element_by_address(elements[0])
                MyQTreeWidgetItem(deviceItem, var.address(), var, self)

    def setStatus(self, message: str, timeout: int = 0, stdout: bool = True):
        """ Modify the message displayed in the status bar and add error message to logger """
        self.statusBar.showMessage(message, timeout)
        if not stdout: print(message, file=sys.stderr)

    def closeEvent(self, event):
        # self.timer.stop()
        clearVariablesMenu()

        self.variablesWidget.clear()
        self.devicesWidget.clear()

        if not self.has_parent:
            closePlotter()
            closeMonitors()
            closeSliders()

            import pyqtgraph as pg
            try:
                # Prevent 'RuntimeError: wrapped C/C++ object of type ViewBox has been deleted' when reloading gui
                for view in pg.ViewBox.AllViews.copy().keys():
                    pg.ViewBox.forgetView(id(view), view)
                    # OPTIMIZE: forget only view used in monitor/gui
                pg.ViewBox.quit()
            except: pass

        for children in self.findChildren(QtWidgets.QWidget):
            children.deleteLater()

        super().closeEvent(event)

        if not self.has_parent:
            QtWidgets.QApplication.quit()  # close the app


class MyQTreeWidgetItem(QtWidgets.QTreeWidgetItem):

    def __init__(self,
                 itemParent: Union[QtWidgets.QTreeWidget,
                                   QtWidgets.QTreeWidgetItem],
                 name: str,
                 variable: Union[Variable, Variable_og],
                 gui: QtWidgets.QMainWindow):

        self.name = name
        self.variable = variable
        self.gui = gui

        if is_Variable(self.variable):
            super().__init__(itemParent, ['', name])
        else:
            super().__init__(itemParent, [name])
            return None

        nameWidget = QtWidgets.QLineEdit()
        nameWidget.setText(name)
        nameWidget.setAlignment(QtCore.Qt.AlignCenter)
        nameWidget.returnPressed.connect(self.renameVariable)
        nameWidget.textEdited.connect(lambda: setLineEditBackground(
            nameWidget, 'edited'))
        setLineEditBackground(nameWidget, 'synced')
        self.gui.variablesWidget.setItemWidget(self, 1, nameWidget)
        self.nameWidget = nameWidget

        rawValueWidget = MyLineEdit()
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
        palette = valueWidget.palette()
        palette.setColor(QtGui.QPalette.Base,
                         palette.color(QtGui.QPalette.Base).darker(107))
        valueWidget.setPalette(palette)
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
        monitoringAction.setIcon(icons['monitor'])
        monitoringAction.setEnabled(
            (hasattr(self.variable, 'readable')  # Action don't have readable
             and self.variable.readable
             and self.variable.type in (int, float, np.ndarray, pd.DataFrame)
             ) or (
                 is_Variable(self.variable)
                 and (has_eval(self.variable.raw) or isinstance(
                     self.variable.value, (int, float, np.ndarray, pd.DataFrame)))
                 ))

        plottingAction = menu.addAction("Capture to plotter")
        plottingAction.setIcon(icons['plotter'])
        plottingAction.setEnabled(monitoringAction.isEnabled())

        menu.addSeparator()
        sliderAction = menu.addAction("Create a slider")
        sliderAction.setIcon(icons['slider'])
        sliderAction.setEnabled(
            (hasattr(self.variable, 'writable')
             and self.variable.writable
             and self.variable.type in (int, float)))

        choice = menu.exec_(
            self.gui.variablesWidget.viewport().mapToGlobal(position))
        if choice == monitoringAction:
            openMonitor(self.variable, has_parent=True)
        if choice == plottingAction:
            openPlotter(variable=self.variable, has_parent=True)
        elif choice == sliderAction:
            openSlider(self.variable, gui=self.gui, item=self)

    def renameVariable(self) -> None:
        new_name = self.nameWidget.text()
        if new_name == self.name:
            setLineEditBackground(self.nameWidget, 'synced')
            return None

        if new_name in VARIABLES:
            self.gui.setStatus(
                f"Error: {new_name} already exist!", 10000, False)
            return None

        new_name = clean_string(new_name)

        try:
            rename_variable(self.name, new_name)
        except Exception as e:
            self.gui.setStatus(f'Error: {e}', 10000, False)
        else:
            self.name = new_name
            new_name = self.nameWidget.setText(self.name)
            setLineEditBackground(self.nameWidget, 'synced')
            self.gui.setStatus('')
        return None

    def refresh_rawValue(self):
        raw_value_str = data_to_str(self.variable.raw)

        self.rawValueWidget.setText(raw_value_str)
        setLineEditBackground(self.rawValueWidget, 'synced')

        if has_variable(self.variable.raw):  # OPTIMIZE: use hide and show instead but doesn't hide on instantiation
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
        value_str = data_to_str(value)

        self.valueWidget.setText(value_str)
        self.typeWidget.setText(str(type(value)).split("'")[1])


    def changeRawValue(self):
        name = self.name
        raw_value = self.rawValueWidget.text()
        try:
            if not has_eval(raw_value):
                raw_value = str_to_data(raw_value)
            else:
                # get all variables
                raw_value_check = raw_value[len(EVAL): ]  # Allows variable with name 'eval'
                pattern1 = r'[a-zA-Z][a-zA-Z0-9._]*'
                matches1 = re.findall(pattern1, raw_value_check)
                # get variables not unclosed by ' or " (gives bad name so needs to check with all variables)
                pattern2 = r'(?<!["\'])([a-zA-Z][a-zA-Z0-9._]*)(?!["\'])'
                matches2 = re.findall(pattern2, raw_value_check)
                matches = list(set(matches1) & set(matches2))
                # Add device/variable name to matches
                for match in list(matches):
                    matches.append(match.split('.')[0])
                matches = list(set(matches))
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
            value_str = data_to_str(value)

            self.valueWidget.setText(value_str)
            self.typeWidget.setText(str(type(value)).split("'")[1])
            # self.gui.refresh()  # OPTIMIZE replace by each variable send update signal
