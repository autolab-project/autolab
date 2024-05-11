# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:12:24 2019

@author: qchat
"""

import os

import numpy as np
import pandas as pd
import pyqtgraph as pg
from qtpy import QtWidgets, QtGui

from .display import DisplayValues
from ..GUI_utilities import (get_font_size, setLineEditBackground,
                             pyqtgraph_fig_ax, pyqtgraph_image)
from ..icons import icons


class FigureManager:
    """ Manage the figure of the scanner """

    def __init__(self, gui: QtWidgets.QMainWindow):

        self.gui = gui
        self.curves = []

        self._font_size = get_font_size() + 1

        # Configure and initialize the figure in the GUI
        self.fig, self.ax = pyqtgraph_fig_ax()
        self.gui.graph.addWidget(self.fig)
        self.figMap, widget = pyqtgraph_image()
        self.gui.graph.addWidget(widget)
        self.figMap.hide()

        getattr(self.gui, 'variable_x_comboBox').activated.connect(
            self.variableChanged)
        getattr(self.gui, 'variable_y_comboBox').activated.connect(
            self.variableChanged)

        # Number of traces
        self.nbtraces = 5
        self.gui.nbTraces_lineEdit.setText(f'{self.nbtraces:g}')
        self.gui.nbTraces_lineEdit.returnPressed.connect(self.nbTracesChanged)
        self.gui.nbTraces_lineEdit.textEdited.connect(lambda: setLineEditBackground(
            self.gui.nbTraces_lineEdit,'edited', self._font_size))
        setLineEditBackground(self.gui.nbTraces_lineEdit, 'synced', self._font_size)

        # Window to show scan data
        self.gui.displayScanData_pushButton.clicked.connect(self.displayScanDataButtonClicked)
        self.gui.displayScanData_pushButton.hide()
        self.displayScan = DisplayValues("Scan", size=(500, 300))
        self.displayScan.setWindowIcon(QtGui.QIcon(icons['DataFrame']))

        # comboBox with scan id
        self.gui.data_comboBox.activated.connect(self.data_comboBoxClicked)
        self.gui.data_comboBox.hide()

        # Combobo to select the recipe to plot
        self.gui.scan_recipe_comboBox.activated.connect(self.scan_recipe_comboBoxCurrentChanged)
        self.gui.scan_recipe_comboBox.hide()

        # Combobox to select datafram to plot
        self.gui.dataframe_comboBox.activated.connect(self.dataframe_comboBoxCurrentChanged)
        self.gui.dataframe_comboBox.addItem("Scan")
        self.gui.dataframe_comboBox.hide()

        self.gui.toolButton.hide()
        self.clearMenuID()

    def clearMenuID(self):
        self.gui.toolButton.setText("Parameter")
        self.gui.toolButton.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        self.gui.toolButton.setMenu(QtWidgets.QMenu(self.gui.toolButton))

        # TODO: add bool 'all' like in drivers

        self.menuBoolList = []  # OPTIMIZE: edit: maybe not necessary <- when will merge everything, maybe have some class MetaDataset with init(dataSet) to collect all dataSet and organize data relative to scan id and dataframe
        self.menuWidgetList = []
        self.menuActionList = []
        self.nbCheckBoxMenuID = 0

    def addCheckBox2MenuID(self, name_ID: int):
        self.menuBoolList.append(True)
        checkBox = QtWidgets.QCheckBox(self.gui)
        checkBox.setChecked(True)  # Warning: trigger stateChanged (which do reloadData)
        checkBox.stateChanged.connect(lambda state, checkBox=checkBox: self.checkBoxChanged(checkBox, state))
        checkBox.setText(str(name_ID))
        self.menuWidgetList.append(checkBox)
        action = QtWidgets.QWidgetAction(self.gui.toolButton)
        action.setDefaultWidget(checkBox)
        self.gui.toolButton.menu().addAction(action)
        self.menuActionList.append(action)
        self.nbCheckBoxMenuID += 1

    def removeLastCheckBox2MenuID(self):
        self.menuBoolList.pop(-1)
        self.menuWidgetList.pop(-1)
        self.gui.toolButton.menu().removeAction(self.menuActionList.pop(-1))
        self.nbCheckBoxMenuID -= 1  # edit: not true anymore because display only one scan <- will cause "Error encountered for scan id 1: list index out of range" if do scan with n points and due a new scan with n-m points

    def checkBoxChanged(self, checkBox: QtWidgets.QCheckBox, state: bool):
        index = self.menuWidgetList.index(checkBox)
        self.menuBoolList[index] = bool(state)
        if self.gui.dataframe_comboBox.currentText() != "Scan":
            self.reloadData()

    def data_comboBoxClicked(self):
        """ This function select a dataset """
        if len(self.gui.dataManager.datasets) != 0:
            self.gui.data_comboBox.show()
            dataset = self.gui.dataManager.getLastSelectedDataset()
            index = self.gui.scan_recipe_comboBox.currentIndex()

            resultNamesList = list(dataset)
            AllItems = [self.gui.scan_recipe_comboBox.itemText(i) for i in range(self.gui.scan_recipe_comboBox.count())]

            if AllItems != resultNamesList:
                self.gui.scan_recipe_comboBox.clear()
                self.gui.scan_recipe_comboBox.addItems(resultNamesList)
                if (index + 1) > len(resultNamesList) or index == -1: index = 0
                self.gui.scan_recipe_comboBox.setCurrentIndex(index)

            if self.gui.scan_recipe_comboBox.count() > 1:
                self.gui.scan_recipe_comboBox.show()
            else:
                self.gui.scan_recipe_comboBox.hide()

            self.dataframe_comboBoxCurrentChanged()
        else:
            self.gui.data_comboBox.hide()

        # Change save button text to inform on scan that will be saved
        self.gui.save_pushButton.setText('Save '+self.gui.data_comboBox.currentText().lower())

    def scan_recipe_comboBoxCurrentChanged(self):
        self.dataframe_comboBoxCurrentChanged()

    def dataframe_comboBoxCurrentChanged(self):

        self.updateDataframe_comboBox()
        self.resetCheckBoxMenuID()

        self.gui.dataManager.updateDisplayableResults()
        self.reloadData()

        data_name = self.gui.dataframe_comboBox.currentText()

        if data_name == "Scan" or self.fig.isHidden():
            self.gui.toolButton.hide()
        else:
            self.gui.toolButton.show()

    def updateDataframe_comboBox(self):
        # Executed each time the queue is read
        index = self.gui.dataframe_comboBox.currentIndex()
        recipe_name = self.gui.scan_recipe_comboBox.currentText()
        dataset = self.gui.dataManager.getLastSelectedDataset()

        if dataset is None or recipe_name not in dataset: return None

        sub_dataset = dataset[recipe_name]

        resultNamesList = ["Scan"] + [
            i for i, val in sub_dataset.dictListDataFrame.items() if not isinstance(
                val[0], (str, tuple))]  # Remove this condition if want to plot string or tuple: Tuple[List[str], int]

        AllItems = [self.gui.dataframe_comboBox.itemText(i) for i in range(self.gui.dataframe_comboBox.count())]

        if resultNamesList != AllItems:  # only refresh if change labels, to avoid gui refresh that prevent user to click on combobox
            self.gui.dataframe_comboBox.clear()
            self.gui.dataframe_comboBox.addItems(resultNamesList)
            if (index + 1) > len(resultNamesList): index = 0
            self.gui.dataframe_comboBox.setCurrentIndex(index)

        if len(resultNamesList) == 1:
            self.gui.dataframe_comboBox.hide()
        else:
            self.gui.dataframe_comboBox.show()

    def resetCheckBoxMenuID(self):
        recipe_name = self.gui.scan_recipe_comboBox.currentText()
        dataset = self.gui.dataManager.getLastSelectedDataset()
        data_name = self.gui.dataframe_comboBox.currentText()

        if dataset is not None and recipe_name in dataset and data_name != "Scan":
            sub_dataset = dataset[recipe_name]

            dataframe = sub_dataset.dictListDataFrame[data_name]
            nb_id = len(dataframe)
            nb_bool = len(self.menuBoolList)

            if nb_id != nb_bool:
                if nb_id > nb_bool:
                    for i in range(nb_bool+1, nb_id+1):
                        self.addCheckBox2MenuID(i)
                else:
                    for i in range(nb_bool-nb_id):
                        self.removeLastCheckBox2MenuID()

    # AXE LABEL
    ###########################################################################

    def setLabel(self, axe: str, value: str):
        """ This function changes the label of the given axis """
        axes = {'x':'bottom', 'y':'left'}
        if value == '': value = ' '
        self.ax.setLabel(axes[axe], value, **{'color':0.4, 'font-size': '12pt'})

    # PLOT DATA
    ###########################################################################

    def clearData(self):
        """ This function removes any plotted curves """
        for curve in self.curves:
            try: self.ax.removeItem(curve)  # try because curve=None if close before end of scan
            except: pass
        self.curves = []

    def reloadData(self):
        ''' This function removes any plotted curves and reload all required curves from
        data available in the data manager'''
        # Remove all curves
        self.clearData()

        # Get current displayed result
        data_name = self.gui.dataframe_comboBox.currentText()
        variable_x = self.gui.variable_x_comboBox.currentText()
        variable_y = self.gui.variable_y_comboBox.currentText()
        data_id = int(self.gui.data_comboBox.currentIndex()) + 1
        data_len = len(self.gui.dataManager.datasets)
        selectedData = data_len - data_id

        if variable_x is None:
            return None

        # Label update
        self.setLabel('x', variable_x)
        self.setLabel('y', variable_y)

        self.gui.frame_axis.show()
        if data_name == "Scan":
            nbtraces_temp  = self.nbtraces
            self.gui.nbTraces_lineEdit.show()
            self.gui.graph_nbTracesLabel.show()
        else:
            nbtraces_temp = 1  # decided to only show the last scan data for dataframes
            self.gui.nbTraces_lineEdit.hide()
            self.gui.graph_nbTracesLabel.hide()

        # Load the last results data
        data: pd.DataFrame = self.gui.dataManager.getData(
            nbtraces_temp, [variable_x, variable_y],
            selectedData=selectedData, data_name=data_name)

        # update displayScan
        self.refreshDisplayScanData()

        # Plot data
        if data is not None:
            true_nbtraces = max(nbtraces_temp, len(data))  # not good but avoid error
            if len(data) != 0:
                for temp_data in data:
                    if temp_data is not None: break
                else: return None

            if len(data) != 0 and isinstance(data[0], np.ndarray):  # to avoid errors
                image_data = np.empty((len(data), *temp_data.shape))

            for i in range(len(data)):
                # Data
                subdata: pd.DataFrame = data[i]

                if subdata is None: continue

                if isinstance(subdata, str):  # Could think of someway to show text. Currently removed it from dataset directly
                    print("Warning: Can't display text")
                    continue
                if isinstance(subdata, tuple):
                    print("Warning: Can't display tuple")
                    continue

                subdata = subdata.astype(float)

                if isinstance(subdata, np.ndarray):  # is image
                    self.fig.hide()
                    self.figMap.show()
                    self.gui.frame_axis.hide()
                    image_data[i] = subdata
                    if i == len(data)-1:
                        if image_data.ndim == 3:
                            x,y = (0, 1) if self.figMap.imageItem.axisOrder == 'col-major' else (1, 0)
                            axes = {'t': 0, 'x': x+1, 'y': y+1, 'c': None}  # to avoid a special case in pg that incorrectly assumes the axis
                        else:
                            axes = None
                        self.figMap.setImage(image_data, axes=axes)# xvals=() # Defined which axe is major using pg.setConfigOption('imageAxisOrder', 'row-major') in gui start-up so no need to .T data
                        self.figMap.setCurrentIndex(len(self.figMap.tVals))

                else: # not an image (is pd.DataFrame)
                    self.figMap.hide()
                    self.fig.show()
                    x = subdata.loc[:,variable_x]
                    y = subdata.loc[:,variable_y]
                    if isinstance(x, pd.DataFrame):
                        print(f"Warning: At least two variables have the same name. Data plotted is incorrect for {variable_x}!")
                    if isinstance(y, pd.DataFrame):
                        print(f"Warning: At least two variables have the same name. Data plotted is incorrect for {variable_y}!")
                        y = y.iloc[:, 0]

                    if i == (len(data) - 1):
                        color = 'r'
                        alpha = 1
                    else:
                        color = 'k'
                        alpha = (true_nbtraces - (len(data) - 1 - i)) / true_nbtraces

                    # Plot
                    # OPTIMIZE: known issue but from pyqtgraph, error if use FFT on one point
                    curve = self.ax.plot(x, y, symbol='x', symbolPen=color, symbolSize=10, pen=color, symbolBrush=color)
                    curve.setAlpha(alpha, False)
                    self.curves.append(curve)

    def variableChanged(self, index):
        """ This function is called when the displayed result has been changed
        in the combo box. It proceeds to the change. """
        if self.gui.variable_x_comboBox.currentIndex() != -1 and self.gui.variable_y_comboBox.currentIndex() != -1:
            self.reloadData()
        else:
            self.clearData()

    # TRACES
    ###########################################################################

    def nbTracesChanged(self):
        """ This function is called when the number of traces displayed has been changed
        in the GUI. It proceeds to the change and update the plot. """
        value = self.gui.nbTraces_lineEdit.text()
        check = False
        try:
            value = int(float(value))
            assert value > 0
            self.nbtraces = value
            check = True
        except:
            pass

        self.gui.nbTraces_lineEdit.setText(f'{self.nbtraces:g}')
        setLineEditBackground(self.gui.nbTraces_lineEdit, 'synced', self._font_size)

        if check is True and self.gui.variable_y_comboBox.currentIndex() != -1:
            self.reloadData()

    # Show data
    ###########################################################################
    def refreshDisplayScanData(self):
        self.gui.displayScanData_pushButton.show()
        recipe_name = self.gui.scan_recipe_comboBox.currentText()
        datasets = self.gui.dataManager.getLastSelectedDataset()
        if datasets is not None and recipe_name in datasets:
            name = f"Scan{self.gui.data_comboBox.currentIndex()+1}"
            if self.gui.scan_recipe_comboBox.count() > 1:
                name += f", {recipe_name}"
            self.displayScan.setWindowTitle(name)
            self.displayScan.refresh(datasets[recipe_name].data)

    def displayScanDataButtonClicked(self):
        """ This function opens a window showing the scan data for the displayed scan id """
        self.refreshDisplayScanData()
        self.displayScan.show()

    # SAVE FIGURE
    ###########################################################################

    def save(self, filename: str):
        """ This function save the figure with the provided filename """
        raw_name, extension = os.path.splitext(filename)
        new_filename = raw_name + ".png"
        exporter = pg.exporters.ImageExporter(self.fig.plotItem)
        exporter.export(new_filename)

    def close(self):
        """ Called by scanner on closing """
        self.displayScan.close()
        self.fig.deleteLater()  # prevent crash without traceback when reopenning scanner multiple times
        self.figMap.deleteLater()
