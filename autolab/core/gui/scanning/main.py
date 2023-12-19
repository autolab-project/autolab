# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 22:08:29 2019

@author: qchat
"""
import os
import sys

from qtpy import QtWidgets, uic, QtGui

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
        ui_path = os.path.join(os.path.dirname(__file__), 'interface.ui')
        uic.loadUi(ui_path, self)
        self.setWindowTitle("AUTOLAB Scanner")
        self.splitter.setSizes([500, 700])  # Set the width of the two main widgets
        self.setAcceptDrops(True)
        self.recipeDict = {}

        # Loading of the different centers
        self.figureManager = FigureManager(self)
        self.scanManager = ScanManager(self)
        self.dataManager = DataManager(self)
        self.configManager = ConfigManager(self)

        self.configManager.addRecipe("recipe")  # add one recipe by default
        self.addRecipe_pushButton.clicked.connect(lambda: self.configManager.addRecipe("recipe"))

    def _addRecipe(self, recipe_name: str):
        self.scan_recipe_comboBox.addItem(recipe_name)
        self.selectRecipe_comboBox.addItem(recipe_name)
        self.selectRecipe_comboBox.setCurrentIndex(self.selectRecipe_comboBox.count()-1)
        self._show_recipe_combobox()

        self.recipeDict[recipe_name] = {}  # order of creation matter
        self.recipeDict[recipe_name]['recipeManager'] = RecipeManager(self, recipe_name)
        self.recipeDict[recipe_name]['rangeManager'] = RangeManager(self, recipe_name)
        self.recipeDict[recipe_name]['parameterManager'] = ParameterManager(self, recipe_name)

    def _removeRecipe(self, recipe_name: str):  # order of creation matter
        test = self.recipeDict.pop(recipe_name)
        test['recipeManager']._removeTree()

        index = self.scan_recipe_comboBox.findText(recipe_name)  # assert no duplicate name
        self.scan_recipe_comboBox.removeItem(index)
        self.selectRecipe_comboBox.removeItem(index)
        self._show_recipe_combobox()

    def _show_recipe_combobox(self):
        dataSet_id = len(self.configManager.config.keys())
        if dataSet_id > 1:
            self.scan_recipe_comboBox.show()
            self.selectRecipe_comboBox.show()
        else:
            self.scan_recipe_comboBox.hide()
            self.selectRecipe_comboBox.hide()

    def _clearRecipe(self):
        for recipe_name in list(self.recipeDict.keys()):
            self._removeRecipe(recipe_name)

        self.recipeDict.clear()  # remove recipe from gui with __del__ in recipeManager
        self.scan_recipe_comboBox.clear()

    def dropEvent(self, event):
        """ Set parameter if drop compatible variable onto scanner (excluding recipe area) """
        filename = event.mimeData().urls()[0].toLocalFile()
        self.configManager.import_configPars(filename)

        qwidget_children = self.findChildren(QtWidgets.QWidget)
        for widget in qwidget_children:
            widget.setGraphicsEffect(None)

    def dragEnterEvent(self, event):
        """ Only accept config file (url) and parameter from controlcenter """
        if event.mimeData().hasUrls():
            event.accept()

            qwidget_children = self.findChildren(QtWidgets.QWidget)
            for widget in qwidget_children:
                shadow = QtWidgets.QGraphicsColorizeEffect()
                shadow.setColor(QtGui.QColor(20,20,20))
                shadow.setStrength(1)
                widget.setGraphicsEffect(shadow)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        qwidget_children = self.findChildren(QtWidgets.QWidget)
        for widget in qwidget_children:
            widget.setGraphicsEffect(None)

    def closeEvent(self, event):
        """ This function does some steps before the window is really killed """
        # Stop ongoing scan
        if self.scanManager.isStarted() :
            self.scanManager.stop()

        # Stop datamanager timer
        self.dataManager.timer.stop()

        # Delete reference of this window in the control center
        self.mainGui.clearScanner()
        for recipe in self.recipeDict.values():
            recipe['rangeManager'].displayParameter.close()
        self.figureManager.displayScan.close()

    def setStatus(self, message: str, timeout: int = 0, stdout: bool = True):
        """ Modify the message displayed in the status bar and add error message to logger """
        self.statusBar.showMessage(message, msecs=timeout)
        if not stdout: print(message, file=sys.stderr)


    def setLineEditBackground(self, obj, state: str):
        """ Function used to set the background color of a QLineEdit widget,
        based on its editing state """

        if state == 'synced':
            color='#D2FFD2' # vert
        if state == 'edited':
            color='#FFE5AE' # orange

        obj.setStyleSheet("QLineEdit:enabled {background-color: %s; font-size: 9pt}" % color)





def cleanString(name: str) -> str:
    """ This function clears the given name from special characters """
    for character in r'*."/\[]:;|, ':
        name = name.replace(character, '')

    return name
