# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 14:42:16 2024

@author: Jonathan
"""

from typing import List

from qtpy import QtCore, QtWidgets, QtGui

from . import main
from ...devices import Device


class MyQTreeWidget(QtWidgets.QTreeWidget):
    customMimeType = "autolab/MyQTreeWidget-selectedItems"

    reorderSignal = QtCore.Signal(object)

    def __init__(self, parent: QtWidgets.QFrame,
                 gui: QtWidgets.QMainWindow, recipe_name: str):

        self.recipe_name = recipe_name
        self.scanner = gui
        QtWidgets.QTreeWidget.__init__(self, parent)
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

                for it in items:
                    name = it.text(0)
                    stepType = self.scanner.configManager.getRecipeStepType(recipe_name_output, name)
                    stepElement = self.scanner.configManager.getRecipeStepElement(recipe_name_output, name)
                    stepValue = self.scanner.configManager.getRecipeStepValue(recipe_name_output, name)
                    self.scanner.configManager.configHistory.active = False
                    self.scanner.configManager.delRecipeStep(recipe_name_output, name)
                    self.scanner.configManager.configHistory.active = True
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
        """ Check if drag event is acceptable """
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

    def menu(self, gui: QtWidgets.QMainWindow,
             variable: Device, position: QtCore.QPoint):
        """ Provides the menu when the user right click on an item """
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


class MyQTabWidget(QtWidgets.QTabWidget):

    def __init__(self, frame:  QtWidgets.QFrame,
                 gui: QtWidgets.QMainWindow, recipe_name: str):

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
        """ Provides the menu when the user right click on an item """
        if not self.gui.scanManager.isStarted():
            menu = QtWidgets.QMenu()
            renameRecipeAction = menu.addAction("Rename")
            removeRecipeAction = menu.addAction("Remove")
            menu.addSeparator()

            recipeLink = self.gui.configManager.getRecipeLink(self.recipe_name)
            if len(recipeLink) == 1:  # A bit too restrictive but do the work
                renameRecipeAction.setEnabled(True)
            else:
                renameRecipeAction.setEnabled(False)

            IS_ACTIVE = self.gui.configManager.getActive(self.recipe_name)

            if IS_ACTIVE:
                activateRecipeAction = menu.addAction("Disable")
            else:
                activateRecipeAction = menu.addAction("Enable")

            menu.addSeparator()

            addParameterAction = menu.addAction("Add Parameter")

            removeMenuActions = {}
            for parameter in self.gui.configManager.parameterList(self.recipe_name):
                removeMenuActions[parameter['name']] = menu.addAction(f"Remove {parameter['name']}")

            menu.addSeparator()
            moveUpRecipeAction = menu.addAction("Move up")
            moveDownRecipeAction = menu.addAction("Move down")

            config = self.gui.configManager.config
            keys = list(config.keys())
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
                self.addParameter()
            elif choice in removeMenuActions.values():
                param_name = list(removeMenuActions.keys())[list(removeMenuActions.values()).index(choice)]
                self.removeParameter(param_name)

    def renameRecipe(self):
        """ Prompts the user for a new recipe name and apply it to the selected recipe """
        if not self.gui.scanManager.isStarted():
            newName, state = QtWidgets.QInputDialog.getText(
                self.gui, self.recipe_name, f"Set {self.recipe_name} new name",
                QtWidgets.QLineEdit.Normal, self.recipe_name)

            newName = main.cleanString(newName)

            if newName != '':
                self.gui.configManager.renameRecipe(
                    self.recipe_name, newName)

    def addParameter(self):
        """ Proxy to add parameter to config """
        self.gui.configManager.addParameter(self.recipe_name)

    def removeParameter(self, param_name: str):
        """ Proxy to remove parameter to config """
        self.gui.configManager.removeParameter(self.recipe_name, param_name)


class parameterQFrame(QtWidgets.QFrame):
    # customMimeType = "autolab/MyQTreeWidget-selectedItems"

    def __init__(self, parent: QtWidgets.QMainWindow, recipe_name: str, param_name: str):
        self.recipe_name = recipe_name
        self.param_name = param_name
        QtWidgets.QFrame.__init__(self, parent)
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
