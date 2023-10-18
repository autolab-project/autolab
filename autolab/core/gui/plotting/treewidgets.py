# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:29:07 2019

@author: qchat
"""


import os
from PyQt5 import QtCore, QtWidgets
from ...devices import DEVICES
from ... import paths, config
import pandas as pd
import numpy as np
import sip


class TreeWidgetItemModule(QtWidgets.QTreeWidgetItem):

    """ This class represents a module in an item of the tree """

    def __init__(self,itemParent,name,nickname,gui):

        QtWidgets.QTreeWidgetItem.__init__(self,itemParent,[nickname,'Module'])
        self.setTextAlignment(1,QtCore.Qt.AlignHCenter)
        self.name = name
        self.nickname = nickname
        self.module = None
        self.loaded = False
        self.gui = gui

        self.is_not_submodule = type(gui.tree) is type(itemParent)

    def load(self,module):

        """ This function loads the entire module (submodules, variables, actions) """

        self.module = module

        # Submodules
        subModuleNames = self.module.list_modules()
        for subModuleName in subModuleNames :
            subModule = getattr(self.module,subModuleName)
            item = TreeWidgetItemModule(self, subModuleName,subModuleName,self.gui)
            item.load(subModule)

        # Variables
        varNames = self.module.list_variables()
        for varName in varNames :
            variable = getattr(self.module,varName)
            TreeWidgetItemVariable(self, variable,self.gui)


        # Actions
        actNames = self.module.list_actions()
        for actName in actNames :
            action = getattr(self.module,actName)
            TreeWidgetItemAction(self, action,self.gui)

        # Change loaded status
        self.loaded = True


    def menu(self,position):

        """ This function provides the menu when the user right click on an item """

        if self.is_not_submodule and self.loaded:
            menu = QtWidgets.QMenu()
            disconnectDevice = menu.addAction(f"Disconnect {self.nickname}")

            choice = menu.exec_(self.gui.tree.viewport().mapToGlobal(position))

            if choice == disconnectDevice :
                device = self.gui.active_plugin_dict[self.nickname]
                try: device.instance.close()  # not device close because device.close will remove device from DEVICES list
                except: pass
                self.gui.active_plugin_dict.pop(self.nickname)

                for i in range(self.childCount()):
                    self.removeChild(self.child(0))
                self.loaded = False





class TreeWidgetItemAction(QtWidgets.QTreeWidgetItem):

    """ This class represents an action in an item of the tree """

    def __init__(self,itemParent,action,gui) :

        displayName = f'{action.name}'
        if action.unit is not None :
            displayName += f' ({action.unit})'

        QtWidgets.QTreeWidgetItem.__init__(self,itemParent,[displayName,'Action'])
        self.setTextAlignment(1,QtCore.Qt.AlignHCenter)

        self.gui = gui
        self.action = action

        if self.action.has_parameter :
            if self.action.type in [int,float,str,pd.DataFrame,np.ndarray] :
                self.executable = True
                self.has_value = True
            else :
                self.executable = False
                self.has_value = False
        else :
            self.executable = True
            self.has_value = False

        # Main - Column 2 : actionread button
        if self.executable is True :
            self.execButton = QtWidgets.QPushButton()
            self.execButton.setText("Execute")
            self.execButton.clicked.connect(self.execute)
            self.gui.tree.setItemWidget(self, 2, self.execButton)

        # Main - Column 3 : QlineEdit if the action has a parameter
        if self.has_value :
            self.valueWidget = QtWidgets.QLineEdit()
            self.valueWidget.setAlignment(QtCore.Qt.AlignCenter)
            self.gui.tree.setItemWidget(self, 3, self.valueWidget)
            self.valueWidget.returnPressed.connect(self.execute)

        # Tooltip
        if self.action._help is None : tooltip = 'No help available for this action'
        else : tooltip = self.action._help
        self.setToolTip(0,tooltip)


    def readGui(self):

        """ This function returns the value in good format of the value in the GUI """

        value = self.valueWidget.text()
        if value == '' :
            if self.action.unit == "filename":
                from PyQt5 import QtWidgets
                value = QtWidgets.QFileDialog.getOpenFileName(self.gui, caption="Filename", filter="Text Files (*.txt);; Supported text Files (*.txt;*.csv;*.dat);; All Files (*)")[0]
                if value != '':
                    return value
                else:
                    self.gui.statusBar.showMessage(f"Action {self.action.name} cancel filename selection",10000)
            else:
                self.gui.statusBar.showMessage(f"Action {self.action.name} requires a value for its parameter",10000)
        else :
            try :
                value = self.checkVariable(value)
                value = self.action.type(value)
                return value
            except :
                self.gui.statusBar.showMessage(f"Action {self.action.name}: Impossible to convert {value} in type {self.action.type.__name__}",10000)


    def checkVariable(self, value):

        """ Try to execute the given command line (meant to contain device variables) and return the result """

        if str(value).startswith("$eval:"):
            value = str(value)[len("$eval:"):]
            try:
                allowed_dict ={"np":np, "pd":pd}
                allowed_dict.update(DEVICES)
                value = eval(str(value), {}, allowed_dict)
            except:
                pass
        return value


    def execute(self):

        """ Start a new thread to execute the associated action """

        if self.has_value :
            value = self.readGui()
            if value is not None : self.gui.threadManager.start(self,'execute',value=value)
        else :
            self.gui.threadManager.start(self,'execute')





class TreeWidgetItemVariable(QtWidgets.QTreeWidgetItem):

    """ This class represents a variable in an item of the tree """

    def __init__(self,itemParent,variable,gui) :


        self.displayName = f'{variable.name}'
        if variable.unit is not None :
            self.displayName += f' ({variable.unit})'

        QtWidgets.QTreeWidgetItem.__init__(self,itemParent,[self.displayName,'Variable'])
        self.setTextAlignment(1,QtCore.Qt.AlignHCenter)

        self.gui = gui

        self.variable = variable

        # Import Autolab config
        control_center_config = config.get_control_center_config()
        self.precision = int(control_center_config['precision'])

        # Signal creation and associations in autolab devices instances
        self.readSignal = ReadSignal()
        self.readSignal.signal.connect(self.writeGui)
        self.variable._read_signal = self.readSignal
        self.writeSignal = WriteSignal()
        self.writeSignal.signal.connect(self.valueEdited)
        self.variable._write_signal = self.writeSignal

        # Main - Column 2 : Creation of a READ button if the variable is readable
        if self.variable.readable and self.variable.type in [int,float,bool,str] :
            self.readButton = QtWidgets.QPushButton()
            self.readButton.setText("Read")
            self.readButton.clicked.connect(self.read)
            self.gui.tree.setItemWidget(self, 2, self.readButton)

        # Main - column 3 : Creation of a VALUE widget, depending on the type

        ## QLineEdit or QLabel
        if self.variable.type in [int,float,str,pd.DataFrame,np.ndarray]:

            if self.variable.writable :
                self.valueWidget = QtWidgets.QLineEdit()
                self.valueWidget.setAlignment(QtCore.Qt.AlignCenter)
                self.valueWidget.returnPressed.connect(self.write)
                self.valueWidget.textEdited.connect(self.valueEdited)
                # self.valueWidget.setPlaceholderText(self.variable._help)  # OPTIMIZE: Could be nice but take too much place. Maybe add it as option
            elif self.variable.readable and self.variable.type in [int,float,str] :
                self.valueWidget = QtWidgets.QLineEdit()
                self.valueWidget.setReadOnly(True)
                self.valueWidget.setStyleSheet("QLineEdit {border : 1px solid #a4a4a4; background-color : #f4f4f4}")
                self.valueWidget.setAlignment(QtCore.Qt.AlignCenter)
            else:
                self.valueWidget = QtWidgets.QLabel()
                self.valueWidget.setAlignment(QtCore.Qt.AlignCenter)

            self.gui.tree.setItemWidget(self, 3, self.valueWidget)

        ## QCheckbox for boolean variables
        elif self.variable.type in [bool] :
            self.valueWidget = QtWidgets.QCheckBox()
            self.valueWidget.stateChanged.connect(self.valueEdited)
            self.valueWidget.stateChanged.connect(self.write)
            hbox = QtWidgets.QHBoxLayout()
            hbox.addWidget(self.valueWidget)
            hbox.setAlignment(QtCore.Qt.AlignCenter)
            hbox.setSpacing(0)
            hbox.setContentsMargins(0,0,0,0)
            widget = QtWidgets.QWidget()
            widget.setLayout(hbox)
            if self.variable.writable is False : # Disable interaction is not writable
                self.valueWidget.setEnabled(False)
            self.gui.tree.setItemWidget(self, 3, widget)

        # Main - column 4 : indicator (status of the actual value : known or not known)
        if self.variable.type in [int,float,str,bool,np.ndarray,pd.DataFrame] :
            self.indicator = QtWidgets.QLabel()
            self.gui.tree.setItemWidget(self, 4, self.indicator)

        # Tooltip
        if self.variable._help is None : tooltip = 'No help available for this variable'
        else : tooltip = self.variable._help
        if hasattr(self.variable, "type"):
            variable_type = str(self.variable.type).split("'")[1]
            tooltip += f" ({variable_type})"
        self.setToolTip(0,tooltip)


    def writeGui(self,value):

        """ This function displays a new value in the GUI """
        if not sip.isdeleted(self.valueWidget):  # avoid crash if device closed and try to write gui (if close device before reading finihsed)
            # Update value
            if self.variable.numerical :
                self.valueWidget.setText(f'{value:.{self.precision}g}') # default is .6g
            elif self.variable.type in [str] :
                self.valueWidget.setText(value)
            elif self.variable.type in [bool] :
                self.valueWidget.setChecked(value)

            # Change indicator light to green
            if self.variable.type in [int,float,bool,str,np.ndarray,pd.DataFrame] :
                self.setValueKnownState(True)



    def readGui(self):

        """ This function returns the value in good format of the value in the GUI """

        if self.variable.type in [int,float,str,np.ndarray,pd.DataFrame] :
            value = self.valueWidget.text()
            if value == '' :
                self.gui.statusBar.showMessage(f"Variable {self.variable.name} requires a value to be set",10000)
            else :
                try :
                    value = self.checkVariable(value)
                    value = self.variable.type(value)
                    return value
                except :
                    self.gui.statusBar.showMessage(f"Variable {self.variable.name}: Impossible to convert {value} in type {self.variable.type.__name__}",10000)

        elif self.variable.type in [bool] :
            value = self.valueWidget.isChecked()
            return value


    def checkVariable(self, value):

        """ Check if value is a device variable address and if is it, return its value """

        if str(value).startswith("$eval:"):
            value = str(value)[len("$eval:"):]
            try:
                allowed_dict ={"np":np, "pd":pd}
                allowed_dict.update(DEVICES)
                value = eval(str(value), {}, allowed_dict)
            except:
                pass
        return value


    def setValueKnownState(self,state):

        """ Turn the color of the indicator depending of the known state of the value """

        if state is True : self.indicator.setStyleSheet("background-color:#70db70") #green
        else : self.indicator.setStyleSheet("background-color:#ff8c1a") #orange



    def read(self):

        """ Start a new thread to READ the associated variable """

        self.setValueKnownState(False)
        self.gui.threadManager.start(self,'read')



    def write(self):

        """ Start a new thread to WRITE the associated variable """
        value = self.readGui()
        if value is not None :
            self.gui.threadManager.start(self,'write',value=value)




    def valueEdited(self):

        """ Function call when the value displayed in not sure anymore.
            The value has been modified either in the GUI (but not sent) or by command line """

        self.setValueKnownState(False)



    def menu(self,position):

        """ This function provides the menu when the user right click on an item """

        if not self.isDisabled():
            menu = QtWidgets.QMenu()


            saveAction = menu.addAction("Read and save as...")


            saveAction.setEnabled(self.variable.readable)

            choice = menu.exec_(self.gui.tree.viewport().mapToGlobal(position))

            if choice == saveAction :
                self.saveValue()


    def saveValue(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self.gui, f"Save {self.variable.name} value",
                                        os.path.join(paths.USER_LAST_CUSTOM_FOLDER,f'{self.variable.address()}.txt'),
                                        filter="Text Files (*.txt);; Supported text Files (*.txt;*.csv;*.dat);; All Files (*)")[0]

        path = os.path.dirname(filename)
        if path != '' :
            paths.USER_LAST_CUSTOM_FOLDER = path
            try :
                self.gui.statusBar.showMessage(f"Saving value of {self.variable.name}...",5000)
                self.variable.save(filename)
                self.gui.statusBar.showMessage(f"Value of {self.variable.name} successfully read and save at {filename}",5000)
            except Exception as e :
                self.gui.statusBar.showMessage(f"An error occured: {str(e)}",10000)


# Signals can be emitted only from QObjects
# These class provides convenient ways to use signals
class ReadSignal(QtCore.QObject):
    signal = QtCore.pyqtSignal(object)
    def emit(self,value):
        self.signal.emit(value)

class WriteSignal(QtCore.QObject):
    signal = QtCore.pyqtSignal()
    def emit(self):
        self.signal.emit()
