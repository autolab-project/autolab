# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:22:35 2019

@author: qchat
"""

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import os
import numpy as np

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class FigureManager:

    def __init__(self,gui):
        
        self.gui = gui
        
        # Configure and initialize the figure in the GUI
        self.fig = Figure()
        matplotlib.rcParams.update({'font.size': 12})
        self.ax = self.fig.add_subplot(111)        
        self.ax.set_xlabel('Time [s]')
        ylabel = f'{self.gui.variable.address()}'

        if self.gui.variable.unit is not None :
            ylabel += f' ({self.gui.variable.unit})'
        self.ax.set_ylabel(ylabel)
        self.ax.grid()

        self.plot = self.ax.plot([0],[0],'x-',color='r')[0]
        self.plot_mean = self.ax.plot([0],[0],'--',color='grey')[0]
        self.plot_min = self.ax.plot([0],[0],'-',color='grey')[0]
        self.plot_max = self.ax.plot([0],[0],'-',color='grey')[0]
        self.ymin = 0
        self.ymax = 0
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

    def update(self,xlist,ylist):
        
        """ This function update the figure in the GUI """ 
        
        # Data retrieval
        self.plot.set_xdata(xlist)
        self.plot.set_ydata(ylist)

        # update toolbar with new data (remove forward back history and set home to displayed lim)
        self.toolbar.update()
        # self.toolbar.set_message("test") # write texte top-right where cursors values are displayed

        # X axis update
        xlist = self.plot.get_xdata()

        xmin = min(xlist)
        xmax = max(xlist)

        if xmin != xmax :
            self.ax.set_xlim(xmin,xmax+0.15*(xmax-xmin))
        else :
            self.ax.set_xlim(xmin-0.1,xmin+0.1)
        
        # Y axis update
        ylist = self.plot.get_ydata()
        ymin = min(ylist)
        ymax = max(ylist)

        if ymin != ymax :
            self.ax.set_ylim(ymin-0.1*(ymax-ymin),ymax+0.1*(ymax-ymin))
        else :
            self.ax.set_ylim(ymin-0.1,ymin+0.1)

        if self.ymin == 0:
            self.ymin = ymin
        if self.ymax == 0:
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
            self.gui.dataDisplay.display(ylist[-1])

        self.redraw()


    def redraw(self):
        
        """ This function finalize the figure update in the GUI """
        try :
            self.fig.tight_layout()
        except :
            pass
        self.canvas.draw()


    def clear(self):
        self.ymin = 0
        self.ymax = 0
        self.update([0],[0])


    def save(self,filename):
        """ This function save the figure with the provided filename """

        raw_name, extension = os.path.splitext(filename)
        new_filename = raw_name+".png"
        self.fig.savefig(new_filename, dpi=300)
