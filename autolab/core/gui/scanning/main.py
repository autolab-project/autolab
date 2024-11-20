# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 22:08:29 2019

@author: qchat
"""
from typing import List
import os
import sys
import shutil
from functools import partial
from collections import OrderedDict

from qtpy import QtWidgets, QtCore, uic, QtGui

from .config import ConfigManager
from .figure import FigureManager
from .parameter import ParameterManager
from .recipe import RecipeManager
from .scan import ScanManager
from .data import DataManager
from ..icons import icons
from ..GUI_instances import openVariablesMenu, openPlotter
from ...paths import PATHS
from ...utilities import boolean, SUPPORTED_EXTENSION
from ...config import get_scanner_config, load_config, change_autolab_config


class Scanner(QtWidgets.QMainWindow):

    def __init__(self, parent: QtWidgets.QMainWindow):

        self.mainGui = parent

        # Configuration of the window
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'interface.ui')
        uic.loadUi(ui_path, self)
        self.setWindowTitle("AUTOLAB - Scanner")
        self.setWindowIcon(icons['scanner'])
        self.splitter.setSizes([500, 700])  # Set the width of the two main widgets
        self.setAcceptDrops(True)
        self.recipeDict = {}
        self._append = False  # option for import config
        self._copy_step_info = None  # used by tree (in recipe) for copy paste step

        # Loading of the different centers
        self.figureManager = FigureManager(self)
        self.scanManager = ScanManager(self)
        self.dataManager = DataManager(self)
        self.configManager = ConfigManager(self)

        # Configuration menu
        configMenu = self.menuBar.addMenu('Configuration')

        self.importAction = configMenu.addAction('Import configuration')
        self.importAction.setIcon(icons['import'])
        self.importAction.triggered.connect(self.importActionClicked)
        self.importAction.setStatusTip("Import configuration file")

        self.openRecentMenu = configMenu.addMenu('Import recent configuration')
        self.populateOpenRecent()

        configMenu.addSeparator()

        exportAction = configMenu.addAction('Export current configuration')
        exportAction.setIcon(icons['export'])
        exportAction.triggered.connect(self.exportActionClicked)
        exportAction.setStatusTip("Export current configuration file")

        # Edition menu
        editMenu = self.menuBar.addMenu('Edit')
        self.undo = editMenu.addAction('Undo')
        self.undo.setIcon(icons['undo'])
        self.undo.setShortcut(QtGui.QKeySequence("Ctrl+Z"))
        self.undo.triggered.connect(self.configManager.undoClicked)
        self.undo.setEnabled(False)
        self.undo.setStatusTip("Revert recipe changes")
        self.redo = editMenu.addAction('Redo')
        self.redo.setIcon(icons['redo'])
        self.redo.setShortcut(QtGui.QKeySequence("Ctrl+Y"))
        self.redo.triggered.connect(self.configManager.redoClicked)
        self.redo.setEnabled(False)
        self.redo.setStatusTip("Reapply recipe changes")

        guiMenu = self.menuBar.addMenu('Panels')

        plotAction = guiMenu.addAction('Plotter')
        plotAction.setIcon(icons['plotter'])
        plotAction.triggered.connect(lambda: openPlotter(has_parent=True))
        plotAction.setStatusTip('Open the plotter in another window')

        variablesMenuAction = guiMenu.addAction('Variables')
        variablesMenuAction.setIcon(icons['variables'])
        variablesMenuAction.triggered.connect(lambda: openVariablesMenu(True))
        variablesMenuAction.setStatusTip("Open the variable menu in another window")

        self.configManager.addRecipe("recipe")  # add one recipe by default
        self.configManager.undoClicked() # avoid false history
        self.setStatus("")
        self.addRecipe_pushButton.clicked.connect(
            lambda: self.configManager.addRecipe("recipe"))

        self.selectRecipe_comboBox.activated.connect(self._updateSelectParameter)

        # Save button configuration
        self.save_pushButton.clicked.connect(self.saveButtonClicked)
        self.save_pushButton.setEnabled(False)
        self.save_all_pushButton.clicked.connect(self.saveAllButtonClicked)
        self.save_all_pushButton.setEnabled(False)

        # Clear button configuration
        self.clear_pushButton.clicked.connect(self.clear)
        self.clear_pushButton.setEnabled(False)

        self.variable_x2_comboBox.hide()
        self.label_scan_2D.hide()

        for splitter in (self.splitter, self.splitterGraph):
            for i in range(splitter.count()):
                handle = splitter.handle(i)
                handle.setStyleSheet("background-color: #DDDDDD;")
                handle.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            obj.setStyleSheet("background-color: #AAAAAA;")  # Hover color
        elif event.type() == QtCore.QEvent.Leave:
            obj.setStyleSheet("background-color: #DDDDDD;")  # Normal color
        return super().eventFilter(obj, event)

    def populateOpenRecent(self):
        """ https://realpython.com/python-menus-toolbars/#populating-python-menus-dynamically """
        self.openRecentMenu.clear()

        if os.path.exists(PATHS['history_config']):
            with open(PATHS['history_config'], 'r') as f:
                filenames = f.readlines()
            for filename in reversed(filenames):
                filename = filename.rstrip('\n')
                action = QtWidgets.QAction(filename, self)
                action.setIcon(icons['import'])
                action.setEnabled(os.path.exists(filename))
                action.triggered.connect(
                    partial(self.configManager.import_configPars, filename))
                self.openRecentMenu.addAction(action)

        self.openRecentMenu.addSeparator()
        action = QtWidgets.QAction('Clear list', self)
        action.setIcon(icons['remove'])
        action.triggered.connect(self.clearOpenRecent)
        self.openRecentMenu.addAction(action)

    def addOpenRecent(self, filename: str):

        if not os.path.exists(PATHS['history_config']):
            with open(PATHS['history_config'], 'w') as f:
                f.write(filename + '\n')
        else:
            with open(PATHS['history_config'], 'r') as f:
                lines = f.readlines()
            lines.append(filename)
            lines = [line.rstrip('\n')+'\n' for line in lines]
            lines = list(reversed(list(dict.fromkeys(reversed(lines)))))  # unique names
            lines = lines[-10:]
            with open(PATHS['history_config'], 'w') as f:
                f.writelines(lines)

        self.populateOpenRecent()

    def clearOpenRecent(self):
        if os.path.exists(PATHS['history_config']):
            try: os.remove(PATHS['history_config'])
            except: pass

        self.populateOpenRecent()

    def clear(self):
        """ This reset any recorded data, and the GUI accordingly """
        self.dataManager.datasets = []
        self.figureManager.clearData()
        self.figureManager.figMap.hide()
        self.figureManager.fig.show()
        self.figureManager.setLabel("x", " ")
        self.figureManager.setLabel("y", " ")
        self.frameAxis.show()
        self.variable_x_comboBox.clear()
        self.variable_x2_comboBox.clear()
        self.variable_y_comboBox.clear()
        self.variable_x2_checkBox.show()
        self.data_comboBox.clear()
        self.data_comboBox.hide()
        self.save_pushButton.setEnabled(False)
        self.save_all_pushButton.setEnabled(False)
        self.clear_pushButton.setEnabled(False)
        self.save_pushButton.setText('Save scan1')
        self.progressBar.setValue(0)
        self.progressBar.setStyleSheet("")
        self.displayScanData_pushButton.hide()
        self.sendScanData_pushButton.hide()
        self.dataframe_comboBox.clear()
        self.dataframe_comboBox.addItems(["Scan"])
        self.dataframe_comboBox.hide()
        self.scan_recipe_comboBox.setCurrentIndex(0)
        self.scan_recipe_comboBox.hide()
        self.refresh_widget(self.clear_pushButton)

    @staticmethod
    def refresh_widget(widget: QtWidgets.QWidget):
        """ Avoid intermediate disabled state when badly refreshed """
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def _addRecipe(self, recipe_name: str):
        """ Adds recipe to managers. Called by configManager """
        self._update_recipe_combobox()  # recreate all and display first index
        self.selectRecipe_comboBox.setCurrentIndex(
            self.selectRecipe_comboBox.count()-1)  # display last index

        self.recipeDict[recipe_name] = {}  # order of creation matter
        self.recipeDict[recipe_name]['recipeManager'] = RecipeManager(self, recipe_name)
        self.recipeDict[recipe_name]['parameterManager'] = OrderedDict()

        for parameter in self.configManager.parameterList(recipe_name):
            self._addParameter(recipe_name, parameter['name'])

    def _removeRecipe(self, recipe_name: str):  # order of creation matter
        """ Removes recipe from managers. Called by configManager and self """
        test = self.recipeDict.pop(recipe_name)
        test['recipeManager']._removeWidget()
        self._update_recipe_combobox()
        self._updateSelectParameter()

    def _activateRecipe(self, recipe_name: str, state: bool):
        """ Activates/Deactivates an existing recipe. Called by configManager and recipeManager """
        active = bool(state)
        self._update_recipe_combobox()
        self.recipeDict[recipe_name]['recipeManager']._activateTree(active)

    def _update_recipe_combobox(self):
        """ Shows recipe combobox if multi recipes else hide """
        prev_index = self.selectRecipe_comboBox.currentIndex()

        self.selectRecipe_comboBox.clear()
        self.selectRecipe_comboBox.addItems(self.configManager.recipeNameList())

        new_index = min(prev_index, self.selectRecipe_comboBox.count()-1)
        self.selectRecipe_comboBox.setCurrentIndex(new_index)

        dataSet_id = len(self.configManager.recipeNameList())
        if dataSet_id > 1:
            self.selectRecipe_comboBox.show()
            self.label_selectRecipeParameter.show()
        else:
            self.selectRecipe_comboBox.hide()
            # OPTIMIZE: seperate condition for label
            recipe_name = self.selectRecipe_comboBox.currentText()
            if (recipe_name != ""
                    and len(self.configManager.parameterList(recipe_name)) > 1):
                self.selectParameter_comboBox.show()
            else:
                self.label_selectRecipeParameter.hide()

    def _clearRecipe(self):
        """ Clears recipes from managers. Called by configManager """
        for recipe_name in list(self.recipeDict):
            self._removeRecipe(recipe_name)

    def _addParameter(self, recipe_name: str, param_name: str):
        """ Adds parameter to managers. Called by configManager and self """
        new_ParameterManager = ParameterManager(self, recipe_name, param_name)
        self.recipeDict[recipe_name]['parameterManager'][param_name] = new_ParameterManager

        layoutAll = self.recipeDict[recipe_name]['recipeManager']._layoutAll
        layoutAll.insertWidget(
            layoutAll.count()-1, new_ParameterManager.mainFrame, stretch=0)

        self._updateSelectParameter()
        self.selectParameter_comboBox.setCurrentIndex(
            self.selectParameter_comboBox.count()-1)

    def _removeParameter(self, recipe_name: str, param_name: str):
        """ Removes parameter from managers. Called by configManager """
        test = self.recipeDict[recipe_name]['parameterManager'].pop(param_name)
        test._removeWidget()

        self._updateSelectParameter()

    def _updateSelectParameter(self):
        """ Updates selectParameter_comboBox. Called by configManager and self """
        recipe_name = self.selectRecipe_comboBox.currentText()

        prev_index = self.selectParameter_comboBox.currentIndex()
        if prev_index == -1: prev_index = 0

        self.selectParameter_comboBox.clear()
        if recipe_name != "":
            self.selectParameter_comboBox.addItems(
                self.configManager.parameterNameList(recipe_name))
            self.selectParameter_comboBox.setCurrentIndex(prev_index)

        if self.selectParameter_comboBox.currentText() == "":
            self.selectParameter_comboBox.setCurrentIndex(
                self.selectParameter_comboBox.count()-1)

        #Shows parameter combobox if multi parameters else hide
        if (recipe_name != ""
                and len(self.configManager.parameterList(recipe_name)) > 1):
            self.selectParameter_comboBox.show()
            self.label_selectRecipeParameter.show()
        else:
            self.selectParameter_comboBox.hide()
            if not self.selectRecipe_comboBox.isVisible():
                self.label_selectRecipeParameter.hide()

    def _refreshParameterRange(self, recipe_name: str, param_name: str,
                               newName: str = None):
        """ Updates parameterManager with new parameter name """
        recipeDictParam = self.recipeDict[recipe_name]['parameterManager']

        if newName is None:
            recipeDictParam[param_name].refresh()
        else:
            if param_name in recipeDictParam:
                recipeDictParam[newName] = recipeDictParam.pop(param_name)
                recipeDictParam[newName].changeName(newName)
                recipeDictParam[newName].refresh()
            else:
                print(f"Error: Can't refresh parameter '{param_name}', not found in recipeDictParam '{recipeDictParam}'",
                      file=sys.stderr)

        self._updateSelectParameter()

    def _refreshRecipe(self, recipe_name: str):
        self.recipeDict[recipe_name]['recipeManager'].refresh()

    def _resetRecipe(self):
        """ Resets recipe """
        self._clearRecipe()  # before everything to have access to recipe and del it

        for recipe_name in self.configManager.recipeNameList():
            self._addRecipe(recipe_name)
            for parameterManager in self.recipeDict[recipe_name]['parameterManager'].values():
                parameterManager.refresh()
            self._refreshRecipe(recipe_name)

    def importActionClicked(self):
        """ Prompts the user for a configuration filename,
        and import the current scan configuration from it """

        class ImportDialog(QtWidgets.QDialog):

            def __init__(self, parent: QtWidgets.QMainWindow, append: bool):

                super().__init__(parent)
                self.setWindowTitle("Import AUTOLAB configuration file")
                self.setWindowModality(QtCore.Qt.ApplicationModal)  # this block GUI interaction (easier than checking every interaction possible to avoid bugs if change recipe or have multiple dialogs)

                self.append = append

                urls = [
                    QtCore.QUrl.fromLocalFile(QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.HomeLocation)),
                    QtCore.QUrl.fromLocalFile(QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DesktopLocation)),
                    QtCore.QUrl.fromLocalFile(QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)),
                    QtCore.QUrl.fromLocalFile(QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DownloadLocation)),
                    QtCore.QUrl.fromLocalFile(os.environ['TEMP']),
                ]

                layout = QtWidgets.QVBoxLayout(self)
                self.setLayout(layout)

                file_dialog = QtWidgets.QFileDialog(self, QtCore.Qt.Widget)
                file_dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog)
                file_dialog.setSidebarUrls(urls)
                file_dialog.setWindowFlags(file_dialog.windowFlags() & ~QtCore.Qt.Dialog)
                file_dialog.setDirectory(PATHS['last_folder'])
                file_dialog.setNameFilters(["AUTOLAB configuration file (*.conf)", "Any Files (*)"])
                layout.addWidget(file_dialog)

                appendCheck = QtWidgets.QCheckBox('Append', self)
                appendCheck.setChecked(append)
                appendCheck.stateChanged.connect(self.appendCheckChanged)
                layout.addWidget(appendCheck)

                self.exec_ = file_dialog.exec_
                self.selectedFiles = file_dialog.selectedFiles

            def appendCheckChanged(self, event):
                self.append = event

            def closeEvent(self, event):
                for children in self.findChildren(QtWidgets.QWidget):
                    children.deleteLater()

                super().closeEvent(event)

        main_dialog = ImportDialog(self, self._append)
        main_dialog.show()

        once_or_append = True
        while once_or_append:
            if main_dialog.exec_() == QtWidgets.QInputDialog.Accepted:
                filenames = main_dialog.selectedFiles()

                self._append = main_dialog.append
                once_or_append = self._append and len(filenames) != 0

                for filename in filenames:
                    if filename != '':
                        self.configManager.import_configPars(
                            filename, append=self._append)
            else:
                once_or_append = False

        main_dialog.deleteLater()

    def exportActionClicked(self):
        """ Prompts the user for a configuration file path,
        and export the current scan configuration in it """
        filename = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export AUTOLAB configuration file",
            os.path.join(PATHS['last_folder'], 'config.conf'),
            "AUTOLAB configuration file (*.conf);;All Files (*)")[0]

        if filename != '':
            path = os.path.dirname(filename)
            PATHS['last_folder'] = path

            try:
                self.configManager.export(filename)
                self.setStatus(
                    f"Current configuration successfully saved at {filename}",
                    5000)
            except Exception as e:
                self.setStatus(f"An error occured: {str(e)}", 10000, False)
            else:
                self.addOpenRecent(filename)

    def saveAllButtonClicked(self):
        self._saveData(self.dataManager.datasets)

    def saveButtonClicked(self):
        self._saveData([self.dataManager.getLastSelectedDataset()])

    def _saveData(self, all_data: List[dict]):
        """ This function is called when the save button is clicked.
        It asks a path and starts the procedure to save the data """
        filename = QtWidgets.QFileDialog.getSaveFileName(
            self,  caption="Save data",
            directory=PATHS['last_folder'],
            filter=SUPPORTED_EXTENSION)[0]
        path = os.path.dirname(filename)

        save_folder, extension = os.path.splitext(filename)

        if path != '':
            PATHS['last_folder'] = path
            self.setStatus('Saving data...', 5000)

            for scanset in all_data:
                i = self.dataManager.datasets.index(scanset)
                scan_name = f'scan{i+1}'

                if len(all_data) == 1:
                    scan_filename = save_folder
                    new_configname = f'{save_folder}.conf'
                else:
                    scan_filename = f'{save_folder}_{scan_name}'
                    new_configname = f'{save_folder}_{scan_name}.conf'

                for recipe_name in scanset:
                    dataset = scanset[recipe_name]

                    if len(scanset) == 1:
                        filename_recipe = f'{scan_filename}{extension}'
                    else:
                        filename_recipe = f'{scan_filename}_{recipe_name}{extension}'
                    dataset.save(filename_recipe)

                scanset.saved = True
                scanner_config = get_scanner_config()
                save_config = boolean(scanner_config["save_config"])

                if save_config:
                    config_name = os.path.join(
                        os.path.dirname(dataset.folder_dataset_temp), 'config.conf')

                    if os.path.exists(config_name):
                        shutil.copy(config_name, new_configname)
                    else:
                        if scanset is not self.dataManager.getLastDataset():
                            print("Warning: Can't find config for this dataset, save latest config instead",
                                  file=sys.stderr)
                        self.configManager.export(new_configname)  # BUG: it saves latest config instead of dataset config because no record available of previous config. (I did try to put back self.config to dataset but config changes with new dataset (copy doesn't help and deepcopy not possible)

                    self.addOpenRecent(new_configname)

                if len(all_data) == 1 and boolean(scanner_config["save_figure"]):
                        self.figureManager.save(filename)

            if len(all_data) == 1:
                self.setStatus(
                    f'{scan_name} successfully saved in {filename}', 5000)
            else:
                self.setStatus(
                    f'All scans successfully saved as {save_folder}_[...].txt', 5000)

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

        scanner_config = get_scanner_config()
        ask_close = boolean(scanner_config["ask_close"])
        if ask_close and not all([scanset.saved for scanset in self.dataManager.datasets]):
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Scanner")
            msg_box.setText("Some data hasn't been saved, close scanner anyway?")
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes
                                       | QtWidgets.QMessageBox.No)

            checkbox = QtWidgets.QCheckBox("Don't ask again")
            msg_box.setCheckBox(checkbox)

            msg_box.show()
            res = msg_box.exec_()

            autolab_config = load_config('autolab_config')
            autolab_config['scanner']['ask_close'] = str(not checkbox.isChecked())
            change_autolab_config(autolab_config)

            if res == QtWidgets.QMessageBox.No:
                event.ignore()  # Prevent the window from closing
                return None

        self.mainGui.clearScanner()

        for recipe in self.recipeDict.values():
            for parameterManager in recipe['parameterManager'].values():
                parameterManager.close()

        self.figureManager.close()

        # Remove scan variables from VARIABLES
        try: self.configManager.updateVariableConfig([])
        except: pass

        for children in self.findChildren(QtWidgets.QWidget):
            children.deleteLater()

        super().closeEvent(event)

    def setStatus(self, message: str, timeout: int = 0, stdout: bool = True):
        """ Modifies displayed message in status bar and adds error message to logger """
        self.statusBar.showMessage(message, timeout)
        if not stdout: print(message, file=sys.stderr)
