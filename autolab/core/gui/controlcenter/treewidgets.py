# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:29:07 2019

@author: qchat
"""


from PyQt5 import QtCore, QtWidgets
from ..monitoring.main import Monitor
import os
from autolab import paths


class TreeWidgetItemModule(QtWidgets.QTreeWidgetItem):
    
    """ This class represents a module in an item of the tree """
    
    def __init__(self,itemParent,name,gui):
        
        QtWidgets.QTreeWidgetItem.__init__(self,itemParent,[name,'Module'])
        self.setTextAlignment(1,QtCore.Qt.AlignHCenter)
        self.name = name
        self.module = None
        self.loaded = False
        self.gui = gui

        
        
        
    def load(self,module):
        
        """ This function loads the entire module (submodules, variables, actions) """
        
        self.module = module
        
        # Submodules
        subModuleNames = self.module.list_modules()
        for subModuleName in subModuleNames : 
            subModule = getattr(self.module,subModuleName)
            item = TreeWidgetItemModule(self, subModuleName,self.gui)
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
            if self.action.type in [int,float,str] : 
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
            self.execButton.pressed.connect(self.execute)
            self.gui.tree.setItemWidget(self, 2, self.execButton)
        
        # Main - Column 3 : QlineEdit if the action has a parameter
        if self.has_value :
            self.valueWidget = QtWidgets.QLineEdit()
            self.valueWidget.setAlignment(QtCore.Qt.AlignCenter)
            self.gui.tree.setItemWidget(self, 3, self.valueWidget)
               
        # Tooltip
        if self.action._help is None : tooltip = 'No help available for this action'
        else : tooltip = self.action._help
        self.setToolTip(0,tooltip)
        
        
    def readGui(self):
        
        """ This function returns the value in good format of the value in the GUI """
        
        value = self.valueWidget.text()
        if value == '' :
            self.gui.statusbar.showMessage(f"Action {self.action.name} requires a value for its parameter",10000)
        else : 
            try : 
                value = self.action.type(value)
                return value
            except :
                self.gui.statusbar.showMessage(f"Action {self.action.name}: Impossible to convert {value} in type {self.action.type.__name__}",10000)
            
        
        
    def execute(self):
        
        """ Start a new thread to execute the associated action """
        
        if self.has_value :
            value = self.readGui()
            if value is not None : self.gui.threadManager.start(self,'execute',value=value)
        else : 
            self.gui.threadManager.start(self,'execute')
                


    def menu(self,position):
        
        """ This function provides the menu when the user right click on an item """
        
        menu = QtWidgets.QMenu()            
        scanRecipe = menu.addAction("Do in scan recipe")
            
        choice = menu.exec_(self.gui.tree.viewport().mapToGlobal(position))
            
        if choice == scanRecipe : 
            self.gui.addStepToScanRecipe('action',self.action)


        
        
        
        
class TreeWidgetItemVariable(QtWidgets.QTreeWidgetItem):   

    """ This class represents a variable in an item of the tree """     
    
    def __init__(self,itemParent,variable,gui) :
        
        displayName = f'{variable.name}'
        if variable.unit is not None :
            displayName += f' ({variable.unit})'

        QtWidgets.QTreeWidgetItem.__init__(self,itemParent,[displayName,'Variable'])
        self.setTextAlignment(1,QtCore.Qt.AlignHCenter)
        
        self.gui = gui

        self.variable = variable
        
        self.monitor = None
        
        # Signal creation and associations in autolab devices instances         
        self.readSignal = ReadSignal()
        self.readSignal.signal.connect(self.writeGui)
        self.variable._read_signal = self.readSignal
        self.writeSignal = WriteSignal()
        self.writeSignal.signal.connect(self.valueEdited)
        self.variable._write_signal = self.writeSignal
        
        # Main - Column 2 : Creation of a READ button
        if self.variable.readable and self.variable.type in [int,float,bool,str] :
            self.readButton = QtWidgets.QPushButton()
            self.readButton.setText("Read")
            self.readButton.pressed.connect(self.read)
            self.gui.tree.setItemWidget(self, 2, self.readButton)
        
        # Main - column 3 : Creation of a VALUE widget, depending on the type, and if the variable is readable
        
        ## QLineEdit or QLabel 
        if self.variable.type in [int,float,str] : 
            
            if self.variable.writable :
                self.valueWidget = QtWidgets.QLineEdit()
                self.valueWidget.setAlignment(QtCore.Qt.AlignCenter)
                self.valueWidget.returnPressed.connect(self.write)
                self.valueWidget.textEdited.connect(self.valueEdited)
            else :
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
        if self.variable.type in [int,float,str,bool] :
            self.indicator = QtWidgets.QLabel()
            self.gui.tree.setItemWidget(self, 4, self.indicator)
            
        # Tooltip
        if self.variable._help is None : tooltip = 'No help available for this variable'
        else : tooltip = self.variable._help
        self.setToolTip(0,tooltip)
                   
            
    def writeGui(self,value):
        
        """ This function displays a new value in the GUI """
        
        # Update value
        if self.variable.numerical :
            self.valueWidget.setText(f'{value:g}')
        elif self.variable.type in [str] :
            self.valueWidget.setText(value)
        elif self.variable.type in [bool] :
            self.valueWidget.setChecked(value)
            
        # Change indicator light to green
        if self.variable.type in [int,float,bool,str] :
            self.setValueKnownState(True)
            
            
            
    def readGui(self):
        
        """ This function returns the value in good format of the value in the GUI """
        
        if self.variable.type in [int,float,str] :
            value = self.valueWidget.text()
            if value == '' :
                self.gui.statusbar.showMessage(f"Variable {self.variable.name} requires a value to be set",10000)
            else :
                try : 
                    value = self.variable.type(value)
                    return value
                except : 
                    self.gui.statusbar.showMessage(f"Variable {self.variable.name}: Impossible to convert {value} in type {self.variable.type.__name__}",10000)
        
        elif self.variable.type in [bool] :
            value = self.valueWidget.isChecked()
            return value


    def setValueKnownState(self,state):
        
        """ Turn the color of the indicator depending of the known state of the value """
        
        if state is True : self.indicator.setStyleSheet(f"background-color:#70db70") #green
        else : self.indicator.setStyleSheet(f"background-color:#ff8c1a") #orange
            
            
    
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
                
        menu = QtWidgets.QMenu()
        
        monitoringAction = menu.addAction("Start monitoring")
        menu.addSeparator()
        scanParameterAction = menu.addAction("Set as scan parameter")
        scanMeasureStepAction = menu.addAction("Measure in scan recipe")
        scanSetStepAction = menu.addAction("Set value in scan recipe")
        menu.addSeparator()
        saveAction = menu.addAction("Read and save as...")
        
        monitoringAction.setEnabled( self.variable.readable and self.variable.numerical )
        scanParameterAction.setEnabled(self.variable.parameter_allowed)
        scanMeasureStepAction.setEnabled(self.variable.readable)
        saveAction.setEnabled(self.variable.readable)
        scanSetStepAction.setEnabled(self.variable.writable)
        
                        
        choice = menu.exec_(self.gui.tree.viewport().mapToGlobal(position))

        if choice == monitoringAction : 
            self.openMonitor()
        elif choice == scanParameterAction :
            self.gui.setScanParameter(self.variable) 
        elif choice == scanMeasureStepAction :
            self.gui.addStepToScanRecipe('measure',self.variable) 
        elif choice == scanSetStepAction :
            self.gui.addStepToScanRecipe('set',self.variable) 
        elif choice == saveAction :
            self.saveValue()
            
    def saveValue(self):
        
        path = QtWidgets.QFileDialog.getSaveFileName(self.gui, f"Save {self.variable.name} value", 
                                        os.path.join(paths.USER_LAST_CUSTOM_FOLDER,f'{self.variable.address()}.txt'), 
                                        "Text file (*.txt)")[0]
        if path != '' :
            paths.USER_LAST_CUSTOM_FOLDER = path
            try : 
                self.gui.statusbar.showMessage(f"Saving value of {self.variable.name}...",5000)
                self.variable.save(path)
                self.gui.statusbar.showMessage(f"Value of {self.variable.name} successfully read and save at {path}",5000)
            except Exception as e :
                self.gui.statusbar.showMessage(f"An error occured: {str(e)}",10000)
            


    def openMonitor(self):
        
        """ This function open the monitor associated to this variable. """
        
        # If the monitor is not already running, create one
        if id(self) not in self.gui.monitors.keys(): 
            self.gui.monitors[id(self)] = Monitor(self)
            self.gui.monitors[id(self)].show()
        
        # If the monitor is already running, just make as the front window
        else :  
            self.gui.monitors[id(self)].setWindowState(self.monitor.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.gui.monitors[id(self)].activateWindow()
        

        
        
    def clearMonitor(self):
        
        """ This clear the gui instance reference when quitted """
        if id(self) in self.gui.monitors.keys(): 
            self.gui.monitors.pop(id(self))
            
            
            
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
