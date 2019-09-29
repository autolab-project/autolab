# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:10:31 2019

@author: qchat
"""

import collections
from queue import Queue
from PyQt5 import QtCore,QtWidgets
import usit
import distutils
import os 
import numpy as np
import pandas as pd
import tempfile

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
        
        
        
    def getPlotData(self,nbDataset,resultName):
        
        """ This function returns to the figure manager the required data """
        
        dataList = []
        
        for i in range(nbDataset) :
            try :
                dataset = self.datasets[-(i+1)]
                data = dataset.getData(resultName)
                dataList.append(data)
            except :
                break
            
        dataList.reverse()
        
        return dataList
        
        
        
    def saveButtonClicked(self):
        
        """ This function is called when the save button is clicked. 
        It asks a path and starts the procedure to save the data """
        
        dataset = self.getLastDataset()
        if dataset is not None :
            
            path = str(QtWidgets.QFileDialog.getExistingDirectory(self.gui, 
                                                              "Select Directory",
                                                              usit.core.USER_LAST_CUSTOM_FOLDER_PATH))
     
            if path != '' :
                dataset.save(path)
                self.gui.figureManager.save(path)
                
            self.gui.statusBar.showMessage(f'Last dataset successfully saved in {path}',5000)
        
        

    def clear(self):
        
        """ This reset any recorded data, and the GUI accordingly """
        
        self.datasets = []
        self.initialized = False
        self.gui.variable_comboBox.clear()
        self.gui.save_pushButton.setEnabled(False)
        
        
        
    def getLastDataset(self):
        
        """ This return the current (last created) dataset """
        
        if len(self.datasets)>0 :
            return self.datasets[-1]
        
        
        
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
        for i in range(lenQueue) :
            try : point = self.queue.get()
            except : break
            dataset.addPoint(point)
            count += 1
        
        # Upload the plot if new data available
        if count > 0 :
            
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
        
        dataset = self.getLastDataset()
        
        resultNamesList = []
        for resultName in dataset.data.columns :
            if resultName not in ['id',dataset.config['parameter']['name']] :
                try : 
                    float(dataset.data.iloc[0][resultName])
                    resultNamesList.append(resultName)
                except : 
                    pass
    
        self.gui.variable_comboBox.clear()
        self.gui.variable_comboBox.addItems(resultNamesList)
        
        
        
        
        
        
        
        
class Dataset():
    
    def __init__(self,gui,config):
        
        self.gui = gui
        self.config = config
     
        self.data = pd.DataFrame()
        self.tempFolderPath = tempfile.mkdtemp() # Creates a temporary directory for this dataset
        self.new = True
        
        # Save current config in the temp directory
        self.gui.configManager.export(os.path.join(self.tempFolderPath,'config.conf'))
        
        

    def getData(self,resultName):
        
        """ This function returns a dataframe with two columns : the parameter value,
        and the requested result value """
        
        data = self.data[[self.config['parameter']['name'],resultName]]
        data.rename(columns={self.config['parameter']['name']: 'x', resultName: 'y'},inplace=True)
        return data
    
    
    
    def save(self,path):
        
        """ This function saved the dataset in the provided path """
        
        distutils.dir_util.copy_tree(self.tempFolderPath,path)
        
    
    
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
            if resultType in [np.ndarray,pd.DataFrame,str]:
                folderPath = os.path.join(self.tempFolderPath,resultName)
                if os.path.exists(folderPath) is False : os.mkdir(folderPath)
                filePath = os.path.join(folderPath,f'{ID}.txt')
                usit.core.devices.save(element,result,filePath)
                
            # Else write it on a file, in a temp directory
            else : 
                simpledata[resultName] = result
            
        # Store data in the dataset's dataframe
        self.data = self.data.append(simpledata,ignore_index=True)
        if ID == 1 : 
            self.data = self.data[simpledata.keys()] # reorder columns
            header = True
        else :
            header = False
        self.data.tail(1).to_csv(os.path.join(self.tempFolderPath,f'data.txt'),index=False,mode='a',header=header)
        
        
        
    def __len__(self):
        
        """ Returns the number of data point of this dataset """
        
        return len(self.data)
    
    