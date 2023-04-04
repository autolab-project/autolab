# -*- coding: utf-8 -*-
"""
Created on Oct 2022

@author: jonathan based on qchat
"""
from PyQt5 import QtCore, QtWidgets, uic
import os

from .figure import FigureManager
from .data import DataManager
from .analyze import AnalyzeManager


class Plotter(QtWidgets.QMainWindow):

    def __init__(self,mainGui):#, driver=None):

        # if driver is not None:
        #     # OLD TODO: implement connection here (see ct400)
        #     # Will not do it because it is not good to mixed GUI and drivers
        #     pass

        self.active = False
        self.mainGui = mainGui

        # Configuration of the window
        QtWidgets.QMainWindow.__init__(self)
        ui_path = os.path.join(os.path.dirname(__file__),'interface.ui')
        uic.loadUi(ui_path,self)
        self.setWindowTitle("AUTOLAB Plotter")

        # Loading of the different centers
        self.figureManager = FigureManager(self)
        self.dataManager = DataManager(self)
        self.analyzeManager = AnalyzeManager()

        # Save button
        self.save_pushButton.clicked.connect(self.dataManager.saveButtonClicked)
        self.save_pushButton.setEnabled(False)

        # Clear button
        self.clear_pushButton.clicked.connect(self.dataManager.clear)
        self.clear_all_pushButton.clicked.connect(self.dataManager.clear_all)
        self.clear_pushButton.setEnabled(False)
        self.clear_all_pushButton.setEnabled(False)

        # Open button
        self.openButton.clicked.connect(self.dataManager.importActionClicked)

        # comboBox with data id
        self.data_comboBox.activated['QString'].connect(self.dataManager.data_comboBoxClicked)

        # Number of traces
        self.nbTraces_lineEdit.setText(f'{self.figureManager.nbtraces:g}')
        self.nbTraces_lineEdit.returnPressed.connect(self.nbTracesChanged)
        self.nbTraces_lineEdit.textEdited.connect(lambda : self.setLineEditBackground(self.nbTraces_lineEdit,'edited'))
        self.setLineEditBackground(self.nbTraces_lineEdit,'synced')

        for axe in ['x','y'] :
            getattr(self,f'logScale_{axe}_checkBox').stateChanged.connect(lambda b, axe=axe:self.logScaleChanged(axe))
            getattr(self,f'variable_{axe}_comboBox').currentIndexChanged.connect(self.variableChanged)
            getattr(self,f'autoscale_{axe}_checkBox').stateChanged.connect(lambda b, axe=axe:self.figureManager.autoscaleChanged(axe))
            getattr(self,f'autoscale_{axe}_checkBox').setChecked(True)

        # Target Value line edit
        self.targetValue_lineEdit.setText("-1")
        self.targetValue_lineEdit.returnPressed.connect(self.targetValueChanged)
        self.targetValue_lineEdit.textEdited.connect(lambda : self.setLineEditBackground(self.targetValue_lineEdit,'edited'))
        self.setLineEditBackground(self.targetValue_lineEdit,'synced')

        # Depth Value spinbox edit
        self.depthValue_spinBox.setValue(1)
        self.depthValue_spinBox.valueChanged.connect(self.depthValueChanged)

        # Level Value doublespinbox edit
        self.levelValue_doubleSpinBox.setValue(-3.)
        self.levelValue_doubleSpinBox.valueChanged.connect(self.levelValueChanged)

        # Cursor checkbox
        self.displayCursorCheckBox.clicked.connect(self.displayCursorCheckBoxClicked)

        self.driver_lineEdit.setText(f'{self.dataManager.driverValue}')
        self.driver_lineEdit.returnPressed.connect(self.driverChanged)
        self.driver_lineEdit.textEdited.connect(lambda : self.setLineEditBackground(self.driver_lineEdit,'edited'))
        self.setLineEditBackground(self.driver_lineEdit,'synced')

        # Plot button
        self.plotDataButton.clicked.connect(self.refreshPlotData)

        # Timer
        self.timer_time = 0.5  # This plotter is not meant for fast plotting like the monitor, be aware it may crash with too high refreshing rate
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(int(self.timer_time*1000)) # ms
        self.timer.timeout.connect(self.autoRefreshPlotData)

        self.auto_plotDataButton.clicked.connect(self.autoRefreshChanged)
        self.overwriteDataButton.clicked.connect(self.overwriteDataChanged)

        # Delay
        self.delay_lineEdit.setText(str(self.timer_time))
        self.delay_lineEdit.returnPressed.connect(self.delayChanged)
        self.delay_lineEdit.textEdited.connect(lambda : self.setLineEditBackground(self.delay_lineEdit,'edited'))
        self.setLineEditBackground(self.delay_lineEdit,'synced')

    def overwriteDataChanged(self):
        """ Set overwrite name for data import """

        self.dataManager.setOverwriteData(self.overwriteDataButton.isChecked())

    def autoRefreshChanged(self):
        """ Set if auto refresh call for driver data """

        if self.auto_plotDataButton.isChecked():
            self.timer.start()
        else:
            self.timer.stop()

    def autoRefreshPlotData(self):
        """ Function that refresh plot every timer interval """
        # OPTIMIZE: timer should not call a heavy function, idealy just take data to plot
        self.refreshPlotData()

    def refreshPlotData(self):
        """ This function get the last dataset data and display it onto the Plotter GUI """

        driverValue = self.dataManager.getDriverValue()

        try:
            driverVariable = self.dataManager.getDriverName(driverValue)
            dataset = self.dataManager.importDriverData(driverVariable)
            data_name = dataset.name
            self.figureManager.start(dataset)
            self.statusBar.showMessage(f"Display the data: '{data_name}'",5000)
        except Exception as error:
            self.statusBar.showMessage(f"Can't refresh data: {error}",10000)

    def driverChanged(self):
        """ This function start the update of the target value in the data manager
        when a changed has been detected """

        # Send the new value
        try:
            value = str(self.driver_lineEdit.text())
            self.dataManager.setDriverValue(value)
        except Exception as er:
            self.statusBar.showMessage(f"ERROR Can't change driver variable: {er}", 10000)
        else:
            # Rewrite the GUI with the current value
            self.updateDriverValueGui()

    def updateDriverValueGui(self):
        """ This function ask the current value of the target value in the data
        manager, and then update the GUI """

        value = self.dataManager.getDriverValue()
        self.driver_lineEdit.setText(f'{value}')
        self.setLineEditBackground(self.driver_lineEdit,'synced')

    def logScaleChanged(self,axe):
        """ This function is called when the log scale state is changed in the GUI. """

        state = getattr(self,f'logScale_{axe}_checkBox').isChecked()
        self.figureManager.setLogScale(axe,state)
        self.figureManager.redraw()

    def variableChanged(self,index):
        """ This function is called when the displayed result has been changed in
        the combo box. It proceeds to the change. """

        self.figureManager.clearData()

        if self.variable_x_comboBox.currentIndex() != -1 and self.variable_y_comboBox.currentIndex() != -1 :
            self.figureManager.reloadData()

    def nbTracesChanged(self):
        """ This function is called when the number of traces displayed has been changed
        in the GUI. It proceeds to the change and update the plot. """

        value = self.nbTraces_lineEdit.text()

        check = False
        try:
            value = int(float(value))
            assert value > 0
            self.figureManager.nbtraces = value
            check = True
        except:
            pass

        self.nbTraces_lineEdit.setText(f'{self.figureManager.nbtraces:g}')
        self.setLineEditBackground(self.nbTraces_lineEdit,'synced')

        if check is True and self.variable_y_comboBox.currentIndex() != -1 :
            self.figureManager.reloadData()

    def depthValueChanged(self):
        """ This function start the update of the target value in the data manager
        when a changed has been detected """

        # Send the new value
        try:
            value = int(self.depthValue_spinBox.value())
            self.dataManager.setDepthValue(value)
        except:
            pass

        # Rewrite the GUI with the current value
        value = int(self.dataManager.getDepthValue())
        self.depthValue_spinBox.setValue(value)

        self.displayCursorCheckBoxClicked()

    def levelValueChanged(self):
        """ This function start the update of the target value in the data manager
        when a changed has been detected """

        # Send the new value
        try:
            value = float(self.levelValue_doubleSpinBox.value())
            self.dataManager.setLevelValue(value)
        except:
            pass

        # Rewrite the GUI with the current value
        value = float(self.dataManager.getLevelValue())
        self.levelValue_doubleSpinBox.setValue(value)

        self.displayCursorCheckBoxClicked()

    def targetValueChanged(self):
        """ This function start the update of the target value in the data manager
        when a changed has been detected """

        # Send the new value
        try:
            value = float(self.targetValue_lineEdit.text())
            self.dataManager.setTargetValue(value)
        except:
            pass

        # Rewrite the GUI with the current value
        value = self.dataManager.getTargetValue()
        self.targetValue_lineEdit.setText(f'{value}')
        self.setLineEditBackground(self.targetValue_lineEdit,'synced')

        self.displayCursorCheckBoxClicked()

    def displayCursorCheckBoxClicked(self):
        """ This function set the cursors ON/OFF """

        if self.displayCursorCheckBox.isChecked():
            self.display3dbButtonClicked()
        else:
            self.figureManager.displayCursors([None]*3, [None]*3)

    def display3dbButtonClicked(self):
        """ Function to calculate and display cursors """
        self.clearStatusBar()

        targetValue = self.dataManager.getTargetValue()
        depth = self.dataManager.getDepthValue()
        level = self.dataManager.getLevelValue()

        if targetValue == -1:
            targetValue = "default"

        try:
            self.analyzeManager.data.set_data_name(self.dataManager.getLastSelectedDataset().name)
            self.analyzeManager.data.add_data(self.dataManager.getLastSelectedDataset().data)
            self.analyzeManager.data.set_x_label(self.figureManager.getLabel("x"))
            self.analyzeManager.data.set_y_label(self.figureManager.getLabel("y"))

            # TODO: add  x_left right.. output to GUI
            results = self.analyzeManager.analyze.bandwidth.search_bandwitdh(targetValue, depth=depth, level=level)
            x_left = results["x_left"]
            x_right = results["x_right"]
            x_max = results["x_max"]
            y_left = results["y_left"]
            y_right = results["y_right"]
            y_max = results["y_max"]

            x = [x_left, x_max, x_right]
            y = [y_left, y_max, y_right]

            if self.displayCursorCheckBox.isChecked():
                self.figureManager.displayCursors(x, y)

        except Exception as error:
            self.statusBar.showMessage(f"Can't display markers: {error}",10000)


    def closeEvent(self,event):
        """ This function does some steps before the window is really killed """

        # Delete reference of this window in the control center
        self.timer.stop()
        self.mainGui.clearPlotter()


    def setLineEditBackground(self,obj,state):

        """ Function used to set the background color of a QLineEdit widget,
        based on its editing state """

        if state == 'synced' :
            color='#D2FFD2' # vert
        if state == 'edited' :
            color='#FFE5AE' # orange

        # if "QLineEdit".lower() in str(obj).lower():
        obj.setStyleSheet("QLineEdit:enabled {background-color: %s; font-size: 9pt}"%color)
        # elif "QSpinBox".lower() in str(obj).lower():
        #     obj.setStyleSheet("QSpinBox {background-color : %s}"%color)
        # else:
        #     print(str(obj), "Not implemented")

    def clearStatusBar(self):
        self.statusBar.showMessage('')


    def delayChanged(self):
        """ This function start the update of the delay in the thread manager
        when a changed has been detected """

        # Send the new value
        try :
            value = float(self.delay_lineEdit.text())
            assert value >= 0
            self.timer_time = value
        except :
            pass

        # Rewrite the GUI with the current value
        self.updateDelayGui()


    def updateDelayGui(self):
        """ This function ask the current value of the delay in the data
        manager, and then update the GUI """

        value = self.timer_time
        self.delay_lineEdit.setText(f'{value:.10g}')
        self.timer.setInterval(int(value*1000))  # ms
        self.setLineEditBackground(self.delay_lineEdit,'synced')


def cleanString(name):

    """ This function clears the given name from special characters """

    for character in '*."/\[]:;|, ' :
        name = name.replace(character,'')
    return name
