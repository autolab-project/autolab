# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 15:11:17 2021

@author: Jonathan Peltier based on qchat
"""

import os

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
import matplotlib


class FigureManager:

    def __init__(self,gui):

        self.gui = gui

        # Configure and initialize the figure in the GUI
        self.fig = Figure()
        matplotlib.rcParams.update({'font.size': 12})
        self.ax = self.fig.add_subplot(111)

        self.ax.set_xlabel('Wavelength [nm]')
        self.ax.set_ylabel('Transfert function (dB)')

        self.ax.minorticks_on()
        self.ax.grid(True, which='major')
        self.ax.grid(True, which='minor', alpha=0.4)

        self.curves = []

        self.cursor_left = self.ax.plot([None],[None],'--',color='grey', label="Cursor left")[0]
        self.cursor_right = self.ax.plot([None],[None],'--',color='grey', label="Cursor right")[0]
        self.cursor_max = self.ax.plot([None],[None],'--',color='grey', label="Cursor max")[0]
        self.cursor_left_3db = self.ax.plot([None],[None],'--',color='grey', label="Cursor left 3db")[0]
        self.cursor_right_3db = self.ax.plot([None],[None],'--',color='grey', label="Cursor right 3db")[0]
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


    def reloadData(self):

        """ This function update the figure in the GUI """

        self.clearData()

        all_data = dict(self.gui.dataManager.getAllData()).copy() # get copy of data

        if len(all_data) != 0:

            data_name = self.gui.data_comboBox.currentText() # get principal plot name
            test = all_data.get(data_name)

            if test is not None:
                all_data.pop(data_name)  # remove principal plot

            for data in all_data.values():
                try:  # not the most useful data but plot them if exists (could become problematic if overlap with "1")
                    curve = self.ax.plot(data["L"], data["O"], '-', color='k', alpha=0.5)[0]
                    self.curves.append(curve)
                except:
                    pass
                curve = self.ax.plot(data["L"], data["1"], '-', color='k', alpha=0.8)[0]
                self.curves.append(curve)

        # Data retrieval
        data = self.gui.dataManager.getData()

        if data is not None:
            try:
                curve = self.ax.plot(data["L"], data["O"], '-', color='C1', alpha=0.5, label="Laser output (dBm)")[0]
                self.curves.append(curve)
            except:
                pass
            curve = self.ax.plot(data["L"], data["1"], '-', color='C0', label="Transfert function (dB)")[0]
            self.curves.append(curve)

        # Figure finalization
        self.redraw()

    def doAutoscale(self):

        if len(self.curves) != 0:
            self.toolbar.update()

            curve = self.curves[-1]

            # X axis update
            xlist = curve.get_xdata()

            xmin = min(xlist)
            xmax = max(xlist)
            if xmin != xmax :
                self.ax.set_xlim(xmin-0.02*(xmax-xmin),xmax+0.02*(xmax-xmin))
            else:
                self.ax.set_xlim(xmin-0.1,xmin+0.1)

            # Y axis update
            ylist = curve.get_ydata()
            ymin = min(ylist)
            ymax = max(ylist)
            if ymin != ymax :
                self.ax.set_ylim(ymin-0.1*(ymax-ymin),ymax+0.1*(ymax-ymin))
            else :
                self.ax.set_ylim(ymin-0.1,ymin+0.1)

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
        if extension != ".png":
            extension = ".png"

        new_filename = raw_name+extension
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



    def clearData(self):

        for curve in self.curves:
            curve.remove()
        self.curves = []
        self.redraw()
