# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:29:07 2019

@author: qchat
"""


import os
from typing import Any, Union

import pandas as pd
import numpy as np
from qtpy import QtCore, QtWidgets, QtGui

from ..icons import icons
from ..GUI_utilities import (MyLineEdit, MyInputDialog, MyQCheckBox, MyQComboBox,
                             qt_object_exists)
from ..GUI_instances import openMonitor, openSlider, openPlotter, openAddDevice
from ...paths import PATHS
from ...config import get_control_center_config
from ...variables import eval_variable, has_eval
from ...devices import close, list_loaded_devices
from ...utilities import (SUPPORTED_EXTENSION, str_to_array, array_to_str,
                          dataframe_to_str, str_to_dataframe, create_array,
                          str_to_tuple)


class CustomMenu(QtWidgets.QMenu):
    """ Menu with action containing sub-menu for recipe and parameter selection """

    def __init__(self, gui):
        super().__init__()
        self.gui = gui
        self.current_menu = 1
        self.selected_action = None

        self.recipe_cb = self.gui.scanner.selectRecipe_comboBox if (
            self.gui.scanner) else None
        self.recipe_names = [self.recipe_cb.itemText(i) for i in range(
            self.recipe_cb.count())] if self.recipe_cb else []
        self.param_cb = self.gui.scanner.selectParameter_comboBox if (
            self.gui.scanner) else None

        self.HAS_RECIPE = len(self.recipe_names) > 1
        self.HAS_PARAM = (self.param_cb.count() > 1 if self.param_cb is not None
                          else False)

    def addAnyAction(self, action_text='', icon_name='',
                     param_menu_active=False) -> Union[QtWidgets.QWidgetAction,
                                                       QtWidgets.QAction]:

        if self.HAS_RECIPE or (self.HAS_PARAM and param_menu_active):
            action = self.addCustomAction(action_text, icon_name,
                                          param_menu_active=param_menu_active)
        else:
            action = self.addAction(action_text)
            if icon_name != '':
                action.setIcon(QtGui.QIcon(icons[icon_name]))

        return action

    def addCustomAction(self, action_text='', icon_name='',
                        param_menu_active=False) -> QtWidgets.QWidgetAction:
        """ Create an action with a sub menu for selecting a recipe and parameter """

        def close_menu():
            self.selected_action = action_widget
            self.close()

        def handle_hover():
            """ Fixe bad hover behavior and refresh radio_button """
            self.setActiveAction(action_widget)
            recipe_name = self.recipe_cb.currentText()
            action = recipe_menu.actions()[self.recipe_names.index(recipe_name)]
            radio_button = action.defaultWidget()

            if not radio_button.isChecked():
                radio_button.setChecked(True)

        def handle_radio_click(name):
            """ Update parameters available, open parameter menu if available
            and close main menu to validate the action """
            if self.current_menu == 1:
                self.recipe_cb.setCurrentIndex(self.recipe_names.index(name))
                self.gui.scanner._updateSelectParameter()
                recipe_menu.close()

                if param_menu_active:
                    param_items = [self.param_cb.itemText(i) for i in range(
                        self.param_cb.count())]

                    if len(param_items) > 1:
                        self.current_menu = 2
                        setup_menu_parameter(param_menu)
                        return None
            else:
                update_parameter(name)
                param_menu.close()
                self.current_menu = 1
                action_button.setMenu(recipe_menu)

            close_menu()

        def reset_menu(button: QtWidgets.QToolButton):
            QtWidgets.QApplication.sendEvent(
                button, QtCore.QEvent(QtCore.QEvent.Leave))
            self.current_menu = 1
            action_button.setMenu(recipe_menu)

        def setup_menu_parameter(param_menu: QtWidgets.QMenu):
            param_items = [self.param_cb.itemText(i) for i in range(
                self.param_cb.count())]
            param_name = self.param_cb.currentText()

            param_menu.clear()
            for param_name_i in param_items:
                add_radio_button_to_menu(param_name_i, param_name, param_menu)

            action_button.setMenu(param_menu)
            action_button.showMenu()

        def update_parameter(name: str):
            param_items = [self.param_cb.itemText(i) for i in range(
                self.param_cb.count())]
            self.param_cb.setCurrentIndex(param_items.index(name))
            self.gui.scanner._updateSelectParameter()

        def add_radio_button_to_menu(item_name: str, current_name: str,
                                     target_menu: QtWidgets.QMenu):
            widget = QtWidgets.QWidget()
            radio_button = QtWidgets.QRadioButton(item_name, widget)
            action = QtWidgets.QWidgetAction(self.gui)
            action.setDefaultWidget(radio_button)
            target_menu.addAction(action)

            if item_name == current_name:
                radio_button.setChecked(True)

            radio_button.clicked.connect(
                lambda: handle_radio_click(item_name))

        # Add custom action
        action_button = QtWidgets.QToolButton()
        action_button.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        action_button.setText(f"   {action_text}")
        action_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        action_button.setAutoRaise(True)
        action_button.clicked.connect(close_menu)
        action_button.enterEvent = lambda event: handle_hover()
        if icon_name != '':
            action_button.setIcon(QtGui.QIcon(icons[icon_name]))

        action_widget = QtWidgets.QWidgetAction(action_button)
        action_widget.setDefaultWidget(action_button)
        self.addAction(action_widget)

        recipe_menu = QtWidgets.QMenu()
        # recipe_menu.aboutToShow.connect(lambda: self.set_clickable(False))
        recipe_menu.aboutToHide.connect(lambda: reset_menu(action_button))

        if param_menu_active:
            param_menu = QtWidgets.QMenu()
            # param_menu.aboutToShow.connect(lambda: self.set_clickable(False))
            param_menu.aboutToHide.connect(lambda: reset_menu(action_button))

        recipe_name = self.gui.scanner.selectRecipe_comboBox.currentText()

        for recipe_name_i in self.recipe_names:
            add_radio_button_to_menu(recipe_name_i, recipe_name, recipe_menu)

        action_button.setMenu(recipe_menu)

        return action_widget


class TreeWidgetItemModule(QtWidgets.QTreeWidgetItem):
    """ This class represents a module in an item of the tree """

    def __init__(self, itemParent, name, gui):

        self.name = name
        self.module = None
        self.loaded = False
        self.gui = gui
        self.is_not_submodule = isinstance(gui.tree, type(itemParent))

        if self.is_not_submodule:
            super().__init__(itemParent, [name, 'Device'])
        else:
            super().__init__(itemParent, [name, 'Module'])

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
        if self.is_not_submodule:
            if self.loaded:
                menu = QtWidgets.QMenu()
                disconnectDevice = menu.addAction(f"Disconnect {self.name}")
                disconnectDevice.setIcon(QtGui.QIcon(icons['disconnect']))

                choice = menu.exec_(self.gui.tree.viewport().mapToGlobal(position))

                if choice == disconnectDevice:
                    close(self.name)

                    for i in range(self.childCount()):
                        self.removeChild(self.child(0))

                    self.loaded = False

                if not list_loaded_devices():
                    self.gui.timerQueue.stop()
            elif id(self) in self.gui.threadManager.threads_conn:
                menu = QtWidgets.QMenu()
                cancelDevice = menu.addAction('Cancel loading')
                cancelDevice.setIcon(QtGui.QIcon(icons['disconnect']))

                choice = menu.exec_(self.gui.tree.viewport().mapToGlobal(position))

                if choice == cancelDevice:
                    self.gui.itemCanceled(self)
            else:
                menu = QtWidgets.QMenu()
                modifyDeviceChoice = menu.addAction('Modify device')
                modifyDeviceChoice.setIcon(QtGui.QIcon(icons['rename']))

                choice = menu.exec_(self.gui.tree.viewport().mapToGlobal(position))

                if choice == modifyDeviceChoice:
                    openAddDevice(gui=self.gui, name=self.name)


class TreeWidgetItemAction(QtWidgets.QTreeWidgetItem):
    """ This class represents an action in an item of the tree """

    def __init__(self, itemParent, action, gui):

        displayName = f'{action.name}'
        if action.unit is not None:
            displayName += f' ({action.unit})'

        super().__init__(itemParent, [displayName, 'Action'])
        self.setTextAlignment(1, QtCore.Qt.AlignHCenter)

        self.gui = gui
        self.action = action

        if self.action.has_parameter:
            if self.action.type in [int, float, str, np.ndarray, pd.DataFrame]:
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
            self.valueWidget = MyLineEdit()
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
                if self.action.unit == "filename":  # TODO: LEGACY (to remove later)
                    self.gui.setStatus("Using 'filename' as unit is depreciated in favor of 'open-file' and 'save-file'" \
                                       f"\nUpdate driver '{self.action.address().split('.')[0]}' to remove this warning",
                                       10000, False)
                    self.action.unit = "open-file"

                if self.action.unit == "open-file":
                    filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                        self.gui, caption=f"Open file - {self.action.address()}",
                        directory=PATHS['last_folder'],
                        filter=SUPPORTED_EXTENSION)
                elif self.action.unit == "save-file":
                    filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                        self.gui, caption=f"Save file - {self.action.address()}",
                        directory=PATHS['last_folder'],
                        filter=SUPPORTED_EXTENSION)

                if filename != '':
                    path = os.path.dirname(filename)
                    PATHS['last_folder'] = path
                    return filename
                else:
                    self.gui.setStatus(
                        f"Action {self.action.address()} cancel filename selection",
                        10000)
            elif self.action.unit == "user-input":
                main_dialog = MyInputDialog(self.gui, self.action.address())
                main_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
                main_dialog.show()

                if main_dialog.exec_() == QtWidgets.QInputDialog.Accepted:
                    response = main_dialog.textValue()
                else:
                    response = ''

                if qt_object_exists(main_dialog): main_dialog.deleteLater()

                if response != '':
                    return response
                else:
                    self.gui.setStatus(
                        f"Action {self.action.address()} cancel user input",
                        10000)
            else:
                self.gui.setStatus(
                    f"Action {self.action.address()} requires a value for its parameter",
                    10000, False)
        else:
            try:
                value = eval_variable(value)
                if self.action.type in [np.ndarray]:
                    if isinstance(value, str): value = str_to_array(value)
                elif self.action.type in [pd.DataFrame]:
                    if isinstance(value, str): value = str_to_dataframe(value)
                else:
                    value = self.action.type(value)
                return value
            except Exception as e:
                self.gui.setStatus(
                    f"Action {self.action.address()}: {e}",
                    10000, False)

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
            menu = CustomMenu(self.gui)

            scanRecipe = menu.addAnyAction('Do in scan recipe', 'action')

            choice = menu.exec_(self.gui.tree.viewport().mapToGlobal(position))
            if choice is None: choice = menu.selected_action

            if choice == scanRecipe:
                recipe_name = self.gui.getRecipeName()
                self.gui.addStepToScanRecipe(recipe_name, 'action', self.action)


class TreeWidgetItemVariable(QtWidgets.QTreeWidgetItem):
    """ This class represents a variable in an item of the tree """

    def __init__(self, itemParent, variable, gui):

        displayName = f'{variable.name}'
        if variable.unit is not None:
            displayName += f' ({variable.unit})'

        super().__init__(itemParent, [displayName, 'Variable'])
        self.setTextAlignment(1, QtCore.Qt.AlignHCenter)

        self.gui = gui
        self.variable = variable

        # Import Autolab config
        control_center_config = get_control_center_config()
        self.precision = int(control_center_config['precision'])

        # Signal creation and associations in autolab devices instances
        self.readSignal = ReadSignal()
        self.readSignal.read.connect(self.writeGui)
        self.variable._read_signal = self.readSignal
        self.writeSignal = WriteSignal()
        self.writeSignal.writed.connect(self.valueWrited)
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
                self.readButtonCheck.stateChanged.connect(
                    self.readButtonCheckEdited)
                self.readButtonCheck.setToolTip(
                    'Toggle reading in text, ' \
                    'careful can truncate data and impact performance')
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
                self.valueWidget = MyLineEdit()
                self.valueWidget.setAlignment(QtCore.Qt.AlignCenter)
                self.valueWidget.returnPressed.connect(self.write)
                self.valueWidget.textEdited.connect(self.valueEdited)
                self.valueWidget.setMaxLength(10000000)  # default is 32767, not enought for array and dataframe
                # self.valueWidget.setPlaceholderText(self.variable._help)  # Could be nice but take too much place. Maybe add it as option
            elif self.variable.readable:
                self.valueWidget = QtWidgets.QLineEdit()
                self.valueWidget.setMaxLength(10000000)
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

            self.valueWidget = MyQCheckBox(self)
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

            if self.variable.writable:
                self.valueWidget = MyQComboBox()
                self.valueWidget.wheel = False  # prevent changing value by mistake
                self.valueWidget.key = False
                self.valueWidget.activated.connect(self.write)
                self.valueWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                self.valueWidget.customContextMenuRequested.connect(self.openInputDialog)
            elif self.variable.readable:
                self.valueWidget = MyQComboBox()
                self.valueWidget.readonly = True
            else:
                self.valueWidget = QtWidgets.QLabel()
                self.valueWidget.setAlignment(QtCore.Qt.AlignCenter)

            self.gui.tree.setItemWidget(self, 3, self.valueWidget)

        # Main - column 4 : indicator (status of the actual value : known or not known)
        if self.variable.type in [
                int, float, str, bool, tuple, np.ndarray, pd.DataFrame]:
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

    def openInputDialog(self, position: QtCore.QPoint):
        """ Only used for tuple """
        menu = QtWidgets.QMenu()
        modifyTuple = menu.addAction("Modify tuple")
        modifyTuple.setIcon(QtGui.QIcon(icons['tuple']))

        choice = menu.exec_(self.valueWidget.mapToGlobal(position))

        if choice == modifyTuple:
            main_dialog = MyInputDialog(self.gui, self.variable.address())
            main_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            if self.variable.type in [tuple]:
                main_dialog.setTextValue(str(self.variable.value))
            main_dialog.show()

            if main_dialog.exec_() == QtWidgets.QInputDialog.Accepted:
                response = main_dialog.textValue()
            else:
                response = ''

            if qt_object_exists(main_dialog): main_dialog.deleteLater()

            if response != '':
                try:
                    if has_eval(response):
                        response = eval_variable(response)
                    if self.variable.type in [tuple]:
                        response = str_to_tuple(str(response))
                except Exception as e:
                    self.gui.setStatus(
                        f"Variable {self.variable.address()}: {e}", 10000, False)
                    return None

                self.variable(response)

                if self.variable.readable:
                    self.variable()

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
                items = [self.valueWidget.itemText(i)
                         for i in range(self.valueWidget.count())]
                if value[0] != items:
                    self.valueWidget.clear()
                    self.valueWidget.addItems(value[0])
                self.valueWidget.setCurrentIndex(value[1])
            elif self.variable.type in [np.ndarray, pd.DataFrame]:

                if self.variable.writable or self.readButtonCheck.isChecked():
                    if self.variable.type in [np.ndarray]:
                        self.valueWidget.setText(array_to_str(value))
                    if self.variable.type in [pd.DataFrame]:
                        self.valueWidget.setText(dataframe_to_str(value))
                # else:
                #     self.valueWidget.setText('')

            # Change indicator light to green
            if self.variable.type in [
                    int, float, bool, str, tuple, np.ndarray, pd.DataFrame]:
                self.setValueKnownState(True)

    def readGui(self):
        """ This function returns the value in good format of the value in the GUI """
        if self.variable.type in [int, float, str, np.ndarray, pd.DataFrame]:
            value = self.valueWidget.text()
            if value == '':
                self.gui.setStatus(
                    f"Variable {self.variable.address()} requires a value to be set",
                    10000, False)
            else:
                try:
                    value = eval_variable(value)
                    if self.variable.type in [np.ndarray]:
                        if isinstance(value, str): value = str_to_array(value)
                        else: value = create_array(value)
                    elif self.variable.type in [pd.DataFrame]:
                        if isinstance(value, str): value = str_to_dataframe(value)
                    else:
                        value = self.variable.type(value)
                    return value
                except Exception as e:
                    self.gui.setStatus(
                        f"Variable {self.variable.address()}: {e}",
                        10000, False)

        elif self.variable.type in [bool]:
            value = self.valueWidget.isChecked()
            return value
        elif self.variable.type in [tuple]:
            items = [self.valueWidget.itemText(i)
                     for i in range(self.valueWidget.count())]
            value = (items, self.valueWidget.currentIndex())
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

    def valueWrited(self, value: Any):
        """ Function call when the value displayed in not sure anymore.
            The value has been modified either in the GUI (but not sent)
            or by command line.
            If variable not readable, write the value sent to the GUI """
        # BUG: I got an error when changing emit_write to set value, need to reproduce it
        try:
            self.writeGui(value)
            self.indicator.setStyleSheet("background-color:#FFFF00")  # yellow
        except Exception as e:
            self.gui.setStatus(f"SHOULD NOT RAISE ERROR: {e}", 10000, False)


    def valueEdited(self):
        """ Function call when the value displayed in not sure anymore.
            The value has been modified either in the GUI (but not sent)
            or by command line """
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
            menu = CustomMenu(self.gui)
            monitoringAction = menu.addAction("Start monitoring")
            monitoringAction.setIcon(QtGui.QIcon(icons['monitor']))
            plottingAction = menu.addAction("Capture to plotter")
            plottingAction.setIcon(QtGui.QIcon(icons['plotter']))
            menu.addSeparator()
            sliderAction = menu.addAction("Create a slider")
            sliderAction.setIcon(QtGui.QIcon(icons['slider']))
            menu.addSeparator()

            scanParameterAction = menu.addAnyAction(
                'Set as scan parameter', 'parameter', param_menu_active=True)
            scanMeasureStepAction = menu.addAnyAction(
                'Measure in scan recipe', 'measure')
            scanSetStepAction = menu.addAnyAction(
                'Set value in scan recipe', 'write')

            menu.addSeparator()
            saveAction = menu.addAction("Read and save as...")
            saveAction.setIcon(QtGui.QIcon(icons['read-save']))

            monitoringAction.setEnabled(
                self.variable.readable and self.variable.type in [
                    int, float, np.ndarray, pd.DataFrame])
            plottingAction.setEnabled(monitoringAction.isEnabled())
            sliderAction.setEnabled((self.variable.writable
                                     #and self.variable.readable
                                     and self.variable.type in [int, float]))
            scanParameterAction.setEnabled(self.variable.parameter_allowed)
            scanMeasureStepAction.setEnabled(self.variable.readable)
            saveAction.setEnabled(self.variable.readable)
            scanSetStepAction.setEnabled(self.variable.writable)

            choice = menu.exec_(self.gui.tree.viewport().mapToGlobal(position))
            if choice is None: choice = menu.selected_action

            if choice == monitoringAction:
                openMonitor(self.variable, has_parent=True)
            if choice == plottingAction:
                openPlotter(variable=self.variable, has_parent=True)
            elif choice == sliderAction:
                openSlider(self.variable, gui=self.gui, item=self)
            elif choice == scanParameterAction:
                recipe_name = self.gui.getRecipeName()
                param_name = self.gui.getParameterName()
                self.gui.setScanParameter(recipe_name, param_name, self.variable)
            elif choice == scanMeasureStepAction:
                recipe_name = self.gui.getRecipeName()
                self.gui.addStepToScanRecipe(recipe_name, 'measure', self.variable)
            elif choice == scanSetStepAction:
                recipe_name = self.gui.getRecipeName()
                value = self.variable.value if self.variable.type in [tuple] else None
                self.gui.addStepToScanRecipe(
                    recipe_name, 'set', self.variable, value=value)
            elif choice == saveAction: self.saveValue()

    def saveValue(self):
        """ Prompt user for filename to save data of the variable """
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.gui, f"Save {self.variable.address()} value", os.path.join(
                PATHS['last_folder'], f'{self.variable.address()}.txt'),
            filter=SUPPORTED_EXTENSION)

        path = os.path.dirname(filename)
        if path != '':
            PATHS['last_folder'] = path
            try:
                self.gui.setStatus(
                    f"Saving value of {self.variable.address()}...", 5000)
                self.variable.save(filename)
                self.gui.setStatus(
                    f"Value of {self.variable.address()} successfully read " \
                    f"and save at {filename}", 5000)
            except Exception as e:
                self.gui.setStatus(f"An error occured: {e}", 10000, False)


# Signals can be emitted only from QObjects
# These class provides convenient ways to use signals
class ReadSignal(QtCore.QObject):
    read = QtCore.Signal(object)
    def emit_read(self, value):
        self.read.emit(value)

class WriteSignal(QtCore.QObject):
    writed = QtCore.Signal(object)
    def emit_write(self, value):
        self.writed.emit(value)
