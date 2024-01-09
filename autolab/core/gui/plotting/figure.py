# -*- coding: utf-8 -*-
"""
Created on Oct 2022

@author: jonathan based on qchat
"""
import os

import pyqtgraph as pg
import pyqtgraph.exporters

from ... import utilities


class FigureManager :

    def __init__(self,gui):

        self.gui = gui
        self.curves = []

        # Configure and initialize the figure in the GUI
        self.fig, self.ax = utilities.pyqtgraph_fig_ax()
        self.gui.graph.addWidget(self.fig)

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
                        self.gui.setStatus(f'Data {new_dataset.name} already plotted !',5000)
                        return
                    else:
                        self.gui.data_comboBox.setCurrentIndex(dataSet_id-1)
                        self.gui.dataManager.updateDisplayableResults()

                        self.gui.save_pushButton.setEnabled(True)

                        self.gui.clear_pushButton.setEnabled(True)
                        self.gui.clear_all_pushButton.setEnabled(True)
                        self.gui.openButton.setEnabled(True)

                        self.gui.setStatus(f'Data {new_dataset.name} updated !',5000)
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

            self.gui.data_comboBox.setCurrentIndex(dataSet_id-1)  # trigger the currentIndexChanged event but don't trigger activated

            # dataset.update(new_dataset)

            self.gui.dataManager.updateDisplayableResults()

            self.gui.save_pushButton.setEnabled(True)

            self.gui.clear_pushButton.setEnabled(True)
            self.gui.clear_all_pushButton.setEnabled(True)
            self.gui.openButton.setEnabled(True)

            self.gui.setStatus(f'Data {new_dataset.name} plotted !',5000)

        except Exception as e :
            self.gui.setStatus(f'ERROR The data cannot be plotted with the given dataset : {str(e)}',10000, False)


    # AXE LABEL
    ###########################################################################

    def getLabel(self, axe: str):
        """ This function get the label of the given axis """
        return getattr(self.gui, f"variable_{axe}_comboBox").currentText()

    def setLabel(self, axe: str, value: str):
        """ This function changes the label of the given axis """
        axes = {'x':'bottom', 'y':'left'}
        if value == '': value = ' '
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
                            curve = self.ax.plot(x, y, pen=color)
                            curve.setAlpha(alpha, False)
                        else:
                            curve = self.ax.plot(x, y, symbol='x', symbolPen=color, symbolSize=10, pen=color, symbolBrush=color)
                            curve.setAlpha(alpha, False)
                    elif i > (data_id-1):
                        if len(x) > 300:
                            curve = self.ax.plot(x, y, pen=pg.mkPen(color=color, style=pg.QtCore.Qt.DashLine))
                            curve.setAlpha(alpha, False)
                        else:
                            curve = self.ax.plot(x, y, symbol='+', symbolPen=color, symbolSize=10, pen=pg.mkPen(color=color, style=pg.QtCore.Qt.DashLine), symbolBrush=color)
                            curve.setAlpha(alpha, False)
                    self.curves.append(curve)

            # Data
            i = (data_id-1)
            subdata = data[i]

            if subdata is not None:
                subdata = subdata.astype(float)
                x = subdata.loc[:,variable_x]
                y = subdata.loc[:,variable_y]

                # Apprearance:
                color = '#1f77b4'
                alpha = 1

                # Plot
                if len(x) > 300:
                    curve = self.ax.plot(x, y, pen=color, clear=True)
                    curve.setAlpha(alpha, False)
                else:
                    curve = self.ax.plot(x, y, symbol='x', symbolPen=color, symbolSize=10, pen=color, symbolBrush=color)
                    curve.setAlpha(alpha, False)
                self.curves.append(curve)

            self.gui.plugin_refresh()


    # SAVE FIGURE
    ###########################################################################

    def save(self,filename):
        """ This function save the figure with the provided filename """

        raw_name, extension = os.path.splitext(filename)
        new_filename = raw_name+".png"
        exporter = pg.exporters.ImageExporter(self.fig.plotItem)
        exporter.export(new_filename)
