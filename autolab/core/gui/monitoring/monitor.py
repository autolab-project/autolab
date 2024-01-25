# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:21:49 2019

@author: qchat
"""
import time
import threading
from queue import Queue

from qtpy import QtCore, QtWidgets

from ...devices import Device


class MonitorManager:

    def __init__(self, gui: QtWidgets.QMainWindow):

        self.gui = gui

        # Configure a new thread
        self.thread = MonitorThread(self.gui.variable, self.gui.queue)
        self.thread.errorSignal.connect(self.error)

    def error(self, error: Exception):
        """ This function is called when the errorSignal of the thread is raised.
        It update the pause button and displays the error in the GUI """
        self.gui.pauseButton.setText('Resume')
        self.gui.setStatus(f'Error : {error} ', 10000, False)

    def start(self):
        """ This function start the thread """
        self.thread.start()

    def setDelay(self, value):
        """ Set the delay in the thread """
        self.thread.delay = value

    def getDelay(self):
        """ Returns the current delay of the thread """
        return self.thread.delay

    def isPaused(self):
        """ This function returns whether the thread is paused or not """
        return self.thread.pauseFlag.is_set()

    def resume(self):
        """ This function resume the monitoring """
        self.thread.pauseFlag.clear()

    def pause(self):
        """ This function pause the monitoring """
        self.thread.pauseFlag.set()

    def close(self):
        """ This function stops the thread and wait for its complete deletion """
        self.resume()
        self.thread.stopFlag.set()
        self.thread.wait()


class MonitorThread(QtCore.QThread):
    """ This thread class is dedicated to read the variable, and send its data to GUI through a queue """

    errorSignal = QtCore.Signal(object)

    def __init__(self, variable: Device, queue: Queue):

        QtCore.QThread.__init__(self)
        self.variable = variable
        self.queue = queue

        self.pauseFlag = threading.Event()
        self.stopFlag = threading.Event()

        self.delay = 0

    def run(self):

        t_ini = time.time()
        pauseLength = 0
        pauseStartedTime = None

        while not self.stopFlag.is_set():
            # If the thread just resume, take into account the delay it has been paused
            if pauseStartedTime is not None:
                pauseLength += time.time() - pauseStartedTime
                pauseStartedTime = None

            # Time measure
            now = time.time() - t_ini - pauseLength

            try:
                # Measure variable
                value = self.variable()

                # Check type
                try:
                    value = float(value)
                except TypeError:
                    assert hasattr(value, "shape"), "If data is not a float, should be an array or a dataframe"

                # Send signal new data
                self.queue.put([now,value])

            except Exception as e:
                self.errorSignal.emit(e)
                self.pauseFlag.set()

            # If not the thread may be too fast
            time.sleep(self.delay)

            # pause
            while self.pauseFlag.is_set():
                if pauseStartedTime is None:
                    pauseStartedTime = time.time()
                time.sleep(0.1)
