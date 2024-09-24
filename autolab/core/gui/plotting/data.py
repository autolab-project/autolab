# -*- coding: utf-8 -*-
"""
Created on Oct 2022

@author: jonathan based on qchat
"""

from typing import List, Union, Any
import os
import sys
import csv

import numpy as np
import pandas as pd

try:
    from pandas._libs.lib import no_default
except:
    no_default = None

from qtpy import QtWidgets

from ...paths import PATHS
from ...config import load_config
from ...utilities import data_to_dataframe, SUPPORTED_EXTENSION
from ...devices import DEVICES, get_element_by_address, list_devices
from ...elements import Variable as Variable_og
from ...variables import list_variables, get_variable, Variable


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
        if fp.read(1) not in ("#", "!", "\n"):
            skiprows = None
        else:
            skiprows = 1
            fp.readline()
            while fp.read(1) in ("#", "!", "\n"):
                skiprows += 1
                fp.readline()
    return skiprows


def find_header(filename, sep=no_default, skiprows=None):
    try:
        df = pd.read_csv(filename, sep=sep, header=None, nrows=5, skiprows=skiprows)
    except Exception:
        if type(skiprows) is not None: skiprows += 1
        df = pd.read_csv(filename, sep=sep, header=None, nrows=5, skiprows=skiprows)
    else:
        if skiprows == 1:
            try:
                df_columns = pd.read_csv(filename, sep=sep, header="infer",
                                         skiprows=0, nrows=0)
            except Exception:
                pass
            else:
                columns = list(df_columns.columns)
                if columns[0] == "#":
                    columns.pop(0)
                    if len(columns) == len(df):
                        return (0, 1, columns)  # (header, skiprows, columns)

    try:
        first_row = df.iloc[0].values.astype("float")
        return (("infer", skiprows, no_default)
                if tuple(first_row) == tuple([i for i in range(len(first_row))])
                else (None, skiprows, no_default))
    except:
        pass
    df_header = pd.read_csv(filename, sep=sep, nrows=5, skiprows=skiprows)

    return (("infer", skiprows, no_default)
            if tuple(df.dtypes) != tuple(df_header.dtypes)
            else (None, skiprows, no_default))


def importData(filename):
    """ This function open the data with the provided filename """

    skiprows = _skiprows(filename)
    sep = find_delimiter(filename)
    (header, skiprows, columns) = find_header(filename, sep, skiprows)
    try:
        data = pd.read_csv(filename, sep=sep, header=header,
                           skiprows=skiprows, names=columns)
    except TypeError:
        data = pd.read_csv(filename, sep=sep, header=header,
                           skiprows=skiprows, names=None)  # for pandas 1.2: names=None but sep=no_default
    except:
        data = pd.read_csv(filename, sep="\t", header=header,
                           skiprows=skiprows, names=columns)

    assert len(data) != 0, "Can't import empty DataFrame"
    data = data_to_dataframe(data)
    return data


class DataManager:

    def __init__(self, gui: QtWidgets.QMainWindow):

        self.gui = gui
        self._clear()
        self.overwriteData = True

        plotter_config = load_config("plotter_config")
        if ('device' in plotter_config.sections()
                and 'address' in plotter_config['device']):
            self.variable_address = str(plotter_config['device']['address'])
        else:
            self.variable_address = ''

    def _clear(self):
        self.datasets = []
        self.last_variables = []

    def setOverwriteData(self, value: bool):
        self.overwriteData = bool(value)

    def getDatasetsNames(self) -> List[str]:
        names = []
        for dataset in self.datasets:
            names.append(dataset.name)
        return names

    @staticmethod
    def getUniqueName(name: str, names_list: List[str]):
        """ This function adds a number next to basename in case this basename
        is already taken """
        raw_name, extension = os.path.splitext(name)

        if extension in (".txt", ".csv", ".dat"):
            basename = raw_name
            putext = True
        else:
            basename = name
            putext = False

        compt = 0
        while True:
            if name in names_list:
                compt += 1
                if putext:
                    name = basename+'_' + str(compt) + extension
                else:
                    name = basename + '_' + str(compt)
            else:
                break
        return name

    def set_variable_address(self, value: str):
        """ This function set the address of the target variable """
        # Can raise errors
        self.getVariable(value)
        # If no errors
        self.variable_address = value

    def get_variable_address(self) -> str:
        """ This function returns the value of the target device value """
        return self.variable_address

    def getVariable(self, name: str) -> Union[Variable, Variable_og]:
        """ This function returns the name of the target device value """
        assert name != '', 'Need to provide a variable name'
        device = name.split(".")[0]

        if device in list_variables():
            assert device == name, f"Can only use '{device}' directly"
            variable = get_variable(name)
        elif device in list_devices():
            assert device in DEVICES, f"Device '{device}' is closed"
            variable = get_element_by_address(name)  # Can raise 'name' not found in module 'device'
            assert isinstance(variable, Variable_og), (
                f"Need a variable but '{name}' is a {str(type(variable).__name__)}")
            assert variable.readable, f"Variable '{name}' is not readable"
            var_type = str(variable.type).split("'")[1]
            assert variable.type in (int, float, np.ndarray, pd.DataFrame), (
                f"Datatype '{var_type}' of '{name}' is not supported")
        else:
            assert False, f"'{device}' is neither a device nor a variable"

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
        filenames = QtWidgets.QFileDialog.getOpenFileNames(
            self.gui, "Import data file", PATHS['last_folder'],
            filter=SUPPORTED_EXTENSION)[0]
        if not filenames:
            return None
        else:
            self.importAction(filenames)

    def importAction(self, filenames: List[str]):
        dataset = None
        for i, filename in enumerate(filenames):
            try:
                dataset = self.importData(filename)
            except Exception as e:
                self.gui.setStatus(
                    f"Impossible to load data from {filename}: {e}",
                    10000, False)
                if len(filenames) != 1:
                    print(f"Impossible to load data from {filename}: {e}",
                          file=sys.stderr)
            else:
                self.gui.setStatus(f"File {filename} loaded successfully", 5000)
        if dataset is not None:
            self.gui.figureManager.start(dataset)

        path = os.path.dirname(filename)
        PATHS['last_folder'] = path

    def importDeviceData(self, variable: Union[Variable, Variable_og, pd.DataFrame, Any]):
        """ This function open the data of the provided device """
        if isinstance(variable, pd.DataFrame):
            name = variable.name if hasattr(variable, 'name') else 'dataframe'
            data = variable
        elif isinstance(variable, (Variable, Variable_og)):
            name = variable.address()
            data = variable()  # read value
        else:
            name = 'data'
            data = variable
        data = data_to_dataframe(data)  # format value

        if self.overwriteData:
            data_name = name
        else:
            names_list = self.getDatasetsNames()
            data_name = DataManager.getUniqueName(
                name, names_list)

        dataset = self.newDataset(data_name, data)
        return dataset

    def importData(self, filename: str):
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

    def _addData(self, new_dataset):
        names = self.gui.dataManager.getDatasetsNames()

        if self.gui.overwriteDataButton.isChecked() and new_dataset.name in names:
            dataSet_id = names.index(new_dataset.name) + 1
            current_dataset = self.gui.dataManager.datasets[dataSet_id-1]

            if not new_dataset.data.equals(current_dataset.data):
                current_dataset.update(new_dataset)
        else:
            # Prepare a new dataset in the plotter
            self.gui.dataManager.addDataset(new_dataset)

    def getData(self, nbDataset: int, var_list: List[str], selectedData: int = 0):
        """ This function returns to the figure manager the required data """
        dataList = []
        for i in range(selectedData, nbDataset+selectedData):
            if i < len(self.datasets):
                dataset = self.datasets[-(i+1)]
                try:
                    data = dataset.getData(var_list)
                except:
                    data = None
                dataList.append(data)
            else:
                break
        dataList.reverse()

        return dataList

    def saveButtonClicked(self):
        """ This function is called when the save button is clicked.
        It asks a path and starts the procedure to save the data """
        dataset = self.getLastSelectedDataset()
        if dataset is not None:
            filename = QtWidgets.QFileDialog.getSaveFileName(
                self.gui, caption="Save data", directory=PATHS['last_folder'],
                filter=SUPPORTED_EXTENSION)[0]
            path = os.path.dirname(filename)

            if path != '':
                PATHS['last_folder'] = path
                self.gui.setStatus('Saving data...', 5000)

                dataset.save(filename)
                self.gui.figureManager.save(filename)

                self.gui.setStatus(
                    f'Last dataset successfully saved in {filename}', 5000)

    def clear(self):
        """ Clear displayed dataset """
        data_name = self.gui.data_comboBox.currentText()
        index = self.gui.data_comboBox.currentIndex()
        nbr_data = self.gui.data_comboBox.count()  # how many item left

        try:
            dataset = self.getLastSelectedDataset()
            self.deleteData(dataset)
            self.gui.data_comboBox.removeItem(index)
            self.gui.setStatus(f"Removed {data_name}", 5000)
        except Exception as e:
            self.gui.setStatus(f"Can't delete: {e}", 10000, False)
            pass

        if self.gui.data_comboBox.count() == 0:
            self.clear_all()
            return

        else:
            # if last point but exist other data takes previous data else keep index
            if index == (nbr_data-1) and index != 0:
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
            return self.datasets[self.gui.data_comboBox.currentIndex()]

    def addDataset(self, dataset):
        """ This function add the given dataset to datasets list """
        self.datasets.append(dataset)

    def newDataset(self, name: str, data: pd.DataFrame):
        """ This function creates a new dataset """
        dataset = Dataset(name, data)
        self._addData(dataset)
        return dataset

    def updateDisplayableResults(self):
        """ This function update the combobox in the GUI that displays the
        names of the results that can be plotted """
        dataset = self.getLastSelectedDataset()

        variables_list = list(dataset.data.columns)

        if variables_list != self.last_variables:
            self.last_variables = variables_list
            result_names = []

            for result_name in variables_list:
                    try:
                        float(dataset.data.iloc[0][result_name])
                        result_names.append(result_name)
                    except Exception as e:
                        self.gui.setStatus(f"Can't plot data: {e}", 10000, False)
                        return None

            variable_x = self.gui.variable_x_comboBox.currentText()
            variable_y = self.gui.variable_y_comboBox.currentText()

            # If can, put back previous x and y variable in combobox
            is_id = (len(variables_list) != 0
                     and variables_list[0] == "id"
                     and len(variables_list) > 2)

            if is_id:
                # move id form begin to end
                name=result_names.pop(0)
                result_names.append(name)

            AllItems = [self.gui.variable_x_comboBox.itemText(i)
                        for i in range(self.gui.variable_x_comboBox.count())]

            # only refresh if change labels, to avoid gui refresh that prevent user to click on combobox
            if result_names != AllItems:
                self.gui.variable_x_comboBox.clear()
                self.gui.variable_y_comboBox.clear()

                self.gui.variable_x_comboBox.addItems(result_names)  # slow (0.25s)

                if len(result_names) != 0:
                    # move first item to end (only for y axis)
                    name=result_names.pop(0)
                    result_names.append(name)

                self.gui.variable_y_comboBox.addItems(result_names)

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

    def __init__(self, name: str, data: pd.DataFrame):

        self.name = name
        self.data = data

    def getData(self, var_list: List[str]):
        """ This function returns a dataframe with two columns:
        the parameter value, and the requested result value """
        if var_list[0] == var_list[1]: return self.data.loc[:, [var_list[0]]]
        else: return self.data.loc[:, var_list]

    def update(self, dataset):
        """ Change name and data of this dataset """
        self.name = dataset.name
        self.data = dataset.data

    def save(self,filename: str):
        """ This function saved the dataset in the provided path """
        self.data.to_csv(filename, index=False)

    def __len__(self):
        """ Returns the number of data point of this dataset """
        return len(self.data)
