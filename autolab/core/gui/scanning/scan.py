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


class ScanManager :

    def __init__(self,gui):
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

        # comboBox with data id
        self.gui.data_comboBox.activated['QString'].connect(self.data_comboBoxClicked)


    # START AND STOP
    #############################################################################

    def startButtonClicked(self):

        """ This function is called when the start / stop button is pressed.
        Do the expected action """

        if self.isStarted() is False :
            self.start()
        else :
            self.stop()



    def isStarted(self):

        """ Returns True or False whether the scan is currently running or not """

        return self.thread is not None



    def start(self) :

        """ This function start a scan """

        self.gui.data_comboBox.setEnabled(False)
        # Test if current config is valid to start a scan
        test = False
        try :
            config = self.gui.configManager.getConfig()
            assert config['parameter']['element'] is not None, "Parameter not set"
            assert len(config['recipe']) > 0, "Recipe is empty"
            test = True
        except Exception as e :
            self.gui.setStatus(f'ERROR The scan cannot start with the current configuration : {str(e)}',10000, False)

        if test is True :

            # Prepare a new dataset in the datacenter
            self.gui.dataManager.newDataset(config)

            # put dataset id onto the combobox and associate data to it
            dataSet_id = len(self.gui.dataManager.datasets)
            self.gui.data_comboBox.addItem(str(dataSet_id))
            self.gui.data_comboBox.setCurrentIndex(int(dataSet_id)-1)  # trigger the currentIndexChanged event but don't trigger activated['QString']


            # Start a new thread
            ## Opening
            self.thread = ScanThread(self.gui.dataManager.queue, config)
            ## Signal connections
            self.thread.errorSignal.connect(self.error)
            self.thread.startStepSignal.connect(lambda stepName, recipe_name:self.setStepProcessingState(stepName, recipe_name, 'started'))
            self.thread.finishStepSignal.connect(lambda stepName, recipe_name:self.setStepProcessingState(stepName, recipe_name, 'finished'))
            self.thread.startParameterSignal.connect(lambda:self.gui.parameterManager.setProcessingState('started'))
            self.thread.finishParameterSignal.connect(lambda:self.gui.parameterManager.setProcessingState('finished'))
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

    def setStepProcessingState(self, stepName, recipe_name, state):
        if recipe_name == "initrecipe":
            self.gui.recipeManager_begin.setStepProcessingState(stepName, state)
        elif recipe_name == "recipe":
            self.gui.recipeManager.setStepProcessingState(stepName, state)
        elif recipe_name == "endrecipe":
            self.gui.recipeManager_end.setStepProcessingState(stepName, state)

    def resetStepsProcessingState(self, recipe_name):
        if recipe_name == "initrecipe":
            self.gui.recipeManager_begin.resetStepsProcessingState()
        elif recipe_name == "recipe":
            self.gui.recipeManager.resetStepsProcessingState()
        elif recipe_name == "endrecipe":
            self.gui.recipeManager_end.resetStepsProcessingState()

    def stop(self):

        """ This function stop manually the scan """

        self.disableContinuousMode()
        self.thread.stopFlag.set()
        self.resume()
        self.thread.wait()

        self.gui.data_comboBox.setEnabled(True)



    # SIGNALS
    #############################################################################

    def finished(self):

        """ This function is called when the scan thread is finished. It restores
        the GUI in a ready mode, and start a new scan if in continuous mode """

        self.gui.start_pushButton.setText('Start')
        self.gui.pause_pushButton.setEnabled(False)
        self.gui.clear_pushButton.setEnabled(True)
        self.gui.parameterManager.setProcessingState('idle')
        self.gui.configManager.importAction.setEnabled(True)
        self.gui.configManager.updateUndoRedoButtons()
        self.gui.dataManager.timer.stop()
        self.gui.dataManager.sync() # once again to be sure we grabbed every data
        self.thread = None

        self.gui.data_comboBox.setEnabled(True)

        if self.isContinuousModeEnabled() :
            self.start()



    def error(self,error):

        """ This function is called if an error occured during the scan.
        It displays it in the status bar """

        self.gui.setStatus(f'Error : {error} ',10000, False)





    # CONTINUOUS MODE
    #############################################################################

    def isContinuousModeEnabled(self):

        """ Returns True or False whether the continuous scan mode is enabled or not """

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
            if self.isPaused() is False :
                self.pause()
            else :
                self.resume()



    def isPaused(self):

        """ Returns True or False whether the scan is paused or not """

        return self.thread is not None and self.thread.pauseFlag.is_set() is True



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


    def data_comboBoxClicked(self):

        """ This function select a dataset """

        if len(self.gui.dataManager.datasets) != 0:
            self.gui.figureManager.reloadData()
            self.gui.displayScanData_pushButton.setEnabled(True)
            if self.gui.figureManager.displayScan.active:
                self.gui.figureManager.displayScan.refresh(self.gui.dataManager.getLastSelectedDataset().data)


class ScanThread(QtCore.QThread):

    """ This thread class is dedicated to read the variable, and send its data to GUI through a queue """

    # Signals
    errorSignal = QtCore.Signal(object)
    startParameterSignal = QtCore.Signal()
    finishParameterSignal = QtCore.Signal()
    startStepSignal = QtCore.Signal(object, object)
    finishStepSignal = QtCore.Signal(object, object)
    recipeCompletedSignal = QtCore.Signal(object)



    def __init__(self, queue, config):

        QtCore.QThread.__init__(self)
        self.config = config
        self.queue = queue

        self.pauseFlag = threading.Event()
        self.stopFlag = threading.Event()



    def run(self):

        # Load scan configuration
        parameter = self.config['parameter']['element']
        name = self.config['parameter']['name']
        startValue,endValue = self.config['range']
        nbpts = self.config['nbpts']
        logScale = self.config['log']

        # Creates the array of values for the parameter
        if logScale is False :
            paramValues = np.linspace(startValue,endValue,nbpts,endpoint=True)
        else :
            paramValues = np.logspace(m.log10(startValue),m.log10(endValue),nbpts,endpoint=True)

        if len(self.config['initrecipe']) != 0:
            dataPoint = collections.OrderedDict()
            dataPoint[name] = paramValues[0]
            try:
                dataPoint = self.processRecipe(dataPoint, recipe_name='initrecipe')
            except Exception as e :
                # If an error occurs, stop the scan and send an error signal
                self.errorSignal.emit(e)
                self.stopFlag.set()

            # Send the whole data in the queue
            if self.stopFlag.is_set() is False : self.queue.put(dataPoint)

        # Start the scan
        for i, paramValue in enumerate(paramValues):

            if self.stopFlag.is_set() is False :
                try :

                    # Set the parameter value
                    self.startParameterSignal.emit()
                    parameter(paramValue)
                    self.finishParameterSignal.emit()

                    # Start the recipe
                    dataPoint = collections.OrderedDict()
                    dataPoint[name] = paramValue
                    dataPoint = self.processRecipe(dataPoint, recipe_name='recipe')

                    # Send the whole data in the queue
                    if self.stopFlag.is_set() is False : self.queue.put(dataPoint)


                except Exception as e :

                    # If an error occurs, stop the scan and send an error signal
                    self.errorSignal.emit(e)
                    self.stopFlag.set()


                # Wait until the scan is no more in pause
                while self.pauseFlag.is_set() :
                    time.sleep(0.1)

            else :
                break

        # Start the endrecipe
        if len(self.config['endrecipe']) != 0:
            dataPoint = collections.OrderedDict()
            dataPoint[name] = paramValues[-1]
            try:
                dataPoint = self.processRecipe(dataPoint, recipe_name='endrecipe')
            except Exception as e :
                # If an error occurs, stop the scan and send an error signal
                self.errorSignal.emit(e)
                self.stopFlag.set()
            # Send the whole data in the queue
            if self.stopFlag.is_set() is False : self.queue.put(dataPoint)


    def processRecipe(self,dataPoint, recipe_name='recipe'):

        """ This function executes the scan recipe """
        for stepInfos in self.config[recipe_name] :

            if self.stopFlag.is_set() is False :

                # Process the recipe step
                result = self.processElement(stepInfos, recipe_name)
                if result is not None :
                    dataPoint[stepInfos['name']] =  result

                # Wait until the scan is no more in pause
                while self.pauseFlag.is_set() :
                    time.sleep(0.1)

            else :
                break

        self.recipeCompletedSignal.emit(recipe_name)

        return dataPoint



    def processElement(self,stepInfos, recipe_name='recipe'):

        """ This function processes the recipe step """
        element = stepInfos['element']
        stepType = stepInfos['stepType']

        self.startStepSignal.emit(stepInfos['name'], recipe_name)

        result = None
        if stepType == 'measure' :
            result = element()
        if stepType == 'set' :
            value = self.checkVariable(stepInfos['value'])
            element(value)
        if stepType == 'action' :
            if stepInfos['value'] is not None :
                value = self.checkVariable(stepInfos['value'])
                element(value)
            else :
                element()

        self.finishStepSignal.emit(stepInfos['name'], recipe_name)

        return result


    def checkVariable(self, value):

        """ Check if value is a device variable address and if is it, return its value """

        if str(value).startswith("$eval:"):
            value = str(value)[len("$eval:"):]
            try:
                allowed_dict ={"np":np, "pd":pd}
                allowed_dict.update(DEVICES)
                value = eval(str(value), {}, allowed_dict)
            except:
                pass
        return value
