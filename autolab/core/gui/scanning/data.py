# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:10:31 2019

@author: qchat
"""

from collections import OrderedDict
from queue import Queue
import os
import shutil
import tempfile
import sys
import random
from typing import List, Union

import numpy as np
import pandas as pd
from qtpy import QtCore, QtWidgets

from ...config import get_scanner_config
from ...utilities import boolean, create_array, data_to_dataframe
from ...variables import has_eval, eval_safely


class DataManager:
    """ Manage data from a scan """

    def __init__(self, gui: QtWidgets.QMainWindow):

        self.gui = gui
        self.datasets = []
        self.queue = Queue()

        scanner_config = get_scanner_config()
        self.save_temp = boolean(scanner_config["save_temp"])

        # Timer
        self.timer = QtCore.QTimer(self.gui)
        self.timer.setInterval(33) #30fps
        self.timer.timeout.connect(self.sync)

    def getData(self, nbDataset: int, var_list: List[str],
                selectedData: int = 0, data_name: str = "Scan",
                filter_condition: List[dict] = []) -> List[pd.DataFrame]:
        """ Returns the required data """
        dataList = []
        recipe_name = self.gui.scan_recipe_comboBox.currentText()

        for i in range(selectedData, nbDataset+selectedData):
            if i < len(self.datasets):
                scanset = self.datasets[-(i+1)]
                if recipe_name not in scanset: continue
                if not scanset.display: continue
                dataset = scanset[recipe_name]
                data = None

                if data_name == "Scan":
                    try:
                        data = dataset.getData(var_list, data_name=data_name,
                                               filter_condition=filter_condition)  # OPTIMIZE: Currently can't recover dataset if error before end of first recipe loop
                    except KeyError:
                        pass  # this occurs when plot variable from scani that is not in scanj
                    except Exception as e:
                        self.gui.setStatus(
                            f"Scan warning: Can't plot Scan{len(self.datasets)-i}: {e}",
                            10000, False)
                    dataList.append(data)
                elif dataset.data_arrays.get(data_name) is not None:
                    dataList2 = []

                    try:
                        ids = dataset.getData(['id'], data_name='Scan',
                                              filter_condition=filter_condition)
                        ids = ids['id'].values - 1
                    except KeyError:
                        ids = []

                    for index in ids:
                        try:
                            data = dataset.getData(
                                var_list, data_name=data_name, dataID=index)
                        except Exception as e:
                            self.gui.setStatus(
                                f"Scan warning: Can't plot Scan{len(self.datasets)-i}" \
                                    f" and dataframe {data_name} with ID {index+1}: {e}",
                                10000, False)
                        dataList2.append(data)

                    dataList2.reverse()
                    dataList.extend(dataList2)
            else:
                break

        dataList.reverse()
        return dataList

    def getLastDataset(self) -> Union[dict, None]:
        """ Returns the last created dataset """
        return self.datasets[-1] if len(self.datasets) > 0 else None

    def getLastSelectedDataset(self) -> Union[dict, None]:
        """ Returns the last selected dataset """
        index = self.gui.data_comboBox.currentIndex()
        if index != -1 and index < len(self.datasets):
            return self.datasets[index]
        return None

    def newDataset(self, config: dict):
        """ Creates and returns a new empty dataset """
        maximum = 0
        scanset = ScanSet()

        if self.save_temp:
            FOLDER_TEMP = os.environ['TEMP']  # This variable can be changed at autolab start-up
            folder_dataset_temp = tempfile.mkdtemp(dir=FOLDER_TEMP) # Creates a temporary directory for this dataset
            self.gui.configManager.export(
                os.path.join(folder_dataset_temp, 'config.conf'))
        else:
            folder_dataset_temp = str(random.random())

        for recipe_name, recipe in config.items():

            if recipe['active']:
                sub_folder = os.path.join(folder_dataset_temp, recipe_name)
                if self.save_temp: os.mkdir(sub_folder)

                dataset = Dataset(sub_folder, recipe_name,
                                  config, save_temp=self.save_temp)
                scanset[recipe_name] = dataset

                # bellow just to know maximum point
                nbpts = 1
                for parameter in recipe['parameter']:
                    if 'values' in parameter:
                        if has_eval(parameter['values']):
                            values = eval_safely(parameter['values'])
                            if isinstance(values, str):
                                nbpts *= 11  # OPTIMIZE: can't know length in this case without doing eval (should not do eval here because can imagine recipe_2 with param set at end of recipe_1)
                                self.gui.progressBar.setStyleSheet(
                                    "QProgressBar::chunk {background-color: orange;}")
                            else:
                                values = create_array(values)
                                nbpts *= len(values)
                        else: nbpts *= len(parameter['values'])
                    else: nbpts *= parameter['nbpts']

                maximum += nbpts

                # OBSOLETE: see if remove completely recipe in recipe
                list_recipe_nbpts_new = [[recipe, nbpts]]
                has_sub_recipe = True

                while has_sub_recipe:
                    has_sub_recipe = False
                    recipe_nbpts_list = list_recipe_nbpts_new

                    for recipe_nbpts in recipe_nbpts_list:
                        recipe_i, nbpts = recipe_nbpts

                        for step in recipe_i['recipe']:
                            if step['stepType'] == "recipe":
                                has_sub_recipe = True
                                other_recipe = config[step['element']]
                                other_nbpts = 1

                                for parameter in other_recipe['parameter']:
                                    if 'values' in parameter:
                                        other_nbpts *= len(parameter['values'])
                                    else:
                                        other_nbpts *= parameter['nbpts']
                                sub_nbpts = nbpts * other_nbpts
                                maximum += sub_nbpts
                                list_recipe_nbpts_new.append([other_recipe, sub_nbpts])

                        list_recipe_nbpts_new.remove(recipe_nbpts)

        self.datasets.append(scanset)
        self.gui.progressBar.setMaximum(maximum)

    def sync(self):
        """ This function sync the last dataset with the data available in the queue """
        # Empty the queue
        count = 0
        scanset = self.getLastDataset()
        lenQueue = self.queue.qsize()

        # Add scan data to dataset
        for _ in range(lenQueue):
            try: point = self.queue.get()  # point is collections.OrderedDict{0:recipe_name, 'parameter_name':parameter_value, 'step1_name':step1_value, 'step2_name':step2_value, ...}
            except: break

            recipe_name = list(point.values())[0]
            dataset = scanset[recipe_name]
            dataset.addPoint(point)
            count += 1

        # Upload the plot if new data available
        if count > 0:
            # Update progress bar
            progress = 0

            for dataset_name in self.gui.configManager.getRecipeActive():
                progress += len(scanset[dataset_name])

            self.gui.progressBar.setValue(progress)

            self.gui.save_pushButton.setEnabled(True)
            if len(self.datasets) != 1:
                self.gui.save_all_pushButton.setEnabled(True)

            # Update plot
            self.gui.figureManager.data_comboBoxClicked()

    def updateDisplayableResults(self):
        """ This function update the combobox in the GUI that displays the names of
        the results that can be plotted """
        data_name = self.gui.dataframe_comboBox.currentText()
        recipe_name = self.gui.scan_recipe_comboBox.currentText()
        scanset = self.getLastSelectedDataset()

        if scanset is None or recipe_name not in scanset: return None

        dataset = scanset[recipe_name]

        data = None
        if data_name == "Scan": data = dataset.data
        else:
            if dataset.data_arrays.get(data_name) is not None:
                for data in dataset.data_arrays[data_name]:  # used only to get columns name
                    if data is not None: break
            else: return None
            # if text or if image of type ndarray return
            if isinstance(data, str) or (
                    isinstance(data, np.ndarray) and not (
                        len(data.T.shape) == 1 or (
                            len(data.T.shape) != 0 and data.T.shape[0] == 2))):
                self.gui.variable_x_comboBox.clear()
                self.gui.variable_x2_comboBox.clear()
                self.gui.variable_y_comboBox.clear()
                return None

            try: data = data_to_dataframe(data)
            except AssertionError:  # if np.ndarray of string for example
                self.gui.variable_x_comboBox.clear()
                self.gui.variable_x2_comboBox.clear()
                self.gui.variable_y_comboBox.clear()
                return None

        result_names = []

        for result_name in data.columns:
            if result_name not in ['id']:
                try:
                    point = data.iloc[0][result_name]
                    if isinstance(point, pd.Series):
                        print('Warning: At least two variables have the same name.' \
                              f" Data acquisition is incorrect for {result_name}!",
                              file=sys.stderr)
                        float(point[0])
                    else:
                        float(point)
                    result_names.append(result_name)
                except:
                    pass

        variable_x_index = self.gui.variable_x_comboBox.currentIndex()
        variable_y_index = self.gui.variable_y_comboBox.currentIndex()

        items = [self.gui.variable_x_comboBox.itemText(i) for i in range(
            self.gui.variable_x_comboBox.count())]

        if result_names != items:  # only refresh if change labels, to avoid gui refresh that prevent user to click on combobox
            self.gui.variable_x_comboBox.clear()
            self.gui.variable_x2_comboBox.clear()
            self.gui.variable_x_comboBox.addItems(result_names)  # parameter first
            self.gui.variable_x2_comboBox.addItems(result_names)
            if result_names:
                name = result_names.pop(0)
                result_names.append(name)

            self.gui.variable_y_comboBox.clear()
            self.gui.variable_y_comboBox.addItems(result_names)  # first numerical measure first

            if data_name == "Scan":
                if variable_x_index != -1:
                    self.gui.variable_x_comboBox.setCurrentIndex(variable_x_index)
                    self.gui.variable_x2_comboBox.setCurrentIndex(variable_x_index)
                if variable_y_index != -1:
                    self.gui.variable_y_comboBox.setCurrentIndex(variable_y_index)
        return None


class Dataset():
    """ Collection of data from a recipe """
    def __init__(self, folder_dataset_temp: str, recipe_name: str, config: dict,
                 save_temp: bool = True):
        self._data_temp = []
        self.recipe_name = recipe_name
        self.folders = []
        self.data_arrays = {}
        self.folder_dataset_temp = folder_dataset_temp
        self.new = True
        self.save_temp = save_temp

        recipe = config[self.recipe_name]
        list_recipe = [recipe]
        list_recipe_new = [recipe]
        has_sub_recipe = True

        while has_sub_recipe:  # OBSOLETE
            has_sub_recipe = False
            recipe_list = list_recipe_new

            for recipe_i in recipe_list:
                for step in recipe_i['recipe']:
                    if step['stepType'] == "recipe":
                        has_sub_recipe = True
                        other_recipe = config[step['element']]
                        list_recipe_new.append(other_recipe)
                        list_recipe.append(other_recipe)

                list_recipe_new.remove(recipe_i)

        list_param = [recipe['parameter'] for recipe in list_recipe]
        self.list_param = sum(list_param, [])

        list_step = [recipe['recipe'] for recipe in list_recipe]
        self.list_step = sum(list_step, [])

        self.header = (["id"]
                       + [step['name'] for step in self.list_param]
                       + [step['name'] for step in self.list_step if (
                           step['stepType'] == 'measure'
                           and step['element'].type in [int, float, bool])]
                       )
        self.data = pd.DataFrame(columns=self.header)

    def getData(self, var_list: List[str], data_name: str = "Scan",
                dataID: int = 0, filter_condition: List[dict] = []) -> pd.DataFrame:
        """ This function returns a dataframe with two columns : the parameter value,
        and the requested result value """
        if data_name == "Scan":
            data = self.data
        else:
            data = self.data_arrays[data_name][dataID]

            if (data is not None
                    and not isinstance(data, str)
                    and (len(data.T.shape) == 1 or (
                        len(data.T.shape) != 0 and data.T.shape[0] == 2))):
                data = data_to_dataframe(data)
            else:  # Image
                return data

        # Add var for filtering
        for var_filter in filter_condition:
            if var_filter['enable']:
                if (var_filter['name'] not in var_list
                        and var_filter['name'] != ''
                        and var_filter['name'] is not None):
                    var_list.append(var_filter['name'])
                elif isinstance(var_filter['condition'], str):
                    for key in self.header:
                        if key in var_filter['condition']:
                            var_list.append(key)

        if any(map(lambda v: v in var_list, list(data.columns))):
            data = data.loc[:,~data.columns.duplicated()].copy()  # unique data column
            unique_var_list = list(dict.fromkeys(var_list))  # unique var_list
            # Filter data
            for var_filter in filter_condition:
                if var_filter['enable']:
                    if var_filter['name'] in data:
                        filter_cond = var_filter['condition']
                        filter_name = var_filter['name']
                        filter_value = var_filter['value']
                        mask = filter_cond(data[filter_name], filter_value)
                        data = data[mask]
                    elif isinstance(var_filter['condition'], str):
                        filter_cond = var_filter['condition']
                        if filter_cond:
                            try:
                                data = data.query(filter_cond)
                            except:
                                # If error, output empty dataframe
                                data = pd.DataFrame(columns=self.header)
                                break

            return data.loc[:,unique_var_list]

        return None

    def save(self, filename: str):
        """ This function saved the dataset in the provided path """
        dataset_folder = os.path.splitext(filename)[0]
        data_name = os.path.join(self.folder_dataset_temp, 'data.txt')

        if os.path.exists(data_name):
            shutil.copy(data_name, filename)
        else:
            self.data.to_csv(filename, index=False, header=self.header)

        if self.folders:
            if not os.path.exists(dataset_folder): os.mkdir(dataset_folder)
            for tmp_folder in self.folders:
                array_name = os.path.basename(tmp_folder)
                dest_folder = os.path.join(dataset_folder, array_name)

                if os.path.exists(tmp_folder):
                    try:
                        shutil.copytree(tmp_folder, dest_folder,
                                        dirs_exist_ok=True)  # python >=3.8 only
                    except:
                        if os.path.exists(dest_folder):
                            shutil.rmtree(dest_folder, ignore_errors=True)
                        shutil.copytree(tmp_folder, dest_folder)
                else:
                    # This is only executed if no temp folder is set
                    if not os.path.exists(dest_folder): os.mkdir(dest_folder)

                    if array_name in self.data_arrays:
                        list_data = self.data_arrays[array_name]  # data is list representing id 1,2

                        for i, value in enumerate(list_data):
                            path = os.path.join(dest_folder, f"{i+1}.txt")

                            if isinstance(value, (int, float, bool, str, tuple)):
                                with open(path, 'w') as f: f.write(str(value))
                            elif isinstance(value, bytes):
                                with open(path, 'wb') as f: f.write(value)
                            elif isinstance(value, np.ndarray):
                                df = pd.DataFrame(value)
                                df.to_csv(path, index=False, header=None)  # faster and handle better different dtype than np.savetxt
                            elif isinstance(value, pd.DataFrame):
                                value.to_csv(path, index=False)

    def addPoint(self, dataPoint: OrderedDict):
        """ This function add a data point (parameter value, and results) in the dataset """
        ID = len(self.data) + 1
        simpledata = OrderedDict()
        simpledata['id'] = ID

        for result_name, result in dataPoint.items():

            if result_name == 0: continue  # skip first result which is recipe_name

            elements = [step['element'] for step in (
                self.list_param+self.list_step) if step['name']==result_name]
            element = elements[0]
            # should always find exactly one element in list above

            # If the result is displayable (numerical), keep it in memory
            if element is None or element.type in [int, float, bool]:
                simpledata[result_name] = result
            else : # Else write it on a file, in a temp directory
                results_folder = os.path.join(self.folder_dataset_temp, result_name)

                if self.save_temp:
                    if not os.path.exists(results_folder): os.mkdir(results_folder)
                    result_path = os.path.join(results_folder, f'{ID}.txt')

                    if element is not None:
                        element.save(result_path, value=result)

                if results_folder not in self.folders:
                    self.folders.append(results_folder)

                if self.data_arrays.get(result_name) is None:
                    self.data_arrays[result_name] = []

                self.data_arrays[result_name].append(result)

        self._data_temp.append(simpledata)
        self.data = pd.DataFrame(self._data_temp, columns=self.header)

        if self.save_temp:
            if not os.path.exists(self.folder_dataset_temp):
                print(f'Warning: {self.folder_dataset_temp} has been created ' \
                      'but should have been created earlier. ' \
                      'Check that you have not lost any data',
                      file=sys.stderr)
                os.mkdir(self.folder_dataset_temp)
            if ID == 1:
                self.data.tail(1).to_csv(
                    os.path.join(self.folder_dataset_temp, 'data.txt'),
                    index=False, mode='a', header=self.header)
            else:
                self.data.tail(1).to_csv(
                    os.path.join(self.folder_dataset_temp, 'data.txt'),
                    index=False, mode='a', header=False)

    def __len__(self):
        """ Returns the number of data point of this dataset """
        return len(self.data)


class ScanSet(dict):
    """ Collection of data from a scan """
    # TODO: use this in scan plot
    display = True
    color = 'default'
    saved = False
