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
from typing import List

import numpy as np
import pandas as pd
from qtpy import QtCore, QtWidgets

from ... import paths
from ... import config as autolab_config
from ... import utilities


class DataManager:
    """ Manage data from a scan """

    def __init__(self, gui: QtWidgets.QMainWindow):

        self.gui = gui
        self.datasets = list()
        self.queue = Queue()
        self.initialized = False

        scanner_config = autolab_config.get_scanner_config()
        self.save_temp = utilities.boolean(scanner_config["save_temp"])

        # Timer
        self.timer = QtCore.QTimer(self.gui)
        self.timer.setInterval(33) #30fps
        self.timer.timeout.connect(self.sync)

        # Save button configuration
        self.gui.save_pushButton.clicked.connect(self.saveButtonClicked)
        self.gui.save_pushButton.setEnabled(False)

        # Clear button configuration
        self.gui.clear_pushButton.clicked.connect(self.clear)

    def getData(self, nbDataset: int, varList: list,
                selectedData: int = 0, data_name: str = "Scan"):
        """ This function returns to the figure manager the required data """
        dataList = []
        recipe_name = self.gui.scan_recipe_comboBox.currentText()

        for i in range(selectedData, nbDataset+selectedData):
            if i < len(self.datasets):
                dataset = self.datasets[-(i+1)][recipe_name]

                if data_name == "Scan":
                    try:
                        data = dataset.getData(varList, data_name=data_name)  # OPTIMIZE: Currently can't recover dataset if error before end of first recipe loop
                    except Exception as e:
                        data = None
                        self.gui.setStatus(f"Error encountered for scan id {selectedData+1}: {e}",
                                           10000, False)
                    dataList.append(data)
                elif dataset.dictListDataFrame.get(data_name) is not None:
                    dataList2 = []
                    lenListDataFrame = len(dataset.dictListDataFrame[data_name])

                    for index in range(lenListDataFrame):
                        try:
                            data = None
                            checkBoxChecked = self.gui.figureManager.menuBoolList[index]
                            if checkBoxChecked:
                                data = dataset.getData(varList, data_name=data_name, dataID=index)
                        except Exception as e:
                            self.gui.setStatus(f"Error encountered for scan id {selectedData+1} and dataframe {data_name} with ID {index+1}: {e}",
                                               10000, False)
                        dataList2.append(data)

                    dataList2.reverse()
                    dataList.extend(dataList2)
            else:
                break

        dataList.reverse()
        return dataList

    def saveButtonClicked(self):
        """ This function is called when the save button is clicked.
        It asks a path and starts the procedure to save the data """
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.gui,  caption="Save data",
            directory=paths.USER_LAST_CUSTOM_FOLDER,
            filter=utilities.SUPPORTED_EXTENSION)
        path = os.path.dirname(filename)

        if path != '':
            paths.USER_LAST_CUSTOM_FOLDER = path
            self.gui.setStatus('Saving data...', 5000)
            datasets = self.getLastSelectedDataset()

            for dataset_name in datasets.keys():
                dataset = datasets[dataset_name]

                if len(datasets) == 1:
                    filename_recipe = filename
                else:
                    dataset_folder, extension = os.path.splitext(filename)
                    filename_recipe = f'{dataset_folder}_{dataset_name}{extension}'
                dataset.save(filename_recipe)

            scanner_config = autolab_config.get_scanner_config()
            save_config = utilities.boolean(scanner_config["save_config"])

            if save_config:
                dataset_folder, extension = os.path.splitext(filename)
                new_configname = dataset_folder + ".conf"
                config_name = os.path.join(os.path.dirname(dataset.tempFolderPath), 'config.conf')

                if os.path.exists(config_name):
                    shutil.copy(config_name, new_configname)
                else:
                    if datasets is not self.getLastDataset():
                        print("Warning: Can't find config for this dataset, save lastest config instead", file=sys.stderr)
                    self.gui.configManager.export(new_configname)  # BUG: it saves latest config instead of dataset config because no record available of previous config. (I did try to put back self.config to dataset but config changes with new dataset (copy doesn't help and deepcopy not possible)

            if utilities.boolean(scanner_config["save_figure"]):
                self.gui.figureManager.save(filename)

            self.gui.setStatus(f'Last dataset successfully saved in {filename}',
                               5000)

    def clear(self):
        """ This reset any recorded data, and the GUI accordingly """
        self.datasets = list()
        self.initialized = False
        self.gui.figureManager.clearData()
        self.gui.figureManager.clearMenuID()
        self.gui.figureManager.figMap.hide()
        self.gui.figureManager.fig.show()
        self.gui.figureManager.setLabel("x", " ")
        self.gui.figureManager.setLabel("y", " ")
        self.gui.nbTraces_lineEdit.show()
        self.gui.graph_nbTracesLabel.show()
        self.gui.frame_axis.show()
        self.gui.toolButton.hide()
        self.gui.variable_x_comboBox.clear()
        self.gui.variable_y_comboBox.clear()
        self.gui.data_comboBox.clear()
        self.gui.save_pushButton.setEnabled(False)
        self.gui.progressBar.setValue(0)
        self.gui.displayScanData_pushButton.setEnabled(False)
        self.gui.dataframe_comboBox.clear()
        self.gui.dataframe_comboBox.addItems(["Scan"])
        self.gui.dataframe_comboBox.setEnabled(False)
        self.gui.dataframe_comboBox.hide()
        self.gui.scan_recipe_comboBox.setCurrentIndex(0)
        self.gui.scan_recipe_comboBox.setEnabled(False)

    def getLastDataset(self) -> dict:
        """ This return the last created dataset """
        return self.datasets[-1] if len(self.datasets) > 0 else None

    def getLastSelectedDataset(self) -> List[dict]:
        """ This return the last selected dataset """
        return self.datasets[self.gui.data_comboBox.currentIndex()]

    def newDataset(self, config: dict):
        """ This function creates and returns a new empty dataset """
        maximum = 0
        datasets = dict()

        if self.save_temp:
            temp_folder = os.environ['TEMP']  # This variable can be changed at autolab start-up
            tempFolderPath = tempfile.mkdtemp(dir=temp_folder) # Creates a temporary directory for this dataset
            self.gui.configManager.export(os.path.join(tempFolderPath, 'config.conf'))
        else:
            import random
            tempFolderPath = str(random.random())

        for recipe_name in list(config.keys()):
            recipe = config[recipe_name]

            if recipe['active']:
                sub_folder = os.path.join(tempFolderPath, recipe_name)
                if self.save_temp: os.mkdir(sub_folder)

                dataset = Dataset(sub_folder, recipe_name,
                                  config, save_temp=self.save_temp)
                datasets[recipe_name] = dataset

                # bellow just to know maximum point
                nbpts = 1
                for parameter in recipe['parameter']:
                    if 'values' in parameter:
                        nbpts *= len(parameter['values'])
                    else:
                        nbpts *= parameter['nbpts']

                maximum += nbpts

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

        self.datasets.append(datasets)
        self.gui.progressBar.setMaximum(maximum)

    def sync(self):
        """ This function sync the last dataset with the data available in the queue """
        # Empty the queue
        count = 0
        datasets = self.getLastDataset()
        lenQueue = self.queue.qsize()

        for i in range(lenQueue):
            try: point = self.queue.get()  # point is collections.OrderedDict{0:recipe_name, 'parameter_name':parameter_value, 'step1_name':step1_value, 'step2_name':step2_value, ...}
            except: break

            recipe_name = list(point.values())[0]
            dataset = datasets[recipe_name]
            dataset.addPoint(point)
            count += 1

        # Upload the plot if new data available
        if count > 0:
            # Update progress bar
            progress = 0

            for dataset_name in self.gui.configManager.getRecipeActive():
                progress += len(datasets[dataset_name])

            self.gui.progressBar.setValue(progress)

            # Update dataframe combobox and checkbox
            listDataFrame = list(dataset.dictListDataFrame.values())
            if len(listDataFrame) != 0:
                nb_id = 0
                for dataframe in listDataFrame:
                    if len(dataframe) > nb_id:
                        nb_id = len(dataframe)

                # not-oPTIMIZE: edit: not necessary if show only one scan <- values will not correspond to previous scan if start a new scan with a different range parameter
                nb_total = 1
                for nbpts_i in [parameter['nbpts'] for parameter in self.gui.configManager.parameterList(recipe_name)]: nb_total *= nbpts_i

                while self.gui.figureManager.nbCheckBoxMenuID > nb_total:
                    self.gui.figureManager.removeLastCheckBox2MenuID()

                if self.gui.figureManager.nbCheckBoxMenuID >= nb_id:
                    paramValue = nb_id
                    self.gui.figureManager.menuWidgetList[nb_id-1].setText(str(paramValue))

                prev_id = self.gui.figureManager.nbCheckBoxMenuID
                while self.gui.figureManager.nbCheckBoxMenuID < nb_id:
                    prev_id += 1
                    paramValue = prev_id
                    self.gui.figureManager.addCheckBox2MenuID(paramValue)

                if self.gui.dataframe_comboBox.currentText() != "Scan":
                    self.gui.figureManager.reloadData()

            # Executed after the first start of a new config scan
            if not self.initialized:
                self.gui.scan_recipe_comboBox.setCurrentText(recipe_name)
                self.updateDisplayableResults()
                self.gui.save_pushButton.setEnabled(True)
                self.initialized = True

            # Executed after any dataset newly created and fed
            if dataset.new:  # OBSOLETE: was used to add only new point to plot instead of resending everything. Removed it with the introdution of dataframe plot
                # self.gui.figureManager.reloadData()
                dataset.new = False

            self.gui.figureManager.data_comboBoxClicked()

    def updateDisplayableResults(self):
        """ This function update the combobox in the GUI that displays the names of
        the results that can be plotted """
        data_name = self.gui.dataframe_comboBox.currentText()
        recipe_name = self.gui.scan_recipe_comboBox.currentText()
        dataset = self.getLastSelectedDataset()[recipe_name]

        if data_name == "Scan":
            data = dataset.data
        else:
            if dataset.dictListDataFrame.get(data_name) is not None:
                for data in dataset.dictListDataFrame[data_name]:  # used only to get columns name
                    if data is not None:
                        break
            else:
                return None
            # if text or if image of type ndarray return
            if type(data) is str or (type(data) is np.ndarray and not (len(data.T.shape) == 1 or data.T.shape[0] == 2)):
                self.gui.variable_x_comboBox.clear()
                self.gui.variable_y_comboBox.clear()
                return None

            try:
                data = utilities.formatData(data)
            except AssertionError as e:  # if np.ndarray of string for example
                self.gui.variable_x_comboBox.clear()
                self.gui.variable_y_comboBox.clear()
                # self.gui.setStatus(f"Error, can't plot data {data_name}: {e}", 10000, False)  # already catched by getData
                return None

        resultNamesList = []

        for resultName in data.columns:
            if resultName not in ['id']:
                try:
                    point = data.iloc[0][resultName]
                    if isinstance(point, pd.Series):
                        print(f"Warning: At least two variables have the same name. Data acquisition is incorrect for {resultName}!", file=sys.stderr)
                        float(point[0])
                    else:
                        float(point)
                    resultNamesList.append(resultName)
                except:
                    pass

        variable_x_index = self.gui.variable_x_comboBox.currentIndex()
        variable_y_index = self.gui.variable_y_comboBox.currentIndex()

        AllItems = [self.gui.variable_x_comboBox.itemText(i) for i in range(self.gui.variable_x_comboBox.count())]

        if resultNamesList != AllItems:  # only refresh if change labels, to avoid gui refresh that prevent user to click on combobox
            self.gui.variable_x_comboBox.clear()
            self.gui.variable_x_comboBox.addItems(resultNamesList)  # parameter first

            if resultNamesList:
                name = resultNamesList.pop(0)
                resultNamesList.append(name)

            self.gui.variable_y_comboBox.clear()
            self.gui.variable_y_comboBox.addItems(resultNamesList)  # first numerical measure first

            if data_name == "Scan":
                if variable_x_index != -1: self.gui.variable_x_comboBox.setCurrentIndex(variable_x_index)
                if variable_y_index != -1: self.gui.variable_y_comboBox.setCurrentIndex(variable_y_index)


class Dataset():
    """ Collection of data from a scan """

    def __init__(self, tempFolderPath: str, recipe_name: str, config: dict,
                 save_temp: bool = True):
        self.all_data_temp = list()
        self.recipe_name = recipe_name
        self.list_array = list()
        self.dictListDataFrame = dict()
        self.tempFolderPath = tempFolderPath
        self.new = True
        self.save_temp = save_temp

        recipe = config[self.recipe_name]
        list_recipe = [recipe]
        list_recipe_new = [recipe]
        has_sub_recipe = True

        while has_sub_recipe:
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

        self.header = ["id"] + [step['name'] for step in self.list_param] + [step['name'] for step in self.list_step if step['stepType'] == 'measure' and step['element'].type in [int, float, bool]]
        self.data = pd.DataFrame(columns=self.header)

    def getData(self, varList: list, data_name: str = "Scan",
                dataID: int = 0) -> pd.DataFrame:
        """ This function returns a dataframe with two columns : the parameter value,
        and the requested result value """
        if data_name == "Scan":
            data = self.data
        else:
            data = self.dictListDataFrame[data_name][dataID]

            if ((data is not None)
                    and (type(data) is not str)
                    and (len(data.T.shape) == 1 or data.T.shape[0] == 2)):
                data = utilities.formatData(data)
            else:  # Image
                return data

        if any(map(lambda v: v in varList, list(data.columns))):
            if varList[0] == varList[1]: return data.loc[:, [varList[0]]]
            else: return data.loc[:,varList]
        else:
            return None

    def save(self, filename: str):
        """ This function saved the dataset in the provided path """
        dataset_folder, extension = os.path.splitext(filename)
        data_name = os.path.join(self.tempFolderPath, 'data.txt')

        if os.path.exists(data_name):
            shutil.copy(data_name, filename)
        else:
            self.data.to_csv(filename, index=False, header=self.header)

        if self.list_array:
            if not os.path.exists(dataset_folder): os.mkdir(dataset_folder)
            for tmp_folder in self.list_array:
                array_name = os.path.basename(tmp_folder)
                dest_folder = os.path.join(dataset_folder, array_name)

                if os.path.exists(tmp_folder):
                    shutil.copytree(tmp_folder, dest_folder, dirs_exist_ok=True)
                else:
                    # This is only executed if no temp folder is set
                    if not os.path.exists(dest_folder): os.mkdir(dest_folder)

                    if array_name in self.dictListDataFrame.keys():
                        list_data = self.dictListDataFrame[array_name]  # data is list representing id 1,2

                        for i, value in enumerate(list_data):
                            path = os.path.join(dest_folder, f"{i+1}.txt")

                            if type(value) in [int, float, bool, str, tuple]:
                                with open(path, 'w') as f: f.write(str(value))
                            elif type(value) == bytes:
                                with open(path, 'wb') as f: f.write(value)
                            elif type(value) == np.ndarray:
                                df = pd.DataFrame(value)
                                df.to_csv(path, index=False, header=None)  # faster and handle better different dtype than np.savetxt
                            elif type(value) == pd.DataFrame:
                                value.to_csv(path, index=False)

    def addPoint(self, dataPoint: OrderedDict):
        """ This function add a data point (parameter value, and results) in the dataset """
        ID = len(self.data) + 1
        simpledata = OrderedDict()
        simpledata['id'] = ID

        for resultName in dataPoint.keys():
            result = dataPoint[resultName]

            if resultName == 0:  # skip first result which is recipe_name
                continue
            else:
                element_list = [step['element'] for step in self.list_param if step['name']==resultName]
                if len(element_list) != 0:
                    element = element_list[0]
                else:
                    element_list = [step['element'] for step in self.list_step if step['name']==resultName]
                    if len(element_list) != 0:
                        element = element_list[0]
                # should always find element in lists above

            # If the result is displayable (numerical), keep it in memory
            if element is None or element.type in [int, float, bool]:
                simpledata[resultName] = result
            else : # Else write it on a file, in a temp directory
                folderPath = os.path.join(self.tempFolderPath, resultName)

                if self.save_temp:
                    if not os.path.exists(folderPath): os.mkdir(folderPath)
                    filePath = os.path.join(folderPath, f'{ID}.txt')

                    if element is not None:
                        element.save(filePath, value=result)

                if folderPath not in self.list_array:
                    self.list_array.append(folderPath)

                if self.dictListDataFrame.get(resultName) is None:
                    self.dictListDataFrame[resultName] = []

                self.dictListDataFrame[resultName].append(result)

        self.all_data_temp.append(simpledata)
        self.data = pd.DataFrame(self.all_data_temp, columns=self.header)

        if self.save_temp:
            if ID == 1:
                self.data.tail(1).to_csv(os.path.join(self.tempFolderPath, 'data.txt'), index=False, mode='a', header=self.header)
            else :
                self.data.tail(1).to_csv(os.path.join(self.tempFolderPath, 'data.txt'), index=False, mode='a', header=False)

    def __len__(self):
        """ Returns the number of data point of this dataset """
        return len(self.data)
