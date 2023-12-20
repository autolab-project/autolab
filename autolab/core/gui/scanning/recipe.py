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

    def __init__(self, parent, gui, recipe_name):
        self.recipe_name = recipe_name
        self.scanner = gui
        QtWidgets.QTreeWidget.__init__(self, parent)
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
                    stepType = self.scanner.configManager.getRecipeStepType(recipe_name_output, name)
                    stepElement = self.scanner.configManager.getRecipeStepElement(recipe_name_output, name)
                    stepValue = self.scanner.configManager.getRecipeStepValue(recipe_name_output, name)
                    self.scanner.configManager.delRecipeStep(recipe_name_output, name)
                    self.scanner.configManager.addRecipeStep(self.recipe_name, stepType, stepElement, name, stepValue)

        else: # event comes from controlcenter -> check type to add step
            gui = event.source().gui
            variable = event.source().last_drag

            if variable:
                if variable._element_type == "variable":
                    if variable.readable and variable.writable:
                        self.menu(gui, variable, event.pos())
                    elif variable.readable:
                        gui.addStepToScanRecipe(self.recipe_name, 'measure', variable)
                    elif variable.writable:
                        gui.addStepToScanRecipe(self.recipe_name, 'set', variable)
                elif variable._element_type == "action":
                    gui.addStepToScanRecipe(self.recipe_name, 'action', variable)

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

    def menu(self, gui, variable, position: QtCore.QPoint):
        """ This function provides the menu when the user right click on an item """
        menu = QtWidgets.QMenu()
        scanMeasureStepAction = menu.addAction("Measure in scan recipe")
        scanSetStepAction = menu.addAction("Set value in scan recipe")
        scanMeasureStepAction.setEnabled(variable.readable)
        scanSetStepAction.setEnabled(variable.writable)
        choice = menu.exec_(self.viewport().mapToGlobal(position))
        if choice == scanMeasureStepAction:
            gui.addStepToScanRecipe(self.recipe_name, 'measure', variable)
        elif choice == scanSetStepAction:
            gui.addStepToScanRecipe(self.recipe_name, 'set', variable)


class parameterQFrame(QtWidgets.QFrame):
    # customMimeType = "autolab/MyQTreeWidget-selectedItems"

    def __init__(self, parent, recipe_name: str):
        self.recipe_name = recipe_name
        QtWidgets.QFrame.__init__(self, parent)
        self.setAcceptDrops(True)

    def dropEvent(self, event):
        """ Set parameter if drop compatible variable onto scanner (excluding recipe area) """
        if hasattr(event.source(), "last_drag"):
            gui = event.source().gui
            variable = event.source().last_drag
            if variable and variable.parameter_allowed:
                gui.setScanParameter(self.recipe_name, variable)

        self.setGraphicsEffect(None)

    def dragEnterEvent(self, event):
        """ Only accept config file (url) and parameter from controlcenter """
        # OPTIMIZE: create mimedata like for recipe if want to drag/drop parameter to recipe or parap to param
        if (hasattr(event.source(), "last_drag") and (hasattr(event.source().last_drag, "parameter_allowed") and event.source().last_drag.parameter_allowed)):
            event.accept()

            shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=25, xOffset=3, yOffset=3)
            self.setGraphicsEffect(shadow)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setGraphicsEffect(None)


class RecipeManager:
    """ Manage a recipe from a scan """

    def __init__(self, gui, recipe_name: str):

        self.gui = gui
        self.recipe_name = recipe_name

        # Import Autolab config
        scanner_config = config.get_scanner_config()
        self.precision = scanner_config['precision']

        self._addTree()

        self.defaultItemBackground = None

    def __del__(self):
        self._removeTree()

    def _addTree(self):

        # OPTIMIZE: should be in diff file so diff manager can access it without using recipemanager

        # Create recipe widget (parameter, scanrange, recipe)
        # Parameter frame
        frameParameter = parameterQFrame(self.gui, self.recipe_name)
        # frameParameter.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frameParameter.setMinimumSize(0, 32)
        frameParameter.setMaximumSize(16777215, 32)
        frameParameter.setToolTip(f"Drag and drop a variable or use the right click option of a variable from the control panel to add a recipe to the tree: {self.recipe_name}")

        parameterName_lineEdit = QtWidgets.QLineEdit('', frameParameter)
        parameterName_lineEdit.setMinimumSize(0, 20)
        parameterName_lineEdit.setMaximumSize(16777215, 20)
        parameterName_lineEdit.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        parameterName_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        parameterName_lineEdit.setToolTip('Name of the parameter, as it will displayed in the data')
        self.parameterName_lineEdit = parameterName_lineEdit

        parameterAddressIndicator_label = QtWidgets.QLabel("Address:", frameParameter)
        parameterAddressIndicator_label.setMinimumSize(0, 20)
        parameterAddressIndicator_label.setMaximumSize(16777215, 20)
        parameterAddressIndicator_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        parameterAddress_label = QtWidgets.QLabel("<variable>", frameParameter)
        parameterAddress_label.setMinimumSize(0, 20)
        parameterAddress_label.setMaximumSize(16777215, 20)
        parameterAddress_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        parameterAddress_label.setToolTip('Address of the parameter')
        self.parameterAddress_label = parameterAddress_label

        unit_label = QtWidgets.QLabel("uA", frameParameter)
        unit_label.setMinimumSize(0, 20)
        unit_label.setMaximumSize(16777215, 20)
        unit_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.unit_label = unit_label

        displayParameter_pushButton = QtWidgets.QPushButton("Parameter")
        displayParameter_pushButton.setMinimumSize(0, 23)
        displayParameter_pushButton.setMaximumSize(16777215, 23)
        self.displayParameter_pushButton = displayParameter_pushButton

        layoutParameter = QtWidgets.QHBoxLayout(frameParameter)
        layoutParameter.addWidget(parameterName_lineEdit)
        layoutParameter.addWidget(unit_label)
        layoutParameter.addWidget(parameterAddressIndicator_label)
        layoutParameter.addWidget(parameterAddress_label)
        layoutParameter.addWidget(displayParameter_pushButton)


        # Scanrange frame
        frameScanRange = QtWidgets.QFrame()
        # frameScanRange.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frameScanRange.setMinimumSize(0, 60)
        frameScanRange.setMaximumSize(16777215, 60)

        # first grid
        labelStart = QtWidgets.QLabel("Start", frameScanRange)
        start_lineEdit = QtWidgets.QLineEdit('0', frameScanRange)
        start_lineEdit.setToolTip('Start value of the scan')
        start_lineEdit.setMinimumSize(0, 20)
        start_lineEdit.setMaximumSize(16777215, 20)
        start_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.start_lineEdit = start_lineEdit

        labelEnd = QtWidgets.QLabel("End", frameScanRange)
        end_lineEdit = QtWidgets.QLineEdit('10', frameScanRange)
        end_lineEdit.setMinimumSize(0, 20)
        end_lineEdit.setMaximumSize(16777215, 20)
        end_lineEdit.setToolTip('End value of the scan')
        end_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.end_lineEdit = end_lineEdit

        startEndGridLayout = QtWidgets.QGridLayout(frameScanRange)
        startEndGridWidget = QtWidgets.QWidget(frameScanRange)
        startEndGridWidget.setLayout(startEndGridLayout)
        startEndGridLayout.addWidget(labelStart, 0, 0)
        startEndGridLayout.addWidget(start_lineEdit, 0, 1)
        startEndGridLayout.addWidget(labelEnd, 1, 0)
        startEndGridLayout.addWidget(end_lineEdit, 1, 1)

        # second grid
        labelMean = QtWidgets.QLabel("Mean", frameScanRange)
        mean_lineEdit = QtWidgets.QLineEdit('5', frameScanRange)
        mean_lineEdit.setMinimumSize(0, 20)
        mean_lineEdit.setMaximumSize(16777215, 20)
        mean_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.mean_lineEdit = mean_lineEdit

        labelWidth = QtWidgets.QLabel("Width", frameScanRange)
        width_lineEdit = QtWidgets.QLineEdit('10', frameScanRange)
        width_lineEdit.setMinimumSize(0, 20)
        width_lineEdit.setMaximumSize(16777215, 20)
        width_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.width_lineEdit = width_lineEdit

        meanWidthGridLayout = QtWidgets.QGridLayout(frameScanRange)
        meanWidthGridWidget = QtWidgets.QWidget(frameScanRange)
        meanWidthGridWidget.setLayout(meanWidthGridLayout)
        meanWidthGridLayout.addWidget(labelMean, 0, 0)
        meanWidthGridLayout.addWidget(mean_lineEdit, 0, 1)
        meanWidthGridLayout.addWidget(labelWidth, 1, 0)
        meanWidthGridLayout.addWidget(width_lineEdit, 1, 1)

        # third grid
        labelNbpts = QtWidgets.QLabel("Nb points", frameScanRange)
        nbpts_lineEdit = QtWidgets.QLineEdit('11', frameScanRange)
        nbpts_lineEdit.setMinimumSize(0, 20)
        nbpts_lineEdit.setMaximumSize(16777215, 20)
        nbpts_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.nbpts_lineEdit = nbpts_lineEdit

        labelStep = QtWidgets.QLabel("Step", frameScanRange)
        step_lineEdit = QtWidgets.QLineEdit('1', frameScanRange)
        step_lineEdit.setMinimumSize(0, 20)
        step_lineEdit.setMaximumSize(16777215, 20)
        step_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.step_lineEdit = step_lineEdit
        scanLog_checkBox = QtWidgets.QCheckBox("Log")
        self.scanLog_checkBox = scanLog_checkBox

        nptsStepGridLayout = QtWidgets.QGridLayout(frameScanRange)
        nptsStepGridWidget = QtWidgets.QWidget(frameScanRange)
        nptsStepGridWidget.setLayout(nptsStepGridLayout)
        nptsStepGridLayout.addWidget(labelNbpts, 0, 0)
        nptsStepGridLayout.addWidget(nbpts_lineEdit, 0, 1)
        nptsStepGridLayout.addWidget(labelStep, 1, 0)
        nptsStepGridLayout.addWidget(step_lineEdit, 1, 1)
        nptsStepGridLayout.addWidget(scanLog_checkBox, 1, 2)

        layoutScanRange = QtWidgets.QHBoxLayout(frameScanRange)
        layoutScanRange.setContentsMargins(0,0,0,0)
        layoutScanRange.setSpacing(0)
        layoutScanRange.addWidget(startEndGridWidget)
        layoutScanRange.addStretch()
        layoutScanRange.addWidget(meanWidthGridWidget)
        layoutScanRange.addStretch()
        layoutScanRange.addWidget(nptsStepGridWidget)

        # Recipe frame
        frameRecipe = QtWidgets.QFrame()
        # frameRecipe.setFrameShape(QtWidgets.QFrame.StyledPanel)

        # Tree configuration
        self.tree = MyQTreeWidget(frameRecipe, self.gui, self.recipe_name)
        self.tree.setHeaderLabels(['Step name', 'Type', 'Element address', 'Value'])
        self.tree.header().resizeSection(0, 100)
        self.tree.header().resizeSection(1, 60)
        self.tree.header().resizeSection(2, 150)
        self.tree.itemDoubleClicked.connect(self.itemDoubleClicked)
        self.tree.reorderSignal.connect(self.orderChanged)
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.tree.setDropIndicatorShown(True)
        self.tree.setAlternatingRowColors(True)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.tree.customContextMenuRequested.connect(self.rightClick)
        self.tree.setMinimumSize(0, 200)
        self.tree.setMaximumSize(16777215, 16777215)

        layoutRecipe = QtWidgets.QVBoxLayout(frameRecipe)
        layoutRecipe.addWidget(self.tree)

        # Qframe and QTab for close+parameter+scanrange+recipe
        frameAll = QtWidgets.QFrame()
        # frameAll.setFrameShape(QtWidgets.QFrame.StyledPanel)
        layoutAll = QtWidgets.QVBoxLayout(frameAll)
        layoutAll.setContentsMargins(0,0,0,0)
        layoutAll.setSpacing(0)
        layoutAll.addWidget(frameParameter)
        layoutAll.addWidget(frameScanRange)
        layoutAll.addWidget(frameRecipe)

        class MyQTabWidget(QtWidgets.QTabWidget):

            def __init__(self, frame, gui, recipe_name):
                self.recipe_name = recipe_name
                self.gui = gui
                QtWidgets.QTabWidget.__init__(self)

                self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                self.customContextMenuRequested.connect(self.menu)
                self.tabBarDoubleClicked.connect(self.renameRecipe)

                self.addTab(frame, self.recipe_name)
                stylesheet = """
                    QTabWidget>QWidget>QWidget{background: rgb(240, 240, 240);}
                    """
                self.setStyleSheet(stylesheet)

            def menu(self, position: QtCore.QPoint):
                """ This function provides the menu when the user right click on an item """
                menu = QtWidgets.QMenu()
                renameRecipeAction = menu.addAction("Rename")
                removeRecipeAction = menu.addAction("Remove")
                choice = menu.exec_(self.mapToGlobal(QtCore.QPoint(0, 20)))  # don't use position to avoid confusion with tree element when very closed

                if choice == renameRecipeAction:
                    self.renameRecipe()
                if choice == removeRecipeAction:
                    self.gui.configManager.removeRecipe(self.recipe_name)

            def renameRecipe(self):
                """ This function prompts the user for a new step name,
                and apply it to the selected step """
                newName, state = QtWidgets.QInputDialog.getText(
                    self.gui, self.recipe_name, f"Set {self.recipe_name} new name",
                    QtWidgets.QLineEdit.Normal, self.recipe_name)

                newName = main.cleanString(newName)
                if newName != '':
                    self.gui.configManager.renameRecipe(
                        self.recipe_name, newName)

        frameAll2 = MyQTabWidget(frameAll, self.gui, self.recipe_name)
        self._frame = frameAll2
        self.gui.verticalLayout_recipe.addWidget(self._frame)

    def _removeTree(self):
        if hasattr(self, '_frame'):
            try:
                self._frame.hide()
                self._frame.deleteLater()
                del self._frame
            except: pass

    def orderChanged(self, event):
        newOrder = [self.tree.topLevelItem(i).text(0) for i in range(self.tree.topLevelItemCount())]
        self.gui.configManager.setRecipeOrder(self.recipe_name, newOrder)

    def refresh(self):
        """ Refresh the whole scan recipe displayed from the configuration center """
        self.tree.clear()
        recipe = self.gui.configManager.getRecipe(self.recipe_name)

        for step in recipe:

            # Loading step informations
            item = QtWidgets.QTreeWidgetItem()
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsDropEnabled)

            # Column 1 : Step name
            item.setText(0, step['name'])

            # Column 2 : Step type
            if step['stepType'] == 'measure':
                item.setText(1, 'Measure')
            elif step['stepType']  == 'set':
                item.setText(1, 'Set')
            elif step['stepType']  == 'action':
                item.setText(1, 'Do')

            # Column 3 : Element address
            item.setText(2, step['element'].address())

            # Column 4 : Value if stepType is 'set'
            value = step['value']
            if value is not None:
                try:
                    if step['element'].type in [bool, str]:
                       item.setText(3, f'{value}')
                    else:
                       item.setText(3, f'{value:.{self.precision}g}')
                except ValueError:
                    item.setText(3, f'{value}')

            # Add item to the tree
            self.tree.addTopLevelItem(item)
            self.defaultItemBackground = item.background(0)

    def rightClick(self, position: QtCore.QPoint):
        """ This functions provide a menu where the user right clicked """
        item = self.tree.itemAt(position)

        if not self.gui.scanManager.isStarted() and item is not None:
            name = item.text(0)
            stepType = self.gui.configManager.getRecipeStepType(
                self.recipe_name, name)
            element = self.gui.configManager.getRecipeStepElement(
                self.recipe_name, name)

            menuActions = {}

            menu = QtWidgets.QMenu()
            menuActions['rename'] = menu.addAction("Rename")
            if stepType == 'set' or (stepType == 'action' and element.type in [
                    int,float,str,pd.DataFrame,np.ndarray]) :
                menuActions['setvalue'] = menu.addAction("Set value")
            menuActions['remove'] = menu.addAction("Remove")

            choice = menu.exec_(self.tree.viewport().mapToGlobal(position))

            if 'rename' in menuActions.keys() and choice == menuActions['rename']:
                self.renameStep(name)
            elif 'remove' in menuActions.keys() and choice == menuActions['remove']:
                self.gui.configManager.delRecipeStep(self.recipe_name, name)
            elif 'setvalue' in menuActions.keys() and choice == menuActions['setvalue']:
                self.setStepValue(name)

    def renameStep(self, name: str):
        """ This function prompts the user for a new step name,
        and apply it to the selected step """
        newName, state = QtWidgets.QInputDialog.getText(
            self.gui, name, f"Set {name} new name",
            QtWidgets.QLineEdit.Normal, name)

        newName = main.cleanString(newName)
        if newName != '':
            self.gui.configManager.renameRecipeStep(
                self.recipe_name, name, newName)

    def setStepValue(self, name: str):
        """ This function prompts the user for a new step value,
        and apply it to the selected step """
        element = self.gui.configManager.getRecipeStepElement(
            self.recipe_name, name)
        value = self.gui.configManager.getRecipeStepValue(
            self.recipe_name, name)

        # Default value displayed in the QInputDialog
        try:
            defaultValue = f'{value:.{self.precision}g}'
        except ValueError:
            defaultValue = f'{value}'
        value,state = QtWidgets.QInputDialog.getText(
            self.gui, name, f"Set {name} value",
            QtWidgets.QLineEdit.Normal, defaultValue)

        if value != '':
            try:
                try:
                    assert self.checkVariable(value), "Need $eval: to evaluate the given string"
                except:
                    # Type conversions
                    if element.type in [int]:
                        value = int(value)
                    elif element.type in [float]:
                        value = float(value)
                    elif element.type in [str]:
                        value = str(value)
                    elif element.type in [bool]:
                        if value == "False": value = False
                        elif value == "True": value = True
                        value = int(value)
                        assert value in [0, 1]
                        value = bool(value)
                    else:
                        assert self.checkVariable(value), "Need $eval: to evaluate the given string"
                # Apply modification
                self.gui.configManager.setRecipeStepValue(
                    self.recipe_name, name, value)
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

    def checkVariable(self, value) -> bool:
        """ Check if value start with '$eval:'. Will not try to check if variables exists"""
        return True if str(value).startswith("$eval:") else False

    def itemDoubleClicked(self, item, column: int):
        """ This function executes an action depending where the user double clicked """
        name = item.text(0)
        stepType = self.gui.configManager.getRecipeStepType(self.recipe_name, name)
        element = self.gui.configManager.getRecipeStepElement(self.recipe_name, name)

        if column == 0:
            self.renameStep(name)
        elif column == 3:
            if stepType == 'set' or (stepType == 'action' and element.type in [
                    int,float,str,pd.DataFrame,np.ndarray]):
                self.setStepValue(name)

    def setStepProcessingState(self, name: str, state: str):
        """ This function set the background color of a recipe step during the scan """
        item = self.tree.findItems(name, QtCore.Qt.MatchExactly, 0)[0]

        if state is None:
            item.setBackground(0, self.defaultItemBackground)
        elif state == 'started':
            item.setBackground(0, QtGui.QColor('#ff8c1a'))
        elif state == 'finished':
            item.setBackground(0, QtGui.QColor('#70db70'))

    def resetStepsProcessingState(self):
        """ This function reset the background color of a recipe once the scan is finished """
        for name in self.gui.configManager.getNames(self.recipe_name, option='recipe'):
            self.setStepProcessingState(name, None)


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
