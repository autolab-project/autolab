# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:08:45 2019

@author: qchat
"""

import os
import time
import math as m
import threading
from collections import OrderedDict
from queue import Queue
from itertools import product

import numpy as np
from qtpy import QtCore, QtWidgets

from ..GUI_utilities import qt_object_exists, MyInputDialog, MyFileDialog
from ..GUI_instances import instances
from ...paths import PATHS
from ...variables import eval_variable, set_variable, has_eval
from ...utilities import create_array


class ScanManager:
    """ Manage a scan using a dedicated thread """

    def __init__(self, gui: QtWidgets.QMainWindow):
        self.gui = gui

        # Start / Stop button configuration
        self.gui.start_pushButton.clicked.connect(self.startButtonClicked)
        self.gui.stop_pushButton.clicked.connect(self.stopButtonClicked)
        self.gui.stop_pushButton.setEnabled(False)

        # Pause / Resume button configuration
        self.gui.pause_pushButton.clicked.connect(self.pauseButtonClicked)
        self.gui.pause_pushButton.setEnabled(False)

        # Progress bar configuration
        self.gui.progressBar.setMinimum(0)
        self.gui.progressBar.setValue(0)

        # Thread
        self.thread = None
        self.main_dialog = None

    # START AND STOP
    #############################################################################

    def startButtonClicked(self):
        """ Called when the start button is pressed.
        Do the expected action """
        if not self.isStarted():
            self.start()

    def stopButtonClicked(self):
        """ Called when the stop button is pressed.
        Do the expected action """
        if self.isStarted():
            self.stop()

    def isStarted(self):
        """ Returns True or False whether the scan is currently running or not """
        return self.thread is not None

    def start(self):
        """ Starts a scan """
        try:
            self.gui.configManager.checkConfig()  #  raise error if config not valid
            config = self.gui.configManager.config
        except Exception as e:
            self.gui.setStatus(f'ERROR The scan cannot start with the current configuration: {str(e)}', 10000, False)
            return None

        # Should not be possible
        if self.thread is not None:
            self.gui.setStatus('ERROR: A scan thread already exists!', 10000, False)
            try: self.thread.finished()
            except: pass
            self.thread = None
            return None

        # Only if current config is valid to start a scan

        # Pause monitors if option selected in monitors
        for var_id in set([id(step['element'])
                       for recipe in config.values()
                       for step in recipe['recipe']+recipe['parameter']]):
            if var_id in instances['monitors']:
                monitor = instances['monitors'][var_id]
                if (monitor.pause_on_scan
                        and not monitor.monitorManager.isPaused()):
                    monitor.pauseButtonClicked()

        # Prepare a new dataset in the datacenter
        self.gui.dataManager.newDataset(config)

        # put dataset id onto the combobox and associate data to it
        dataSet_id = len(self.gui.dataManager.datasets)
        self.gui.data_comboBox.addItem(f'scan{dataSet_id}')
        self.gui.data_comboBox.setCurrentIndex(int(dataSet_id)-1)  # trigger the currentIndexChanged event but don't trigger activated

        # Start a new thread
        ## Opening
        self.thread = ScanThread(self.gui.dataManager.queue, config)
        ## Signal connections
        self.thread.errorSignal.connect(self.error)
        self.thread.userSignal.connect(self.handler_user_input)

        self.thread.startParameterSignal.connect(
            lambda recipe_name, param_name: self.setParameterProcessingState(
                recipe_name, param_name, 'started'))
        self.thread.finishParameterSignal.connect(
            lambda recipe_name, param_name: self.setParameterProcessingState(
                recipe_name, param_name, 'finished'))
        self.thread.parameterCompletedSignal.connect(
            lambda recipe_name, param_name: self.resetParameterProcessingState(
                recipe_name, param_name))

        self.thread.startStepSignal.connect(
            lambda recipe_name, stepName: self.setStepProcessingState(
                recipe_name, stepName, 'started'))
        self.thread.finishStepSignal.connect(
            lambda recipe_name, stepName: self.setStepProcessingState(
                recipe_name, stepName, 'finished'))
        self.thread.recipeCompletedSignal.connect(
            lambda recipe_name: self.resetStepsProcessingState(recipe_name))
        self.thread.scanCompletedSignal.connect(self.scanCompleted)

        self.thread.finished.connect(self.finished)

        # Starting
        self.thread.start()

        # Start data center timer
        self.gui.dataManager.timer.start()

        # Update gui
        self.gui.start_pushButton.setEnabled(False)
        self.gui.stop_pushButton.setEnabled(True)
        self.gui.pause_pushButton.setEnabled(True)
        self.gui.clear_pushButton.setEnabled(False)
        self.gui.progressBar.setValue(0)
        self.gui.progressBar.setStyleSheet("")
        self.gui.importAction.setEnabled(False)
        self.gui.openRecentMenu.setEnabled(False)
        self.gui.undo.setEnabled(False)
        self.gui.redo.setEnabled(False)
        self.gui.setStatus('Scan started!', 5000)
        self.gui.refresh_widget(self.gui.start_pushButton)

    def handler_user_input(self, stepInfos: dict):
        unit = stepInfos['element'].unit
        name = stepInfos['name']

        if unit in ("open-file", "save-file"):

            if unit == "open-file":
                self.main_dialog = MyFileDialog(self.gui, name,
                                                QtWidgets.QFileDialog.AcceptOpen)
                self.main_dialog.show()

                if self.main_dialog.exec_() == QtWidgets.QInputDialog.Accepted:
                    filename = self.main_dialog.selectedFiles()[0]
                else:
                    filename = ''

            elif unit == "save-file":
                self.main_dialog = MyFileDialog(self.gui, name,
                                                QtWidgets.QFileDialog.AcceptSave)
                self.main_dialog.show()

                if self.main_dialog.exec_() == QtWidgets.QInputDialog.Accepted:
                    filename = self.main_dialog.selectedFiles()[0]
                else:
                    filename = ''

            if filename != '':
                path = os.path.dirname(filename)
                PATHS['last_folder'] = path

            if qt_object_exists(self.main_dialog): self.main_dialog.deleteLater()
            if self.thread is not None: self.thread.user_response = filename

        elif unit == 'user-input':
            self.main_dialog = MyInputDialog(self.gui, name)
            self.main_dialog.show()

            if self.main_dialog.exec_() == QtWidgets.QInputDialog.Accepted:
                response = self.main_dialog.textValue()
            else:
                response = ''

            if qt_object_exists(self.main_dialog): self.main_dialog.deleteLater()

            if has_eval(response):
                try:
                    response = eval_variable(response)
                except Exception as e:
                    self.thread.errorSignal.emit(e)
                    self.thread.stopFlag.set()

            if self.thread is not None: self.thread.user_response = response
        else:
            if self.thread is not None: self.thread.user_response = f"Unknown unit '{unit}'"

    def scanCompleted(self):
        if not qt_object_exists(self.gui.progressBar):
            return None

        if self.thread.stopFlag.is_set():
            self.gui.progressBar.setStyleSheet(
                "QProgressBar::chunk {background-color: red;}")
            # self.gui.setStatus('Scan stopped!', 5000)  # not good because hide error message
        else:
            self.gui.setStatus('Scan finished!', 5000)
            self.gui.progressBar.setMaximum(1)
            self.gui.progressBar.setValue(1)
            self.gui.progressBar.setStyleSheet("")

            # Start monitors if option selected in monitors
            for var_id in set([id(step['element'])
                           for recipe in self.thread.config.values()
                           for step in recipe['recipe']+recipe['parameter']]):
                if var_id in instances['monitors']:
                    monitor = instances['monitors'][var_id]
                    if (monitor.start_on_scan
                            and monitor.monitorManager.isPaused()):
                        monitor.pauseButtonClicked()

    def setStepProcessingState(self, recipe_name: str, stepName: str, state: str):
        self.gui.recipeDict[recipe_name]['recipeManager'].setStepProcessingState(stepName, state)

    def resetStepsProcessingState(self, recipe_name: str):
        self.gui.recipeDict[recipe_name]['recipeManager'].resetStepsProcessingState()

    def setParameterProcessingState(self, recipe_name: str, param_name: str, state: str):
        self.gui.recipeDict[recipe_name]['parameterManager'][param_name].setProcessingState(state)

    def resetParameterProcessingState(self, recipe_name: str, param_name: str):
        self.gui.recipeDict[recipe_name]['parameterManager'][param_name].setProcessingState('idle')

    def stop(self):
        """ Stops manually the scan """
        self.disableContinuousMode()
        self.thread.stopFlag.set()
        self.thread.user_response = 'Close'  # needed to stop scan
        self.resume()
        if self.main_dialog and qt_object_exists(self.main_dialog):
            self.main_dialog.deleteLater()
        self.thread.wait()
    # SIGNALS
    #############################################################################

    def finished(self):
        """ This function is called when the scan thread is finished.
        It restores the GUI in a ready mode, and start a new scan if in
        continuous mode """
        if not qt_object_exists(self.gui.stop_pushButton):
            return None
        self.gui.stop_pushButton.setEnabled(False)
        self.gui.pause_pushButton.setEnabled(False)
        self.gui.clear_pushButton.setEnabled(True)
        self.gui.importAction.setEnabled(True)
        self.gui.openRecentMenu.setEnabled(True)
        self.gui.configManager.updateUndoRedoButtons()
        self.gui.dataManager.timer.stop()
        self.gui.dataManager.sync() # once again to be sure we grabbed every data
        self.thread = None
        self.gui.refresh_widget(self.gui.stop_pushButton)

        if self.isContinuousModeEnabled():
            self.start()
        else:
            self.gui.start_pushButton.setEnabled(True)

    def error(self, error: Exception):
        """ Called if an error occured during the scan.
        It displays it in the status bar """
        self.gui.setStatus(f'Scan error: {error}', 10000, False)


    # CONTINUOUS MODE
    #############################################################################

    def isContinuousModeEnabled(self) -> bool:
        """ Returns True or False whether the continuous scan mode is enabled
        or not """
        return self.gui.continuous_checkBox.isChecked()

    def disableContinuousMode(self):
        """ Disables the continuous scan mode """
        self.gui.continuous_checkBox.setChecked(False)

    # PAUSE
    #############################################################################

    def pauseButtonClicked(self):
        """ Called when the Pause/Resume button is clicked.
        It does the required action """
        if self.isStarted():
            self.resume() if self.isPaused() else self.pause()

    def isPaused(self):
        """ Returns True or False whether the scan is paused or not """
        return (self.thread is not None) and (self.thread.pauseFlag.is_set() is True)

    def pause(self):
        """ Pauses the scan """
        self.thread.pauseFlag.set()
        self.gui.dataManager.timer.stop()
        self.gui.dataManager.sync() # once again to be sure we grabbed every data
        self.gui.pause_pushButton.setText('Resume')

    def resume(self):
        """ Resumes the scan """
        try:
            # One possible error is device closed while scan was paused
            self.gui.configManager.checkConfig()  #  raise error if config not valid
        except Exception as e:
            self.gui.setStatus(f'WARNING The scan cannot resume: {str(e)}', 10000, False)
            return None
        self.thread.pauseFlag.clear()
        self.gui.dataManager.timer.start()
        self.gui.pause_pushButton.setText('Pause')


class ScanThread(QtCore.QThread):
    """ This thread class is dedicated to read the variable,
        and send its data to GUI through a queue """
    # Signals
    userSignal = QtCore.Signal(dict)
    errorSignal = QtCore.Signal(object)

    startParameterSignal = QtCore.Signal(object, object)
    finishParameterSignal = QtCore.Signal(object, object)
    parameterCompletedSignal = QtCore.Signal(object, object)

    startStepSignal = QtCore.Signal(object, object)
    finishStepSignal = QtCore.Signal(object, object)
    recipeCompletedSignal = QtCore.Signal(object)
    scanCompletedSignal = QtCore.Signal()

    def __init__(self, queue: Queue, config: dict):
        super().__init__()
        self.config = config
        self.queue = queue

        self.pauseFlag = threading.Event()
        self.stopFlag = threading.Event()

        self.user_response = None

    def run(self):
        # Start the scan
        for recipe_name in self.config:
            if self.config[recipe_name]['active']: self.execRecipe(recipe_name)

        self.scanCompletedSignal.emit()

    def execRecipe(self, recipe_name: str,
                   initPoint: OrderedDict = None):
        """ Executes a recipe. initPoint is obsolete, was used to add parameters values
        and master-recipe name to a sub-recipe """

        paramValues_list = []


        for parameter in self.config[recipe_name]['parameter']:
            param_name = parameter['name']

            if 'values' in parameter:
                paramValues = parameter['values']
                try:
                    paramValues = eval_variable(paramValues)
                    paramValues = create_array(paramValues)
                except Exception as e:
                    self.errorSignal.emit(e)
                    self.stopFlag.set()
            else:
                startValue, endValue = parameter['range']
                nbpts = parameter['nbpts']
                logScale = parameter['log']

                # Creates the array of values for the parameter
                if logScale:
                    paramValues = np.logspace(m.log10(startValue), m.log10(endValue), nbpts, endpoint=True)
                else:
                    paramValues = np.linspace(startValue, endValue, nbpts, endpoint=True)

            set_variable(param_name, paramValues[0])
            paramValues_list.append(paramValues)

        ID = 0
        # iter over each parameter (do once if no parameter!)
        for i, paramValueList in enumerate(product(*paramValues_list)):

            if not self.stopFlag.is_set():

                if initPoint is None:  # OBSOLETE
                    initPoint = OrderedDict()
                    initPoint[0] = recipe_name

                initPointStep = initPoint.copy()

                try:
                    self._source_of_error = None
                    ID += 1
                    set_variable('ID', ID)

                    for parameter, paramValue in zip(
                            self.config[recipe_name]['parameter'], paramValueList):
                        self._source_of_error = parameter
                        element = parameter['element']
                        param_name = parameter['name']

                        set_variable(param_name, element.type(
                                paramValue) if element is not None else paramValue)

                        # Set the parameter value
                        self.startParameterSignal.emit(recipe_name, param_name)
                        if element is not None: element(paramValue)
                        self.finishParameterSignal.emit(recipe_name, param_name)

                        initPointStep[param_name] = paramValue

                    dataPoint = initPointStep.copy()

                    # Start the recipe
                    dataPoint = self.processStep(
                        recipe_name, dataPoint, initPointStep)
                    # Send the whole data in the queue
                    if not self.stopFlag.is_set(): self.queue.put(dataPoint)

                except Exception as e:
                    # If an error occurs, stop the scan and send an error signal
                    name = self._source_of_error['name']
                    if self._source_of_error['element'] is not None:
                        address = f"='{self._source_of_error['element'].address()}'"
                    else: address = ''

                    try:
                        from pyvisa import VisaIOError
                    except:
                        e = f"In recipe '{recipe_name}' for step '{name}': {e}"
                    else:
                        if str(e) == str(VisaIOError(-1073807339)):
                            e = f"Timeout reached for device {address}. Acquisition time may be too long. If so, you can increase timeout delay in the driver to avoid this error."
                        else:
                            e = f"In recipe '{recipe_name}' for step '{name}': {e}"

                    self.errorSignal.emit(e)
                    self.stopFlag.set()

                # Wait until the scan is no more in pause
                while self.pauseFlag.is_set():
                    time.sleep(0.1)
            else:
                break

        for parameter in self.config[recipe_name]['parameter']:
            self.parameterCompletedSignal.emit(recipe_name, parameter['name'])

    def processStep(self, recipe_name: str,
                    dataPoint: OrderedDict,
                    initPoint: OrderedDict):
        """ Executes the recipe step """
        for stepInfos in self.config[recipe_name]['recipe']:
            self._source_of_error = stepInfos

            if not self.stopFlag.is_set():
                # Process the recipe step
                result = self.processElement(recipe_name, stepInfos, initPoint)

                if result is not None:
                    dataPoint[stepInfos['name']] = result

                # Wait until the scan is no more in pause
                while self.pauseFlag.is_set():
                    time.sleep(0.1)
            else:
                break

        self.recipeCompletedSignal.emit(recipe_name)
        return dataPoint

    def processElement(self, recipe_name: str, stepInfos: dict,
                       initPoint: OrderedDict):
        """ Processes the recipe step """
        element = stepInfos['element']
        stepType = stepInfos['stepType']
        self.startStepSignal.emit(recipe_name, stepInfos['name'])
        result = None

        if stepType == 'measure':
            result = element()
            set_variable(stepInfos['name'], result)
        elif stepType == 'set':
            value = eval_variable(stepInfos['value'])
            if element.type in [bytes] and isinstance(value, str): value = value.encode()
            if element.type in [np.ndarray]: value = create_array(value)
            element(value)
        elif stepType == 'action':
            if stepInfos['value'] is not None:
                # Open dialog for open file, save file or input text
                if isinstance(stepInfos['value'], str) and stepInfos['value'] == '':
                    self.userSignal.emit(stepInfos)
                    while (not self.stopFlag.is_set()
                           and self.user_response is None):
                        time.sleep(0.1)
                    if not self.stopFlag.is_set():
                        element(self.user_response)
                    self.user_response = None
                else:
                    value = eval_variable(stepInfos['value'])
                    if element.type in [bytes] and isinstance(value, str): value = value.encode()
                    if element.type in [np.ndarray]: value = create_array(value)
                    element(value)
            else:
                element()
        elif stepType == 'recipe':  # OBSOLETE
            self.execRecipe(element, initPoint=initPoint)  # Execute a recipe in the recipe

        self.finishStepSignal.emit(recipe_name, stepInfos['name'])
        return result
