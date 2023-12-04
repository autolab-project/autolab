# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:12:24 2019

@author: qchat
"""


import os

import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph.Qt import QtWidgets

from .display import DisplayValues
from ... import utilities


class FigureManager :

    def __init__(self,gui):

        self.gui = gui

        self.curves = []

        # Configure and initialize the figure in the GUI
        self.fig, self.ax = utilities.pyqtgraph_fig_ax()
        self.gui.graph.addWidget(self.fig)

        for axe in ['x','y'] :
            getattr(self.gui,f'variable_{axe}_comboBox').activated['QString'].connect(self.variableChanged)

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

        # Figure form tab DataFrame
        self.gui.tabWidget.currentChanged.connect(self.tabWidgetCurrentChanged)
        self.gui.tabWidget.setTabEnabled(1, False)  # disable 2D map tab until it is ready
        self.gui.dataframe_comboBox.activated['QString'].connect(self.dataframe_comboBoxCurrentChanged)
        self.gui.dataframe_comboBox.setEnabled(False)

        self.gui.toolButton.setEnabled(False)
        self.clearMenuID()

        # Map plot
        self.figMap, self.axMap = utilities.pyqtgraph_fig_ax()
        self.gui.graphMap.addWidget(self.figMap)


    def clearMenuID(self):
        self.gui.toolButton.setText("Parameter")
        self.gui.toolButton.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        self.gui.toolButton.setMenu(QtWidgets.QMenu(self.gui.toolButton))

        self.menuBoolList = list()  # TODO: when will merge everything, maybe have some class MetaDataset with init(dataSet) to collect all dataSet and organize data relative to scan id and dataframe
        self.menuWidgetList = list()
        self.menuActionList = list()
        self.nbCheckBoxMenuID = 0


    def addCheckBox2MenuID(self, name_ID):

        self.menuBoolList.append(True)
        checkBox = QtWidgets.QCheckBox(self.gui)
        checkBox.stateChanged.connect(lambda state, checkBox=checkBox: self.checkBoxChanged(checkBox, state))
        checkBox.setText(str(name_ID))
        self.menuWidgetList.append(checkBox)
        action = QtWidgets.QWidgetAction(self.gui.toolButton)
        action.setDefaultWidget(checkBox)
        self.gui.toolButton.menu().addAction(action)
        self.menuActionList.append(action)
        self.nbCheckBoxMenuID += 1
        checkBox.setChecked(True)  # trigger stateChanged (need to reloadData when create checkBox)

    def removeLastCheckBox2MenuID(self):
        self.menuBoolList.pop(-1)
        self.menuWidgetList.pop(-1)
        self.gui.toolButton.menu().removeAction(self.menuActionList.pop(-1))
        self.nbCheckBoxMenuID -= 1  # will cause "Error encountered for scan id 1: list index out of range" if do scan with n points and due a new scan with n-m points

    def checkBoxChanged(self, checkBox, state):

        index = self.menuWidgetList.index(checkBox)
        self.menuBoolList[index] = bool(state)
        if self.gui.dataframe_comboBox.currentText() != "Scan":
            self.reloadData()


    def dataframe_comboBoxCurrentChanged(self):
        self.gui.dataManager.updateDisplayableResults()
        self.reloadData()

    def tabWidgetCurrentChanged(self):
        """ See if use tab or not for Map plot """
        print("currentIndex", self.gui.tabWidget.currentIndex())  # 0 is first
        print("currentWidget", self.gui.tabWidget.currentWidget())  # tab is first
        print("isTabEnabled 1", self.gui.tabWidget.isTabEnabled(1))  # if enable not visible
        # print("setCurrentIndex 1", self.gui.tabWidget.setCurrentIndex(1))
        # print("setCurrentWidget tab", self.gui.tabWidget.setCurrentWidget(self.gui.tab))

        if self.gui.tabWidget.currentIndex() == 0:
            print("in Curve plot")
        elif self.gui.tabWidget.currentIndex() == 1:
            print("in Map plot")
            if len(self.gui.dataManager.datasets) != 0:
                dataset = self.gui.dataManager.getLastSelectedDataset()

                for dataName in dataset.dictListDataFrame:
                    colors = ('#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf')
                    for i in range(len(dataset.dictListDataFrame[dataName])):
                        color = colors[i % len(colors)]
                        data = dataset.dictListDataFrame[dataName][i]
                        df = utilities.formatData(data)
                        curve = self.axMap.plot(df["0"], df["1"], symbol='x', symbolPen=color, symbolSize=10, pen=color, symbolBrush=color)
        else:
            print("not implemented")




    # AXE LABEL
    ###########################################################################

    def setLabel(self,axe,value):

        """ This function changes the label of the given axis """

        axes = {'x':'bottom', 'y':'left'}
        self.ax.setLabel(axes[axe], value, **{'color':0.4, 'font-size': '12pt'})






    # PLOT DATA
    ###########################################################################


    def clearData(self):

        """ This function removes any plotted curves """

        for curve in self.curves :
            self.ax.removeItem(curve)
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

        # Label update
        self.setLabel('x',variable_x)
        self.setLabel('y',variable_y)

        # Load the last results data
        try :
            data = self.gui.dataManager.getData(self.nbtraces,[variable_x,variable_y], selectedData=selectedData, data_name=data_name)
        except :
            data = None

        # Plot them
        if data is not None :
            true_nbtraces = max(self.nbtraces, len(data))  # OPTIMIZE: not good but avoid error

            for i in range(len(data)) :
                # Data
                subdata = data[i]

                if subdata is None:
                    continue

                subdata = subdata.astype(float)
                x = subdata.loc[:,variable_x]
                y = subdata.loc[:,variable_y]

                # could look at https://stackoverflow.com/questions/12761806/matplotlib-2-different-legends-on-same-graph
                # Appearance:  # TODO: change color and alpha for dataframe  should have color loop for id and alpha loop for dataset so for len(id) color ...
                # can't do it now, need to change how dataset from getData because if change scan range, will have diff size and can't loop color equaly
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



    def reloadLastData(self):

        ''' This functions update the data of the last curve
        Only for scan plot '''

        # Get current displayed result
        variable_x = self.gui.variable_x_comboBox.currentText()
        variable_y = self.gui.variable_y_comboBox.currentText()

        data = self.gui.dataManager.getData(1,[variable_x,variable_y])[0]

        # Update plot data
        if data is not None:
            data = data.astype(float)

            self.curves[-1].setData(data.loc[:,variable_x], data.loc[:,variable_y])

        self.gui.displayScanData_pushButton.setEnabled(True)
        if self.displayScan.active:
            self.displayScan.refresh(self.gui.dataManager.getLastSelectedDataset().data)

        self.gui.dataframe_comboBox.setEnabled(True)




    def variableChanged(self,index):

        """ This function is called when the displayed result has been changed in
        the combo box. It proceeds to the change. """

        if self.gui.variable_x_comboBox.currentIndex() != -1 and self.gui.variable_y_comboBox.currentIndex() != -1 :
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
        try :
            value = int(float(value))
            assert value > 0
            self.nbtraces = value
            check = True
        except :
            pass

        self.gui.nbTraces_lineEdit.setText(f'{self.nbtraces:g}')
        self.gui.setLineEditBackground(self.gui.nbTraces_lineEdit,'synced')

        if check is True and self.gui.variable_y_comboBox.currentIndex() != -1 :
            self.reloadData()


    # Show data
    ###########################################################################

    def displayScanDataButtonClicked(self):

        """ This function opens a window showing the scan data for the displayed scan id """

        if not self.displayScan.active:
            self.displayScan.refresh(self.gui.dataManager.getLastSelectedDataset().data)
        self.displayScan.show()


    # SAVE FIGURE
    ###########################################################################

    def save(self,filename):

        """ This function save the figure with the provided filename """

        raw_name, extension = os.path.splitext(filename)
        new_filename = raw_name+".png"
        exporter = pg.exporters.ImageExporter(self.fig.plotItem)
        exporter.export(new_filename)
