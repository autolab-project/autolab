# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 22:08:29 2019

@author: qchat
"""
import os
import sys
from collections import OrderedDict

from qtpy import QtWidgets, uic, QtGui

from .config import ConfigManager
from .figure import FigureManager
from .parameter import ParameterManager
from .recipe import RecipeManager
from .scan import ScanManager
from .data import DataManager
from .scanrange import RangeManager
from ..icons import icons


class Scanner(QtWidgets.QMainWindow):

    def __init__(self, mainGui: QtWidgets.QMainWindow):

        self.mainGui = mainGui

        # Configuration of the window
        QtWidgets.QMainWindow.__init__(self)
        ui_path = os.path.join(os.path.dirname(__file__), 'interface.ui')
        uic.loadUi(ui_path, self)
        self.setWindowTitle("AUTOLAB Scanner")
        self.setWindowIcon(QtGui.QIcon(icons['scanner']))
        self.splitter.setSizes([500, 700])  # Set the width of the two main widgets
        self.setAcceptDrops(True)
        self.recipeDict = {}

        # Loading of the different centers
        self.figureManager = FigureManager(self)
        self.scanManager = ScanManager(self)
        self.dataManager = DataManager(self)
        self.configManager = ConfigManager(self)

        self.configManager.addRecipe("recipe")  # add one recipe by default
        self.configManager.undoClicked() # avoid false history
        self.setStatus("")
        self.addRecipe_pushButton.clicked.connect(lambda: self.configManager.addRecipe("recipe"))

        self.selectRecipe_comboBox.activated.connect(self._updateSelectParameter)

    def _addRecipe(self, recipe_name: str):
        """ Adds recipe to managers. Called by configManager """
        if self.configManager.config[recipe_name]['active']:
            self.scan_recipe_comboBox.addItem(recipe_name)

        self.selectRecipe_comboBox.addItem(recipe_name)
        self.selectRecipe_comboBox.setCurrentIndex(self.selectRecipe_comboBox.count()-1)
        self._show_recipe_combobox()

        self.recipeDict[recipe_name] = {}  # order of creation matter
        self.recipeDict[recipe_name]['recipeManager'] = RecipeManager(self, recipe_name)

        self.recipeDict[recipe_name]['parameterManager'] = OrderedDict()
        self.recipeDict[recipe_name]['rangeManager'] = OrderedDict()

        for parameter in self.configManager.parameterList(recipe_name):
            self._addParameter(recipe_name, parameter['name'])

    def _removeRecipe(self, recipe_name: str):  # order of creation matter
        """ Removes recipe from managers. Called by configManager and self """
        test = self.recipeDict.pop(recipe_name)
        test['recipeManager']._removeWidget()

        index = self.scan_recipe_comboBox.findText(recipe_name)  # assert no duplicate name
        self.scan_recipe_comboBox.removeItem(index)
        index = self.selectRecipe_comboBox.findText(recipe_name)  # assert no duplicate name
        self.selectRecipe_comboBox.removeItem(index)
        self._show_recipe_combobox()

    def _activateRecipe(self, recipe_name: str, state: bool):
        """ Activates/Deactivates an existing recipe. Called by configManager and recipeManager """
        active = bool(state)
        index = self.scan_recipe_comboBox.findText(recipe_name)

        if active:
            if index == -1:
                self.scan_recipe_comboBox.addItem(recipe_name)
        else:
            self.scan_recipe_comboBox.removeItem(index)

        self.recipeDict[recipe_name]['recipeManager']._activateTree(active)

    def _show_recipe_combobox(self):
        """ Shows recipe combobox if multi recipes else hide """
        dataSet_id = len(self.configManager.config.keys())
        if dataSet_id > 1:
            self.scan_recipe_comboBox.show()
            self.selectRecipe_comboBox.show()
        else:
            self.scan_recipe_comboBox.hide()
            self.selectRecipe_comboBox.hide()

    def _clearRecipe(self):
        """ Clears recipes from managers. Called by configManager """
        for recipe_name in list(self.recipeDict.keys()):
            self._removeRecipe(recipe_name)

        self.recipeDict.clear()  # remove recipe from gui with __del__ in recipeManager
        self.scan_recipe_comboBox.clear()
        self.selectRecipe_comboBox.clear()
        self.selectParameter_comboBox.clear()

    def _addParameter(self, recipe_name: str, param_name: str):
        """ Adds parameter to managers. Called by configManager and self """
        new_ParameterManager = ParameterManager(self, recipe_name, param_name)
        self.recipeDict[recipe_name]['parameterManager'][param_name] = new_ParameterManager

        new_RangeManager = RangeManager(self, recipe_name, param_name)
        self.recipeDict[recipe_name]['rangeManager'][param_name] = new_RangeManager

        layoutAll = self.recipeDict[recipe_name]['recipeManager']._layoutAll
        layoutAll.insertWidget(len(layoutAll)-1, new_ParameterManager.frameParameter)
        layoutAll.insertWidget(len(layoutAll)-1, new_RangeManager.frameScanRange)

        self._updateSelectParameter()
        self.selectParameter_comboBox.setCurrentIndex(self.selectParameter_comboBox.count()-1)

    def _removeParameter(self, recipe_name: str, param_name: str):
        """ Removes parameter from managers. Called by configManager """
        test = self.recipeDict[recipe_name]['parameterManager'].pop(param_name)
        test._removeWidget()
        test = self.recipeDict[recipe_name]['rangeManager'].pop(param_name)
        test._removeWidget()

        self._updateSelectParameter()

    def _updateSelectParameter(self):
        """ Updates selectParameter_comboBox. Called by configManager and self """
        recipe_name = self.selectRecipe_comboBox.currentText()

        prev_index = self.selectParameter_comboBox.currentIndex()
        if prev_index == -1: prev_index = 0

        self.selectParameter_comboBox.clear()
        self.selectParameter_comboBox.addItems(self.configManager.parameterNameList(recipe_name))
        self.selectParameter_comboBox.setCurrentIndex(prev_index)

        if self.selectParameter_comboBox.currentText() == "":
            self.selectParameter_comboBox.setCurrentIndex(self.selectParameter_comboBox.count()-1)

        self._show_parameter_combobox()

    def _show_parameter_combobox(self):
        """ Shows parameter combobox if multi parameters else hide """
        recipe_name = self.selectRecipe_comboBox.currentText()

        if len(self.configManager.parameterList(recipe_name)) > 1:
            self.selectParameter_comboBox.show()
        else:
            self.selectParameter_comboBox.hide()

    def dropEvent(self, event):
        """ Imports config file if event has url of a file """
        filename = event.mimeData().urls()[0].toLocalFile()
        self.configManager.import_configPars(filename)

        qwidget_children = self.findChildren(QtWidgets.QWidget)
        for widget in qwidget_children:
            widget.setGraphicsEffect(None)

    def dragEnterEvent(self, event):
        """ Only accept config file (url) """
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
        """ Does some steps before the window is really killed """
        # Stop ongoing scan
        if self.scanManager.isStarted():
            self.scanManager.stop()

        # Stop datamanager timer
        self.dataManager.timer.stop()

        # Delete reference of this window in the control center
        self.mainGui.clearScanner()
        for recipe in self.recipeDict.values():
            for rangeManager in recipe['rangeManager'].values():
                rangeManager.displayParameter.close()

        self.figureManager.displayScan.close()
        self.figureManager.fig.close()  # prevent crash without traceback when reopenning scanner multiple times
        self.figureManager.figMap.close()

    def setStatus(self, message: str, timeout: int = 0, stdout: bool = True):
        """ Modifies displayed message in status bar and adds error message to logger """
        self.statusBar.showMessage(message, msecs=timeout)
        if not stdout: print(message, file=sys.stderr)

    def setLineEditBackground(self, obj, state: str):
        """ Sets background color of a QLineEdit widget based on its editing state """
        if state == 'synced': color='#D2FFD2' # vert
        if state == 'edited': color='#FFE5AE' # orange

        obj.setStyleSheet("QLineEdit:enabled {background-color: %s; font-size: 9pt}" % color)
