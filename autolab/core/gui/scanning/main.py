# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 22:08:29 2019

@author: qchat
"""
from PyQt5 import QtWidgets, uic
import os

from .config import ConfigManager
from .figure import FigureManager
from .parameter import ParameterManager
from .recipe import RecipeManager
from .scan import ScanManager
from .data import DataManager
from .scanrange import RangeManager

class Scanner(QtWidgets.QMainWindow):
        
    def __init__(self,mainGui):
        
        self.mainGui = mainGui
        
        # Configuration of the window
        QtWidgets.QMainWindow.__init__(self)
        ui_path = os.path.join(os.path.dirname(__file__),'interface.ui')
        uic.loadUi(ui_path,self)
        self.setWindowTitle(f"AUTOLAB Scanner")
        self.splitter.setSizes([500, 700])  # Set the width of the two main widgets
        # self.splitter_recipe.setSizes([80, 223, 80])  # set the height of the three recipe widgets

        # OPTIMIZE: temporary untill begin and end are functionnal
        self.splitter_recipe.setChildrenCollapsible(True)
        self.splitter_recipe.setSizes([0, 483, 0])  # set the height of the three recipe widgets

        # Loading of the different centers
        self.configManager = ConfigManager(self)
        self.figureManager = FigureManager(self)
        self.parameterManager = ParameterManager(self)
        self.recipeManager_begin = RecipeManager(self, self.tree_layout_begin)
        self.recipeManager = RecipeManager(self, self.tree_layout)
        self.recipeManager_end = RecipeManager(self, self.tree_layout_end)
        self.scanManager = ScanManager(self)
        self.dataManager = DataManager(self)
        self.rangeManager = RangeManager(self)



    def closeEvent(self,event):
        
        """ This function does some steps before the window is really killed """
        # Stop ongoing scan
        if self.scanManager.isStarted() :
            self.scanManager.stop()
            
        # Stop datamanager timer
        self.dataManager.timer.stop()
        
        # Delete reference of this window in the control center
        self.mainGui.clearScanner()
        
        
        
    def setLineEditBackground(self,obj,state):
        
        """ Function used to set the background color of a QLineEdit widget, 
        based on its editing state """
        
        if state == 'synced' :
            color='#D2FFD2' # vert
        if state == 'edited' :
            color='#FFE5AE' # orange
            
        obj.setStyleSheet("QLineEdit:enabled {background-color: %s; font-size: 9pt}"%color)
        
        
        
        
        
def cleanString(name):
    
    """ This function clears the given name from special characters """
    
    for character in '*."/\[]:;|, ' :
        name = name.replace(character,'')
    return name

































