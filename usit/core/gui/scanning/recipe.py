# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:15:26 2019

@author: qchat
"""

from PyQt5 import QtCore, QtWidgets, QtGui
from . import main 

class RecipeManager :
    
    def __init__(self,gui):
        
        self.gui = gui
        
        # Tree configuration
        self.tree = self.gui.recipe_treeWidget
        self.tree.setHeaderLabels(['Step name','Type','Element address','Value'])
        self.tree.header().resizeSection(3, 50)
        self.tree.itemDoubleClicked.connect(self.itemDoubleClicked)
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.tree.setAlternatingRowColors(True)        
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.rightClick)
                
        self.defaultItemBackground = None
        
        
        
    def refresh(self):
        
        """ Refresh the whole scan recipe displayed from the configuration center """
        
        self.tree.clear()
        
        recipe = self.gui.configManager.getRecipe()

        for i in range(len(recipe)):
            
            # Loading step informations
            step = recipe[i]
            item = QtWidgets.QTreeWidgetItem()
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsDropEnabled)
            
            # Column 1 : Step name
            item.setText(0,step['name'])
            
            # Column 2 : Step type
            if step['stepType'] == 'measure' : 
                item.setText(1,'Measure variable')
            elif step['stepType']  == 'set' : 
                item.setText(1,'Set variable')
            elif step['stepType']  == 'action' : 
                item.setText(1,'Do action')
                            
            # Column 3 : Element address
            item.setText(2,step['element'].getAddress())
            
            # Column 4 : Value if stepType is 'set'
            value = step['value']
            if value is not None : 
                if step['element'].type in [bool,str] :
                   item.setText(3,f'{value}')
                else :
                   item.setText(3,f'{value:g}')
            
            # Add item to the tree
            self.tree.addTopLevelItem(item)
            self.defaultItemBackground = item.background(0)
            
            
            
    def rightClick(self,position):
        
        """ This functions provide a menu where the user right clicked """
    
        item = self.tree.itemAt(position)
        
        if item is not None and self.gui.scanManager.isStarted() is False :
            
            name = item.text(0)
            stepType = self.gui.configManager.getRecipeStepType(name)
                        
            menuActions = {}
            
            menu = QtWidgets.QMenu()         
            menuActions['rename'] = menu.addAction("Rename")
            if stepType == 'set' : 
                menuActions['setvalue'] = menu.addAction("Set value")
            menuActions['remove'] = menu.addAction("Remove")
            
            choice = menu.exec_(self.tree.viewport().mapToGlobal(position))
            
            if 'rename' in menuActions.keys() and choice == menuActions['rename'] :
                self.renameStep(name)                
            elif 'remove' in menuActions.keys() and choice == menuActions['remove'] :
                self.gui.configManager.delRecipeStep(name)
            elif 'setvalue' in menuActions.keys() and choice == menuActions['setvalue'] :
                self.setStepValue(name)

        
        
    def renameStep(self,name):
        
        """ This function prompts the user for a new step name, and apply it to the selected step """
        
        newName,state = QtWidgets.QInputDialog.getText(self.gui, name, f"Set {name} new name",
                                                 QtWidgets.QLineEdit.Normal, name)
        
        newName = main.cleanString(newName)
        if newName != '' :
            self.gui.configManager.renameRecipeStep(name,newName)
            
   
            
    def setStepValue(self,name):
        
        """ This function prompts the user for a new step value, and apply it to the selected step """
        
        element = self.gui.configManager.getRecipeStepElement(name)
        value = self.gui.configManager.getRecipeStepValue(name)
        
        # Default value displayed in the QInputDialog
        if element.type in [str] :
            defaultValue = f'{value}'
        else :
            defaultValue = f'{value:g}'
        
        value,state = QtWidgets.QInputDialog.getText(self.gui, 
                                                     name, 
                                                     f"Set {name} value",
                                                     QtWidgets.QLineEdit.Normal, defaultValue)
        
        if value != '' :
            
            try :   
                
                # Type conversions
                if element.type in [int]:
                    value = int(value)
                elif element.type in [float] :
                    value = float(value)
                elif element.type in [str] :
                    value = str(value)
                elif element.type in [bool]:
                    value = int(value)
                    assert value in [0,1]
                    value = bool(value)
                
                # Apply modification
                self.gui.configManager.setRecipeStepValue(name,value)
                
            except :
                pass
            
            
            
    def itemDoubleClicked(self,item,column):
        
        """ This function executes an action depending where the user double clicked """
        
        name = item.text(0)
        stepType = self.gui.configManager.getRecipeStepType(name)
        
        if column == 0 : 
            self.renameStep(name)
        if column == 3 and stepType == 'set' :
            self.setStepValue(name)
   
    

    def setStepProcessingState(self,name,state):
        
        """ This function set the background color of a recipe step during the scan """
        
        item = self.tree.findItems(name, QtCore.Qt.MatchExactly, 0)[0]
        
        if state is None :
            item.setBackground(0,self.defaultItemBackground)
        if state == 'started' :
            item.setBackground(0, QtGui.QColor('#ff8c1a'))
        elif state == 'finished' :
            item.setBackground(0, QtGui.QColor('#70db70'))
                                               
        
        
    def resetStepsProcessingState(self):
        
        """ This function reset the background color of a recipe once the scan is finished """
        
        for name in self.gui.configManager.getNames(option='recipe'):
            self.setStepProcessingState(name,None)
            

