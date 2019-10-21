# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:14:28 2019

@author: qchat
"""
import numpy as np
import math as m

class RangeManager : 
    
    def __init__(self,gui):
        
        self.gui = gui
        
        # Widget 'return pressed' signal connections
        self.gui.scanLog_checkBox.stateChanged.connect(self.scanLogChanged)
        self.gui.nbpts_lineEdit.returnPressed.connect(self.nbptsChanged)
        self.gui.step_lineEdit.returnPressed.connect(self.stepChanged)
        self.gui.start_lineEdit.returnPressed.connect(self.startChanged)
        self.gui.end_lineEdit.returnPressed.connect(self.endChanged)
        self.gui.mean_lineEdit.returnPressed.connect(self.meanChanged)
        self.gui.width_lineEdit.returnPressed.connect(self.widthChanged)
        
        # Widget 'text edited' signal connections
        self.gui.nbpts_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.nbpts_lineEdit,'edited'))
        self.gui.step_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.step_lineEdit,'edited'))
        self.gui.start_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.start_lineEdit,'edited'))
        self.gui.end_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.end_lineEdit,'edited'))
        self.gui.mean_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.mean_lineEdit,'edited'))
        self.gui.width_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.width_lineEdit,'edited'))
        
        # Push button
        self.gui.fromFigure_pushButton.clicked.connect(self.fromFigureButtonClicked)
        self.gui.fromFigure_pushButton.setEnabled(False)
        
        self.refresh()
                        
        
        
    def fromFigureButtonClicked(self):
        
        """ This function sets the start and end value, and log state, of the scan from currrent figure range """
        
        xrange = self.gui.figureManager.getRange('x')
        self.gui.configManager.setRange(xrange)
        
        log = self.gui.figureManager.isLogScaleEnabled('x')
        self.gui.configManager.setLog(log)
        
        
        
    def refresh(self):
        
        """ This function refreshes all the values displayed of the scan configuration
        from the configuration center"""
        
        xrange = self.gui.configManager.getRange()
        
        # Start
        start = xrange[0]
        self.gui.start_lineEdit.setText(f'{start:g}')
        self.gui.setLineEditBackground(self.gui.start_lineEdit,'synced')
        
        # End
        end = xrange[1]
        self.gui.end_lineEdit.setText(f'{end:g}')
        self.gui.setLineEditBackground(self.gui.end_lineEdit,'synced')
        
        # Mean
        mean = (start+end)/2
        self.gui.mean_lineEdit.setText(f'{mean:g}')
        self.gui.setLineEditBackground(self.gui.mean_lineEdit,'synced')
        
        # Width        
        width = abs(end-start)
        self.gui.width_lineEdit.setText(f'{width:g}')
        self.gui.setLineEditBackground(self.gui.width_lineEdit,'synced')
        
        # Nbpts
        nbpts = self.gui.configManager.getNbPts()
        self.gui.nbpts_lineEdit.setText(f'{nbpts:g}')
        self.gui.setLineEditBackground(self.gui.nbpts_lineEdit,'synced')
        
        # Log 
        log = self.gui.configManager.getLog()
        self.gui.scanLog_checkBox.setChecked(log)
        
        # Step
        if log is False :
            step = width / (nbpts-1)
            self.gui.step_lineEdit.setText(f'{step:g}')
            self.gui.step_lineEdit.setEnabled(True)
        else :
            self.gui.step_lineEdit.setEnabled(False)
            self.gui.step_lineEdit.setText('')
        self.gui.setLineEditBackground(self.gui.step_lineEdit,'synced')
            
            
        
    def nbptsChanged(self) :
        
        """ This function changes the number of point of the scan """
        
        value = self.gui.nbpts_lineEdit.text()
        
        try :
            value = int(float(value))
            assert value > 2
            self.gui.configManager.setNbPts(value)
        except :
            self.refresh()
        
        
        
    def stepChanged(self) :
        
        """ This function changes the step size of the scan """
        
        value = self.gui.step_lineEdit.text()

        try :
            value = float(value)
            assert value > 0
            xrange = list(self.gui.configManager.getRange())
            width = xrange[1]-xrange[0]
            nbpts = round(abs(width)/value)+1
            self.gui.configManager.setNbPts(nbpts)
            xrange[1] = xrange[0]+np.sign(width)*(nbpts-1)*value
            self.gui.configManager.setRange(xrange)
        except :
            self.refresh()
        
        
        
    def startChanged(self) : 
        
        """ This function changes the start value of the scan """
        
        value = self.gui.start_lineEdit.text()
        
        try:
            value=float(value)
            log = self.gui.configManager.getLog()
            if log is True : assert value>0
            print(value,log,'pas de soucis')
            xrange = list(self.gui.configManager.getRange())
            xrange[0] = value
            self.gui.configManager.setRange(xrange)
        except:
            self.refresh()



    def endChanged(self) : 
        
        """ This function changes the end value of the scan """
        
        value = self.gui.end_lineEdit.text()
        
        try:
            value=float(value)
            log = self.gui.configManager.getLog()
            if log is True : assert value>0
            xrange = list(self.gui.configManager.getRange())
            xrange[1] = value
            self.gui.configManager.setRange(xrange)
        except :
            self.refresh()



    def meanChanged(self) : 
        
        """ This function changes the mean value of the scan """
        
        value = self.gui.mean_lineEdit.text()
        
        try:
            value=float(value)
            log = self.gui.configManager.getLog()
            if log is True : assert value>0
            xrange = list(self.gui.configManager.getRange())
            xrange_new = xrange.copy()
            xrange_new[0] = value - (xrange[1]-xrange[0])/2
            xrange_new[1] = value + (xrange[1]-xrange[0])/2
            assert xrange_new[0] > 0
            assert xrange_new[1] > 0
            self.gui.configManager.setRange(xrange_new)
        except:
            self.refresh()
     
        
        
    def widthChanged(self) : 
        
        """ This function changes the width of the scan """
        
        value = self.gui.width_lineEdit.text()
        
        try:
            value=float(value)
            log = self.gui.configManager.getLog()
            if log is True : assert value>0
            xrange = list(self.gui.configManager.getRange())
            xrange_new = xrange.copy()
            xrange_new[0] = (xrange[1]+xrange[0])/2 - value/2
            xrange_new[1] = (xrange[1]+xrange[0])/2 + value/2  
            assert xrange_new[0] > 0
            assert xrange_new[1] > 0
            self.gui.configManager.setRange(xrange_new)
        except:
            self.refresh()
        
        
        
    def scanLogChanged(self):
        
        """ This function changes the log state of the scan """
        
        state = self.gui.scanLog_checkBox.isChecked()
        if state is True :
            xrange = list(self.gui.configManager.getRange())
            change = False
            if xrange[1] <= 0 : 
                xrange[1] = 1
                change = True
            if xrange[0] <= 0 : 
                xrange[0] = 10**(m.log10(xrange[1])-1)
                change = True
            if change is True : 
                self.gui.configManager.setRange(xrange)
        
        self.gui.configManager.setLog(state)
                