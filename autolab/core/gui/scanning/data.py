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

import numpy as np
import pandas as pd
from qtpy import QtCore, QtWidgets

from ... import paths
from ... import config
from ... import utilities


class DataManager :

    def __init__(self,gui):

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



    def getData(self,nbDataset,varList, selectedData=0, data_name="Scan"):

        """ This function returns to the figure manager the required data """

        dataList = []

        for i in range(selectedData, nbDataset+selectedData) :
            if i < len(self.datasets) :
                dataset = self.datasets[-(i+1)]
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
                self.gui.setStatus('Saving data...',5000)

                scanner_config = config.get_scanner_config()
                save_config = utilities.boolean(scanner_config["save_config"])
                dataset.save(filename, save_config=save_config)
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
        self.gui.figureManager.setLabel("x","")
        self.gui.figureManager.setLabel("y","")
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


    def getLastDataset(self):

        """ This return the current (last created) dataset """

        if len(self.datasets) > 0:
            return self.datasets[-1]


    def getLastSelectedDataset(self):

        """ This return the current (last selected) dataset """

        return self.datasets[self.gui.data_comboBox.currentIndex()]



    def newDataset(self,config):

        """ This function creates and returns a new empty dataset """

        dataset = Dataset(self.gui,config)
        self.datasets.append(dataset)
        maximum = config['nbpts']
        if len(config['initrecipe']) != 0:
            maximum += 1
        if len(config['endrecipe']) != 0:
            maximum += 1
        self.gui.progressBar.setMaximum(maximum)
        return dataset



    def sync(self):

        """ This function sync the last dataset with the data available in the queue """

        # Empty the queue
        count = 0
        dataset = self.getLastDataset()
        lenQueue = self.queue.qsize()

        for i in range(lenQueue):

            try : point = self.queue.get()
            except : break
            dataset.addPoint(point)
            count += 1

            # Useless TODO if decide to change how scan is done (recipe class from v2) and how data is stored
            # TODO: redo dataframe plot with a better logic: create dict with dataframe name as key \
            # and the values is a dict with all information needed to create checkbox \
            # with it can have unique checkbox list and bool for each dataframe and over multiple scan id
            # Maybe create a class instead of dict that regroup everything related to a dataframe of a recipe
            listDataFrame = list(dataset.dictListDataFrame.values())
            if len(listDataFrame) != 0:
                nb_id = 0
                for dataframe in listDataFrame:
                    if len(dataframe) > nb_id:
                        nb_id = len(dataframe)

                # OPTIMIZE: values will not correspond to previous scan if start a new scan with a different range parameter
                nb_total =  (dataset.config["nbpts"]
                             + int(len(dataset.config['initrecipe']) != 0)
                             + int(len(dataset.config['endrecipe']) != 0))

                while self.gui.figureManager.nbCheckBoxMenuID > nb_total:
                    self.gui.figureManager.removeLastCheckBox2MenuID()

                if self.gui.figureManager.nbCheckBoxMenuID >= nb_id:
                    if (len(dataset.config['endrecipe']) != 0) and (nb_id == nb_total):
                        paramValue = "end"
                    else:
                        paramValue = list(point.values())[0]
                    self.gui.figureManager.menuWidgetList[nb_id-1].setText(str(paramValue))

                while self.gui.figureManager.nbCheckBoxMenuID < nb_id:
                    # OPTIMIZE: could add condition on dataframe in init to add box init only if there is dataframe in it but need to change condition on end
                    if len(dataset.config['initrecipe']) != 0 and self.gui.figureManager.nbCheckBoxMenuID == 0:
                        paramValue = "init"
                    elif (len(dataset.config['endrecipe']) != 0) and ((self.gui.figureManager.nbCheckBoxMenuID + 1) == nb_total):
                        paramValue = "end"
                    else:
                        paramValue = list(point.values())[0]
                    self.gui.figureManager.addCheckBox2MenuID(paramValue)



        # Upload the plot if new data available
        if count > 0:
            # Updagte progress bar
            self.gui.progressBar.setValue(len(dataset))

            # Executed after the first start of a new config scan
            if self.initialized is False :
                self.updateDisplayableResults()
                self.gui.save_pushButton.setEnabled(True)
                self.initialized = True

            # Executed after any dataset newly created and fed
            if dataset.new is True :
                self.gui.figureManager.reloadData()
                dataset.new = False

            # Executed each time the queue is read
            data_name = self.gui.dataframe_comboBox.currentText()
            if data_name == "Scan":
                self.gui.figureManager.reloadLastData()
            else:
                self.gui.figureManager.reloadData()

            index = self.gui.dataframe_comboBox.currentIndex()
            key_list = []
            for dataset_key in self.datasets:
                list_dataframe_key = list(dataset_key.dictListDataFrame.keys())
                if len(key_list) < len(list_dataframe_key):
                    key_list = list_dataframe_key
            resultNamesList = ["Scan"] + key_list
            self.gui.dataframe_comboBox.clear()
            self.gui.dataframe_comboBox.addItems(resultNamesList)

            self.gui.dataframe_comboBox.setCurrentIndex(index)




    def updateDisplayableResults(self) :

        """ This function update the combobox in the GUI that displays the names of
        the results that can be plotted """

        dataset = self.getLastSelectedDataset()
        data_name = self.gui.dataframe_comboBox.currentText()

        if data_name == "Scan":
            data = dataset.data
        else:
            if dataset.dictListDataFrame.get(data_name) is not None:
                for data in dataset.dictListDataFrame[data_name]:  # used only to get columns name
                    if data is not None:
                        break
            else:
                return
            if not (len(data.T.shape) == 1 or data.T.shape[0] == 2):
                self.gui.variable_x_comboBox.clear()
                self.gui.variable_y_comboBox.clear()
                return

            data = utilities.formatData(data)

        resultNamesList = []

        for resultName in data.columns :
            if resultName not in ['id'] :
                try :
                    float(data.iloc[0][resultName])
                    resultNamesList.append(resultName)
                except :
                    pass

        self.gui.variable_x_comboBox.clear()
        self.gui.variable_x_comboBox.addItems(resultNamesList) # parameter first

        name=resultNamesList.pop(0)
        resultNamesList.append(name)
        self.gui.variable_y_comboBox.clear()

        self.gui.variable_y_comboBox.addItems(resultNamesList) # first numerical measure first




class Dataset():

    def __init__(self,gui,config):

        self.all_data_temp = list()

        self.gui = gui
        self.config = config

        recipes_list = self.config['initrecipe'] + self.config['recipe'] + self.config['endrecipe']
        self.header = ["id", self.config['parameter']['name']
                       ] + [step['name'] for step in recipes_list if step['stepType'] == 'measure' and step['element'].type in [int,float,bool]]
        self.data = pd.DataFrame(columns=self.header)

        self.list_array = list()
        self.dictListDataFrame = dict()
        self.tempFolderPath = tempfile.mkdtemp() # Creates a temporary directory for this dataset
        self.new = True

        self.gui.configManager.export(os.path.join(self.tempFolderPath,'config.conf'))



    def getData(self,varList, data_name="Scan", dataID=0):

        """ This function returns a dataframe with two columns : the parameter value,
        and the requested result value """

        if data_name == "Scan":
            data = self.data
        else:
            data = self.dictListDataFrame[data_name][dataID]

            if (data is not None) and (len(data.T.shape) == 1 or data.T.shape[0] == 2):
                data = utilities.formatData(data)
            else:  # Image
                return data


        if any(map(lambda v: v in varList, list(data.columns))):
            if varList[0] == varList[1] : return data.loc[:,[varList[0]]]
            else : return data.loc[:,varList]
        else:
            return None



    def save(self,filename, save_config=True):

        """ This function saved the dataset in the provided path """

        dataset_folder, extension = os.path.splitext(filename)
        new_configname = dataset_folder+".conf"

        if save_config:
            config_name = os.path.join(self.tempFolderPath,'config.conf')
            shutil.copy(config_name, new_configname)

        data_name = os.path.join(self.tempFolderPath,'data.txt')
        shutil.copy(data_name, filename)

        if self.list_array:
            if not os.path.exists(dataset_folder): os.mkdir(dataset_folder)

            for tmp_folder in self.list_array:
                array_name = os.path.basename(tmp_folder)
                dest_folder = os.path.join(dataset_folder, array_name)
                shutil.copytree(tmp_folder, dest_folder, dirs_exist_ok=True)


    def addPoint(self,dataPoint):

        """ This function add a data point (parameter value, and results) in the dataset """

        if len(self.config['initrecipe']) == 0 :
            ID = len(self.data)+1
        else:
            ID = len(self.data)

        is_first_id = (ID == 0) or ((ID == 1) and (len(self.config['initrecipe']) == 0))

        simpledata =collections.OrderedDict()
        simpledata['id']=ID

        for resultName in dataPoint.keys():

            result = dataPoint[resultName]

            if resultName == self.config['parameter']['name'] :
                element = self.config['parameter']['element']
            else :
                recipes_list = self.config['initrecipe'] + self.config['recipe'] + self.config['endrecipe']
                element = [step['element'] for step in recipes_list if step['name']==resultName][0]

            # If the result is displayable (numerical), keep it in memory
            if element.type in [int,float,bool]:
                simpledata[resultName] = result

            # Else write it on a file, in a temp directory
            else :
                folderPath = os.path.join(self.tempFolderPath,resultName)
                if not os.path.exists(folderPath) : os.mkdir(folderPath)
                filePath = os.path.join(folderPath,f'{ID}.txt')
                element.save(filePath,value=result)  # OPTIMIZE: very slow if save large data like high resolution image, which block the GUI until completion. First solution: save in diff thread than GUI. Second solution: don't save during scan but risk of loosing data if crash :/. Third option (too heavy for the user) allow to tick if want to save or not a recipe element.
                if folderPath not in self.list_array:
                    self.list_array.append(folderPath)

                resultNameKey = self.dictListDataFrame.get(resultName)
                if resultNameKey is None:
                     if is_first_id:
                         self.dictListDataFrame[resultName] = []
                     else:
                         if len(self.config['initrecipe']) == 0:
                             self.dictListDataFrame[resultName] = [None]*(ID-1)
                         else:
                             self.dictListDataFrame[resultName] = [None]*(ID)


                self.dictListDataFrame[resultName].append(result)

        self.all_data_temp.append(simpledata)
        self.data = pd.DataFrame(self.all_data_temp, columns=self.header)


        if is_first_id:
            self.data.tail(1).to_csv(os.path.join(self.tempFolderPath,'data.txt'),index=False,mode='a',header=self.header)
        else :
            self.data.tail(1).to_csv(os.path.join(self.tempFolderPath,'data.txt'),index=False,mode='a', header=False)




    def __len__(self):

        """ Returns the number of data point of this dataset """

        return len(self.data)
