# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 14:42:16 2024

@author: Jonathan
"""

from typing import List, Union

import numpy as np
import pandas as pd
from qtpy import QtCore, QtWidgets, QtGui

from ..icons import icons
from ...utilities import clean_string, array_to_str, dataframe_to_str
from ...elements import Variable as Variable_og
from ...elements import Action
from ...variables import has_eval
from ...config import get_scanner_config


class MyQTreeWidget(QtWidgets.QTreeWidget):
    customMimeType = "autolab/MyQTreeWidget-selectedItems"

    reorderSignal = QtCore.Signal(object)

    def __init__(self, parent: QtWidgets.QFrame,
                 gui: QtWidgets.QMainWindow, recipe_name: str):

        self.recipe_name = recipe_name
        self.scanner = gui  # gui is scanner
        super().__init__(parent)
        self.setAcceptDrops(True)

    def mimeTypes(self) -> QtWidgets.QTreeWidget.mimeTypes:
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

    def encodeData(self, items: List[QtWidgets.QTreeWidgetItem],
                   stream: QtCore.QDataStream):
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

    def decodeData(self, encoded: QtCore.QByteArray,
                   tree: QtWidgets.QTreeWidget) -> List[QtWidgets.QTreeWidgetItem]:
        items = []
        rows = []
        stream = QtCore.QDataStream(encoded, QtCore.QIODevice.ReadOnly)
        while not stream.atEnd():
            nItems = stream.readInt32()
            for _ in range(nItems):
                path = stream.readInt32()
                row = []
                for _ in range(path):
                    row.append(stream.readInt32())
                rows.append(row)

        for row in rows:
            it = tree.topLevelItem(row[0])
            for ix in row[1:]:
                it = it.child(ix)
            items.append(it)
        return items

    def dropEvent(self, event):
        """ Reorders the recipe if event comes from self.
        Moves a step from another recipe to self if event is of type MyQTreeWidget.
        Else event from controlcenter, adds step for controlcenter """
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

                for it in items:  # should always have one item
                    name = it.text(0)
                    stepType = self.scanner.configManager.getRecipeStepType(recipe_name_output, name)
                    stepElement = self.scanner.configManager.getRecipeStepElement(recipe_name_output, name)
                    stepValue = self.scanner.configManager.getRecipeStepValue(recipe_name_output, name)
                    # OPTIMIZE: prevent cycle between recipe and twice same recipe in a recipe before accepting the drag event

                    if stepElement != self.recipe_name:  # should always be different thanks to drag event refusal of dropping recipe in itself
                        self.scanner.configManager.configHistory.active = False
                        self.scanner.configManager.delRecipeStep(recipe_name_output, name)
                        self.scanner.configManager.configHistory.active = True
                        self.scanner.configManager.addRecipeStep(self.recipe_name, stepType, stepElement, name, stepValue)

                        try: self.scanner.configManager.getAllowedRecipe(self.recipe_name)  # OBSOLETE
                        except ValueError:
                            self.scanner.setStatus('ERROR cycle between recipes detected! change cancelled', 10000, False)
                            self.scanner.configManager.configHistory.active = False
                            self.scanner.configManager.configHistory.go_down()  # to overwrite config with error
                            self.scanner.configManager.delRecipeStep(self.recipe_name, name)
                            self.scanner.configManager.configHistory.active = True
                            self.scanner.configManager.addRecipeStep(recipe_name_output, stepType, stepElement, name, stepValue)

        else: # event comes from controlcenter -> check type to add step
            if hasattr(event.source(), 'gui'): gui = event.source().gui
            else: # OPTIMIZE: event.source() should be either self or instance of MyQTreeWidget but is sometime not recognize as such so goes to else and raise error don't have gui
                message = 'ERROR catched, please create an issue here: https://github.com/autolab-project/autolab/issues with the following informations:'
                message += '\nTitle: event.source() error in scanner'
                message += "\nDescription:"
                message += f"\nEvent source: {event.source()}"
                if hasattr(event.source(), 'customMimeType'):
                    message += f"\nEvent Mime: {event.source().customMimeType}"
                message += f"\nIs MyQTreeWidget: {isinstance(event.source(), MyQTreeWidget)}"
                message += f"\nself: {self}"
                message += f"\nIs self: {event.source() is self}"
                self.scanner.setStatus(message, 0, False)
                return None

            variable = event.source().last_drag

            if variable:
                if variable._element_type == "variable":
                    if variable.readable and variable.writable:
                        self.menu(gui, variable, event.pos())
                    elif variable.readable:
                        gui.addStepToScanRecipe(self.recipe_name, 'measure', variable)
                    elif variable.writable:
                        value = variable.value if variable.type in [tuple] else None
                        gui.addStepToScanRecipe(
                            self.recipe_name, 'set', variable, value=value)
                elif variable._element_type == "action":
                    gui.addStepToScanRecipe(self.recipe_name, 'action', variable)

            # OPTIMIZE: should be done in control panel somehow to catch drop cancel
            self.scanner.mainGui.setWindowState(
                self.scanner.mainGui.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.scanner.mainGui.activateWindow()

    def dragEnterEvent(self, event):
        """ Check if drag event is acceptable """
        # Could use mimeData instead of last_drag but overkill
        if (event.source() is self) or (
                hasattr(event.source(), "last_drag") and hasattr(event.source().last_drag, "_element_type") and event.source().last_drag._element_type != "module"):
            event.accept()
            shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=25, xOffset=3, yOffset=3)
            self.setGraphicsEffect(shadow)

        elif isinstance(event.source(), type(self)):
            try:  # Refuse drop recipe in itself
                if event.mimeData().hasFormat(MyQTreeWidget.customMimeType):
                    encoded = event.mimeData().data(MyQTreeWidget.customMimeType)
                    items = self.decodeData(encoded, event.source())
                    recipe_name_output = event.source().recipe_name
                    for it in items:
                        name = it.text(0)
                        stepElement = self.scanner.configManager.getRecipeStepElement(
                            recipe_name_output, name)
                        if self.recipe_name == stepElement:  # OPTIMIZE: not enought to prevent cycle (see how to use config.getAllowedRecipe)
                            event.ignore()
                            return None
            except: pass

            shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=25, xOffset=3, yOffset=3)
            event.source().setGraphicsEffect(None)
            self.setGraphicsEffect(shadow)
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setGraphicsEffect(None)

    def menu(self, gui: QtWidgets.QMainWindow,
             variable: Union[Variable_og, Action], position: QtCore.QPoint):
        """ Provides the menu when the user right click on an item """
        menu = QtWidgets.QMenu()
        scanMeasureStepAction = menu.addAction("Measure in scan recipe")
        scanMeasureStepAction.setIcon(icons['measure'])
        scanSetStepAction = menu.addAction("Set value in scan recipe")
        scanSetStepAction.setIcon(icons['write'])
        scanMeasureStepAction.setEnabled(variable.readable)
        scanSetStepAction.setEnabled(variable.writable)
        choice = menu.exec_(self.viewport().mapToGlobal(position))
        if choice == scanMeasureStepAction:
            gui.addStepToScanRecipe(self.recipe_name, 'measure', variable)

        elif choice == scanSetStepAction:
            value = variable.value if variable.type in [tuple] else None
            gui.addStepToScanRecipe(
                self.recipe_name, 'set', variable, value=value)

    def keyPressEvent(self, event):
        ctrl = QtCore.Qt.ControlModifier
        shift = QtCore.Qt.ShiftModifier
        mod = event.modifiers()
        if event.key() == QtCore.Qt.Key_R and mod == ctrl:
            self.rename_step(event)
        elif event.key() == QtCore.Qt.Key_C and mod == ctrl:
            self.copy_step(event)
        elif event.key() == QtCore.Qt.Key_V and mod == ctrl:
            self.paste_step(event)
        elif event.key() == QtCore.Qt.Key_Z and mod == ctrl:
            # Note: needed to add setFocus to tree on creation to allow multiple ctrl+z
            self.scanner.configManager.undoClicked()
        elif (
            event.key() == QtCore.Qt.Key_Z and mod == (ctrl | shift)
        ) or (
            event.key() == QtCore.Qt.Key_Y and mod == ctrl
        ):
            self.scanner.configManager.redoClicked()
        elif (event.key() == QtCore.Qt.Key_Delete):
            self.remove_step(event)
        else:
            super().keyPressEvent(event)

    def rename_step(self, event):
        if len(self.selectedItems()) == 0:
            super().keyPressEvent(event)
            return None
        item = self.selectedItems()[0]  # assume can select only one item
        self.scanner.recipeDict[self.recipe_name]['recipeManager'].renameStep(item.text(0))

    def copy_step(self, event):
        if len(self.selectedItems()) == 0:
            super().keyPressEvent(event)
            return None
        item = self.selectedItems()[0]  # assume can select only one item
        self.scanner.recipeDict[self.recipe_name]['recipeManager'].copyStep(item.text(0))

    def paste_step(self, event):
        self.scanner.recipeDict[self.recipe_name]['recipeManager'].pasteStep()

    def remove_step(self, event):
        if len(self.selectedItems()) == 0:
            super().keyPressEvent(event)
            return None
        item = self.selectedItems()[0]  # assume can select only one item
        self.scanner.recipeDict[self.recipe_name]['recipeManager'].removeStep(item.text(0))


class MyQTreeWidgetItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, itemParent: QtWidgets.QTreeWidget, step: dict,
                 gui: QtWidgets.QMainWindow):

        self.gui = gui

        # Import Autolab config
        scanner_config = get_scanner_config()
        self.precision = scanner_config['precision']

        super().__init__(itemParent)

        self.setFlags(self.flags() ^ QtCore.Qt.ItemIsDropEnabled)
        self.setToolTip(0, step['element']._help)

        # Column 1 : Step name
        self.setText(0, step['name'])

        # OPTIMIZE: stepType is a bad name. Possible confusion with element type. stepType should be stepAction or just action
        # Column 2 : Step type
        if step['stepType'] == 'measure':
            self.setText(1, 'Measure')
            self.setIcon(0, icons['measure'])
        elif step['stepType']  == 'set':
            self.setText(1, 'Set')
            self.setIcon(0, icons['write'])
        elif step['stepType']  == 'action':
            self.setText(1, 'Do')
            self.setIcon(0, icons['action'])
        elif step['stepType']  == 'recipe':
            self.setText(1, 'Recipe')
            self.setIcon(0, icons['recipe'])

        # Column 3 : Element address
        if step['stepType'] == 'recipe':
            self.setText(2, step['element'])
        else:
            self.setText(2, step['element'].address())

        # Column 4 : Icon of element type
        etype = step['element'].type
        if etype is int: self.setIcon(3, icons['int'])
        elif etype is float: self.setIcon(3, icons['float'])
        elif etype is bool: self.setIcon(3, icons['bool'])
        elif etype is str: self.setIcon(3, icons['str'])
        elif etype is bytes: self.setIcon(3, icons['bytes'])
        elif etype is tuple: self.setIcon(3, icons['tuple'])
        elif etype is np.ndarray: self.setIcon(3, icons['ndarray'])
        elif etype is pd.DataFrame: self.setIcon(3, icons['DataFrame'])

        # Column 5 : Value if stepType is 'set'
        value = step['value']
        if value is not None:
            if has_eval(value):
                self.setText(4, f'{value}')
            else:
                try:
                    if step['element'].type in [bool, str, tuple]:
                        self.setText(4, f'{value}')
                    elif step['element'].type in [bytes]:
                        self.setText(4, f"{value.decode()}")
                    elif step['element'].type in [np.ndarray]:
                        value = array_to_str(
                            value, threshold=1000000, max_line_width=100)
                        self.setText(4, f'{value}')
                    elif step['element'].type in [pd.DataFrame]:
                        value = dataframe_to_str(value, threshold=1000000)
                        self.setText(4, f'{value}')
                    else:
                       self.setText(4, f'{value:.{self.precision}g}')
                except ValueError:
                    self.setText(4, f'{value}')

        # Column 6 : Unit of element
        unit = step['element'].unit
        if unit is not None:
            self.setText(5, str(unit))

        # set AlignTop to all columns
        for i in range(self.columnCount()):
            self.setTextAlignment(i, QtCore.Qt.AlignTop)
            # OPTIMIZE: icon are not aligned with text: https://www.xingyulei.com/post/qt-button-alignment/index.html


class MyQTabWidget(QtWidgets.QTabWidget):

    def __init__(self, frame:  QtWidgets.QFrame,
                 gui: QtWidgets.QMainWindow, recipe_name: str):

        self.recipe_name = recipe_name
        self.gui = gui
        super().__init__()

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.menu)
        self.tabBarDoubleClicked.connect(self.renameRecipe)

        self.addTab(frame, self.recipe_name)
        stylesheet = """
            QTabWidget>QWidget>QWidget{background: rgb(240, 240, 240);}
            """
        self.setStyleSheet(stylesheet)

    def menu(self, position: QtCore.QPoint):
        """ Provides the menu when the user right click on an item """
        if not self.gui.scanManager.isStarted():

            menu = QtWidgets.QMenu()

            IS_ACTIVE = self.gui.configManager.getActive(self.recipe_name)

            if IS_ACTIVE:
                activateRecipeAction = menu.addAction("Disable recipe")
                activateRecipeAction.setIcon(icons['is-enable'])
            else:
                activateRecipeAction = menu.addAction("Enable recipe")
                activateRecipeAction.setIcon(icons['is-disable'])

            menu.addSeparator()

            renameRecipeAction = menu.addAction("Rename recipe")
            renameRecipeAction.setIcon(icons['rename'])
            removeRecipeAction = menu.addAction("Remove recipe")
            removeRecipeAction.setIcon(icons['remove'])

            menu.addSeparator()

            # OBSOLETE
            recipeLink = self.gui.configManager.getRecipeLink(self.recipe_name)
            if len(recipeLink) == 1:  # A bit too restrictive but do the work
                renameRecipeAction.setEnabled(True)
            else:
                renameRecipeAction.setEnabled(False)

            addParameterAction = menu.addAction("Add parameter")
            addParameterAction.setIcon(icons['add'])

            menu.addSeparator()

            moveUpRecipeAction = menu.addAction("Move recipe up")
            moveUpRecipeAction.setIcon(icons['up'])
            moveDownRecipeAction = menu.addAction("Move recipe down")
            moveDownRecipeAction.setIcon(icons['down'])

            config = self.gui.configManager.config
            keys = list(config)
            pos = keys.index(self.recipe_name)

            if pos == 0: moveUpRecipeAction.setEnabled(False)
            if pos == (len(keys) - 1): moveDownRecipeAction.setEnabled(False)

            choice = menu.exec_(self.mapToGlobal(QtCore.QPoint(0, 20)))  # don't use position to avoid confusion with tree element when very closed

            if choice == renameRecipeAction:
                self.renameRecipe()
            elif choice == removeRecipeAction:
                self.gui.configManager.removeRecipe(self.recipe_name)
            elif choice == activateRecipeAction:
                self.gui.configManager.activateRecipe(self.recipe_name, not IS_ACTIVE)
            elif choice == moveUpRecipeAction:
                keys[pos], keys[pos-1] = keys[pos-1], keys[pos]
                self.gui.configManager.setRecipeOrder(keys)
            elif choice == moveDownRecipeAction:
                keys[pos], keys[pos+1] = keys[pos+1], keys[pos]
                self.gui.configManager.setRecipeOrder(keys)
            elif choice == addParameterAction:
                self.gui.configManager.addParameter(self.recipe_name)

    def renameRecipe(self):
        """ Prompts the user for a new recipe name and apply it to the selected recipe """
        if not self.gui.scanManager.isStarted():
            newName, state = QtWidgets.QInputDialog.getText(
                self.gui, self.recipe_name, f"Set {self.recipe_name} new name",
                QtWidgets.QLineEdit.Normal, self.recipe_name)

            newName = clean_string(newName)

            if newName != '':
                self.gui.configManager.renameRecipe(
                    self.recipe_name, newName)


class ParameterQFrame(QtWidgets.QFrame):
    # customMimeType = "autolab/MyQTreeWidget-selectedItems"

    def __init__(self, parent: QtWidgets.QMainWindow, recipe_name: str, param_name: str):
        self.recipe_name = recipe_name
        self.param_name = param_name
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dropEvent(self, event):
        """ Sets parameter if event comes from controlcenter """
        if hasattr(event.source(), "last_drag"):
            gui = event.source().gui
            variable = event.source().last_drag
            if variable and variable.parameter_allowed:
                gui.setScanParameter(self.recipe_name, self.param_name, variable)

        self.setGraphicsEffect(None)

    def dragEnterEvent(self, event):
        """ Only accept parameter from controlcenter """
        # OPTIMIZE: create mimedata like for recipe if want to drag/drop parameter to recipe or parap to param
        if (hasattr(event.source(), "last_drag") and (hasattr(event.source().last_drag, "parameter_allowed") and event.source().last_drag.parameter_allowed)):
            event.accept()
            shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=25, xOffset=3, yOffset=3)
            self.setGraphicsEffect(shadow)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setGraphicsEffect(None)
