# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:15:26 2019

@author: qchat
"""

from PyQt5 import QtCore, QtWidgets, QtGui
from . import main 

class MyQTreeWidget(QtWidgets.QTreeWidget):
    
    reorderSignal = QtCore.pyqtSignal(object) 
    
    def __init__(self,parent):
        
        QtWidgets.QTreeWidget.__init__(self,parent)
    
    def dropEvent(self, event):
        QtWidgets.QTreeWidget.dropEvent(self, event)
        self.reorderSignal.emit(event)


class RecipeManager :
    
    def __init__(self,gui):
        
        self.gui = gui
        
        # Tree configuration
        #self.tree = self.gui.recipe_treeWidget
        self.tree = MyQTreeWidget(self.gui)
        self.gui.tree_layout.addWidget(self.tree)
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gui.tree_layout.addItem(spacer)
        self.tree.setHeaderLabels(['Step name','Type','Element address','Value'])
        self.tree.header().resizeSection(3, 50)
        self.tree.itemDoubleClicked.connect(self.itemDoubleClicked)
        self.tree.reorderSignal.connect(self.orderChanged)
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.tree.setDropIndicatorShown(True)
        self.tree.setAlternatingRowColors(True)        
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.setMinimumSize(450,500)
        self.tree.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.tree.customContextMenuRequested.connect(self.rightClick)
                
        self.defaultItemBackground = None
        
        
    def orderChanged(self,event):
        newOrder = [self.tree.topLevelItem(i).text(0) for i in range(self.tree.topLevelItemCount())]
        self.gui.configManager.setRecipeOrder(newOrder)
        

    def refresh(self):
        
        """ Refresh the whole scan recipe displayed from the configuration center """
        
        self.tree.clear()
        
        recipe = self.gui.configManager.getRecipe()

        for i in range(len(recipe)):
            
            # Loading step informations
            step = recipe[i]
            item = QtWidgets.QTreeWidgetItem()
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsDropEnabled ) 
            
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
            item.setText(2,step['element'].address())
            
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
            element = self.gui.configManager.getRecipeStepElement(name)
                        
            menuActions = {}
            
            menu = QtWidgets.QMenu()         
            menuActions['rename'] = menu.addAction("Rename")
            if stepType == 'set' or (stepType == 'action' and element.type in [int,float,str]) :
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
        element = self.gui.configManager.getRecipeStepElement(name)
        
        if column == 0 : 
            self.renameStep(name)
        if column == 3 :
            if stepType == 'set' or (stepType == 'action' and element.type in [int,float,str]) :
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
            

#
#class Step:
#    
#    def __init__(self,name):
#        self.name = None
#        
#    def set_name(self,name):
#        self.name = name
#        
#    def message(self,mess):
#        return f'Step {self.name} (self.step_type): {mess}'
#        
#
#class ExecuteActionStep(Step):
#    step_type = 'execute_action'
#    
#    def __init__(self,name,element,value=None):
#        Step.__init__(self,name)
#        
#        # Element
#        assert element._element_type == 'action', self.message('The element has to be an Action')
#        self.action = element
#        
#        # Value
#        if self.action.has_parameter : 
#            assert value is not None, self.message('Parameter value required')
#            self.set_value(value) 
#        else :
#            assert value is None, self.message('This action has no parameter')
#            
#    def set_value(self,value):
#        assert self.action.has_parameter, self.message('This action has no parameter')
#        try : 
#            self.value = self.action.type(value)
#        except : 
#            raise ValueError(self.message(f'Impossible to convert {value} in type {self.element.type.__name__}'))
#        
#    def get_value(self):
#        return self.value
#    
#    def run(self):
#        if self.element.has_parameter : 
#            assert self.value is not None 
#            self.action(self.value)
#        else : 
#            self.action()
#        
#
#    
#class ScanVariableStep:
#    step_type = 'scan_variable'
#    
#    def __init__(self,name,element):
#        
#        Step.__init__(self,name)
#        
#        # Element
#        assert element._element_type == 'variable', self.message('The element has to be a Variable')
#        assert element.writable is True, self.message('The Variable has to be writable')
#        self.variable = element
#        
#        
#class ScanVariableEndStep:
#    step_type = 'scan_variable_end'
#    
#    def __init__(self,name):
#        
#        
#    def run(self):
#        
#        
#        
#class MeasureVariableStep:
#    step_type = 'measure_variable'
#    
#    def __init__(self,name,element):
#        Step.__init__(self,name)
#        
#        # Element
#        assert element._element_type == 'variable', self.message('The element has to be a Variable')
#        assert element.readable is True, self.message('The Variable has to be readable')
#        self.variable = element
#        
#        
#    def run(self):
#        return self.variable()
#        
#        
#        
#    
#class SetVariableStep:
#    step_type = 'set_variable'
#    
#    def __init__(self,name,element,value):
#        Step.__init__(self,name)
#        
#        # Element
#        assert element._element_type == 'variable', self.message('The element has to be a Variable')
#        assert element.writable is True, self.message('The Variable has to be writable')
#        self.variable = element
#        
#        # Value
#        self.set_value(value)
#        
#    
#    def set_value(self,value):
#        try : 
#            self.value = self.variable.type(value)
#        except : 
#            raise ValueError(self.message(f'Impossible to convert {value} in type {self.element.type.__name__}'))
#        
#    def get_value(self):
#        return self.value
#        
#    def run(self):
#        self.variable(self.value)
#        
#    
#    def prompt_value(self):
#            
#        # Default value displayed in the QInputDialog
#        if self.variable.type == str :
#            defaultValue = f'{self.value}'
#        else :
#            defaultValue = f'{self.value:g}'
#        
#        value,state = QtWidgets.QInputDialog.getText(self.gui, 
#                                                     name, 
#                                                     f"Set {name} value",
#                                                     QtWidgets.QLineEdit.Normal, defaultValue)
#        
#        if value != '' :
#            
#            try :   
#                
#                # Type conversions
#                if element.type in [int]:
#                    value = int(value)
#                elif element.type in [float] :
#                    value = float(value)
#                elif element.type in [str] :
#                    value = str(value)
#                elif element.type in [bool]:
#                    value = int(value)
#                    assert value in [0,1]
#                    value = bool(value)
#                
#                # Apply modification
#                self.gui.configManager.setRecipeStepValue(name,value)
#                
#            except :
#                pass
#        
        
        
    