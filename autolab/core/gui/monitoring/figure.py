# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:22:35 2019

@author: qchat
"""

import os

import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph.Qt import QtGui

from ... import config
from ... import utilities


class FigureManager:

    def __init__(self,gui):

        self.gui = gui

        # Import Autolab config
        monitor_config = config.get_monitor_config()
        self.precision = int(monitor_config['precision'])
        self.do_save_figure = utilities.boolean(monitor_config['save_figure'])

        # Configure and initialize the figure in the GUI
        self.fig = pg.PlotWidget()
        self.ax = self.fig.getPlotItem()
        self.ax.setLabel('bottom', self.gui.xlabel, **{'color':0.4, 'font-size': '12pt'})
        self.ax.setLabel('left', self.gui.ylabel, **{'color':0.4, 'font-size': '12pt'})

        # Set your custom font for both axes
        my_font = QtGui.QFont("Times", 12)
        my_font_tick = QtGui.QFont("Times", 10)
        self.ax.getAxis("bottom").label.setFont(my_font)
        self.ax.getAxis("left").label.setFont(my_font)
        self.ax.getAxis("bottom").setTickFont(my_font_tick)
        self.ax.getAxis("left").setTickFont(my_font_tick)
        self.ax.showGrid(x=True, y=True)

        self.plot = self.ax.plot([],[], symbol='x', pen='r', symbolPen='r', symbolSize=10)
        self.plot_mean = self.ax.plot([],[], pen = pg.mkPen(color=0.4, style=pg.QtCore.Qt.DashLine))
        self.plot_min = self.ax.plot([],[], pen =  pg.mkPen(color=0.4))
        self.plot_max = self.ax.plot([],[], pen =  pg.mkPen(color=0.4))
        self.ymin = None
        self.ymax = None

        vb = self.ax.getViewBox()
        vb.enableAutoRange(enable=True)
        vb.setBorder(pg.mkPen(color=0.4))

        ## Text label for the data coordinates of the mouse pointer
        self.dataLabel = pg.LabelItem(color='k', parent=self.ax.getAxis('bottom'))
        self.dataLabel.anchor(itemPos=(1,1), parentPos=(1,1), offset=(0,0))

        # data reader signal connection
        self.ax.scene().sigMouseMoved.connect(self.mouseMoved)

        self.gui.graph.addWidget(self.fig)


    # PLOT DATA
    ###########################################################################

    def update(self,xlist,ylist):

        """ This function update the figure in the GUI """

        # Data retrieval
        self.plot.setData(xlist, ylist)

        xlist, ylist = self.plot.getData()

        if len(xlist) == 0 or len(ylist) == 0:
            return

        xmin = min(xlist)
        xmax = max(xlist)
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

            self.plot_mean.setData([xmin, xmax], [ymean, ymean])

        # Min update
        if self.gui.min_checkBox.isChecked():
            self.plot_min.setData([xmin, xmax], [self.ymin, self.ymin])

        # Max update
        if self.gui.max_checkBox.isChecked():
            self.plot_max.setData([xmin, xmax], [self.ymax, self.ymax])

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


    def mouseMoved(self, point):
        """ This function marks the position of the cursor in data coordinates"""

        vb = self.ax.getViewBox()
        mousePoint = vb.mapSceneToView(point)
        l = f'x = {mousePoint.x():g},  y = {mousePoint.y():g}'
        self.dataLabel.setText(l)


    def clear(self):
        self.ymin = None
        self.ymax = None
        self.update([],[])
        self.gui.dataDisplay.clear()


    def save(self,filename):
        """ This function save the figure with the provided filename """
        if self.do_save_figure:
            raw_name, extension = os.path.splitext(filename)
            new_filename = raw_name+".png"
            exporter = pg.exporters.ImageExporter(self.fig.plotItem)
            exporter.export(new_filename)
