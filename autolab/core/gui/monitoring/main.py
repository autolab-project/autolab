# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 22:08:29 2019

@author: qchat
"""
import os
import sys
import queue

from qtpy import QtCore, QtWidgets, uic, QtGui

from .data import DataManager
from .figure import FigureManager
from .monitor import MonitorManager
from ..icons import icons
from ..GUI_utilities import get_font_size, setLineEditBackground
from ...paths import PATHS
from ...utilities import SUPPORTED_EXTENSION


class Monitor(QtWidgets.QMainWindow):

    def __init__(self, item: QtWidgets.QTreeWidgetItem):
        self.gui = item if isinstance(item, QtWidgets.QTreeWidgetItem) else None
        self.item = item
        self.variable = item.variable

        self._font_size = get_font_size() + 1

        # Configuration of the window
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'interface.ui')
        uic.loadUi(ui_path, self)
        self.setWindowTitle(f"AUTOLAB - Monitor: {self.variable.address()}")
        self.setWindowIcon(QtGui.QIcon(icons['monitor']))
        # Queue
        self.queue = queue.Queue()
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(33)  # 30fps
        self.timer.timeout.connect(self.sync)

        # Window length
        self.windowLength_lineEdit.setText('10')
        self.windowLength_lineEdit.returnPressed.connect(self.windowLengthChanged)
        self.windowLength_lineEdit.textEdited.connect(lambda: setLineEditBackground(
            self.windowLength_lineEdit, 'edited', self._font_size))
        setLineEditBackground(
            self.windowLength_lineEdit, 'synced', self._font_size)

        self.xlabel = 'Time(s)'  # Is changed to x if ndarray or dataframe
        self.ylabel = f'{self.variable.address()}'  # OPTIMIZE: could depend on 1D or 2D

        if self.variable.unit is not None:
            self.ylabel += f'({self.variable.unit})'

        # Delay
        self.delay_lineEdit.setText('0.01')
        self.delay_lineEdit.returnPressed.connect(self.delayChanged)
        self.delay_lineEdit.textEdited.connect(lambda: setLineEditBackground(
            self.delay_lineEdit, 'edited', self._font_size))
        setLineEditBackground(self.delay_lineEdit, 'synced', self._font_size)

        # Pause
        self.pauseButton.clicked.connect(self.pauseButtonClicked)

        # Save
        self.saveButton.clicked.connect(self.saveButtonClicked)

        # Clear
        self.clearButton.clicked.connect(self.clearButtonClicked)

        # Mean
        self.mean_checkBox.clicked.connect(self.mean_checkBoxClicked)

        # Min
        self.min_checkBox.clicked.connect(self.min_checkBoxClicked)

        # Max
        self.max_checkBox.clicked.connect(self.max_checkBoxClicked)

        # Managers
        self.dataManager = DataManager(self)
        self.figureManager = FigureManager(self)
        self.monitorManager = MonitorManager(self)

        # Start
        self.windowLengthChanged()
        self.delayChanged()
        self.monitorManager.start()
        self.timer.start()

    def sync(self):
        """ This function updates the data and then the figure.
        Function called by the time """
        # Empty the queue
        count = 0
        while not self.queue.empty():
            self.dataManager.addPoint(self.queue.get())
            count += 1

        # Upload the plot if new data available
        if count > 0:
            xlist, ylist = self.dataManager.getData()
            self.figureManager.update(xlist, ylist)

    def pauseButtonClicked(self):
        """ This function pause or resume the monitoring """
        if self.monitorManager.isPaused():
            self.timer.start()
            self.pauseButton.setText('Pause')
            self.monitorManager.resume()
        else:
            self.timer.stop()
            self.pauseButton.setText('Resume')
            self.monitorManager.pause()
            self.sync()

    def saveButtonClicked(self):
        """ This function is called when the SAVE button is pressed, and launch the procedure
        to save both the data and the figure """
        # Make sure the monitoring is paused
        if not self.monitorManager.isPaused():
            self.pauseButtonClicked()

        # Ask the filename of the output data
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, caption="Save data", directory=os.path.join(
                PATHS['last_folder'],
                f'{self.variable.address()}_monitor.txt'),
            filter=SUPPORTED_EXTENSION)

        path = os.path.dirname(filename)
        # Save the given path for future, the data and the figure if the path provided is valid
        if path != '':
            PATHS['last_folder'] = path
            self.setStatus('Saving data...', 5000)

            try:
                self.dataManager.save(filename)
                self.figureManager.save(filename)
                self.setStatus(f'Data successfully saved in {filename}.', 5000)
            except Exception as e:
                self.setStatus(f'Error while saving data: {e}', 10000, False)

    def clearButtonClicked(self):
        """ This function clear the displayed data """
        self.dataManager.clear()
        self.figureManager.clear()

    def mean_checkBoxClicked(self):
        """ This function clear the mean plot """
        if not self.mean_checkBox.isChecked():
            self.figureManager.plot_mean.setData([], [])

        xlist, ylist = self.dataManager.getData()

        if len(xlist) > 0: self.figureManager.update(xlist,ylist)

    def min_checkBoxClicked(self):
        """ This function clear the min plot """
        if not self.min_checkBox.isChecked():
            self.figureManager.plot_min.setData([], [])

        xlist, ylist = self.dataManager.getData()

        if len(xlist) > 0: self.figureManager.update(xlist, ylist)

    def max_checkBoxClicked(self):
        """ This function clear the max plot """
        if not self.max_checkBox.isChecked():
            self.figureManager.plot_max.setData([], [])

        xlist, ylist = self.dataManager.getData()

        if len(xlist) > 0: self.figureManager.update(xlist, ylist)

    def closeEvent(self, event):
        """ This function does some steps before the window is really killed """
        self.monitorManager.close()
        self.timer.stop()
        if hasattr(self.item, 'clearMonitor'): self.item.clearMonitor()
        self.figureManager.fig.deleteLater()  # maybe not useful for monitor but was source of crash in scanner if didn't close
        self.figureManager.figMap.deleteLater()

        if self.gui is None:
            import pyqtgraph as pg
            try:
                # Prevent 'RuntimeError: wrapped C/C++ object of type ViewBox has been deleted' when reloading gui
                for view in pg.ViewBox.AllViews.copy().keys():
                    pg.ViewBox.forgetView(id(view), view)
                    # OPTIMIZE: forget only view used in monitor/gui
                pg.ViewBox.quit()
            except: pass

        for children in self.findChildren(QtWidgets.QWidget):
            children.deleteLater()
        super().closeEvent(event)

        if self.gui is None:
            QtWidgets.QApplication.quit()  # close the monitor app

    def windowLengthChanged(self):
        """ This function start the update of the window length in the data manager
        when a changed has been detected """
        # Send the new value
        try:
            value = float(self.windowLength_lineEdit.text())
            assert value > 0
            self.dataManager.setWindowLength(value)
        except: pass

        # Rewrite the GUI with the current value
        self.updateWindowLengthGui()

    def delayChanged(self):
        """ This function start the update of the delay in the thread manager
        when a changed has been detected """
        # Send the new value
        try:
            value = float(self.delay_lineEdit.text())
            assert value >= 0
            self.monitorManager.setDelay(value)
        except: pass

        # Rewrite the GUI with the current value
        self.updateDelayGui()

    def updateWindowLengthGui(self):
        """ This function ask the current value of the window length in the data
        manager, and then update the GUI """
        value = self.dataManager.getWindowLength()
        self.windowLength_lineEdit.setText(f'{value:g}')
        setLineEditBackground(self.windowLength_lineEdit, 'synced', self._font_size)

    def updateDelayGui(self):
        """ This function ask the current value of the delay in the data
        manager, and then update the GUI """
        value = self.monitorManager.getDelay()
        self.delay_lineEdit.setText(f'{value:g}')
        setLineEditBackground(self.delay_lineEdit, 'synced', self._font_size)

    def setStatus(self, message: str, timeout: int = 0, stdout: bool = True):
        """ Modify the message displayed in the status bar and add error message to logger """
        self.statusBar.showMessage(message, timeout)
        if not stdout: print(message, file=sys.stderr)
