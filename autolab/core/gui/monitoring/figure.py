# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:22:35 2019

@author: qchat
"""

import os
import numpy as np
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from ... import config


class FigureManager:

    def __init__(self,gui):

        self.gui = gui

        # Import Autolab config
        monitor_config = config.get_monitor_config()
        self.precision = int(monitor_config['precision'])

        # Configure and initialize the figure in the GUI
        self.fig = Figure()
        matplotlib.rcParams.update({'font.size': 12})
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel(self.gui.xlabel)
        self.ax.set_ylabel(self.gui.ylabel)
        self.ax.grid()

        self.plot = self.ax.plot([],[],'x-',color='r')[0]
        self.plot_mean = self.ax.plot([],[],'--',color='grey')[0]
        self.plot_min = self.ax.plot([],[],'-',color='grey')[0]
        self.plot_max = self.ax.plot([],[],'-',color='grey')[0]
        self.ymin = None
        self.ymax = None
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
            getattr(self.gui,f'autoscale_{axe}_checkBox').stateChanged.connect(lambda b, axe=axe:self.autoscaleChanged(axe))
            getattr(self.gui,f'autoscale_{axe}_checkBox').setChecked(True)



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

        data = getattr(self.plot,f'get_{axe}data')()
        if len(data) > 0 :
            minValue = min(data)
            maxValue = max(data)
            if (minValue,maxValue) != self.getRange(axe) :
                self.setRange(axe,(minValue,maxValue))

            self.toolbar.update()


    # RANGE
    ###########################################################################

    def getRange(self,axe):

        """ This function returns the current range of the given axis """

        return getattr(self.ax,f'get_{axe}lim')()



    def setRange(self,axe,r):

        """ This function sets the current range of the given axis """

        if r[0] != r[1]:
            if axe == "x" and type(self.plot.get_xdata()) is list:
                getattr(self.ax,f'set_{axe}lim')(r[0], r[1]+(r[1]-r[0])*0.1)
            else:
                getattr(self.ax,f'set_{axe}lim')(r[0]-(r[1]-r[0])*0.1, r[1]+(r[1]-r[0])*0.1)
        else:
            getattr(self.ax,f'set_{axe}lim')(r[0]-0.1, r[1]+0.1)



    # PLOT DATA
    ###########################################################################

    def update(self,xlist,ylist):

        """ This function update the figure in the GUI """

        # Data retrieval
        self.plot.set_xdata(xlist)
        self.plot.set_ydata(ylist)

        # X axis update
        xlist = self.plot.get_xdata()

        if not getattr(xlist, 'size', len(xlist)) or not getattr(ylist, 'size', len(ylist)):
            self.redraw()
            return

        xmin = min(xlist)
        xmax = max(xlist)

        # Autoscale
        if self.isAutoscaleEnabled('x') is True : self.doAutoscale('x')
        if self.isAutoscaleEnabled('y') is True : self.doAutoscale('y')

        # Y axis update
        ylist = self.plot.get_ydata()
        ymin = min(ylist)
        ymax = max(ylist)

        if self.ymin is None:
            self.ymin = ymin
        if self.ymax is None:
            self.ymax = ymax

        if ymin < self.ymin:
            self.ymin = ymin
        if ymax > self.ymax:
            self.ymax = ymax

        # Mean update
        if self.gui.mean_checkBox.isChecked():
            ymean = np.mean(ylist)
            self.plot_mean.set_xdata([xmin, xmax])
            self.plot_mean.set_ydata([ymean, ymean])

        # Min update
        if self.gui.min_checkBox.isChecked():
            self.plot_min.set_xdata([xmin, xmax])
            self.plot_min.set_ydata([self.ymin, self.ymin])

        # Max update
        if self.gui.max_checkBox.isChecked():
            self.plot_max.set_xdata([xmin, xmax])
            self.plot_max.set_ydata([self.ymax, self.ymax])

        # Figure finalization
        if len(ylist) >= 1:
            self.gui.dataDisplay.setText(f'{ylist[-1]:.{self.precision}g}')

            width = self.gui.dataDisplay.geometry().width()
            # height = self.gui.dataDisplay.geometry().height()
            # limit = min((width, height))
            new_size = max(width/8, 10)
            new_size = min(new_size, 25)

            font = self.gui.dataDisplay.font()
            font.setPointSize(int(new_size))
            self.gui.dataDisplay.setFont(font)

        self.redraw()


    def redraw(self):

        """ This function finalize the figure update in the GUI """
        try :
            self.fig.tight_layout()
        except :
            pass
        self.canvas.draw()


    def clear(self):
        self.ymin = None
        self.ymax = None
        self.update([],[])
        self.gui.dataDisplay.clear()


    def save(self,filename):
        """ This function save the figure with the provided filename """

        raw_name, extension = os.path.splitext(filename)
        new_filename = raw_name+".png"
        self.fig.savefig(new_filename, dpi=300)
