# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 22:08:29 2019

@author: qchat
"""
from PyQt5 import QtCore, QtWidgets, uic
import os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import threading
import time
import pandas as pd
import usit
import queue

class Monitor(QtWidgets.QMainWindow):
        
    def __init__(self,item):
        
        self.item = item
        self.variable = item.variable
        
        # Configuration of the window
        QtWidgets.QMainWindow.__init__(self)
        ui_path = os.path.join(os.path.dirname(__file__),'monitor.ui')
        uic.loadUi(ui_path,self)
        self.setWindowTitle(f"Monitoring variable {self.variable.name}")
        
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
        self.threadManager = ThreadManager(self)
        
        # Start
        self.windowLengthChanged()
        self.delayChanged()
        self.threadManager.start()
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
        
        if self.threadManager.isPaused() is False :
            self.timer.stop()
            self.pauseButton.setText('Resume')
            self.threadManager.pause()
        else :
            self.timer.start()
            self.pauseButton.setText('Pause')
            self.threadManager.resume()
            
            
        
    def saveButtonClicked(self):
        
        """ This function is called when the SAVE button is pressed, and launch the procedure 
        to save both the data and the figure """
        
        # Make sure the monitoring is paused
        if self.threadManager.isPaused() is False :
            self.threadManager.pauseButtonClicked()
        
        # Ask the path of the output folder
        path = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory",usit.core.USER_LAST_CUSTOM_FOLDER_PATH))
        
        # Save the given path for future, the data and the figure if the path provided is valid
        if path != '' :
            
            usit.core.USER_LAST_CUSTOM_FOLDER_PATH = path
            self.statusBar.showMessage('Saving data...',5000)
            
            try : 
                self.dataManager.save(path)
                self.figureManager.save(path)
                self.statusBar.showMessage(f'Data successfully saved in {path}.',5000)
            except :
                self.statusBar.showMessage('An error occured while saving data !',10000)
            

            
    def closeEvent(self,event):
        
        """ This function does some steps before the window is really killed """
        
        self.threadManager.close()
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
            self.threadManager.setDelay(value)
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
        
        value = self.threadManager.getDelay()
        self.delay_lineEdit.setText(f'{value:g}')
        self.setLineEditBackground(self.delay_lineEdit,'synced')
        
        
        
    

class ThreadManager : 
    
    def __init__(self,gui):
        
        self.gui = gui
        
        # Configure a new thread
        self.thread = MonitorThread(self.gui.variable,self.gui.queue)
        self.thread.errorSignal.connect(self.error)
        
        
        
    def error(self,error):
        
        """ This function is called when the errorSignal of the thread is raised.
        It update the pause button and displays the error in the GUI """
        
        self.gui.pauseButton.setText('Resume')
        self.gui.statusBar.showMessage(f'Error : {error} ',10000)
        
    
    
    def start(self):
        
        """ This function start the thread """
        
        self.thread.start()
        
        
        
    def setDelay(self,value):
        
        """ Set the delay in the thread """

        self.thread.delay = value
        
        
        
    def getDelay(self):
        
        """ Returns the current delay of the thread """
        
        return self.thread.delay
        
        
    
    def isPaused(self):
        
        """ This function returns whether the thread is paused or not """
        
        return self.thread.pauseFlag.is_set()
        

            
    def resume(self):
        
        """ This function resume the monitoring """
        
        self.thread.pauseFlag.clear()
    
    
    
    def pause(self):
        
        """ This function pause the monitoring """
        
        self.thread.pauseFlag.set()          
        
    
    
    def close(self):
        
        """ This function stops the thread and wait for its complete deletion """
        
        self.resume()
        self.thread.stopFlag.set()
        self.thread.wait()

        
        
        
        
        
        
            
class FigureManager :
    
    def __init__(self,gui):
        
        self.gui = gui
        
        # Configure and initialize the figure in the GUI
        self.fig = Figure()
        matplotlib.rcParams.update({'font.size': 12})
        self.ax = self.fig.add_subplot(111)        
        self.ax.set_xlabel('Time [s]')
        self.ax.set_ylabel(f'{self.gui.variable.getAddress()}')
        self.ax.grid()
        self.plot=self.ax.plot([0],[0],color='r')[0]
        # The first time we open a monitor it doesn't work, I don't know why..
        # There is no current event loop in thread 'Thread-7'.
        # More accurately, FigureCanvas doesn't find the event loop the first time it is called
        # The second time it works..
        # Seems to be only in Spyder..
        try : 
            self.canvas = FigureCanvas(self.fig) 
        except :
            self.canvas = FigureCanvas(self.fig)
        self.gui.graph.addWidget(self.canvas)
        self.fig.tight_layout()
        self.canvas.draw()

    
    def update(self,xlist,ylist):
        
        """ This function update the figure in the GUI """ 
        
        # Data retrieval
        self.plot.set_xdata(xlist)
        self.plot.set_ydata(ylist)

        # X axis update
        xlist = self.plot.get_xdata()
        xmin = min(xlist)
        xmax = max(xlist)
        if xmin != xmax :
            self.ax.set_xlim(xmin,xmax+0.15*(xmax-xmin))
        else :
            self.ax.set_xlim(xmin-0.1,xmin+0.1)
        
        # Y axis update
        ylist = self.plot.get_ydata()
        ymin = min(ylist)
        ymax = max(ylist)
        if ymin != ymax :
            self.ax.set_ylim(ymin-0.1*(ymax-ymin),ymax+0.1*(ymax-ymin))
        else :
            self.ax.set_ylim(ymin-0.1,ymin+0.1)
            
        # Figure finalization  
        self.redraw()
        #self.canvas.draw()

            
            
        
    def redraw(self):
        
        """ This function finalize the figure update in the GUI """
        
        try :
            self.fig.tight_layout()
        except :
            pass
        self.canvas.draw()
        
        
        
        
                
    def save(self,path):
        
        """ This function save the figure in the provided path """
        
        self.fig.savefig(os.path.join(path,'figure.jpg'),dpi=300)
        
        
        
        
        
        
        

class DataManager :
    
    def __init__(self,gui):
        
        self.gui = gui
        self.windowLength = 10 #
        
        self.xlist = []
        self.ylist = []
        
        
        
        
    def setWindowLength(self,value):
        
        """ This function set the value of the window length """
        
        self.windowLength = value
        
        
        
    def getWindowLength(self):
        
        """ This function returns the value of the window legnth """
        
        return self.windowLength
    
    
    
    def getData(self):
        
        """ This function update the data of the provided plot object """
        
        return self.xlist,self.ylist
        
        
        
    def save(self,path):
        
        """ This function save the data in a file, in the provided path """
        
        df = pd.DataFrame({'Time [s]':self.xlist,f'{self.gui.variable.name}':self.ylist})
        df.to_csv(os.path.join(path,'data.txt'),index=False)
        
        
        
    def addPoint(self,point):
        
        """ This function append a datapoint [x,y] in the lists of data """ 
        
        x,y = point
        
        # Append data
        self.xlist.append(x)
        self.ylist.append(y)
        
        # Remove too old data (regarding the window length)
        while max(self.xlist)-min(self.xlist) > self.windowLength : 
            self.xlist.pop(0)
            self.ylist.pop(0)
            

        
    
    
    
    



class MonitorThread(QtCore.QThread):
    
    """ This thread class is dedicated to read the variable, and send its data to GUI through a queue """
    
    errorSignal = QtCore.pyqtSignal(object) 

    def __init__(self,variable,queue):
        
        QtCore.QThread.__init__(self)
        self.variable = variable
        self.queue = queue
        
        self.pauseFlag = threading.Event()
        self.stopFlag = threading.Event()
        
        self.delay = 0
        
        
    def run(self):
        
        t_ini = time.time()
        
        pauseLength = 0
        pauseStartedTime = None      
        
        while self.stopFlag.is_set() is False :
                
            # If the thread just resume, take into account the delay it has been paused
            if pauseStartedTime is not None :
                pauseLength += time.time()-pauseStartedTime
                pauseStartedTime = None
            
            # Time measure
            now = time.time() - t_ini - pauseLength
            
            try : 
                
                # Measure variable
                value = self.variable()
                
                # Check type
                value = float(value)
                
                # Send signal new data
                self.queue.put([now,value])
                
            except Exception as e :
                
                self.errorSignal.emit(e)
                self.pauseFlag.set()
            
            # If not the thread may be too fast
            time.sleep(self.delay)
                
            # pause
            while self.pauseFlag.is_set() :
                if pauseStartedTime is None :
                    pauseStartedTime = time.time()
                time.sleep(0.1)
                
        
        
        
        
        
        
