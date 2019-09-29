# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 23:29:33 2017

@author: Quentin Chateiller
quentin.chateiller@c2n.upsaclay.fr

"""

import usit
from PyQt5 import QtCore, QtWidgets, uic
import os 
from ..monitoring.main import Monitor
from ..scanning.main import Scanner


class ControlCenter(QtWidgets.QMainWindow):
        
    def __init__(self):
                
        # Set up the user interface from Designer.
        QtWidgets.QMainWindow.__init__(self)
        ui_path = os.path.join(os.path.dirname(__file__),'controlcenter.ui')
        uic.loadUi(ui_path,self)
                
        # Window configuration
        self.setWindowTitle("USIT Control Center")
        self.setFocus()
        
        # Tree widget configuration
        self.tree.setHeaderLabels(['Objects','Type','Actions','Values',''])
        self.tree.header().setDefaultAlignment(QtCore.Qt.AlignCenter);
        self.tree.header().resizeSection(0, 200)
        self.tree.header().resizeSection(4, 15)
        self.tree.header().setStretchLastSection(False)
        self.tree.itemClicked.connect(self.itemClicked)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.rightClick)
        self.tree.setAlternatingRowColors(True)
        
        # Thread manager
        self.threadManager = ThreadManager(self)
        
        # Scanner / Monitors
        self.scanner = None
        self.monitors = {}
        
        
        scanAction = self.menuBar.addAction('Open scanner')
        scanAction.triggered.connect(self.openScanner)
        scanAction.setToolTip('Open the scanner in another window')  

        
        reportAction = self.menuBar.addAction('Report bugs / suggestions')
        reportAction.triggered.connect(usit.report)
        reportAction.setToolTip('Open the issue webpage of this project on GitHub')  
        

        
    def initialize(self):
        
        """ This function will create the first items in the tree, but will 
        associate only the ones already loaded in usit """
        
        for devName in usit.devices.list() :
            item = TreeWidgetItemModule(self.tree,devName,self)
            if devName in usit.devices.get_loaded_devices() :
                self.associate(item)
        
        
        
    def setStatus(self,message):
    
        """ Modify the message displayed in the status bar """
        
        self.statusbar.showMessage(message)
        
        
        
    def clearStatus(self):
        
        """ Erase the message displayed in the status bar """
        
        self.setStatus('')
        
        
    
    def rightClick(self,position):
        
        """ Function called when a right click has been detected in the tree """
        
        item = self.tree.itemAt(position)
        if hasattr(item,'menu') :
            item.menu(position)
        
        

        
        

    def itemClicked(self,item):
                
        """ Function called when a normal click has been detected in the tree.
            Check the association if it is a main item """
        
        if item.parent() is None and item.loaded is False :
            self.associate(item)
            item.setExpanded(True)
        
        
        
    def associate(self,item):
        
        """ Function called to associate a main module to one item in the tree """
        
        # Try to get / instantiated the device
        check = False
        try : 
            module = getattr(usit.devices,item.name)
            check = True
        except Exception as e : 
            self.setStatus(f'An error occured when loading device {item.name} : str({e})')
            
        # If success, load the entire module (submodules, variables, actions)
        if check is True : 
            item.load(module)
                    
                
            
            

    def openScanner(self):
        
        """ This function open the scanner associated to this variable. """
        
        # If the scanner is not already running, create one
        if self.scanner is None : 
            self.scanner = Scanner(self)
            self.scanner.show()
            self.scanner.activateWindow()
            self.activateWindow() # Put main window back to the front

        
        # If the scanner is already running, just make as the front window
        else :  
            self.scanner.setWindowState(self.scanner.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.scanner.activateWindow()
             
            
            
    def setScanParameter(self,variable):
        
        if self.scanner is None : 
            self.openScanner()
            
        self.scanner.configManager.setParameter(variable)
        
        
    def addStepToScanRecipe(self,stepType,element):
        
        if self.scanner is None : 
            self.openScanner()
        
        self.scanner.configManager.addRecipeStep(stepType,element)
                
                    
    def clearScanner(self):
        
        """ This clear the gui instance reference when quitted """
        
        self.scanner = None
        
        
    def closeEvent(self,event):
        
        """ This function does some steps before the window is really killed """
        
        if self.scanner is not None :
            self.scanner.close()
            
        monitors = list(self.monitors.values())
        for monitor in monitors :
            monitor.close()


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
        subModuleNames = self.module.getModuleList()
        for subModuleName in subModuleNames : 
            subModule = getattr(self.module,subModuleName)
            item = TreeWidgetItemModule(self, subModuleName,self.gui)
            item.load(subModule)
            
        # Variables
        varNames = self.module.getVariableList()
        for varName in varNames : 
            variable = getattr(self.module,varName)
            TreeWidgetItemVariable(self, variable,self.gui)
            
        
        # Actions
        actNames = self.module.getActionList()
        for actName in actNames : 
            action = getattr(self.module,actName)
            TreeWidgetItemAction(self, action,self.gui)
            
        # Change loaded status
        self.loaded = True
 





       
class TreeWidgetItemAction(QtWidgets.QTreeWidgetItem):
    
    """ This class represents an action in an item of the tree """
    
    def __init__(self,itemParent,action,gui) :
        
        QtWidgets.QTreeWidgetItem.__init__(self,itemParent,[action.name,'Action'])
        self.setTextAlignment(1,QtCore.Qt.AlignHCenter)
        
        self.gui = gui
        self.action = action     
        
        # Main - Column 1 : actionread button
        self.execButton = QtWidgets.QPushButton()
        self.execButton.setText("Execute")
        self.execButton.pressed.connect(self.execute)
        self.gui.tree.setItemWidget(self, 2, self.execButton)
                
        
        
    def execute(self):
        
        """ Start a new thread to execute the associated action """
        
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
        
        QtWidgets.QTreeWidgetItem.__init__(self,itemParent,[variable.name,'Variable'])
        self.setTextAlignment(1,QtCore.Qt.AlignHCenter)
        
        self.gui = gui

        self.variable = variable
        
        self.monitor = None
        
        # Signal creation and associations in usit.devices instances         
        self.readSignal = ReadSignal()
        self.readSignal.signal.connect(self.writeGui)
        self.variable._readSignal = self.readSignal
        self.writeSignal = WriteSignal()
        self.writeSignal.signal.connect(self.valueEdited)
        self.variable._writeSignal = self.writeSignal
        
        # Main - Column 1 : Creation of a READ button
        if self.variable.readable and self.variable.type in [int,float,bool,str] :
            self.readButton = QtWidgets.QPushButton()
            self.readButton.setText("Read")
            self.readButton.pressed.connect(self.read)
            self.gui.tree.setItemWidget(self, 2, self.readButton)
        
        # Main - column 2 : Creation of a VALUE widget, depending on the type, and if the variable is readable
        
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
            
        # Main - column 3 : indicator (status of the actual value : known or not known)
        if self.variable.type in [int,float,str,bool] :
            self.indicator = QtWidgets.QLabel()
            self.gui.tree.setItemWidget(self, 4, self.indicator)
            
                   
            
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
            value = self.variable.type(value)
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
        
        self.gui.threadManager.start(self,'write',value=self.readGui())
        
        
        
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
        scanParameterAction.setEnabled(self.variable.parameterAllowed)
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
                                        os.path.join(usit.core.USER_LAST_CUSTOM_FOLDER_PATH,f'{self.variable.name}.txt'), 
                                        "Text file (*.txt)")[0]
        if path != '' :
            usit.core.USER_LAST_CUSTOM_FOLDER_PATH = path
            self.variable.save(path)


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






class ThreadManager :
    
    """ This class is dedicated to manage the different threads, 
    from their creation, to their deletion them after they have been used """
    
    
    def __init__(self,gui):
        self.gui = gui
        self.threads = {}
        
        
        
    def start(self,item,intType,value=None):
        
        """ This function is called when a new thread is requested, 
        for a particular intType interaction type """
        
        # GUI disabling
        self.gui.tree.setEnabled(False)
        
        # Status writing
        if intType == 'read' : status = f'Reading {item.variable.name}...'
        elif intType == 'write' : status = f'Writing {item.variable.name}...'
        elif intType == 'execute' : status = f'Executing {item.action.name}...'
        self.gui.setStatus(status)

        # Thread configuration
        thread = InteractionThread(item,intType,value)
        tid = id(thread)
        self.threads[tid] = thread
        thread.endSignal.connect(lambda error, x=tid : self.threadFinished(x,error))
        thread.finished.connect(lambda x=tid : self.delete(x))
        
        # Starting thread
        thread.start()
        
        
    def threadFinished(self,tid,error):
        
        """ This function is called when a thread has finished its job, with an error or not 
        It uptates the status bar of the GUI in consequence and enabled back the GUI"""
        
        if error is None : self.gui.clearStatus()
        else : self.gui.setStatus(str(error))
        
        self.gui.tree.setEnabled(True)
        
        
        
    def delete(self,tid):
        
        """ This function is called when a thread is about to be deleted. 
        This removes it from the dictionnary self.threads, for a complete deletion """
        
        self.threads.pop(tid)
        
        
        
        
        
        
class InteractionThread(QtCore.QThread):
    
    """ This class is dedicated to operation interaction with the devices, in a new thread """
    
    endSignal = QtCore.pyqtSignal(object)
    
    
    def __init__(self,item,intType,value):
        QtCore.QThread.__init__(self)
        self.item = item
        self.intType = intType
        self.value = value
        
        
        
    def run(self):
        
        """ Depending on the interaction type requested, this function reads or writes a variable, 
        or execute an action. """
        
        error = None
        
        try :
            if self.intType == 'read' : self.item.variable()
            elif self.intType == 'write' : 
                self.item.variable(self.value)
                if self.item.variable.readable : self.item.variable()
            elif self.intType == 'execute' : self.item.action()
            
        except Exception as e:
            error = e
        self.endSignal.emit(error)
       
        