# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:22:35 2019

@author: qchat
"""

import os

import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
from qtpy import QtWidgets

from ... import config
from ... import utilities


class FigureManager:

    def __init__(self, gui: QtWidgets.QMainWindow):

        self.gui = gui

        # Import Autolab config
        monitor_config = config.get_monitor_config()
        self.precision = int(monitor_config['precision'])
        self.do_save_figure = utilities.boolean(monitor_config['save_figure'])

        # Configure and initialize the figure in the GUI
        self.fig, self.ax = utilities.pyqtgraph_fig_ax()
        self.gui.graph.addWidget(self.fig)
        self.figMap = pg.ImageView()
        self.gui.graph.addWidget(self.figMap)
        self.figMap.hide()

        self.setLabel('x', self.gui.xlabel)
        self.setLabel('y', self.gui.ylabel)

        self.plot = self.ax.plot([], [], symbol='x', pen='r', symbolPen='r',
                                 symbolSize=10, symbolBrush='r')
        self.plot_mean = self.ax.plot([], [], pen=pg.mkPen(
            color=0.4, style=pg.QtCore.Qt.DashLine))
        self.plot_min = self.ax.plot([], [], pen=pg.mkPen(color=0.4))
        self.plot_max = self.ax.plot([], [], pen=pg.mkPen(color=0.4))
        self.ymin = None
        self.ymax = None

    # PLOT DATA
    ###########################################################################

    def update(self, xlist: list, ylist: list):
        """ This function update the figure in the GUI """
        if xlist is None: # image
            self.fig.hide()
            self.gui.min_checkBox.hide()
            self.gui.mean_checkBox.hide()
            self.gui.max_checkBox.hide()
            self.figMap.show()
            self.figMap.setImage(ylist)
            return None

        # Data retrieval
        self.plot.setData(xlist, ylist)

        xlist, ylist = self.plot.getData()

        if xlist is None or ylist is None or len(xlist) == 0 or len(ylist) == 0:
            return None

        xmin = min(xlist)
        xmax = max(xlist)
        ymin = min(ylist)
        ymax = max(ylist)

        if self.ymin is None: self.ymin = ymin
        if self.ymax is None: self.ymax = ymax

        if ymin < self.ymin: self.ymin = ymin
        if ymax > self.ymax: self.ymax = ymax

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

    def setLabel(self, axe: str, value: str):
        """ This function changes the label of the given axis """
        axes = {'x':'bottom', 'y':'left'}
        if value == '': value = ' '
        self.ax.setLabel(axes[axe], value, **{'color':0.4, 'font-size': '12pt'})

    def clear(self):
        self.ymin = None
        self.ymax = None
        self.update([],[])
        self.gui.dataDisplay.clear()

    def save(self, filename: str):
        """ This function save the figure with the provided filename """
        if self.do_save_figure:
            raw_name, extension = os.path.splitext(filename)
            new_filename = raw_name+".png"

            if not self.fig.isHidden():
                exporter = pg.exporters.ImageExporter(self.fig.plotItem)
                exporter.export(new_filename)
            else:
                self.figMap.export(new_filename)
