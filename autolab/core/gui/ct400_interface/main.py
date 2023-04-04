# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 15:11:17 2021

@author: Jonathan Peltier based on qchat
"""
from PyQt5 import QtCore, QtWidgets, uic
import os
# import queue

from autolab import paths

from .data import DataManager
from .figure import FigureManager
# from .monitor import MonitorManager


class CT400Gui(QtWidgets.QMainWindow):

    def __init__(self,item, ct400):

        print("CT400Gui is depreciated, use Plotter instead")
        self.item = item
        self.ct400 = ct400

        # Configuration of the window
        QtWidgets.QMainWindow.__init__(self)
        ui_path = os.path.join(os.path.dirname(__file__),'interface.ui')
        uic.loadUi(ui_path,self)
        self.setWindowTitle(f"AUTOLAB CT400 GUI")

        # Queue
        # self.queue = queue.Queue()
        # self.timer = QtCore.QTimer(self)
        # self.timer.setInterval(33) #30fps
        # self.timer.timeout.connect(self.sync)


        # Plot button
        self.plotDataButton.clicked.connect(lambda : self.refreshPlotData("Last Scan"))

        # Save button
        self.saveButton.clicked.connect(self.saveButtonClicked)
        self.saveButton.setEnabled(False)

        # Load button
        self.openButton.clicked.connect(self.openButtonClicked)

        # Delete button
        self.deleteButton.clicked.connect(self.deleteButtonClicked)

        # Cursor checkbox
        self.displayCursorCheckBox.clicked.connect(self.displayCursorCheckBoxClicked)


        # Target wavelength line edit
        self.targetWavelength_lineEdit.setText("-1")
        self.targetWavelength_lineEdit.returnPressed.connect(self.windowTargetWavelengthChanged)
        self.targetWavelength_lineEdit.textEdited.connect(lambda : self.setLineEditBackground(self.targetWavelength_lineEdit,'edited'))
        self.setLineEditBackground(self.targetWavelength_lineEdit,'synced')

        # Choose data to display combobox
        # self.data_comboBox.currentIndexChanged.connect(self.data_comboBoxClicked)
        self.data_comboBox.activated['QString'].connect(self.data_comboBoxClicked)



        # Managers
        self.dataManager = DataManager(self)
        self.figureManager = FigureManager(self)
        # self.monitorManager = MonitorManager(self)

        # Auto scale button
        self.autoScaleButton.clicked.connect(self.figureManager.doAutoscale)

        # Start
        # self.windowLengthChanged()
        # self.monitorManager.start()
        # self.timer.start()

        # OPTIMIZE: functions are too slow
        self.update_data_comboBox()
        self.plotDataClicked()  # plot last existing data
        self.figureManager.doAutoscale()
        self.refreshPlotData()  # try to plot Last Scan
        self.statusBar.showMessage("")  # remove error if no data to display



    def data_comboBoxClicked(self):

        data_name = self.data_comboBox.currentText()

        if data_name != "":
            self.plotDataClicked(data_name)


    def change_index_data_comboBox(self, data_name):

        index = self.data_comboBox.findText(data_name)

        if index == -1:
            raise IndexError(f"No data with the name '{data_name}' found in {list(self.ct400.instance.available_data())}")
        else:
            self.data_comboBox.setCurrentIndex(index)


    def update_data_comboBox(self):
        available_data = list(self.ct400.instance.available_data())

        self.data_comboBox.clear()

        for data_name in available_data:
            self.data_comboBox.addItem(data_name)

        nbr_data = self.data_comboBox.count()  # how many item left
        self.data_comboBox.setCurrentIndex(nbr_data-1)  # show new index


    def deleteButtonClicked(self):

        self.clearStatusBar()

        data_name = self.data_comboBox.currentText()
        index = self.data_comboBox.currentIndex()
        nbr_data = self.data_comboBox.count()  # how many item left

        try:
            self.dataManager.deleteData(data_name)
            self.data_comboBox.removeItem(index)
        except Exception as error:
            self.statusBar.showMessage(f"Can't delete: {error}", 10000)
            pass

        if self.data_comboBox.count() == 0:
            self.saveButton.setEnabled(False)
            self.figureManager.clearData()

        else:
            if index == (nbr_data-1) and index != 0:  # if last point but exist other data takes previous data else keep index
                index -= 1

            self.data_comboBox.setCurrentIndex(index)

        self.data_comboBoxClicked()


    def setLineEditBackground(self,obj,state):

        if state == 'synced' :
            color='#D2FFD2' # vert
        if state == 'edited' :
            color='#FFE5AE' # orange

        obj.setStyleSheet("QLineEdit:enabled {background-color: %s; font-size: 9pt}"%color)



    def windowTargetWavelengthChanged(self):

        """ This function start the update of the target wavelength in the data manager
        when a changed has been detected """

        # Send the new value
        try:
            value = float(self.targetWavelength_lineEdit.text())
            self.dataManager.setTargetWavelength(value)
        except:
            pass

        # Rewrite the GUI with the current value
        self.updateTargetWavelengthGui()

        self.displayCursorCheckBoxClicked()


    def updateTargetWavelengthGui(self):

        """ This function ask the current value of the target wavelength in the data
        manager, and then update the GUI """

        value = self.dataManager.getTargetWavelength()
        self.targetWavelength_lineEdit.setText(f'{value:.10g}')
        self.setLineEditBackground(self.targetWavelength_lineEdit,'synced')


    def displayCursorCheckBoxClicked(self):
        """ This function set the cursors ON/OFF """

        if self.displayCursorCheckBox.isChecked():
            self.display3dbButtonClicked()
        else:
            self.figureManager.displayCursors([None]*3, [None]*3)


    def display3dbButtonClicked(self):

        self.clearStatusBar()

        targetWavelength = self.dataManager.getTargetWavelength()

        try:
            wl, power = self.dataManager.search_3db_wavelength(targetWavelength)

            if self.displayCursorCheckBox.isChecked():
                self.figureManager.displayCursors(wl, power)

        except Exception as error:
            self.statusBar.showMessage(f"Can't display markers: {error}",10000)


    def refreshPlotData(self, data_name="Last Scan"):

        """ This function get the "Last scan" sweep data from the ct400 device
        and display it onto the CT400GUI """

        old_data_name = self.data_comboBox.currentText()
        self.update_data_comboBox()

        try:
            self.change_index_data_comboBox(data_name)
            self.plotDataClicked(data_name)
            self.figureManager.doAutoscale()
            self.statusBar.showMessage(f"Display the data: '{data_name}'",5000)
        except Exception as error:
            try:
                self.change_index_data_comboBox(old_data_name)  # if failed, tries to plot the last displayed sweep (could be deleted from autolab GUI)
            except Exception:
                pass
            self.statusBar.showMessage(f"Can't refresh data: {error}",10000)


    def plotDataClicked(self, data_name=None):

        """ This function displayed the sweep data """

        self.clearStatusBar()

        data = self.dataManager.getData(data_name)

        data_name = self.ct400.instance._last_data_name
        available_data = str(list(self.ct400.instance.available_data()))

        if data is not None:
            self.figureManager.reloadData()
            self.saveButton.setEnabled(True)

            self.displayCursorCheckBoxClicked()
        else:
            self.statusBar.showMessage(f"Can't plot. No data found for the name: {data_name}.\n" \
                  f"Here is the list of available data: {available_data}.", 10000)


    def saveButtonClicked(self):

        """ This function is called when the SAVE button is pressed, and launch the procedure
        to save both the data and the figure """

        self.clearStatusBar()

        # Ask the filename of the output data
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                          caption="Save data",
                                          directory=paths.USER_LAST_CUSTOM_FOLDER,
                                          filter="Text Files (*.txt);; Supported text Files (*.txt;*.csv;*.dat);; All Files (*)")

        path = os.path.dirname(filename)
        # Save the given path for future, the data and the figure if the path provided is valid
        if path != '':

            paths.USER_LAST_CUSTOM_FOLDER = path
            self.statusBar.showMessage('Saving data...',5000)

            try:
                self.dataManager.save(filename)
                self.figureManager.save(filename)
                self.statusBar.showMessage(f'Data successfully saved in {filename}.',5000)
            except Exception as error:
                self.statusBar.showMessage(f'An error occured while saving data ! error:{error}',10000)


    def openButtonClicked(self):
        self.clearStatusBar()
        filename = QtWidgets.QFileDialog.getOpenFileName(self, "Import Scan data",
                                                     paths.USER_LAST_CUSTOM_FOLDER,
                                                     filter="Text Files (*.txt);; Supported text Files (*.txt;*.csv;*.dat);; All Files (*)")[0]

        path = os.path.dirname(filename)
        paths.USER_LAST_CUSTOM_FOLDER = path

        if path != '':
            try:
                self.dataManager.open(filename)

                data_name = self.dataManager.getData_name()  # used to get new filename if not the same as asked (if data already exists with same name)
                self.refreshPlotData(data_name)

                self.statusBar.showMessage(f"Data successfully openned from {filename}.",5000)


            except Exception as error:
                self.statusBar.showMessage(f"Open failed due to {error}",10000)



    def closeEvent(self,event):

        """ This function does some steps before the window is really killed """

        # self.monitorManager.close()
        # self.timer.stop()
        self.item.clearCT400()


    def clearStatusBar(self):
        self.statusBar.showMessage('')
