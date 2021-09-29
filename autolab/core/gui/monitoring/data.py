# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:22:43 2019

@author: qchat
"""

import pandas as pd


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



    def save(self,filename):

        """ This function save the data in a file with the provided filename"""

        df = pd.DataFrame({'Time [s]':self.xlist,f'{self.gui.variable.address()}':self.ylist})
        df.to_csv(filename, index=False)



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


    def clear(self):
        self.xlist.clear()
        self.ylist.clear()

