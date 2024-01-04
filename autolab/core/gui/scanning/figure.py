# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:12:24 2019

@author: qchat
"""


import os

import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph.Qt import QtWidgets

from .display import DisplayValues
from ... import utilities


class FigureManager :
    """ Manage the figure of the scanner """

    def __init__(self, gui):

        self.gui = gui
        self.curves = []

        # Configure and initialize the figure in the GUI
        self.fig, self.ax = utilities.pyqtgraph_fig_ax()
        self.gui.graph.addWidget(self.fig)
        self.figMap = pg.ImageView()
        self.gui.graph.addWidget(self.figMap)
        self.figMap.hide()

        for axe in ['x','y'] :
            getattr(self.gui,f'variable_{axe}_comboBox').activated.connect(self.variableChanged)

        # Number of traces
        self.nbtraces = 5
        self.gui.nbTraces_lineEdit.setText(f'{self.nbtraces:g}')
        self.gui.nbTraces_lineEdit.returnPressed.connect(self.nbTracesChanged)
        self.gui.nbTraces_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.nbTraces_lineEdit,'edited'))
        self.gui.setLineEditBackground(self.gui.nbTraces_lineEdit,'synced')

        # Window to show scan data
        self.gui.displayScanData_pushButton.clicked.connect(self.displayScanDataButtonClicked)
        self.gui.displayScanData_pushButton.setEnabled(False)
        self.displayScan = DisplayValues(self.gui, "Scan", size=(500,300))

        # comboBox with scan id
        self.gui.data_comboBox.activated.connect(self.data_comboBoxClicked)

        # Combobo to select the recipe to plot
        self.gui.scan_recipe_comboBox.activated.connect(self.scan_recipe_comboBoxCurrentChanged)

        # Combobox to select datafram to plot
        self.gui.dataframe_comboBox.activated.connect(self.dataframe_comboBoxCurrentChanged)
        self.gui.dataframe_comboBox.setEnabled(False)
        self.gui.dataframe_comboBox.clear()
        self.gui.dataframe_comboBox.addItems(["Scan"])
        self.gui.dataframe_comboBox.hide()

        self.gui.toolButton.hide()
        self.clearMenuID()

    def clearMenuID(self):
        self.gui.toolButton.setText("Parameter")
        self.gui.toolButton.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        self.gui.toolButton.setMenu(QtWidgets.QMenu(self.gui.toolButton))

        self.menuBoolList = list()  # OPTIMIZE: edit: maybe not necessary <- when will merge everything, maybe have some class MetaDataset with init(dataSet) to collect all dataSet and organize data relative to scan id and dataframe
        self.menuWidgetList = list()
        self.menuActionList = list()
        self.nbCheckBoxMenuID = 0

    def addCheckBox2MenuID(self, name_ID):
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

    def checkBoxChanged(self, checkBox, state):
        index = self.menuWidgetList.index(checkBox)
        self.menuBoolList[index] = bool(state)
        if self.gui.dataframe_comboBox.currentText() != "Scan":
            self.reloadData()

    def data_comboBoxClicked(self):
        """ This function select a dataset """
        if len(self.gui.dataManager.datasets) != 0:
            if self.gui.dataframe_comboBox.currentText() != "Scan":
                self.resetCheckBoxMenuID()
                self.updateDataframe_comboBox()
                self.dataframe_comboBoxCurrentChanged()

            self.reloadData()
            self.gui.displayScanData_pushButton.setEnabled(True)

            if self.displayScan.active:
                dataset = self.gui.dataManager.getLastSelectedDataset()
                recipe_name = self.gui.scan_recipe_comboBox.currentText()
                sub_dataset = dataset[recipe_name]
                self.displayScan.refresh(sub_dataset.data)

    def scan_recipe_comboBoxCurrentChanged(self):
        self.dataframe_comboBoxCurrentChanged()

    def dataframe_comboBoxCurrentChanged(self):
        if self.gui.scan_recipe_comboBox.count() != 1:
            self.resetCheckBoxMenuID()
            self.updateDataframe_comboBox()

        self.gui.dataManager.updateDisplayableResults()
        self.reloadData()

        data_name = self.gui.dataframe_comboBox.currentText()

        if data_name == "Scan" or self.fig.isHidden():
            self.gui.toolButton.hide()
        else:
           self.gui.toolButton.show()

    def updateDataframe_comboBox(self):
        # Executed each time the queue is read
        data_name = self.gui.dataframe_comboBox.currentText()
        if data_name == "Scan":
            self.reloadLastData()
        else:
            self.reloadData()

        index = self.gui.dataframe_comboBox.currentIndex()
        recipe_name = self.gui.scan_recipe_comboBox.currentText()
        dataset = self.gui.dataManager.getLastSelectedDataset()
        sub_dataset = dataset[recipe_name]

        # resultNamesList = ["Scan"] + list(sub_dataset.dictListDataFrame.keys())
        resultNamesList = ["Scan"] + [
            i for i in sub_dataset.dictListDataFrame.keys() if type(
                sub_dataset.dictListDataFrame[i][0]) != str]  # OPTIMIZE: remove this condition if want to plot string

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
        sub_dataset = dataset[recipe_name]
        listDataFrame = list(sub_dataset.dictListDataFrame.values())
        if len(listDataFrame) != 0:
            nb_id = 0
            for dataframe in listDataFrame:
                if len(dataframe) > nb_id:
                    nb_id = len(dataframe)

            self.clearMenuID()

            for i in range(1, nb_id+1):
                self.addCheckBox2MenuID(i)


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
            self.ax.removeItem(curve)
        self.curves = []


    def reloadData(self) -> None:
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

        # Label update
        self.setLabel('x',variable_x)
        self.setLabel('y',variable_y)

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
        try:
            data = self.gui.dataManager.getData(
                nbtraces_temp, [variable_x, variable_y],
                selectedData=selectedData, data_name=data_name)
        except:
            data = None

        # Plot them
        if data is not None:
            true_nbtraces = max(nbtraces_temp, len(data))  # not good but avoid error
            if len(data) != 0:
                for temp_data in data:
                    if temp_data is not None:
                        break
                else:
                    return None

            if len(data) != 0 and type(data[0]) is np.ndarray:  # to avoid errors
                image_data = np.empty((len(data), *temp_data.shape))
            for i in range(len(data)) :
                # Data
                subdata = data[i]

                if subdata is None:
                    continue

                if type(subdata) is str:  # OPTIMIZE: could think of someway to show text. Currently removed it from dataset directly
                    print("Warning: Can't display text")
                    continue

                subdata = subdata.astype(float)

                if type(subdata) is np.ndarray:  # is image
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

                    if i == (len(data)-1) :
                        color = 'r'
                        alpha = 1
                    else:
                        color = 'k'
                        alpha = (true_nbtraces-(len(data)-1-i))/true_nbtraces

                    # Plot
                    curve = self.ax.plot(x, y, symbol='x', symbolPen=color, symbolSize=10, pen=color, symbolBrush=color)
                    curve.setAlpha(alpha, False)
                    self.curves.append(curve)

            self.gui.dataframe_comboBox.setEnabled(True)
            self.gui.scan_recipe_comboBox.setEnabled(True)

    def reloadLastData(self):
        ''' This functions update the data of the last curve
        Only for scan plot '''
        # Get current displayed result
        variable_x = self.gui.variable_x_comboBox.currentText()
        variable_y = self.gui.variable_y_comboBox.currentText()

        data = self.gui.dataManager.getData(1, [variable_x, variable_y])[0]

        # Update plot data
        if data is not None:
            data = data.astype(float)

            self.curves[-1].setData(data.loc[:, variable_x], data.loc[:, variable_y])

        self.gui.displayScanData_pushButton.setEnabled(True)
        if self.displayScan.active:
            dataset = self.gui.dataManager.getLastSelectedDataset()
            recipe_name = self.gui.scan_recipe_comboBox.currentText()
            sub_dataset = dataset[recipe_name]
            self.displayScan.refresh(sub_dataset.data)

        self.gui.dataframe_comboBox.setEnabled(True)
        self.gui.scan_recipe_comboBox.setEnabled(True)

    def variableChanged(self,index):
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
        self.gui.setLineEditBackground(self.gui.nbTraces_lineEdit,'synced')

        if check is True and self.gui.variable_y_comboBox.currentIndex() != -1:
            self.reloadData()


    # Show data
    ###########################################################################

    def displayScanDataButtonClicked(self):
        """ This function opens a window showing the scan data for the displayed scan id """
        if not self.displayScan.active:
            recipe_name = self.gui.scan_recipe_comboBox.currentText()
            self.displayScan.refresh(self.gui.dataManager.getLastSelectedDataset()[recipe_name].data)

        self.displayScan.show()


    # SAVE FIGURE
    ###########################################################################

    def save(self, filename):
        """ This function save the figure with the provided filename """
        raw_name, extension = os.path.splitext(filename)
        new_filename = raw_name + ".png"
        exporter = pg.exporters.ImageExporter(self.fig.plotItem)
        exporter.export(new_filename)
