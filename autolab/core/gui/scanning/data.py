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
from PyQt5 import QtCore,QtWidgets

from ... import paths


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



    def getData(self,nbDataset,varList, selectedData=0):

        """ This function returns to the figure manager the required data """

        dataList = []

        for i in range(selectedData, nbDataset+selectedData) :
            if i < len(self.datasets) :
                dataset = self.datasets[-(i+1)]
                try:
                    data = dataset.getData(varList)  # OPTIMIZE: Currently can't recover dataset if error during first recipe loop
                except:
                    data = None
                    print(f"Error encountered for scan id {selectedData+1}", file=sys.stderr)
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
                self.gui.setStatus('Saving data...',5000)

                dataset.save(filename)
                self.gui.figureManager.save(filename)

                self.gui.setStatus(f'Last dataset successfully saved in {filename}',5000)



    def clear(self):

        """ This reset any recorded data, and the GUI accordingly """

        self.datasets = []
        self.initialized = False
        self.gui.figureManager.clearData()
        self.gui.variable_x_comboBox.clear()
        self.gui.variable_y_comboBox.clear()
        self.gui.data_comboBox.clear()
        self.gui.save_pushButton.setEnabled(False)
        self.gui.progressBar.setValue(0)



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
        self.gui.progressBar.setMaximum(config['nbpts'])
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
            self.gui.figureManager.reloadLastData()



    def updateDisplayableResults(self) :

        """ This function update the combobox in the GUI that displays the names of
        the results that can be plotted """

        dataset = self.getLastSelectedDataset()

        resultNamesList = []
        for resultName in dataset.data.columns :
            if resultName not in ['id'] :
                try :
                    float(dataset.data.iloc[0][resultName])
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

        self.data = pd.DataFrame()
        self.list_array = list()
        self.tempFolderPath = tempfile.mkdtemp() # Creates a temporary directory for this dataset
        self.new = True

        self.gui.configManager.export(os.path.join(self.tempFolderPath,'config.conf'))



    def getData(self,varList):

        """ This function returns a dataframe with two columns : the parameter value,
        and the requested result value """

        if varList[0] == varList[1] : return self.data.loc[:,[varList[0]]]
        else : return self.data.loc[:,varList]



    def save(self,filename):

        """ This function saved the dataset in the provided path """

        dataset_folder, extension = os.path.splitext(filename)
        new_configname = dataset_folder+".conf"

        config_name = os.path.join(self.tempFolderPath,'config.conf')  # TODO: add option to choose if want config saved in autolab config
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

        ID = len(self.data)+1

        simpledata =collections.OrderedDict()
        simpledata['id']=ID

        for resultName in dataPoint.keys():

            result = dataPoint[resultName]

            if resultName == self.config['parameter']['name'] :
                element = self.config['parameter']['element']
            else :
                element = [step['element'] for step in self.config['recipe'] if step['name']==resultName][0]

            resultType = element.type

            # If the result is displayable (numerical), keep it in memory
            if resultType in [int,float,bool]:
                simpledata[resultName] = result

            # Else write it on a file, in a temp directory
            else :
                folderPath = os.path.join(self.tempFolderPath,resultName)
                if not os.path.exists(folderPath) : os.mkdir(folderPath)
                filePath = os.path.join(folderPath,f'{ID}.txt')
                element.save(filePath,value=result)
                if folderPath not in self.list_array:
                    self.list_array.append(folderPath)

        self.all_data_temp.append(simpledata)
        self.data = pd.DataFrame(self.all_data_temp)


        if ID == 1 :
            self.data = self.data[list(simpledata.keys())] # reorder columns
            header = True
        else :
            header = False

        self.data.tail(1).to_csv(os.path.join(self.tempFolderPath,'data.txt'),index=False,mode='a',header=header)



    def __len__(self):

        """ Returns the number of data point of this dataset """

        return len(self.data)
