# -*- coding: utf-8 -*-
"""
Created on Oct 2022

@author: jonathan based on qchat
"""
import os

import pyqtgraph as pg
import pyqtgraph.exporters  # Needed for pg.exporters.ImageExporter

from qtpy import QtWidgets

from ..GUI_utilities import pyqtgraph_fig_ax


class FigureManager:

    def __init__(self, gui: QtWidgets.QMainWindow):

        self.gui = gui
        self.curves = []

        # Configure and initialize the figure in the GUI
        self.fig, self.ax = pyqtgraph_fig_ax()
        self.gui.graph.addWidget(self.fig)

        # Number of traces
        self.nbtraces = 10

    def start(self, new_dataset=None):
        """ This function display data and ajust buttons """
        try:
            result_names = [dataset.name for dataset in self.gui.dataManager.datasets]
            all_items = [self.gui.data_comboBox.itemText(i) for i in range(self.gui.data_comboBox.count())]

            index = self.gui.data_comboBox.currentIndex()

            if result_names != all_items:  # only refresh if change labels, to avoid gui refresh that prevent user to click on combobox
                self.gui.data_comboBox.clear()
                self.gui.data_comboBox.addItems(result_names)  # slow (0.25s)

            if new_dataset is None:
                if (index + 1) > len(result_names) or index == -1: index = 0
                self.gui.data_comboBox.setCurrentIndex(index)
            else:
                index = self.gui.data_comboBox.findText(new_dataset.name)
                self.gui.data_comboBox.setCurrentIndex(index)

            data_name = self.gui.data_comboBox.currentText() # trigger the currentIndexChanged event but don't trigger activated

            self.gui.dataManager.updateDisplayableResults()

            self.gui.save_pushButton.setEnabled(True)
            self.gui.clear_pushButton.setEnabled(True)
            self.gui.clear_all_pushButton.setEnabled(True)
            self.gui.openButton.setEnabled(True)

            self.gui.setStatus(f'Data {data_name} plotted!', 5000)

        except Exception as e:
            self.gui.setStatus(
                f'ERROR The data cannot be plotted with the given dataset: {e}',
                10000, False)

    # AXE LABEL
    ###########################################################################

    def setLabel(self, axe: str, value: str):
        """ This function changes the label of the given axis """
        axes = {'x': 'bottom', 'y': 'left'}
        if value == '': value = ' '
        self.ax.setLabel(axes[axe], value, **{'color': pg.getConfigOption("foreground"),
                                              'font-size': '12pt'})


    # PLOT DATA
    ###########################################################################

    def clearData(self):
        """ This function removes any plotted curves """
        for curve in self.curves:
            self.ax.removeItem(curve)
        self.curves = []

    def reloadData(self):
        ''' This function removes any plotted curves and reload all required curves from
        data available in the data manager'''
        # Remove all curves
        self.clearData()

        # Get current displayed result
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
            # OPTIMIZE: currently load all data and plot more than self.nbtraces if in middle
            # Should change to only load nbtraces and plot nbtraces
            data = self.gui.dataManager.getData(
                data_len, [variable_x,variable_y], selectedData=0)
            # data = self.gui.dataManager.getData(self.nbtraces,[variable_x,variable_y], selectedData=selectedData)
        except:
            data = None

        # Plot them
        if data is not None:

            for i in range(len(data)):
                if i != (data_id - 1):
                    # Data
                    subdata = data[i]
                    if subdata is None:
                        continue

                    subdata = subdata.astype(float)
                    x = subdata.loc[:,variable_x]
                    y = subdata.loc[:,variable_y]

                    # Apprearance:
                    color = pg.getConfigOption("foreground")
                    alpha = (self.nbtraces - abs(data_id - 1 - i)) / self.nbtraces
                    if alpha < 0: alpha = 0

                    # Plot
                    # OPTIMIZE: keep previous style to avoid overwriting it everytime

                    if i < (data_id - 1):
                        if len(x) > 300:
                            curve = self.ax.plot(x, y, pen=color)
                            curve.setAlpha(alpha, False)
                        else:
                            curve = self.ax.plot(
                                x, y, symbol='x', symbolPen=color,
                                symbolSize=10, pen=color, symbolBrush=color)
                            curve.setAlpha(alpha, False)
                    elif i > (data_id - 1):
                        if len(x) > 300:
                            curve = self.ax.plot(
                                x, y, pen=pg.mkPen(color=color,
                                                   style=pg.QtCore.Qt.DashLine))
                            curve.setAlpha(alpha, False)
                        else:
                            curve = self.ax.plot(
                                x, y, symbol='x', symbolPen=color, symbolSize=10,
                                pen=pg.mkPen(color=color, style=pg.QtCore.Qt.DashLine),
                                symbolBrush=color)
                            curve.setAlpha(alpha, False)
                    self.curves.append(curve)

            # Data
            i = (data_id - 1)
            subdata = data[i]

            if subdata is not None:
                subdata = subdata.astype(float)
                x = subdata.loc[:, variable_x]
                y = subdata.loc[:, variable_y]

                # Apprearance:
                color = '#1f77b4'
                alpha = 1

                # Plot
                if len(x) > 300:
                    curve = self.ax.plot(x, y, pen=color)
                    curve.setAlpha(alpha, False)
                else:
                    curve = self.ax.plot(
                        x, y, symbol='x', symbolPen=color, symbolSize=10,
                        pen=color, symbolBrush=color)
                    curve.setAlpha(alpha, False)
                self.curves.append(curve)

            self.gui.plugin_refresh()


    # SAVE FIGURE
    ###########################################################################

    def save(self, filename: str):
        """ This function save the figure with the provided filename """

        raw_name, extension = os.path.splitext(filename)
        new_filename = raw_name+".png"
        exporter = pg.exporters.ImageExporter(self.ax)
        exporter.export(new_filename)
