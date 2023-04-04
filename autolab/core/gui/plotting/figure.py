# -*- coding: utf-8 -*-
"""
Created on Oct 2022

@author: jonathan based on qchat
"""


import os
import math as m
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# matplotlib.rcParams.update({'figure.autolayout': True})  # good but can raise LinAlgError. alternative is to emit signal when change windows


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

        self.cursor_left = self.ax.plot([None],[None],'--',color='grey', label="Cursor left")[0]
        self.cursor_right = self.ax.plot([None],[None],'--',color='grey', label="Cursor right")[0]
        self.cursor_max = self.ax.plot([None],[None],'--',color='grey', label="Cursor max")[0]
        self.cursor_left_3db = self.ax.plot([None],[None],'--',color='grey', label="Cursor left 3db")[0]
        self.cursor_right_3db = self.ax.plot([None],[None],'--',color='grey', label="Cursor right 3db")[0]

        # Number of traces
        self.nbtraces = 10



    def start(self, new_dataset) :

        """ This function display data and ajust buttons """

        try :
            names = self.gui.dataManager.getDatasetsNames()

            if self.gui.overwriteDataButton.isChecked() and new_dataset.name in names:
                dataSet_id = names.index(new_dataset.name)+1
                current_dataset = self.gui.dataManager.datasets[dataSet_id-1]

                if new_dataset.data.equals(current_dataset.data):
                    data_name = self.gui.data_comboBox.currentText()
                    if new_dataset.name == data_name:
                        self.gui.statusBar.showMessage(f'Data {new_dataset.name} already plotted !',5000)
                        return
                    else:
                        self.gui.data_comboBox.setCurrentIndex(dataSet_id-1)
                        self.gui.dataManager.updateDisplayableResults()

                        self.gui.save_pushButton.setEnabled(True)

                        self.gui.clear_pushButton.setEnabled(True)
                        self.gui.clear_all_pushButton.setEnabled(True)
                        self.gui.openButton.setEnabled(True)

                        self.gui.statusBar.showMessage(f'Data {new_dataset.name} updated !',5000)
                        return
                else:
                    current_dataset.update(new_dataset)

            else:
                # Prepare a new dataset in the plotter
                self.gui.dataManager.addDataset(new_dataset)
                dataSet_id = len(self.gui.dataManager.datasets)
                # put dataset id onto the combobox and associate data to it
                self.gui.data_comboBox.addItem(str(new_dataset.name))
                # dataset = self.gui.dataManager.getLastDataset()

            self.gui.data_comboBox.setCurrentIndex(dataSet_id-1)  # trigger the currentIndexChanged event but don't trigger activated['QString']

            # dataset.update(new_dataset)

            self.gui.dataManager.updateDisplayableResults()

            self.gui.save_pushButton.setEnabled(True)

            self.gui.clear_pushButton.setEnabled(True)
            self.gui.clear_all_pushButton.setEnabled(True)
            self.gui.openButton.setEnabled(True)

            self.gui.statusBar.showMessage(f'Data {new_dataset.name} plotted !',5000)

        except Exception as e :
            self.gui.statusBar.showMessage(f'ERROR The data cannot be plotted with the given dataset : {str(e)}',10000)


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
            minValue = min([min(data) for data in datas])
            maxValue = max([max(data) for data in datas])
            if (minValue,maxValue) != self.getRange(axe) :
                self.setRange(axe,(minValue,maxValue))

            self.toolbar.update()


    def add_grid(self, state):
        if state:
            self.ax.minorticks_on()
        else:
            self.ax.minorticks_off()

        self.ax.grid(b=state, which='major')
        self.ax.grid(b=state, which='minor', alpha=0.4)


    # RANGE
    ###########################################################################

    def getRange(self,axe):
        """ This function returns the current range of the given axis """

        return getattr(self.ax,f'get_{axe}lim')()


    def setRange(self,axe,r):
        """ This function sets the current range of the given axis """

        factor = 0.02 if axe == "x" else 0.05
        if r[0] != r[1]:
            getattr(self.ax,f'set_{axe}lim')(r[0]-(r[1]-r[0])*factor, r[1]+(r[1]-r[0])*factor)
        else:
            getattr(self.ax,f'set_{axe}lim')(r[0]-0.1, r[0]+0.1)



    # LOGSCALING
    ###########################################################################


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

    def getLabel(self, axe):
        """ This function get the label of the given axis """

        return getattr(self.gui, f"variable_{axe}_comboBox").currentText()

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
        variable_x = self.getLabel("x")
        variable_y = self.getLabel("y")
        data_id = int(self.gui.data_comboBox.currentIndex()) + 1
        data_len = len(self.gui.dataManager.datasets)
        selectedData = data_len - data_id
        # Label update
        self.setLabel('x',variable_x)
        self.setLabel('y',variable_y)

        # Load the last results data
        try :
            # OPTIMIZE: currently load all data and plot more than self.nbtraces if in middle
            # Should change to only load nbtraces and plot nbtraces
            data = self.gui.dataManager.getData(data_len, [variable_x,variable_y], selectedData=0)
            # data = self.gui.dataManager.getData(self.nbtraces,[variable_x,variable_y], selectedData=selectedData)
        except :
            data = None

        # Plot them
        if data is not None :

            for i in range(len(data)) :
                if i != (data_id-1):
                    # Data
                    subdata = data[i]
                    if subdata is None:
                        continue

                    subdata = subdata.astype(float)
                    x = subdata.loc[:,variable_x]
                    y = subdata.loc[:,variable_y]

                    # Apprearance:
                    color = 'k'
                    alpha = (self.nbtraces-abs(data_id-1-i))/self.nbtraces
                    if alpha < 0: alpha = 0

                    # Plot
                    # OPTIMIZE: keep previous style to avoid overwriting it everytime

                    if i < (data_id-1):
                        if len(x) > 300:
                            curve = self.ax.plot(x,y,'-',color=color,alpha=alpha)[0]
                        else:
                            curve = self.ax.plot(x,y,'x-',color=color,alpha=alpha)[0]
                    elif i > (data_id-1):
                        if len(x) > 300:
                            curve = self.ax.plot(x,y,'--',color=color,alpha=alpha)[0]
                        else:
                            curve = self.ax.plot(x,y,'+--',color=color,alpha=alpha)[0]
                    self.curves.append(curve)

            # Data
            i = (data_id-1)
            subdata = data[i]

            if subdata is not None:
                subdata = subdata.astype(float)
                x = subdata.loc[:,variable_x]
                y = subdata.loc[:,variable_y]

                # Apprearance:
                color = 'C0'
                alpha = 1

                # Plot
                if len(x) > 300:
                    curve = self.ax.plot(x,y,'-',color=color,alpha=alpha)[0]
                else:
                    curve = self.ax.plot(x,y,'x-',color=color,alpha=alpha)[0]
                self.curves.append(curve)

                # Autoscale
                if self.isAutoscaleEnabled('x') is True : self.doAutoscale('x')
                if self.isAutoscaleEnabled('y') is True : self.doAutoscale('y')

            self.gui.targetValueChanged()
            self.redraw()



    def reloadLastData(self):

        ''' This functions update the data of the last curve '''

        # Get current displayed result
        variable_x = self.gui.variable_x_comboBox.currentText()
        variable_y = self.gui.variable_y_comboBox.currentText()

        data = self.gui.dataManager.getData(1,[variable_x,variable_y])[0]
        data = data.astype(float)

        # Update plot data
        if data is not None:
            self.curves[-1].set_xdata(data.loc[:,variable_x])
            self.curves[-1].set_ydata(data.loc[:,variable_y])

        # Autoscale
        if self.isAutoscaleEnabled('x') is True : self.doAutoscale('x')
        if self.isAutoscaleEnabled('y') is True : self.doAutoscale('y')

        self.redraw()



    def displayCursors(self, wl, power):

        xmin, xmax = -1e99, 1e99
        ymin, ymax = -1e99, 1e99

        # left cursor
        self.cursor_left.set_xdata([wl[0], wl[0]])
        self.cursor_left.set_ydata([ymin, ymax])

        # right cursor
        self.cursor_right.set_xdata([wl[2], wl[2]])
        self.cursor_right.set_ydata([ymin, ymax])

        # max cursor
        self.cursor_max.set_xdata([xmin, xmax])
        self.cursor_max.set_ydata([power[1], power[1]])

        # left 3db marker
        self.cursor_left_3db.set_xdata([xmin, xmax])
        self.cursor_left_3db.set_ydata([power[0], power[0]])

        # right 3db marker
        self.cursor_right_3db.set_xdata([xmin, xmax])
        self.cursor_right_3db.set_ydata([power[2], power[2]])

        # remove right 3db marker if same as left
        if len(wl) == 3 and len(power) == 3 and power[0] == power[2]:
            self.cursor_right_3db.set_xdata([None, None])
            self.cursor_right_3db.set_ydata([None, None])

        self.redraw()



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
