# -*- coding: utf-8 -*-
"""
Created on Oct 2022

@author: jonathan based on qchat
"""

# import collections
import os
import csv

import numpy as np
from PyQt5 import QtCore,QtWidgets
from ... import paths
import pandas as pd

try:
    from pandas._libs.lib import no_default
except:
    no_default = None


def find_delimiter(filename):
    sniffer = csv.Sniffer()
    with open(filename) as fp:
        try:
            text = fp.read(5000)
            if text.startswith("#"):
                text = text[len(text.split("\n")[0])+len("\n"):]
            delimiter = sniffer.sniff(text).delimiter
        except:
            # delimiter = ","  # only 1 column
            delimiter = no_default
        if delimiter in ("e", "."):  # sniffer got it wrong
            delimiter = no_default
    return delimiter


def _skiprows(filename):
    with open(filename) as fp:
        skiprows = 1 if fp.read(1) == "#" else None
    return skiprows


def find_header(filename, sep=no_default, skiprows=None):
    df = pd.read_csv(filename, sep=sep, header=None, nrows=5, skiprows=skiprows)
    try:
        first_row = df.iloc[0].values.astype("float")
        return "infer" if tuple(first_row) == tuple([i for i in range(len(first_row))]) else None
    except:
        pass
    df_header = pd.read_csv(filename, sep=sep, nrows=5)

    return "infer" if tuple(df.dtypes) != tuple(df_header.dtypes) else None


def formatData(data):
    """ Format data """

    try:
        data = pd.DataFrame(data)
    except ValueError:
        data = pd.DataFrame([data])
    data.columns = data.columns.astype(str)
    data_type = data.values.dtype
    data[data.columns] = data[data.columns].apply(pd.to_numeric, errors="coerce")
    assert not data.isnull().values.all(), f"Datatype '{data_type}' not supported"

    if data.shape[1] == 1:
        data.rename(columns = {'0':'1'}, inplace=True)
        data.insert(0, "0", range(data.shape[0]))
    return data


def importData(filename):
    """ This function open the data with the provided filename """

    skiprows = _skiprows(filename)
    sep = find_delimiter(filename)
    header = find_header(filename, sep, skiprows)
    try:
        data = pd.read_csv(filename, sep=sep, header=header, skiprows=skiprows)
    except:
        data = pd.read_csv(filename, sep="\t", header=header, skiprows=skiprows)

    data = formatData(data)
    return data




class DataManager :

    def __init__(self,gui):

        self.gui = gui

        self._clear()

        self.overwriteData = True

        self.deviceValue = "ct400.scan.data"

    def _clear(self):
        self.datasets = []
        self.last_variables = []

    def setOverwriteData(self, value):
        self.overwriteData = bool(value)

    def getDatasetsNames(self):
        names = list()
        for dataset in self.datasets:
            names.append(dataset.name)
        return names

    @staticmethod
    def getUniqueName(name, names_list):

        """ This function adds a number next to basename in case this basename is already taken """

        raw_name, extension = os.path.splitext(name)

        if extension in (".txt", ".csv", ".dat"):
            basename = raw_name
            putext = True
        else:
            basename = name
            putext = False

        compt = 0
        while True :
            if name in names_list :
                compt += 1
                if putext:
                    name = basename+'_'+str(compt)+extension
                else:
                    name = basename+'_'+str(compt)
            else :
                break
        return name

    def setDeviceValue(self,value):
        """ This function set the value of the target device value """

        try:
            self.getDeviceName(value)
        except:
            raise NameError(f"The given value '{value}' is not a device variable or the device is closed")
        else:
            self.deviceValue = value

    def getDeviceValue(self):
        """ This function returns the value of the target device value """

        return self.deviceValue

    def getDeviceName(self, name):
        """ This function returns the name of the target device value """

        try:
            module_name, *submodules_name, variable_name = name.split(".")
            module = self.gui.mainGui.tree.findItems(module_name, QtCore.Qt.MatchExactly)[0].module
            for submodule_name in submodules_name:
                module = module.get_module(submodule_name)
            variable = module.get_variable(variable_name)
        except:
            raise NameError(f"The given value '{name}' is not a device variable or the device is closed")
        return variable


    def data_comboBoxClicked(self):

        """ This function select a dataset """
        if len(self.datasets) == 0:
            self.gui.save_pushButton.setEnabled(False)
            self.gui.clear_pushButton.setEnabled(False)
            self.gui.clear_all_pushButton.setEnabled(False)
        else:
            self.updateDisplayableResults()

    def importActionClicked(self):

        """ This function prompts the user for a dataset filename,
        and import the dataset"""

        filenames = QtWidgets.QFileDialog.getOpenFileNames(self.gui, "Import data file",
                                                           paths.USER_LAST_CUSTOM_FOLDER,
                                                           filter="Text Files (*.txt);; Supported text Files (*.txt;*.csv;*.dat);; All Files (*)")[0]
        if not filenames:
            return
        else:
            self.importAction(filenames)

    def importAction(self, filenames):

        for i, filename in enumerate(filenames):

            try :
                dataset = self.importData(filename)
            except Exception as error:
                self.gui.statusBar.showMessage(f"Impossible to load data from {filename}: {error}",10000)
                if len(filenames) != 1:
                    print(f"Impossible to load data from {filename}: {error}")
            else:
                self.gui.statusBar.showMessage(f"File {filename} loaded successfully",5000)

                self.gui.figureManager.start(dataset)

        path = os.path.dirname(filename)
        paths.USER_LAST_CUSTOM_FOLDER = path

    def importDeviceData(self, deviceVariable):
        """ This function open the data of the provided device """

        data = deviceVariable()

        data = formatData(data)

        if self.overwriteData:
            data_name = self.deviceValue
        else:
            names_list = self.getDatasetsNames()
            data_name = DataManager.getUniqueName(self.deviceValue, names_list)

        dataset = self.newDataset(data_name, data)
        return dataset

    def importData(self, filename):
        """ This function open the data with the provided filename """
        # OPTIMIZE: could add option to choose in GUI all options

        data = importData(filename)

        name = os.path.basename(filename)

        if self.overwriteData:
            data_name = name
        else:
            names_list = self.getDatasetsNames()
            data_name = DataManager.getUniqueName(name, names_list)

        dataset = self.newDataset(data_name, data)
        return dataset


    def getData(self,nbDataset,varList, selectedData=0):
        """ This function returns to the figure manager the required data """

        dataList = []

        for i in range(selectedData, nbDataset+selectedData) :
            if i < len(self.datasets) :
                dataset = self.datasets[-(i+1)]
                try:
                    data = dataset.getData(varList)
                except:
                    data = None
                dataList.append(data)
            else :
                break
        dataList.reverse()

        return dataList

    def saveButtonClicked(self):
        """ This function is called when the save button is clicked.
        It asks a path and starts the procedure to save the data """

        dataset = self.getLastSelectedDataset()
        if dataset is not None :

            filename, _ = QtWidgets.QFileDialog.getSaveFileName(self.gui,
                                              caption="Save data",
                                              directory=paths.USER_LAST_CUSTOM_FOLDER,
                                              filter="Text Files (*.txt);; Supported text Files (*.txt;*.csv;*.dat);; All Files (*)")
            path = os.path.dirname(filename)

            if path != '' :
                paths.USER_LAST_CUSTOM_FOLDER = path
                self.gui.statusBar.showMessage('Saving data...',5000)

                dataset.save(filename)
                self.gui.figureManager.save(filename)

                self.gui.statusBar.showMessage(f'Last dataset successfully saved in {filename}',5000)

    def clear(self):
        """ Clear displayed dataset """
        data_name = self.gui.data_comboBox.currentText()
        index = self.gui.data_comboBox.currentIndex()
        nbr_data = self.gui.data_comboBox.count()  # how many item left

        try:
            dataset = self.getLastSelectedDataset()
            self.deleteData(dataset)
            self.gui.data_comboBox.removeItem(index)
            self.gui.statusBar.showMessage(f"Removed {data_name}", 5000)
        except Exception as error:
            self.gui.statusBar.showMessage(f"Can't delete: {error}", 10000)
            pass

        if self.gui.data_comboBox.count() == 0:
            self.clear_all()
            return

        else:
            if index == (nbr_data-1) and index != 0:  # if last point but exist other data takes previous data else keep index
                index -= 1

            self.gui.data_comboBox.setCurrentIndex(index)

        self.data_comboBoxClicked()
        self.gui.plugin_refresh()

    def clear_all(self):
        """ This reset any recorded data, and the GUI accordingly """

        self._clear()

        self.gui.figureManager.clearData()
        self.gui.variable_x_comboBox.clear()
        self.gui.variable_y_comboBox.clear()
        self.gui.data_comboBox.clear()

        self.data_comboBoxClicked()
        self.gui.plugin_refresh()

    def deleteData(self, dataset):
        """ This function remove dataset from the datasets"""

        self.datasets.remove(dataset)

    def getLastSelectedDataset(self):
        """ This return the current (last selected) dataset """

        if len(self.datasets) > 0:
            return self.datasets[self.gui.data_comboBox.currentIndex()] # OPTIMIZE: should be local variable, not gui. thread should change local from gui

    def addDataset(self, dataset):
        """ This function add the given dataset to datasets list """

        self.datasets.append(dataset)

    def newDataset(self, name, data):
        """ This function creates a new dataset """

        dataset = Dataset(self.gui, name, data)
        return dataset

    def updateDisplayableResults(self) :
        """ This function update the combobox in the GUI that displays the names of
        the results that can be plotted """

        dataset = self.getLastSelectedDataset()

        variables_list = list(dataset.data.columns)

        if variables_list != self.last_variables:
            self.last_variables = variables_list
            resultNamesList = []

            for resultName in variables_list :
                    try :
                        float(dataset.data.iloc[0][resultName])
                        resultNamesList.append(resultName)
                    except Exception as er:
                        self.gui.statusBar.showMessage(f"Can't plot data: {er}", 10000)
                        return

            variable_x = self.gui.variable_x_comboBox.currentText()
            variable_y = self.gui.variable_y_comboBox.currentText()

            self.gui.variable_x_comboBox.clear()
            self.gui.variable_y_comboBox.clear()

            # If can, put back previous x and y variable in combobox
            is_id = variables_list[0] == "id" and len(variables_list) > 2

            if is_id:  # move id form begin to end
                name=resultNamesList.pop(0)
                resultNamesList.append(name)

            self.gui.variable_x_comboBox.addItems(resultNamesList)  # slow (0.25s)

            # move first item to end (only for y axis)
            name=resultNamesList.pop(0)
            resultNamesList.append(name)
            self.gui.variable_y_comboBox.addItems(resultNamesList)

            if variable_x in variables_list:
                index = self.gui.variable_x_comboBox.findText(variable_x)
                self.gui.variable_x_comboBox.setCurrentIndex(index)
            # else:  # BAD IDEA: Too slow to be useful, better to rearange items like before
            #     self.gui.variable_x_comboBox.setCurrentIndex(0+is_id)

            if variable_y in variables_list:
                index = self.gui.variable_y_comboBox.findText(variable_y)
                self.gui.variable_y_comboBox.setCurrentIndex(index)
            # else:
            #     self.gui.variable_y_comboBox.setCurrentIndex(1+is_id)
        else:
            self.gui.figureManager.reloadData()  # 0.1s



class Dataset():

    def __init__(self,gui,name, data):

        self.gui = gui
        self.name = name
        self.data = data

    def getData(self,varList):
        """ This function returns a dataframe with two columns : the parameter value,
        and the requested result value """

        if varList[0] == varList[1] : return self.data.loc[:,[varList[0]]]
        else : return self.data.loc[:,varList]

    def update(self, dataset):
        """ Change name and data of this dataset """

        self.name = dataset.name
        self.data = dataset.data

    def save(self,filename):
        """ This function saved the dataset in the provided path """

        self.data.to_csv(filename,index=False)

    def __len__(self):
        """ Returns the number of data point of this dataset """

        return len(self.data)
