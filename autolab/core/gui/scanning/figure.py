# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:12:24 2019

@author: qchat
"""


import os
import math as m

import numpy as np
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtWidgets

# matplotlib.rcParams.update({'figure.autolayout': True})  # good but can raise LinAlgError. alternative is to emit signal when change windows

from .display import DisplayValues
from ... import utilities


class FigureManager :

    def __init__(self,gui):

        self.gui = gui

        self.curves = []

        # Configure and initialize the figure in the GUI
        self.fig = Figure()
        matplotlib.rcParams.update({'font.size': 12})
        self.ax = self.fig.add_subplot(111)

        self.add_grid(True)

        self.ax.set_xlim((0,10))
        self.ax.autoscale(enable=False)
        # The first time we open a monitor it doesn't work, I don't know why..
        # There is no current event loop in thread 'Thread-7'.
        # More accurately, FigureCanvas doesn't find the event loop the first time it is called
        # The second time it works..
        # Seems to be only in Spyder..
        try :
            self.canvas = FigureCanvas(self.fig)
        except :
            self.canvas = FigureCanvas(self.fig)

        self.toolbar = NavigationToolbar(self.canvas, self.gui)
        self.gui.graph.addWidget(self.toolbar)
        self.gui.graph.addWidget(self.canvas)
        self.fig.tight_layout()
        self.canvas.draw()

        for axe in ['x','y'] :
            getattr(self.gui,f'logScale_{axe}_checkBox').stateChanged.connect(lambda b, axe=axe:self.logScaleChanged(axe))
            getattr(self.gui,f'autoscale_{axe}_checkBox').stateChanged.connect(lambda b, axe=axe:self.autoscaleChanged(axe))
            getattr(self.gui,f'autoscale_{axe}_checkBox').setChecked(True)
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
        self.gui.tabWidget.setTabEnabled(1, False)
        self.gui.dataframe_comboBox.activated['QString'].connect(self.dataframe_comboBoxCurrentChanged)
        self.gui.dataframe_comboBox.setEnabled(False)

        self.gui.toolButton.setEnabled(False)
        self.clearMenuID()

        # Map plot
        self.figMap = Figure()
        matplotlib.rcParams.update({'font.size': 12})
        self.axMap = self.figMap.add_subplot(111)
        try :
            self.canvasMap = FigureCanvas(self.figMap)
        except :
            self.canvasMap = FigureCanvas(self.figMap)

        self.toolbarMap = NavigationToolbar(self.canvasMap, self.gui)
        self.gui.graphMap.addWidget(self.toolbarMap)
        self.gui.graphMap.addWidget(self.canvasMap)


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
                    for i in range(len(dataset.dictListDataFrame[dataName])):
                        data = dataset.dictListDataFrame[dataName][i]
                        df = utilities.formatData(data)
                        curve = self.axMap.plot(df["0"],df["1"],'x-')[0]
                self.canvasMap.draw()
        else:
            print("not implemented")


    # AUTOSCALING
    ###########################################################################

    def autoscaleChanged(self,axe):

        """ Set or unset the autoscale mode for the given axis """

        state = self.isAutoscaleEnabled(axe)
        getattr(self.ax,f'set_autoscale{axe}_on')(state)
        if state is True :
            self.doAutoscale(axe)
            self.redraw()



    def isAutoscaleEnabled(self,axe):

        """ This function returns True or False whether the autoscale for the given axis
        is enabled """

        return getattr(self.gui,f'autoscale_{axe}_checkBox').isChecked()



    def doAutoscale(self,axe):

        """ This function proceeds to an autoscale operation of the given axis """

        datas = [getattr(curve,f'get_{axe}data')() for curve in self.curves]
        if len(datas) > 0 :
            min_list = [np.nanmin(data) for data in datas if ~np.isnan(data).all()]
            max_list = [np.nanmax(data) for data in datas if ~np.isnan(data).all()]
            minValue = np.nanmin(min_list) if ~np.isnan(min_list).all() else 0
            maxValue = np.nanmax(max_list) if ~np.isnan(max_list).all() else 0

            if (minValue,maxValue) != self.getRange(axe):
                self.setRange(axe,(minValue,maxValue))

            self.toolbar.update()


    def add_grid(self, state):
        if state:
            self.ax.minorticks_on()
        else:
            self.ax.minorticks_off()

        self.ax.grid(state, which='major')
        self.ax.grid(state, which='minor', alpha=0.4)



    # LOGSCALING
    ###########################################################################

    def logScaleChanged(self,axe):

        """ This function is called when the log scale state is changed in the GUI. """

        state = getattr(self.gui,f'logScale_{axe}_checkBox').isChecked()
        self.setLogScale(axe,state)
        self.redraw()



    def isLogScaleEnabled(self,axe):

        """ This function returns True or False whether the log scale is enabled
        in the given axis """

        return getattr(self.ax,f'get_{axe}scale')() == 'log'



    def setLogScale(self,axe,state):

        """ This functions sets or not the log scale for the given axis """

        if state is True :
            scaleType = 'log'
        else :
            scaleType = 'linear'

        self.checkLimPositive(axe)
        getattr(self.ax,f'set_{axe}scale')(scaleType)  # BUG: crash python if ct400 is openned -> issue between matplotlib and ctypes from ct400 dll lib
        self.add_grid(True)
        # update for bug -> np.log crash python if a dll lib is openned: https://stackoverflow.com/questions/52497031/python-kernel-crashes-if-i-use-np-log10-after-loading-a-dll
        # could change log in matplotlib but not a good solution
        # I added this:
            # if 0 in a: # OPTIMIZE: used to fix the python crash with dll lib openned
            #     a[a == 0] += 1e-200
        # in matplotlib.scale.transform_non_affine at line 210 to fixe the crash

    def checkLimPositive(self,axe):

        """ This function updates the current range of the given axis to be positive,
        in case we enter in a log scale mode """

        axeRange = list(self.getRange(axe))

        change = False
        if axeRange[1] <= 0 :
            axeRange[1] = 1
            change = True
        if axeRange[0] <= 0 :
            axeRange[0] = 10**(m.log10(axeRange[1])-1)
            change = True

        if change is True :
            self.setRange(axe,tuple(axeRange))






    # AXE LABEL
    ###########################################################################

    def setLabel(self,axe,value):

        """ This function changes the label of the given axis """

        getattr(self.ax,f'set_{axe}label')(value)






    # PLOT DATA
    ###########################################################################


    def clearData(self):

        """ This function removes any plotted curves """

        for curve in self.curves :
            curve.remove()
        self.curves = []
        self.redraw()



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
                curve = self.ax.plot(x,y,'x-',color=color,alpha=alpha)[0]
                self.curves.append(curve)

            # Autoscale
            if self.isAutoscaleEnabled('x') is True : self.doAutoscale('x')
            if self.isAutoscaleEnabled('y') is True : self.doAutoscale('y')

            self.redraw()
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

            self.curves[-1].set_xdata(data.loc[:,variable_x])
            self.curves[-1].set_ydata(data.loc[:,variable_y])

        # Autoscale
        if self.isAutoscaleEnabled('x') is True : self.doAutoscale('x')
        if self.isAutoscaleEnabled('y') is True : self.doAutoscale('y')

        self.redraw()

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
        self.fig.savefig(new_filename, dpi=300)


    # redraw
    ###########################################################################

    def redraw(self):

        """ This function make the previous changes appears in the GUI """

        try :
            self.fig.tight_layout()
        except :
            pass
        self.canvas.draw()




    # RANGE
    ###########################################################################

    def getRange(self,axe):

        """ This function returns the current range of the given axis """

        return getattr(self.ax,f'get_{axe}lim')()



    def setRange(self,axe,r):

        """ This function sets the current range of the given axis """

        if r[0] != r[1]:
            getattr(self.ax,f'set_{axe}lim')(r)
        else:
            if r[0] != 0:
                getattr(self.ax,f'set_{axe}lim')(r[0]-r[0]*5e-3, r[1]+r[1]*5e-3)
            else:
                getattr(self.ax,f'set_{axe}lim')(-5e-3, 5e-3)
