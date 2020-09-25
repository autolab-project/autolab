# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 23:29:33 2017

@author: Quentin Chateiller
quentin.chateiller@c2n.upsaclay.fr

"""

import autolab
from PyQt5 import QtCore, QtWidgets, uic, QtGui
import os 
from ..scanning.main import Scanner

from .thread import ThreadManager
from .treewidgets import TreeWidgetItemModule


class ControlCenter(QtWidgets.QMainWindow):
        
    def __init__(self):
                
        # Set up the user interface from Designer.
        QtWidgets.QMainWindow.__init__(self)
        ui_path = os.path.join(os.path.dirname(__file__),'interface.ui')
        uic.loadUi(ui_path,self)
                
        # Window configuration
        self.setWindowTitle("AUTOLAB - Control Panel")
        self.setFocus()
        self.activateWindow()
        
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
        reportAction.triggered.connect(autolab.report)
        reportAction.setToolTip('Open the issue webpage of this project on GitHub')  
        
        helpAction = self.menuBar.addAction('Help')
        helpAction.triggered.connect(autolab.doc)
        helpAction.setToolTip('Open the documentation on Read The Docs website')  
        
    def initialize(self):
        
        """ This function will create the first items in the tree, but will 
        associate only the ones already loaded in autolab """
        
        for devName in autolab.list_local_configs() :
            item = TreeWidgetItemModule(self.tree,devName,self)
            for i in range(5) :
                item.setBackground(i, QtGui.QColor('#9EB7F5')) #vert
            if devName in autolab.list_devices() :
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
            self.setStatus(f'Loading device {item.name}...')
            module = autolab.get_device(item.name)
            check = True
            self.clearStatus()
        except Exception as e : 
            self.setStatus(f'An error occured when loading device {item.name} : {str(e)}')
            
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










