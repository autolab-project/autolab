# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 22:08:29 2019

@author: qchat
"""
from PyQt5 import QtCore, QtWidgets, uic
import os
import queue

from autolab import paths

from .data import DataManager
from .figure import FigureManager
from .monitor import MonitorManager

class Monitor(QtWidgets.QMainWindow):
        
    def __init__(self,item):
        
        self.item = item
        self.variable = item.variable
        
        # Configuration of the window
        QtWidgets.QMainWindow.__init__(self)
        ui_path = os.path.join(os.path.dirname(__file__),'interface.ui')
        uic.loadUi(ui_path,self)
        self.setWindowTitle(f"AUTOLAB Monitor : Variable {self.variable.name}")
        
        # Queue
        self.queue = queue.Queue()
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(33) #30fps
        self.timer.timeout.connect(self.sync)
        
        # Window length
        self.windowLength_lineEdit.setText('10')
        self.windowLength_lineEdit.returnPressed.connect(self.windowLengthChanged)
        self.windowLength_lineEdit.textEdited.connect(lambda : self.setLineEditBackground(self.windowLength_lineEdit,'edited'))
        self.setLineEditBackground(self.windowLength_lineEdit,'synced')

        # Delay
        self.delay_lineEdit.setText('0.01')
        self.delay_lineEdit.returnPressed.connect(self.delayChanged)
        self.delay_lineEdit.textEdited.connect(lambda : self.setLineEditBackground(self.delay_lineEdit,'edited'))
        self.setLineEditBackground(self.delay_lineEdit,'synced')
        
        # Pause
        self.pauseButton.clicked.connect(self.pauseButtonClicked)
        
        # Save
        self.saveButton.clicked.connect(self.saveButtonClicked)
        
        # Managers
        self.dataManager = DataManager(self)
        self.figureManager = FigureManager(self)
        self.monitorManager = MonitorManager(self)
        
        # Start
        self.windowLengthChanged()
        self.delayChanged()
        self.monitorManager.start()
        self.timer.start()
        
    
    def setLineEditBackground(self,obj,state):
        
        if state == 'synced' :
            color='#D2FFD2' # vert
        if state == 'edited' :
            color='#FFE5AE' # orange
            
        obj.setStyleSheet("QLineEdit:enabled {background-color: %s; font-size: 9pt}"%color)
        
        
        
    def sync(self):
        
        """ This function updates the data and than the figure. 
        Function called by the time """
                
        # Empty the queue
        count = 0
        while not self.queue.empty():
            self.dataManager.addPoint(self.queue.get())
            count += 1
        
        # Upload the plot if new data available
        if count > 0 :
            xlist,ylist = self.dataManager.getData()
            self.figureManager.update(xlist,ylist)
        
    
    
    def pauseButtonClicked(self):
        
        """ This function pause or resume the monitoring """
        
        if self.monitorManager.isPaused() is False :
            self.timer.stop()
            self.pauseButton.setText('Resume')
            self.monitorManager.pause()
        else :
            self.timer.start()
            self.pauseButton.setText('Pause')
            self.monitorManager.resume()
            
            
        
    def saveButtonClicked(self):
        
        """ This function is called when the SAVE button is pressed, and launch the procedure 
        to save both the data and the figure """
        
        # Make sure the monitoring is paused
        if self.monitorManager.isPaused() is False :
            self.pauseButtonClicked()
        
        # Ask the path of the output folder
        path = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory",paths.USER_LAST_CUSTOM_FOLDER))
        
        # Save the given path for future, the data and the figure if the path provided is valid
        if path != '' :
            
            paths.USER_LAST_CUSTOM_FOLDER = path
            self.statusBar.showMessage('Saving data...',5000)
            
            try : 
                self.dataManager.save(path)
                self.figureManager.save(path)
                self.statusBar.showMessage(f'Data successfully saved in {path}.',5000)
            except :
                self.statusBar.showMessage('An error occured while saving data !',10000)
            

            
    def closeEvent(self,event):
        
        """ This function does some steps before the window is really killed """
        
        self.monitorManager.close()
        self.timer.stop()
        self.item.clearMonitor()
        
        
        

    def windowLengthChanged(self):
        
        """ This function start the update of the window length in the data manager
        when a changed has been detected """
        
        # Send the new value
        try : 
            value = float(self.windowLength_lineEdit.text())
            assert value > 0
            self.dataManager.setWindowLength(value)
        except : 
            pass
        
        # Rewrite the GUI with the current value
        self.updateWindowLengthGui() 
        
        
        
    def delayChanged(self):
        
        """ This function start the update of the delay in the thread manager
        when a changed has been detected """
        
        # Send the new value
        try : 
            value = float(self.delay_lineEdit.text())
            assert value >= 0
            self.monitorManager.setDelay(value)
        except : 
            pass
        
        # Rewrite the GUI with the current value
        self.updateDelayGui() 
        
        
        
    def updateWindowLengthGui(self):
        
        """ This function ask the current value of the window length in the data
        manager, and then update the GUI """
        
        value = self.dataManager.getWindowLength()
        self.windowLength_lineEdit.setText(f'{value:g}')
        self.setLineEditBackground(self.windowLength_lineEdit,'synced')
        
        
        
        
        
    def updateDelayGui(self):
        
        """ This function ask the current value of the delay in the data
        manager, and then update the GUI """
        
        value = self.monitorManager.getDelay()
        self.delay_lineEdit.setText(f'{value:g}')
        self.setLineEditBackground(self.delay_lineEdit,'synced')
        
        
        
    


        
        
        
        
        
        
        
    
    
    



        
        
        
        
        
        
