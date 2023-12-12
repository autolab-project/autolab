# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:08:45 2019

@author: qchat
"""

import time
import math as m
import threading
import collections

import numpy as np
import pandas as pd
from qtpy import QtCore

from ...devices import DEVICES


class ScanManager:
    """ Manage a scan using a dedicated thread """

    def __init__(self, gui):
        self.gui = gui

        # Start / Stop button configuration
        self.gui.start_pushButton.clicked.connect(self.startButtonClicked)

        # Pause / Resume button configuration
        self.gui.pause_pushButton.clicked.connect(self.pauseButtonClicked)
        self.gui.pause_pushButton.setEnabled(False)

        # Progress bar configuration
        self.gui.progressBar.setMinimum(0)
        self.gui.progressBar.setValue(0)

        # Thread
        self.thread = None


    # START AND STOP
    #############################################################################

    def startButtonClicked(self):
        """ This function is called when the start / stop button is pressed.
        Do the expected action """
        self.stop() if self.isStarted() else self.start()

    def isStarted(self):
        """ Returns True or False whether the scan is currently running or not """
        return self.thread is not None

    def start(self):
        """ This function start a scan """
        self.gui.data_comboBox.setEnabled(False)

        try :
            config = self.gui.configManager.config
            recipe_name_list = list(config.keys())
            assert len(recipe_name_list) != 0, 'Need a recipe to start a scan!'

            for recipe_name in recipe_name_list:
                recipe = config[recipe_name]
                assert len(recipe['recipe']) > 0, f"{recipe_name} is empty"
        except Exception as e :
            self.gui.setStatus(f'ERROR The scan cannot start with the current configuration : {str(e)}',10000, False)
        # Only if current config is valid to start a scan
        else:
            # Prepare a new dataset in the datacenter
            self.gui.dataManager.newDataset(config)

            # put dataset id onto the combobox and associate data to it
            dataSet_id = len(self.gui.dataManager.datasets)
            self.gui.data_comboBox.addItem(f'Scan{dataSet_id}')
            self.gui.data_comboBox.setCurrentIndex(int(dataSet_id)-1)  # trigger the currentIndexChanged event but don't trigger activated['QString']

            # Start a new thread
            ## Opening
            self.thread = ScanThread(self.gui.dataManager.queue, config)
            ## Signal connections
            self.thread.errorSignal.connect(self.error)

            self.thread.startParameterSignal.connect(lambda recipe_name: self.setParameterProcessingState(recipe_name, 'started'))
            self.thread.finishParameterSignal.connect(lambda recipe_name: self.setParameterProcessingState(recipe_name, 'finished'))
            self.thread.parameterCompletedSignal.connect(lambda recipe_name: self.resetParameterProcessingState(recipe_name))

            self.thread.startStepSignal.connect(lambda recipe_name, stepName: self.setStepProcessingState(recipe_name, stepName, 'started'))
            self.thread.finishStepSignal.connect(lambda recipe_name, stepName: self.setStepProcessingState(recipe_name, stepName, 'finished'))
            self.thread.recipeCompletedSignal.connect(lambda recipe_name:self.resetStepsProcessingState(recipe_name))

            self.thread.finished.connect(self.finished)

            # Starting
            self.thread.start()

            # Start data center timer
            self.gui.dataManager.timer.start()

            # Update gui
            self.gui.start_pushButton.setText('Stop')
            self.gui.pause_pushButton.setEnabled(True)
            self.gui.clear_pushButton.setEnabled(False)
            self.gui.progressBar.setValue(0)
            self.gui.configManager.importAction.setEnabled(False)
            self.gui.configManager.undo.setEnabled(False)
            self.gui.configManager.redo.setEnabled(False)
            self.gui.setStatus('Scan started !',5000)

    def setStepProcessingState(self, recipe_name: str, stepName: str, state: str):
        self.gui.recipeDict[recipe_name]['recipeManager'].setStepProcessingState(stepName, state)

    def resetStepsProcessingState(self, recipe_name: str):
        self.gui.recipeDict[recipe_name]['recipeManager'].resetStepsProcessingState()

    def setParameterProcessingState(self, recipe_name: str, state: str):
        self.gui.recipeDict[recipe_name]['parameterManager'].setProcessingState(state)

    def resetParameterProcessingState(self, recipe_name: str):
        self.gui.recipeDict[recipe_name]['parameterManager'].setProcessingState('idle')

    def stop(self):
        """ This function stop manually the scan """
        self.gui.data_comboBox.setEnabled(True)
        self.disableContinuousMode()
        self.thread.stopFlag.set()
        self.resume()
        self.thread.wait()


    # SIGNALS
    #############################################################################

    def finished(self):
        """ This function is called when the scan thread is finished.
        It restores the GUI in a ready mode, and start a new scan if in
        continuous mode """
        self.gui.start_pushButton.setText('Start')
        self.gui.pause_pushButton.setEnabled(False)
        self.gui.clear_pushButton.setEnabled(True)
        self.gui.data_comboBox.setEnabled(True)
        self.gui.configManager.importAction.setEnabled(True)
        self.gui.configManager.updateUndoRedoButtons()
        self.gui.dataManager.timer.stop()
        self.gui.dataManager.sync() # once again to be sure we grabbed every data
        self.thread = None

        if self.isContinuousModeEnabled():
            self.start()

    def error(self, error):
        """ This function is called if an error occured during the scan.
        It displays it in the status bar """
        self.gui.setStatus(f'Scan Error : {error} ', 10000, False)


    # CONTINUOUS MODE
    #############################################################################

    def isContinuousModeEnabled(self):
        """ Returns True or False whether the continuous scan mode is enabled
        or not """
        return self.gui.continuous_checkBox.isChecked()

    def disableContinuousMode(self):
        """ This function disables the continuous scan mode """
        self.gui.continuous_checkBox.setChecked(False)


    # PAUSE
    #############################################################################

    def pauseButtonClicked(self):
        """ This function is called when the Pause / Resume button is clicked.
        It does the required action """
        if self.isStarted() :
            self.resume() if self.isPaused() else self.pause()

    def isPaused(self):
        """ Returns True or False whether the scan is paused or not """
        return (self.thread is not None) and (self.thread.pauseFlag.is_set() is True)

    def pause(self):
        """ This function pauses the scan """
        self.thread.pauseFlag.set()
        self.gui.dataManager.timer.stop()
        self.gui.pause_pushButton.setText('Resume')

    def resume(self):
        """ This function resumes the scan """
        self.thread.pauseFlag.clear()
        self.gui.dataManager.timer.start()
        self.gui.pause_pushButton.setText('Pause')



class ScanThread(QtCore.QThread):
    """ This thread class is dedicated to read the variable, \
        and send its data to GUI through a queue """
    # Signals
    errorSignal = QtCore.Signal(object)

    startParameterSignal = QtCore.Signal(object)
    finishParameterSignal = QtCore.Signal(object)
    parameterCompletedSignal = QtCore.Signal(object)

    startStepSignal = QtCore.Signal(object, object)
    finishStepSignal = QtCore.Signal(object, object)
    recipeCompletedSignal = QtCore.Signal(object)


    def __init__(self, queue, config: dict):
        QtCore.QThread.__init__(self)
        self.config = config
        self.queue = queue

        self.pauseFlag = threading.Event()
        self.stopFlag = threading.Event()

    def run(self):
        # Start the scan
        for recipe_name in self.config.keys():
            # Load scan configuration
            parameter = self.config[recipe_name]['parameter']['element']
            name = self.config[recipe_name]['parameter']['name']
            startValue,endValue = self.config[recipe_name]['range']
            nbpts = self.config[recipe_name]['nbpts']
            logScale = self.config[recipe_name]['log']

            # Creates the array of values for the parameter
            if logScale:
                paramValues = np.logspace(m.log10(startValue), m.log10(endValue), nbpts, endpoint=True)
            else:
                paramValues = np.linspace(startValue, endValue, nbpts, endpoint=True)

            for i, paramValue in enumerate(paramValues):

                if not self.stopFlag.is_set():
                    try:
                        # Set the parameter value
                        self.startParameterSignal.emit(recipe_name)
                        if parameter is not None:
                            parameter(paramValue)
                        self.finishParameterSignal.emit(recipe_name)

                        # Start the recipe
                        dataPoint = collections.OrderedDict()
                        dataPoint[recipe_name] = recipe_name
                        dataPoint[name] = paramValue
                        dataPoint = self.processRecipe(recipe_name, dataPoint)

                        # Send the whole data in the queue
                        if self.stopFlag.is_set() is False: self.queue.put(dataPoint)

                    except Exception as e:
                        # If an error occurs, stop the scan and send an error signal
                        self.errorSignal.emit(e)
                        self.stopFlag.set()

                    # Wait until the scan is no more in pause
                    while self.pauseFlag.is_set():
                        time.sleep(0.1)
                else:
                    break
            self.parameterCompletedSignal.emit(recipe_name)

    def processRecipe(self, recipe_name: str, dataPoint: collections.OrderedDict):
        """ This function executes the scan recipe """
        for stepInfos in self.config[recipe_name]['recipe']:
            if self.stopFlag.is_set() is False:
                # Process the recipe step
                result = self.processElement(recipe_name, stepInfos)
                if result is not None:
                    dataPoint[stepInfos['name']] = result
                # Wait until the scan is no more in pause
                while self.pauseFlag.is_set():
                    time.sleep(0.1)
            else :
                break

        self.recipeCompletedSignal.emit(recipe_name)
        return dataPoint

    def processElement(self, recipe_name: str, stepInfos: dict):
        """ This function processes the recipe step """
        element = stepInfos['element']
        stepType = stepInfos['stepType']
        self.startStepSignal.emit(recipe_name, stepInfos['name'])
        result = None

        if stepType == 'measure':
            result = element()
        elif stepType == 'set':
            value = self.checkVariable(stepInfos['value'])
            element(value)
        elif stepType == 'action':
            if stepInfos['value'] is not None:
                value = self.checkVariable(stepInfos['value'])
                element(value)
            else :
                element()

        self.finishStepSignal.emit(recipe_name, stepInfos['name'])
        return result

    def checkVariable(self, value):
        """ Check if value is a device variable address and if is it, return its value """
        if str(value).startswith("$eval:"):
            value = str(value)[len("$eval:"): ]

            try:
                allowed_dict ={"np": np, "pd": pd}
                allowed_dict.update(DEVICES)
                value = eval(str(value), {}, allowed_dict)
            except:
                pass

        return value
