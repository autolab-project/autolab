# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:13:45 2019

@author: qchat
"""

from . import main

class ParameterManager :
    
    def __init__(self,gui):
        
        self.gui = gui
        
        self.gui.parameterName_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.parameterName_lineEdit,'edited'))
        self.gui.parameterName_lineEdit.returnPressed.connect(self.nameChanged)
        self.gui.parameterName_lineEdit.setEnabled(False)
        
        self.refresh()
        
        
        
    def refresh(self):
        
        """ This functions refreshes all the values of the name and address of the scan parameter, 
        from the configuration center """
                
        # Paramater name, address and unit
        parameter = self.gui.configManager.getParameter()
        
        if parameter is not None :
            name = self.gui.configManager.getParameterName()
            self.gui.parameterName_lineEdit.setEnabled(True)
            address = parameter.address()
            unit = parameter.unit
        else :
            name = ''
            self.gui.parameterName_lineEdit.setEnabled(False)
            address = ''
            unit = ''
            
        self.gui.parameterName_lineEdit.setText(name)
        self.gui.setLineEditBackground(self.gui.parameterName_lineEdit,'synced')
        self.gui.parameterAddress_label.setText(address)
        self.gui.startUnit_label.setText(unit)
        self.gui.meanUnit_label.setText(unit)
        self.gui.widthUnit_label.setText(unit)
        self.gui.endUnit_label.setText(unit)
        self.gui.stepUnit_label.setText(unit)
            
    
    
    def nameChanged(self):
        
        """ This function changes the name of the scan parameter """
        
        newName = self.gui.parameterName_lineEdit.text()
        newName = main.cleanString(newName)
        if newName != '' : 
            self.gui.configManager.setParameterName(newName)
            
            
            
    # PROCESSING STATE BACKGROUND
    ###########################################################################
    

    def setProcessingState(self,state):
        
        """ This function set the background color of the parameter address during the scan """
                
        if state == 'idle' : 
            self.gui.parameterAddress_label.setStyleSheet("font-size: 9pt;")
        else : 
            if state == 'started' : color = '#ff8c1a'
            if state == 'finished' : color = '#70db70'
            self.gui.parameterAddress_label.setStyleSheet(f"background-color: {color}; font-size: 9pt;")
            
        