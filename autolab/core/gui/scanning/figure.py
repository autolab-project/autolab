# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:12:24 2019

@author: qchat
"""

import os
from typing import List

import numpy as np
import pandas as pd
import pyqtgraph as pg
import pyqtgraph.exporters  # Needed for pg.exporters.ImageExporter
from qtpy import QtWidgets, QtCore

from .display import DisplayValues
from ..GUI_instances import openPlotter
from ..GUI_utilities import (get_font_size, setLineEditBackground,
                             pyqtgraph_fig_ax, pyqtgraph_image)
from ..GUI_slider import Slider
from ..icons import icons
from ...variables import Variable


if hasattr(pd.errors, 'UndefinedVariableError'):
    UndefinedVariableError = pd.errors.UndefinedVariableError
elif hasattr(pd.core.computation.ops, 'UndefinedVariableError'): # pd 1.1.5
    UndefinedVariableError = pd.core.computation.ops.UndefinedVariableError
else:
    UndefinedVariableError = Exception


class FigureManager:
    """ Manage the figure of the scanner """

    def __init__(self, gui: QtWidgets.QMainWindow):

        self.gui = gui
        self.curves = []
        self.filter_condition = []

        self._font_size = get_font_size()

        # Configure and initialize the figure in the GUI
        self.fig, self.ax = pyqtgraph_fig_ax()
        self.gui.graph.addWidget(self.fig)
        self.figMap, widget = pyqtgraph_image()
        self.gui.graph.addWidget(widget)
        self.figMap.hide()

        self.gui.variable_x_comboBox.activated.connect(
            self.axisChanged)
        self.gui.variable_x2_comboBox.activated.connect(
            self.axisChanged)
        self.gui.variable_y_comboBox.activated.connect(
            self.axisChanged)

        pgv = pg.__version__.split('.')
        if int(pgv[0]) == 0 and int(pgv[1]) < 12:
            self.gui.variable_x2_checkBox.setEnabled(False)
            self.gui.variable_x2_checkBox.setToolTip(
                "Can't use 2D plot for scan, need pyqtgraph >= 0.13.2")
            self.gui.setStatus(
                "Can't use 2D plot for scan, need pyqtgraph >= 0.13.2",
                10000, False)
        else:
            self.fig.activate_img()
            self.gui.variable_x2_checkBox.stateChanged.connect(self.reloadData)

        # Number of traces
        self.nbtraces = 5
        self.gui.nbTraces_lineEdit.setText(f'{self.nbtraces:g}')
        self.gui.nbTraces_lineEdit.returnPressed.connect(self.nbTracesChanged)
        self.gui.nbTraces_lineEdit.textEdited.connect(
            lambda: setLineEditBackground(
                self.gui.nbTraces_lineEdit, 'edited', self._font_size))
        setLineEditBackground(
            self.gui.nbTraces_lineEdit, 'synced', self._font_size)

        # Window to show scan data
        self.gui.displayScanData_pushButton.setIcon(icons['DataFrame'])
        self.gui.displayScanData_pushButton.clicked.connect(
            self.displayScanDataButtonClicked)
        self.gui.displayScanData_pushButton.hide()
        self.displayScan = DisplayValues("Scan", size=(500, 300))
        self.displayScan.setWindowIcon(icons['DataFrame'])

        self.gui.sendScanData_pushButton.setIcon(icons['plotter'])
        self.gui.sendScanData_pushButton.clicked.connect(
            self.sendScanDataButtonClicked)
        self.gui.sendScanData_pushButton.hide()

        # comboBox with scan id
        self.gui.data_comboBox.activated.connect(self.data_comboBoxClicked)
        self.gui.data_comboBox.hide()

        # Combobo to select the recipe to plot
        self.gui.scan_recipe_comboBox.activated.connect(
            self.scan_recipe_comboBoxCurrentChanged)
        self.gui.scan_recipe_comboBox.hide()

        # Combobox to select datafram to plot
        self.gui.dataframe_comboBox.activated.connect(
            self.dataframe_comboBoxCurrentChanged)
        self.gui.dataframe_comboBox.addItem("Scan")
        self.gui.dataframe_comboBox.hide()

        # Filter widgets
        self.gui.scrollArea_filter.hide()
        self.gui.checkBoxFilter.stateChanged.connect(self.checkBoxFilterChanged)
        self.gui.addFilterPushButton.clicked.connect(
            lambda: self.addFilterClicked('standard'))
        self.gui.addSliderFilterPushButton.clicked.connect(
            lambda: self.addFilterClicked('slider'))
        self.gui.addCustomFilterPushButton.clicked.connect(
            lambda: self.addFilterClicked('custom'))
        self.gui.splitterGraph.setSizes([9000, 1000])  # fixe wrong proportion

    def refresh_filters(self):
        """ Apply filters to data """
        self.filter_condition.clear()

        if self.gui.checkBoxFilter.isChecked():
            # OPTIMIZE: Should never based code on widget/layout position. Can instead create dict or other with all information about filter widgets
            for i in range(self.gui.layoutFilter.count()):
                layout = self.gui.layoutFilter.itemAt(i).widget().layout()

                if layout.count() == 5:
                    enable = bool(layout.itemAt(0).widget().isChecked())
                    variableComboBox = layout.itemAt(1).widget()
                    self.refresh_filter_combobox(variableComboBox)
                    name = variableComboBox.currentText()
                    condition_raw = layout.itemAt(2).widget().currentText()
                    valueWidget = layout.itemAt(3).widget()
                    if isinstance(valueWidget, Slider):
                        value = float(valueWidget.valueWidget.text())  # for custom slider
                        setLineEditBackground(
                            valueWidget.valueWidget, 'synced', self._font_size)
                    else:
                        try:
                            value = float(valueWidget.text())  # for editline
                        except:
                            continue
                        setLineEditBackground(
                            valueWidget, 'synced', self._font_size)

                    convert_condition = {
                        '==': np.equal, '!=': np.not_equal,
                        '<': np.less, '<=': np.less_equal,
                        '>=': np.greater_equal, '>': np.greater
                        }
                    condition = convert_condition[condition_raw]

                    filter_i = {'enable': enable, 'condition': condition,
                                'name': name, 'value': value}

                elif layout.count() == 3:
                    enable = bool(layout.itemAt(0).widget().isChecked())
                    customConditionWidget = layout.itemAt(1).widget()
                    condition_txt = customConditionWidget.text()
                    try:
                        pd.eval(condition_txt)  # syntax check
                    except UndefinedVariableError:
                        pass
                    except Exception:
                        continue
                    setLineEditBackground(
                        customConditionWidget, 'synced', self._font_size)

                    filter_i = {'enable': enable, 'condition': condition_txt,
                                'name': None, 'value': None}

                self.filter_condition.append(filter_i)

        self.reloadData()

    def refresh_filter_combobox(self, comboBox):
        items = []
        for scanset in self.gui.dataManager.datasets:
            for dataset in scanset.values():
                for key in dataset.data.columns:
                    if key not in items:
                        items.append(key)

        existing_items = [comboBox.itemText(i) for i in range(comboBox.count())]
        if items != existing_items:
            comboBox.clear()
            comboBox.addItems(items)

    def addFilterClicked(self, filter_type):
        """ Add filter condition """
        conditionWidget = QtWidgets.QFrame()
        conditionWidget.setFrameShape(QtWidgets.QFrame.StyledPanel)
        conditionLayout = QtWidgets.QHBoxLayout(conditionWidget)

        filterCheckBox = QtWidgets.QCheckBox()
        filterCheckBox.setToolTip('Toggle filter')
        filterCheckBox.setCheckState(QtCore.Qt.Checked)
        filterCheckBox.stateChanged.connect(self.refresh_filters)
        conditionLayout.addWidget(filterCheckBox)

        if filter_type in ('standard', 'slider'):
            variableComboBox = QtWidgets.QComboBox()

            self.refresh_filter_combobox(variableComboBox)
            variableComboBox.activated.connect(self.refresh_filters)
            filterCheckBox.stateChanged.connect(
                lambda: self.refresh_filter_combobox(variableComboBox))
            conditionLayout.addWidget(variableComboBox)

            filterComboBox = QtWidgets.QComboBox()
            items = ['==', '!=', '<', '<=', '>=', '>']
            filterComboBox.addItems(items)
            filterComboBox.activated.connect(self.refresh_filters)
            conditionLayout.addWidget(filterComboBox)

            if filter_type == 'standard':
                valueWidget = QtWidgets.QLineEdit()
                valueWidget.setText('1')
                valueWidget.returnPressed.connect(self.refresh_filters)
                valueWidget.textEdited.connect(lambda: setLineEditBackground(
                    valueWidget, 'edited', self._font_size))
                setLineEditBackground(valueWidget, 'synced', self._font_size)
                conditionLayout.addWidget(valueWidget)
            elif filter_type == 'slider':
                var = Variable('temp', 1.)
                valueWidget = Slider(var)
                valueWidget.minWidget.setText('1.0')
                valueWidget.minWidgetValueChanged()
                valueWidget.changed.connect(self.refresh_filters)
                valueWidget.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                          QtWidgets.QSizePolicy.Fixed)
                conditionLayout.addWidget(valueWidget)

        elif filter_type == 'custom':
            customConditionWidget = QtWidgets.QLineEdit()
            customConditionWidget.setToolTip(
                "Filter condition can be 'id == 1' '1 <= amplitude <= 2' 'id in (1, 2)'")
            customConditionWidget.setText('id == 1')
            customConditionWidget.returnPressed.connect(self.refresh_filters)
            customConditionWidget.textEdited.connect(
                lambda: setLineEditBackground(
                    customConditionWidget, 'edited', self._font_size))
            setLineEditBackground(customConditionWidget, 'synced', self._font_size)
            conditionLayout.addWidget(customConditionWidget)

        removePushButton = QtWidgets.QPushButton()
        removePushButton.setIcon(icons['remove'])
        removePushButton.clicked.connect(
            lambda: self.remove_filter(conditionWidget))
        conditionLayout.addWidget(removePushButton)

        self.gui.layoutFilter.addWidget(conditionWidget)
        self.refresh_filters()

    def remove_filter(self, widget):
        """ Remove filter condition """
        for j in reversed(range(widget.layout().count())):
            widget.layout().itemAt(j).widget().setParent(None)
        widget.setParent(None)
        self.refresh_filters()

    def checkBoxFilterChanged(self):
        """ Show/hide filters frame and refresh filters """
        if self.gui.checkBoxFilter.isChecked():
            if not self.gui.scrollArea_filter.isVisible():
                self.gui.scrollArea_filter.show()
        else:
            if self.gui.scrollArea_filter.isVisible():
                self.gui.scrollArea_filter.hide()

        self.refresh_filters()

    def data_comboBoxClicked(self):
        """ This function select a dataset """
        if len(self.gui.dataManager.datasets) != 0:
            self.gui.data_comboBox.show()
            scanset = self.gui.dataManager.getLastSelectedDataset()
            index = self.gui.scan_recipe_comboBox.currentIndex()

            result_names = list(scanset)
            items = [self.gui.scan_recipe_comboBox.itemText(i) for i in range(
                self.gui.scan_recipe_comboBox.count())]

            if items != result_names:
                self.gui.scan_recipe_comboBox.clear()
                self.gui.scan_recipe_comboBox.addItems(result_names)
                if (index + 1) > len(result_names) or index == -1: index = 0
                self.gui.scan_recipe_comboBox.setCurrentIndex(index)

            if self.gui.scan_recipe_comboBox.count() > 1:
                self.gui.scan_recipe_comboBox.show()
            else:
                self.gui.scan_recipe_comboBox.hide()

            self.dataframe_comboBoxCurrentChanged()
        else:
            self.gui.data_comboBox.hide()

        # Change save button text to inform on scan that will be saved
        self.gui.save_pushButton.setText(
            'Save '+self.gui.data_comboBox.currentText().lower())

    def scan_recipe_comboBoxCurrentChanged(self):
        self.dataframe_comboBoxCurrentChanged()

    def dataframe_comboBoxCurrentChanged(self):

        self.updateDataframe_comboBox()

        self.gui.dataManager.updateDisplayableResults()
        self.reloadData()

        data_name = self.gui.dataframe_comboBox.currentText()

        if data_name == "Scan" or self.fig.isHidden():
            self.gui.variable_x2_checkBox.show()
        else:
            self.gui.variable_x2_checkBox.hide()

    def updateDataframe_comboBox(self):
        # Executed each time the queue is read
        index = self.gui.dataframe_comboBox.currentIndex()
        recipe_name = self.gui.scan_recipe_comboBox.currentText()
        scanset = self.gui.dataManager.getLastSelectedDataset()

        if scanset is None or recipe_name not in scanset: return None

        dataset = scanset[recipe_name]

        result_names = ["Scan"] + [
            i for i, val in dataset.data_arrays.items() if not isinstance(
                val[0], (str, tuple))]  # Remove this condition if want to plot string or tuple: Tuple[List[str], int]

        items = [self.gui.dataframe_comboBox.itemText(i) for i in range(
            self.gui.dataframe_comboBox.count())]

        if result_names != items:  # only refresh if change labels, to avoid gui refresh that prevent user to click on combobox
            self.gui.dataframe_comboBox.clear()
            self.gui.dataframe_comboBox.addItems(result_names)
            if (index + 1) > len(result_names): index = 0
            self.gui.dataframe_comboBox.setCurrentIndex(index)

        if len(result_names) == 1:
            self.gui.dataframe_comboBox.hide()
        else:
            self.gui.dataframe_comboBox.show()

    # AXE LABEL
    ###########################################################################

    def setLabel(self, axe: str, value: str):
        """ Changes the label of the given axis """
        axes = {'x':'bottom', 'y':'left'}
        if value == '': value = ' '
        self.ax.setLabel(axes[axe], value, **{'color': pg.getConfigOption("foreground"),
                                              'font-size': '12pt'})

    # PLOT DATA
    ###########################################################################

    def clearData(self):
        """ Removes any plotted curves """
        for curve in self.curves:
            try: self.ax.removeItem(curve)  # try because curve=None if close before end of scan
            except: pass
        self.curves = []
        self.figMap.clear()

        if self.fig.img_active:
            if self.fig.img.isVisible():
                self.fig.img.hide() # OPTIMIZE: would be better to erase data

    def reloadData(self):
        ''' Removes any plotted curves and reload all required
        curves from data available in the data manager'''
        # Remove all curves
        self.clearData()

        # Get current displayed result
        data_name = self.gui.dataframe_comboBox.currentText()
        variable_x = self.gui.variable_x_comboBox.currentText()
        variable_x2 = self.gui.variable_x2_comboBox.currentText()
        variable_y = self.gui.variable_y_comboBox.currentText()
        data_id = int(self.gui.data_comboBox.currentIndex()) + 1
        data_len = len(self.gui.dataManager.datasets)
        selectedData = data_len - data_id

        if variable_x is None:
            return None

        # Label update
        self.setLabel('x', variable_x)
        self.setLabel('y', variable_y)

        self.displayed_as_image = self.gui.variable_x2_checkBox.isChecked()

        if data_name == "Scan" and not self.displayed_as_image:
            nbtraces_temp  = self.nbtraces
            if not self.gui.nbTraces_lineEdit.isVisible():
                self.gui.nbTraces_lineEdit.show()
                self.gui.graph_nbTracesLabel.show()
        else:
            # decided to only show the last scan data for dataframes and scan displayed as image
            nbtraces_temp = 1
            if self.gui.nbTraces_lineEdit.isVisible():
                self.gui.nbTraces_lineEdit.hide()
                self.gui.graph_nbTracesLabel.hide()

        # Load the last results data
        if self.displayed_as_image:
            var_to_display = [variable_x, variable_x2, variable_y]
        else:
            var_to_display = [variable_x, variable_y]

        can_filter = var_to_display not in (['', ''], ['', '', ''])  # Allows to differentiate images from scan or arrays. Works only because on dataframe_comboBoxCurrentChanged, updateDisplayableResults is called
        filter_condition = self.filter_condition if (
            self.gui.checkBoxFilter.isChecked() and can_filter) else []
        data: List[pd.DataFrame] = self.gui.dataManager.getData(
            nbtraces_temp, var_to_display,
            selectedData=selectedData, data_name=data_name,
            filter_condition=filter_condition)

        # Plot data
        if data is not None:
            true_nbtraces = max(nbtraces_temp, len(data))  # not good but avoid error

            if len(data) != 0:
                # update displayScan
                self.refreshDisplayScanData()
                if not self.gui.displayScanData_pushButton.isVisible():
                    self.gui.displayScanData_pushButton.show()
                    self.gui.sendScanData_pushButton.show()

                for temp_data in data:
                    if temp_data is not None: break
                else: return None

            # If plot scan as image
            if data_name == "Scan" and self.displayed_as_image:

                if not self.gui.frameAxis.isVisible():
                    self.gui.frameAxis.show()

                if not self.gui.variable_x2_comboBox.isVisible():
                    self.gui.variable_x2_comboBox.show()
                    self.gui.label_scan_2D.show()
                    self.gui.label_y_axis.setText('Z axis')

                if not self.fig.isVisible():
                    self.figMap.hide()
                    self.fig.show()

                if not self.fig.colorbar.isVisible():
                    self.fig.colorbar.show()

                self.setLabel('x', variable_x)
                self.setLabel('y', variable_x2)

                if variable_x == variable_x2:
                    return None

                # Data
                if len(data) == 0:
                    return None

                subdata: pd.DataFrame = data[-1]  # Only plot last scan

                if subdata is None:
                    return None

                subdata = subdata.astype(float)

                try:
                    pivot_table = subdata.pivot(
                        index=variable_x, columns=variable_x2, values=variable_y)
                except ValueError:  # if more than 2 parameters
                    return None

                # Extract data for plotting
                x = np.array(pivot_table.columns)
                y = np.array(pivot_table.index)
                z = np.array(pivot_table)

                if 0 in (len(x), len(y), len(z)):
                    return None

                self.fig.update_img(x, y, z)

                if not self.fig.img.isVisible():
                    self.fig.img.show()

                return None

            # If plot scan or array
            if self.gui.variable_x2_comboBox.isVisible():
                self.gui.variable_x2_comboBox.hide()
                self.gui.label_scan_2D.hide()
                self.gui.label_y_axis.setText('Y axis')

            if self.fig.img_active:
                if self.fig.colorbar.isVisible():
                    self.fig.colorbar.hide()

                if self.fig.img.isVisible():
                    self.fig.img.hide()

            if len(data) != 0 and isinstance(data[0], np.ndarray):  # to avoid errors
                images = np.empty((len(data), *temp_data.shape))

            for i in range(len(data)):
                # Data
                subdata: pd.DataFrame = data[i]

                if subdata is None: continue

                if isinstance(subdata, str):  # Could think of someway to show text. Currently removed it from dataset directly
                    print("Warning: Can't display text")
                    continue
                if isinstance(subdata, tuple):
                    print("Warning: Can't display tuple")
                    continue

                subdata = subdata.astype(float)

                if isinstance(subdata, np.ndarray):  # is image
                    if self.fig.isVisible():
                        self.fig.hide()
                        self.figMap.show()
                    if self.gui.frameAxis.isVisible():
                        self.gui.frameAxis.hide()
                    # OPTIMIZE: should be able to plot images of different shapes
                    if subdata.shape == temp_data.shape:
                        images[i] = subdata
                        has_bad_shape = False
                    else:
                        has_bad_shape = True
                    if i == len(data)-1:
                        if images.ndim == 3:
                            if self.figMap.imageItem.axisOrder == 'col-major':
                                x, y = (0, 1)
                            else:
                                x, y = (1, 0)
                            axes = {'t': 0, 'x': x+1, 'y': y+1, 'c': None}  # to avoid a special case in pg that incorrectly assumes the axis
                        else:
                            axes = None
                        if has_bad_shape:
                            images_plot = np.array([subdata])
                            print(f"Warning only plot last {data_name}." \
                                  " Images should have the same shape." \
                                  f" Given {subdata.shape} & {temp_data.shape}")
                        else:
                            images_plot = images
                        try:
                            self.figMap.setImage(images_plot, axes=axes)  # Defined which axe is major using pg.setConfigOption('imageAxisOrder', 'row-major') in gui start-up so no need to .T data
                        except Exception as e:
                            print(f"Warning can't plot {data_name}: {e}")
                            continue
                        self.figMap.setCurrentIndex(len(self.figMap.tVals))

                else: # not an image (is pd.DataFrame)
                    if not self.fig.isVisible():
                        self.fig.show()
                        self.figMap.hide()
                    if not self.gui.frameAxis.isVisible():
                        self.gui.frameAxis.show()

                    try:  # If empty dataframe can't find variables
                        x = subdata.loc[:, variable_x]
                        y = subdata.loc[:, variable_y]
                    except KeyError:
                        continue

                    if isinstance(x, pd.DataFrame):
                        print('Warning: At least two variables have the same name.' \
                              f" Data plotted is incorrect for {variable_x}!")
                    if isinstance(y, pd.DataFrame):
                        print('Warning: At least two variables have the same name.' \
                              f" Data plotted is incorrect for {variable_y}!")
                        y = y.iloc[:, 0]

                    if i == (len(data) - 1):
                        color = 'r'
                        alpha = 1
                    else:
                        color = pg.getConfigOption("foreground")
                        alpha = (true_nbtraces - (len(data) - 1 - i)) / true_nbtraces

                    # TODO: no information about dataset nor scanset in this method! See what could be done
                    # if scanset.color != 'default':
                    #     color = scanset.color

                    # Plot
                    # careful, now that can filter data, need .values to avoid pyqtgraph bug
                    # pyqtgraph 0.11.1 raise hover error if plot deleted
                    curve = self.ax.plot(x.values, y.values, symbol='x',
                                         symbolPen=color, symbolSize=10,
                                         pen=color, symbolBrush=color)
                    curve.setAlpha(alpha, False)
                    self.curves.append(curve)

    def axisChanged(self, index):
        """ Called when the displayed result has been changed
        in the combo box. It proceeds to the change. """
        if (self.gui.variable_x_comboBox.currentIndex() != -1
                and self.gui.variable_y_comboBox.currentIndex() != -1):
            self.reloadData()
        else:
            self.clearData()

    # TRACES
    ###########################################################################

    def nbTracesChanged(self):
        """ Called when the number of traces displayed has been changed
        in the GUI. It proceeds to the change and update the plot. """
        value = self.gui.nbTraces_lineEdit.text()
        check = False
        try:
            value = int(float(value))
            assert value > 0
            self.nbtraces = value
            check = True
        except:
            pass

        self.gui.nbTraces_lineEdit.setText(f'{self.nbtraces:g}')
        setLineEditBackground(self.gui.nbTraces_lineEdit, 'synced', self._font_size)

        if check is True and self.gui.variable_y_comboBox.currentIndex() != -1:
            self.reloadData()

    # Show data
    ###########################################################################
    def refreshDisplayScanData(self):
        recipe_name = self.gui.scan_recipe_comboBox.currentText()
        scanset = self.gui.dataManager.getLastSelectedDataset()
        if scanset is not None and recipe_name in scanset:
            name = f"Scan{self.gui.data_comboBox.currentIndex()+1}"
            if self.gui.scan_recipe_comboBox.count() > 1:
                name += f", {recipe_name}"
            self.displayScan.setWindowTitle(name)
            self.displayScan.refresh(scanset[recipe_name].data)

    def displayScanDataButtonClicked(self):
        """ Opens a window showing the scan data for the displayed scan id """
        self.refreshDisplayScanData()
        self.displayScan.show()

    def sendScanDataButtonClicked(self):
        """ Sends the displayed scan data to plotter """
        recipe_name = self.gui.scan_recipe_comboBox.currentText()
        scanset = self.gui.dataManager.getLastSelectedDataset()
        if scanset is not None and recipe_name in scanset:
            data = scanset[recipe_name].data
            scan_name = self.gui.data_comboBox.currentText()
            data.name = f"{scan_name}_{recipe_name}"
            openPlotter(variable=scanset[recipe_name].data, has_parent=True)

    # SAVE FIGURE
    ###########################################################################

    def save(self, filename: str):
        """ Saves the figure with the provided filename """
        raw_name, extension = os.path.splitext(filename)
        new_filename = raw_name + ".png"
        exporter = pg.exporters.ImageExporter(self.ax)
        exporter.export(new_filename)

    def close(self):
        """ Called by scanner on closing """
        self.displayScan.close()
        self.fig.deleteLater()  # prevent crash without traceback when reopenning scanner multiple times
        self.figMap.deleteLater()
