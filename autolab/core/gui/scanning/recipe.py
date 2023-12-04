# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:15:26 2019

@author: qchat
"""

import numpy as np
import pandas as pd

from qtpy import QtCore, QtWidgets, QtGui

from . import main
from ... import config


class MyQTreeWidget(QtWidgets.QTreeWidget):
    customMimeType = "autolab/MyQTreeWidget-selectedItems"

    reorderSignal = QtCore.Signal(object)

    def __init__(self,parent, recipe_name):
        self.recipe_name = recipe_name
        self.scanner = parent
        QtWidgets.QTreeWidget.__init__(self,parent)
        self.setAcceptDrops(True)

    def mimeTypes(self):
        """Based on https://gist.github.com/eyllanesc/42bcda52a14244445153153a33e7c0dd"""
        mimetypes = QtWidgets.QTreeWidget.mimeTypes(self)
        mimetypes.append(MyQTreeWidget.customMimeType)
        return mimetypes

    def startDrag(self, supportedActions):
        drag = QtGui.QDrag(self)
        mimedata = self.model().mimeData(self.selectedIndexes())

        encoded = QtCore.QByteArray()
        stream = QtCore.QDataStream(encoded, QtCore.QIODevice.WriteOnly)
        self.encodeData(self.selectedItems(), stream)
        mimedata.setData(MyQTreeWidget.customMimeType, encoded)

        drag.setMimeData(mimedata)
        drag.exec_(supportedActions)

    def encodeData(self, items, stream):
        stream.writeInt32(len(items))
        for item in items:
            p = item
            rows = []
            while p is not None:
                rows.append(self.indexFromItem(p).row())
                p = p.parent()
            stream.writeInt32(len(rows))
            for row in reversed(rows):
                stream.writeInt32(row)
        return stream

    def decodeData(self, encoded, tree):
        items = []
        rows = []
        stream = QtCore.QDataStream(encoded, QtCore.QIODevice.ReadOnly)
        while not stream.atEnd():
            nItems = stream.readInt32()
            for i in range(nItems):
                path = stream.readInt32()
                row = []
                for j in range(path):
                    row.append(stream.readInt32())
                rows.append(row)

        for row in rows:
            it = tree.topLevelItem(row[0])
            for ix in row[1:]:
                it = it.child(ix)
            items.append(it)
        return items

    def dropEvent(self, event):

        """ This function is used to reorder the recipe or to add a step from a controlcenter drop """

        self.setGraphicsEffect(None)

        if event.source() is self:  # if event comes frop recipe -> reorder
            self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)  # needed to not create new step but reorder
            QtWidgets.QTreeWidget.dropEvent(self, event)
            self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
            self.reorderSignal.emit(event)
        elif isinstance(event.source(), MyQTreeWidget):  # if event comes from another recipe -> remove from incoming recipe and add to outgoing recipe
            if event.mimeData().hasFormat(MyQTreeWidget.customMimeType):
                encoded = event.mimeData().data(MyQTreeWidget.customMimeType)
                items = self.decodeData(encoded, event.source())
                recipe_name_output = event.source().recipe_name
                for it in items:
                    name = it.text(0)
                    stepType = self.scanner.configManager.getRecipeStepType(name, recipe_name_output)
                    stepElement = self.scanner.configManager.getRecipeStepElement(name, recipe_name_output)
                    stepValue = self.scanner.configManager.getRecipeStepValue(name, recipe_name_output)
                    self.scanner.configManager.delRecipeStep(name, recipe_name_output)
                    self.scanner.configManager.addRecipeStep(stepType, stepElement, name, stepValue, self.recipe_name)
        else: # event comes from controlcenter -> check type to add step
            gui = event.source().gui
            variable = event.source().last_drag
            if variable:
                if variable._element_type == "variable" :
                    if variable.readable and variable.writable:
                        self.menu(gui, variable, event.pos())
                    elif variable.readable:
                        gui.addStepToScanRecipe('measure',variable, self.recipe_name)
                    elif variable.writable:
                        gui.addStepToScanRecipe('set',variable, self.recipe_name)
                elif variable._element_type == "action":
                    gui.addStepToScanRecipe('action',variable, self.recipe_name)

    def dragEnterEvent(self, event):
        # Could use mimeData instead of last_drag but overkill
        if (event.source() is self) or (
                hasattr(event.source(), "last_drag") and hasattr(event.source().last_drag, "_element_type") and event.source().last_drag._element_type != "module"):
            event.accept()
            shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=25, xOffset=3, yOffset=3)
            self.setGraphicsEffect(shadow)

        elif type(event.source()) == type(self):
            shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=25, xOffset=3, yOffset=3)
            event.source().setGraphicsEffect(None)
            self.setGraphicsEffect(shadow)
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setGraphicsEffect(None)

    def menu(self, gui, variable, position):

        """ This function provides the menu when the user right click on an item """

        menu = QtWidgets.QMenu()
        scanMeasureStepAction = menu.addAction("Measure in scan recipe")
        scanSetStepAction = menu.addAction("Set value in scan recipe")
        scanMeasureStepAction.setEnabled(variable.readable)
        scanSetStepAction.setEnabled(variable.writable)
        choice = menu.exec_(self.viewport().mapToGlobal(position))
        if choice == scanMeasureStepAction :
            gui.addStepToScanRecipe('measure',variable, self.recipe_name)
        elif choice == scanSetStepAction :
            gui.addStepToScanRecipe('set',variable, self.recipe_name)


class RecipeManager :

    def __init__(self,gui, recipe_name):

        self.gui = gui
        self.recipe_name = recipe_name

        # Import Autolab config
        scanner_config = config.get_scanner_config()
        self.precision = scanner_config['precision']

        # Tree configuration
        self.tree = MyQTreeWidget(self.gui, self.recipe_name)
        self.tree.setHeaderLabels(['Step name','Type','Element address','Value'])
        self.tree.header().resizeSection(3, 50)
        self.tree.itemDoubleClicked.connect(self.itemDoubleClicked)
        self.tree.reorderSignal.connect(self.orderChanged)
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.tree.setDropIndicatorShown(True)
        self.tree.setAlternatingRowColors(True)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.tree.setMinimumSize(450,500)
        self.tree.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.tree.customContextMenuRequested.connect(self.rightClick)

        if self.recipe_name == 'initrecipe':
            self.gui.tree_layout_begin.addWidget(self.tree)
        elif self.recipe_name == 'recipe':
            self.gui.tree_layout.addWidget(self.tree)
        elif self.recipe_name == 'endrecipe':
            self.gui.tree_layout_end.addWidget(self.tree)

        self.defaultItemBackground = None


    def orderChanged(self,event):
        newOrder = [self.tree.topLevelItem(i).text(0) for i in range(self.tree.topLevelItemCount())]
        self.gui.configManager.setRecipeOrder(newOrder, self.recipe_name)


    def refresh(self):

        """ Refresh the whole scan recipe displayed from the configuration center """

        self.tree.clear()

        recipe = self.gui.configManager.getRecipe(self.recipe_name)

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
                try:
                    if step['element'].type in [bool,str] :
                       item.setText(3,f'{value}')
                    else :
                       item.setText(3,f'{value:.{self.precision}g}')
                except ValueError:
                    item.setText(3,f'{value}')
            # Add item to the tree
            self.tree.addTopLevelItem(item)
            self.defaultItemBackground = item.background(0)



    def rightClick(self,position):

        """ This functions provide a menu where the user right clicked """

        item = self.tree.itemAt(position)

        if item is not None and self.gui.scanManager.isStarted() is False :

            name = item.text(0)
            stepType = self.gui.configManager.getRecipeStepType(name, self.recipe_name)
            element = self.gui.configManager.getRecipeStepElement(name, self.recipe_name)

            menuActions = {}

            menu = QtWidgets.QMenu()
            menuActions['rename'] = menu.addAction("Rename")
            if stepType == 'set' or (stepType == 'action' and element.type in [int,float,str,pd.DataFrame,np.ndarray]) :
                menuActions['setvalue'] = menu.addAction("Set value")
            menuActions['remove'] = menu.addAction("Remove")

            choice = menu.exec_(self.tree.viewport().mapToGlobal(position))

            if 'rename' in menuActions.keys() and choice == menuActions['rename'] :
                self.renameStep(name)
            elif 'remove' in menuActions.keys() and choice == menuActions['remove'] :
                self.gui.configManager.delRecipeStep(name, self.recipe_name)
            elif 'setvalue' in menuActions.keys() and choice == menuActions['setvalue'] :
                self.setStepValue(name)



    def renameStep(self,name):

        """ This function prompts the user for a new step name, and apply it to the selected step """

        newName,state = QtWidgets.QInputDialog.getText(self.gui, name, f"Set {name} new name",
                                                       QtWidgets.QLineEdit.Normal, name)

        newName = main.cleanString(newName)
        if newName != '' :
            self.gui.configManager.renameRecipeStep(name,newName, self.recipe_name)



    def setStepValue(self,name):

        """ This function prompts the user for a new step value, and apply it to the selected step """

        element = self.gui.configManager.getRecipeStepElement(name, self.recipe_name)
        value = self.gui.configManager.getRecipeStepValue(name, self.recipe_name)

        # Default value displayed in the QInputDialog
        try:
            defaultValue = f'{value:.{self.precision}g}'
        except ValueError:
            defaultValue = f'{value}'
        value,state = QtWidgets.QInputDialog.getText(self.gui,
                                                     name,
                                                     f"Set {name} value",
                                                     QtWidgets.QLineEdit.Normal, defaultValue)

        if value != '' :

            try :

                try:
                    assert self.checkVariable(value) == 0, "Need $eval: to evaluate the given string"

                except :
                    # Type conversions
                    if element.type in [int]:
                        value = int(value)
                    elif element.type in [float] :
                        value = float(value)
                    elif element.type in [str] :
                        value = str(value)
                    elif element.type in [bool]:
                        if value == "False": value = False
                        elif value == "True": value = True
                        value = int(value)
                        assert value in [0,1]
                        value = bool(value)
                    else:
                        assert self.checkVariable(value) == 0, "Need $eval: to evaluate the given string"

                # Apply modification
                self.gui.configManager.setRecipeStepValue(name,value, self.recipe_name)

            except Exception as er:
                self.gui.setStatus(f"Can't set step: {er}", 10000, False)
                pass

    ## OLD: this code was used to check if a given variable exists in a device.  Only work for one variable.
    ## If someone think it could be usefull to check if variables exists,
    ## You are welcome to implement a parsing system to check all the variables in the given string
    # def checkVariable(self, value):

    #     """ Check if value is a valid device variable address. For example value='dummy.amplitude' """
    #     module_name, *submodules_name, variable_name = value.split(".")
    #     module = self.gui.mainGui.tree.findItems(module_name, QtCore.Qt.MatchExactly)[0].module
    #     for submodule_name in submodules_name:
    #         module = module.get_module(submodule_name)
    #     module.get_variable(variable_name)

    def checkVariable(self, value):

        """ Check if value start with '$eval:'. Will not try to check if variables exists"""

        if str(value).startswith("$eval:"):
            return 0
        else:
            return -1


    def itemDoubleClicked(self,item,column):

        """ This function executes an action depending where the user double clicked """

        name = item.text(0)
        stepType = self.gui.configManager.getRecipeStepType(name, self.recipe_name)
        element = self.gui.configManager.getRecipeStepElement(name, self.recipe_name)

        if column == 0 :
            self.renameStep(name)
        if column == 3 :
            if stepType == 'set' or (stepType == 'action' and element.type in [int,float,str,pd.DataFrame,np.ndarray]) :
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

        for name in self.gui.configManager.getNames(option='recipe', recipe_name=self.recipe_name):
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
