# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:10:31 2019

@author: qchat
"""

import collections
from queue import Queue
import os
import shutil
import tempfile
import sys

import pandas as pd
from qtpy import QtCore, QtWidgets

from ... import paths
from ... import config
from ... import utilities


class DataManager :
    """ Manage data from a scan """

    def __init__(self, gui):

        self.gui = gui
        self.datasets = []
        self.queue = Queue()
        self.initialized = False

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
                dataset = self.datasets[-(i+1)]
                dataset = dataset[recipe_name]

                if data_name == "Scan":
                    try:
                        data = dataset.getData(varList, data_name=data_name)  # OPTIMIZE: Currently can't recover dataset if error before end of first recipe loop
                    except Exception as e:
                        data = None
                        print(f"Error encountered for scan id {selectedData+1}: {e}", file=sys.stderr)
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
                            print(f"Error encountered for scan id {selectedData+1} and dataframe {data_name} with ID {index+1}: {e}", file=sys.stderr)
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
            filter="Text Files (*.txt);; Supported text Files (*.txt;*.csv;*.dat);; All Files (*)")
        path = os.path.dirname(filename)

        if path != '':
            paths.USER_LAST_CUSTOM_FOLDER = path
            self.gui.setStatus('Saving data...', 5000)
            dataset = self.getLastSelectedDataset()

            for sub_dataset_name in dataset.keys():
                sub_dataset = dataset[sub_dataset_name]

                if len(dataset) == 1:
                    filename_recipe = filename
                else:
                    dataset_folder, extension = os.path.splitext(filename)
                    filename_recipe = f'{dataset_folder}_{sub_dataset_name}{extension}'
                sub_dataset.save(filename_recipe)

            scanner_config = config.get_scanner_config()
            save_config = utilities.boolean(scanner_config["save_config"])

            if save_config:
                dataset_folder, extension = os.path.splitext(filename)
                new_configname = dataset_folder+".conf"
                config_name = os.path.join(os.path.dirname(sub_dataset.tempFolderPath), 'config.conf')
                shutil.copy(config_name, new_configname)

            if utilities.boolean(scanner_config["save_figure"]):
                self.gui.figureManager.save(filename)

            self.gui.setStatus(f'Last dataset successfully saved in {filename}',5000)

    def clear(self):
        """ This reset any recorded data, and the GUI accordingly """
        self.datasets = []
        self.initialized = False
        self.gui.figureManager.clearData()
        self.gui.figureManager.clearMenuID()
        self.gui.figureManager.figMap.hide()
        self.gui.figureManager.fig.show()
        self.gui.figureManager.setLabel("x", "")
        self.gui.figureManager.setLabel("y", "")
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

    def getLastDataset(self):
        """ This return the current (last created) dataset """
        return self.datasets[-1] if len(self.datasets) > 0 else None

    def getLastSelectedDataset(self) -> list:
        """ This return the current (last selected) dataset """
        return self.datasets[self.gui.data_comboBox.currentIndex()]

    def newDataset(self, config: dict):
        """ This function creates and returns a new empty dataset """
        maximum = 0
        dataset_recipes = {}
        tempFolderPath = tempfile.mkdtemp() # Creates a temporary directory for this dataset
        self.gui.configManager.export(os.path.join(tempFolderPath,'config.conf'))

        for recipe_name in list(config.keys()):
            sub_config = config[recipe_name]
            sub_folder = os.path.join(tempFolderPath, recipe_name)
            os.mkdir(sub_folder)
            dataset = Dataset(sub_folder, recipe_name, sub_config)
            dataset_recipes[recipe_name] = dataset
            maximum += sub_config['nbpts']

        self.datasets.append(dataset_recipes)
        self.gui.progressBar.setMaximum(maximum)
        return dataset

    def sync(self):
        """ This function sync the last dataset with the data available in the queue """
        # Empty the queue
        count = 0
        dataset = self.getLastDataset()
        lenQueue = self.queue.qsize()

        for i in range(lenQueue):
            try : point = self.queue.get()  # point is collections.OrderedDict{'recipe_name':recipe_name, 'parameter_name':parameter_value, 'step1_name':step1_value, 'step2_name':step2_value, ...}
            except : break

            recipe_name = list(point.values())[0]
            sub_dataset = dataset[recipe_name]
            sub_dataset.addPoint(point)
            count += 1
            # Useless TODO if decide to change how scan is done (recipe class from v2) and how data is stored
            # OPTIMIZE: redo dataframe plot with a better logic: create dict with dataframe name as key \
            # and the values is a dict with all information needed to create checkbox \
            # with it can have unique checkbox list and bool for each dataframe and over multiple scan id
            # Maybe create a class instead of dict that regroup everything related to a dataframe of a recipe
            listDataFrame = list(sub_dataset.dictListDataFrame.values())
            if len(listDataFrame) != 0:
                nb_id = 0
                for dataframe in listDataFrame:
                    if len(dataframe) > nb_id:
                        nb_id = len(dataframe)

                # not-oPTIMIZE: edit: not necessary if show only one scan <- values will not correspond to previous scan if start a new scan with a different range parameter
                nb_total =  sub_dataset.config["nbpts"]

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

        # Upload the plot if new data available
        if count > 0:
            progress = 0 # Update progress bar

            for sub_dataset_name in dataset.keys():
                if recipe_name == sub_dataset_name:
                    progress += len(dataset[sub_dataset_name])
                    break
                else:
                    progress += dataset[sub_dataset_name].config["nbpts"]

            self.gui.progressBar.setValue(progress)

            # Executed after the first start of a new config scan
            if not self.initialized:
                self.gui.scan_recipe_comboBox.setCurrentText(recipe_name)
                self.updateDisplayableResults()
                self.gui.save_pushButton.setEnabled(True)
                self.initialized = True

            # Executed after any dataset newly created and fed
            if sub_dataset.new:
                self.gui.figureManager.reloadData()
                sub_dataset.new = False

            self.gui.figureManager.updateDataframe_comboBox()

    def updateDisplayableResults(self) :
        """ This function update the combobox in the GUI that displays the names of
        the results that can be plotted """
        data_name = self.gui.dataframe_comboBox.currentText()
        recipe_name = self.gui.scan_recipe_comboBox.currentText()
        dataset = self.getLastSelectedDataset()
        sub_dataset = dataset[recipe_name]

        if data_name == "Scan":
            data = sub_dataset.data
        else:
            if sub_dataset.dictListDataFrame.get(data_name) is not None:
                for data in sub_dataset.dictListDataFrame[data_name]:  # used only to get columns name
                    if data is not None:
                        break
            else:
                return None
            # if text or if image return
            if type(data) is str or not (len(data.T.shape) == 1 or data.T.shape[0] == 2):
                self.gui.variable_x_comboBox.clear()
                self.gui.variable_y_comboBox.clear()
                return None

            data = utilities.formatData(data)

        resultNamesList = []

        for resultName in data.columns:
            if resultName not in ['id']:
                try:
                    float(data.iloc[0][resultName])
                    resultNamesList.append(resultName)
                except:
                    pass

        self.gui.variable_x_comboBox.clear()
        self.gui.variable_x_comboBox.addItems(resultNamesList)  # parameter first

        if resultNamesList:
            name = resultNamesList.pop(0)
            resultNamesList.append(name)

        self.gui.variable_y_comboBox.clear()
        self.gui.variable_y_comboBox.addItems(resultNamesList)  # first numerical measure first


class Dataset():
    """ Collection of data from a scan """

    def __init__(self, tempFolderPath: str, recipe_name: str, config: dict):
        self.all_data_temp = list()
        self.recipe_name = recipe_name
        self.config = config
        self.header = ["id", self.config['parameter']['name']
                       ] + [step['name'] for step in self.config['recipe'] if step['stepType'] == 'measure' and step['element'].type in [int, float, bool]]
        self.data = pd.DataFrame(columns=self.header)
        self.list_array = list()
        self.dictListDataFrame = dict()
        self.tempFolderPath = tempFolderPath
        self.new = True

    def getData(self, varList: list, data_name : str = "Scan", dataID: int = 0):
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
        shutil.copy(data_name, filename)

        if self.list_array:
            if not os.path.exists(dataset_folder): os.mkdir(dataset_folder)
            for tmp_folder in self.list_array:
                array_name = os.path.basename(tmp_folder)
                dest_folder = os.path.join(dataset_folder, array_name)
                shutil.copytree(tmp_folder, dest_folder, dirs_exist_ok=True)

    def addPoint(self, dataPoint: collections.OrderedDict):
        """ This function add a data point (parameter value, and results) in the dataset """
        ID = len(self.data) + 1
        simpledata = collections.OrderedDict()
        simpledata['id'] = ID

        for resultName in dataPoint.keys():
            result = dataPoint[resultName]

            if resultName == self.recipe_name:
                continue
            elif resultName == self.config['parameter']['name']:
                element = self.config['parameter']['element']
            else :
                element = [step['element'] for step in self.config['recipe'] if step['name']==resultName][0]

            # If the result is displayable (numerical), keep it in memory
            if element is None or element.type in [int, float, bool]:
                simpledata[resultName] = result
            else : # Else write it on a file, in a temp directory
                folderPath = os.path.join(self.tempFolderPath, resultName)
                if not os.path.exists(folderPath): os.mkdir(folderPath)
                filePath = os.path.join(folderPath, f'{ID}.txt')

                if element is not None:
                    element.save(filePath, value=result)  # OPTIMIZE: very slow if save large data like high resolution image, which block the GUI until completion. First solution: save in diff thread than GUI. Second solution: don't save during scan but risk of loosing data if crash :/. Third option (too heavy for the user) allow to tick if want to save or not a recipe element.

                if folderPath not in self.list_array:
                    self.list_array.append(folderPath)

                if element.type is not str:  # OPTIMIZE: remove text because can't display it. If in future decide to plot text, remove this condition
                    resultNameKey = self.dictListDataFrame.get(resultName)

                    if resultNameKey is None:
                         if ID == 1:
                             self.dictListDataFrame[resultName] = []

                    self.dictListDataFrame[resultName].append(result)

        self.all_data_temp.append(simpledata)
        self.data = pd.DataFrame(self.all_data_temp, columns=self.header)

        if ID == 1:
            self.data.tail(1).to_csv(os.path.join(self.tempFolderPath,'data.txt'), index=False, mode='a', header=self.header)
        else :
            self.data.tail(1).to_csv(os.path.join(self.tempFolderPath,'data.txt'), index=False, mode='a', header=False)

    def __len__(self):
        """ Returns the number of data point of this dataset """
        return len(self.data)
