# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 22:08:29 2019

@author: qchat
"""
from PyQt5 import QtCore, QtWidgets, uic, QtGui
import os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import threading
import time
import pandas as pd
import usit
from queue import Queue
import math as m
import configparser
import numpy as np
import tempfile
import collections
import distutils
import datetime


class Scanner(QtWidgets.QMainWindow):
        
    def __init__(self,mainGui):
        
        self.mainGui = mainGui
        
        # Configuration of the window
        QtWidgets.QMainWindow.__init__(self)
        ui_path = os.path.join(os.path.dirname(__file__),'scanner.ui')
        uic.loadUi(ui_path,self)
        self.setWindowTitle(f"Usit Scanner")
        
        self.configManager = ConfigManager(self)
        self.figureManager = FigureManager(self)
        self.parameterManager = ParameterManager(self)
        self.recipeManager = RecipeManager(self)        
        self.scanManager = ScanManager(self)
        self.dataManager = DataManager(self)
        self.rangeManager = RangeManager(self)


    def closeEvent(self,event):
        
        """ This function does some steps before the window is really killed """
        
        if self.scanManager.isStarted() :
            self.scanManager.stop()
        self.dataManager.timer.stop()
        self.mainGui.clearScanner()
        
        
    def setLineEditBackground(self,obj,state):
        
        if state == 'synced' :
            color='#D2FFD2' # vert
        if state == 'edited' :
            color='#FFE5AE' # orange
            
        obj.setStyleSheet("QLineEdit:enabled {background-color: %s; font-size: 9pt}"%color)
        
        
        


        
class ConfigManager :
    
    def __init__(self,gui):
        self.gui = gui
        
        configMenu = self.gui.menuBar.addMenu('&Configuration')
        
        self.importAction = configMenu.addAction('Import configuration')
        self.importAction.triggered.connect(self.importActionClicked)
        
        exportAction = configMenu.addAction('Export current configuration')
        exportAction.triggered.connect(self.exportActionClicked)

        self.config = {}
        self.config['parameter'] = {'element':None,'name':None}
        self.config['nbpts'] = 11
        self.config['range'] = (0,10)
        self.config['log'] = False
        self.config['recipe'] = []
       
    # NAMES
    ###########################################################################
        
    def getNames(self,option=None):
        names = [step['name'] for step in self.config['recipe']]
        if self.config['parameter']['element'] is not None and option != 'recipe': 
            names.append(self.config['parameter']['name'])
        return names
        
    def getUniqueName(self,basename):
        
        names = self.getNames()
        name = basename
        
        compt = 0
        while True :
            if name in names :
                compt += 1
                name = basename+'_'+str(compt)
            else :
                break
        return name
        
    # CONFIG MODIFICATIONS
    ###########################################################################   
    
    def setParameter(self,element,name=None):
        if self.gui.scanManager.isStarted() is False :
            self.config['parameter']['element'] = element
            if name is None : name = self.getUniqueName(element.name)
            self.config['parameter']['name'] = name
            self.gui.parameterManager.refresh()
            self.gui.figureManager.xLabelChanged()
            self.gui.dataManager.clear()
            
    def setParameterName(self,name):
        if self.gui.scanManager.isStarted() is False :
            if name != self.config['parameter']['name']:
                name = self.getUniqueName(name)
                self.config['parameter']['name'] = name
                self.gui.figureManager.xLabelChanged()
                self.gui.dataManager.clear()
        self.gui.parameterManager.refresh()
        
    def addRecipeStep(self,stepType,element,name=None,value=None):
        if self.gui.scanManager.isStarted() is False :
            if name is None : name = self.getUniqueName(element.name)
            if stepType == 'set' and value is None: 
                if element.type in [int,float] :
                    value = 0
                elif element.type in [str] :
                    value = ''
                elif element.type in [bool]:
                    value = False
            step = {'stepType':stepType,'element':element,'name':name,'value':value}
            self.config['recipe'].append(step)
            self.gui.recipeManager.refresh()
            self.gui.dataManager.clear()
            
    def delRecipeStep(self,name):
        if self.gui.scanManager.isStarted() is False :
            pos = self.getRecipeStepPosition(name)
            self.config['recipe'].pop(pos)
            self.gui.recipeManager.refresh()
            self.gui.dataManager.clear()
    
    def renameRecipeStep(self,name,newName):
        if self.gui.scanManager.isStarted() is False :
            if newName != name :
                pos = self.getRecipeStepPosition(name)
                newName = self.getUniqueName(newName)
                self.config['recipe'][pos]['name'] = newName
                self.gui.recipeManager.refresh()
                self.gui.dataManager.clear()
                
    def setRecipeStepValue(self,name,value):
        if self.gui.scanManager.isStarted() is False :
            pos = self.getRecipeStepPosition(name)
            if value != self.config['recipe'][pos]['value'] :
                self.config['recipe'][pos]['value'] = value
                self.gui.recipeManager.refresh()
                self.gui.dataManager.clear()    
                
    def setNbPts(self,value):
        if self.gui.scanManager.isStarted() is False :
            self.config['nbpts'] = value
        self.gui.rangeManager.refresh()
        
    def setRange(self,lim):
        if self.gui.scanManager.isStarted() is False :
            if lim != self.config['range'] :
                self.config['range'] = tuple(lim)
        self.gui.rangeManager.refresh()
        
    def setLog(self,state):
        if self.gui.scanManager.isStarted() is False :
            if state != self.config['log']:
                self.config['log'] = state
        self.gui.rangeManager.refresh()
                
            
            
            
    # CONFIG READING
    ###########################################################################

    def getParameter(self):
        return self.config['parameter']['element']
    
    def getParameterName(self):
        return self.config['parameter']['name']
    
    def getRecipeStepElement(self,name):
        pos =  self.getRecipeStepPosition(name)
        return self.config['recipe'][pos]['element']
            
    def getRecipeStepType(self,name):
        pos =  self.getRecipeStepPosition(name)
        return self.config['recipe'][pos]['stepType']
    
    def getRecipeStepValue(self,name):
        pos =  self.getRecipeStepPosition(name)
        return self.config['recipe'][pos]['value']
    
    def getRecipeStepPosition(self,name):
        return [i for i, step in enumerate(self.config['recipe']) if step['name'] == name][0]     
        
    def getLog(self):
        return self.config['log']
    
    def getNbPts(self):
        return self.config['nbpts']
    
    def getRange(self):
        return self.config['range']
    
    def getRecipe(self):
        return self.config['recipe']
                        
    def getConfig(self):
        return self.config
  
    
    
    

    # EXPORT IMPORT ACTIONS
    ###########################################################################

    def exportActionClicked(self):

        path = QtWidgets.QFileDialog.getSaveFileName(self.gui, "Export USIT configuration file", 
                                                     os.path.join(usit.core.USER_LAST_CUSTOM_FOLDER_PATH,'config.conf'), 
                                                     "USIT configuration file (*.conf)")[0]

        if path != '' :
            usit.core.USER_LAST_CUSTOM_FOLDER_PATH = path
            self.export(path)
            
        self.gui.statusBar.showMessage(f"Current configuration successfully saved at {path}",5000)
        
    
    
    def export(self,path):
        
        configPars = configparser.ConfigParser()
        configPars['usit'] = {'version':usit.__version__,
                              'timestamp':str(datetime.datetime.now())}
                
        configPars['parameter'] = {}
        if self.config['parameter']['element'] is not None :
            configPars['parameter']['name'] = self.config['parameter']['name']
            configPars['parameter']['address'] = self.config['parameter']['element'].getAddress()
        configPars['parameter']['nbpts'] = str(self.config['nbpts'])
        configPars['parameter']['start_value'] = str(self.config['range'][0])
        configPars['parameter']['end_value'] = str(self.config['range'][1])
        configPars['parameter']['log'] = str(int(self.config['log']))
        
        configPars['recipe'] = {}
        for i in range(len(self.config['recipe'])) :
            configPars['recipe'][f'{i+1}_name'] = self.config['recipe'][i]['name']
            configPars['recipe'][f'{i+1}_stepType'] = self.config['recipe'][i]['stepType']
            configPars['recipe'][f'{i+1}_address'] = self.config['recipe'][i]['element'].getAddress()
            if self.config['recipe'][i]['stepType'] == 'set' :
                value = self.config['recipe'][i]['value']
                if self.config['recipe'][i]['element'].type in [str] :
                    valueStr = f'{value}'
                else :
                    valueStr = f'{value:g}'
                configPars['recipe'][f'{i+1}_value'] = valueStr
                
        with open(path, 'w') as configfile:
            configPars.write(configfile)
            
        
    def importActionClicked(self):
        
        path = QtWidgets.QFileDialog.getOpenFileName(self.gui, "Import USIT configuration file", 
                                                     usit.core.USER_LAST_CUSTOM_FOLDER_PATH,
                                                     "USIT configuration file (*.conf)")[0]
        if path != '' :
            
            configPars = configparser.ConfigParser()
            configPars.read(path)
            
            try :
            
                assert 'parameter' in configPars
                config = {}
                
                if 'address' in configPars['parameter'] :
                    element = usit.devices.getElementByAddress(configPars['parameter']['address'])
                    assert element is not None, f"Parameter {configPars['parameter']['address']} not found."
                    assert 'name' in configPars['parameter'], f"Parameter name not found."
                    config['parameter'] = {'element':element,'name':configPars['parameter']['name']}
                    
                
                assert 'recipe' in configPars
                for key in ['nbpts','start_value','end_value','log'] :
                    assert key in configPars['parameter'], "Missing parameter key {key}."
                    config['nbpts'] = int(configPars['parameter']['nbpts'])
                    start = float(configPars['parameter']['start_value'])
                    end = float(configPars['parameter']['end_value'])
                    config['range'] = (start,end)
                    config['log'] = bool(int(configPars['parameter']['log']))                    
                
                
                config['recipe'] = []

                while True :
                    step = {}
                    
                    i = len(config['recipe'])+1
    
                    if f'{i}_name' in configPars['recipe']:
                        
                        step['name'] = configPars['recipe'][f'{i}_name']
                        name = step['name']
                        
                        assert f'{i}_stepType' in configPars['recipe'], f"Missing stepType in step {i} ({name})."
                        step['stepType'] = configPars['recipe'][f'{i}_stepType']
                        
                        assert f'{i}_address' in configPars['recipe'], f"Missing address in step {i} ({name})."
                        address = configPars['recipe'][f'{i}_address']
                        element = usit.devices.getElementByAddress(address)
                        assert element is not None, f"Address {address} not found for step {i} ({name})."
                        step['element'] = element
                        
                        if step['stepType']=='set' :
                            assert f'{i}_value' in configPars['recipe'], f"Missing value in step {i} ({name})."
                            value = configPars['recipe'][f'{i}_value']
                            if element.type in [int]:
                                value = int(value)
                            elif element.type in [float] :
                                value = float(value)
                            elif element.type in [str] :
                                value = str(value)
                            elif element.type in [bool]:
                                value = int(value)
                                assert value in [0,1]
                                value = bool(value)
                            step['value'] = value
                        else :
                            step['value'] = None
                                                        
                        config['recipe'].append(step)
                        
    
                    else :
                        break
                
                
                self.config = config
                
                self.gui.dataManager.clear()
                self.gui.parameterManager.refresh()
                self.gui.recipeManager.refresh()
                self.gui.rangeManager.refresh()
                self.gui.figureManager.xLabelChanged()
                
                self.gui.statusBar.showMessage(f"Configuration file loaded successfully",5000)
            
            except Exception as e :
                
                self.gui.statusBar.showMessage(f"Impossible to load configuration file: "+str(e),10000)
            
        
    
        

        
class RecipeManager :
    
    def __init__(self,gui):
        
        self.gui = gui
        self.tree = self.gui.recipe_treeWidget
        
        self.tree.setHeaderLabels(['Step name','Type','Element address','Value'])
        self.tree.header().resizeSection(3, 50)
        
        self.tree.itemDoubleClicked.connect(self.itemDoubleClicked)
        
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.tree.setAlternatingRowColors(True)        
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.rightClick)
                
        self.defaultItemBackground = None
        
        
        
    def refresh(self):
        
        
        
        self.tree.clear()
        
        recipe = self.gui.configManager.getRecipe()

        for i in range(len(recipe)):
            
            # Loading step informations
            step = recipe[i]
            item = QtWidgets.QTreeWidgetItem()
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsDropEnabled)
            
            # Column 1 : Step name
            item.setText(0,step['name'])
            
            # Column 2 : Step type
            if step['stepType'] == 'measure' : 
                item.setText(1,'Measure variable')
            elif step['stepType']  == 'set' : 
                item.setText(1,'Set variable')
            elif step['stepType']  == 'action' : 
                item.setText(1,'Do action')
                            
            # Column 3 : Element address
            item.setText(2,step['element'].getAddress())
            
            # Column 4 : Value if stepType is 'set'
            value = step['value']
            if value is not None : 
                if step['element'].type in [bool,str] :
                   item.setText(3,f'{value}')
                else :
                   item.setText(3,f'{value:g}')
            
            # Add item to the tree
            self.tree.addTopLevelItem(item)
            self.defaultItemBackground = item.background(0)
            
            
            
    def rightClick(self,position):
    
        item = self.tree.itemAt(position)
        
        if item is not None and self.gui.scanManager.isStarted() is False :
            
            name = item.text(0)
            stepType = self.gui.configManager.getRecipeStepType(name)
                        
            menuActions = {}
            
            menu = QtWidgets.QMenu()         
            menuActions['rename'] = menu.addAction("Rename")
            if stepType == 'set' : 
                menuActions['setvalue'] = menu.addAction("Set value")
            menuActions['remove'] = menu.addAction("Remove")
            
            choice = menu.exec_(self.tree.viewport().mapToGlobal(position))
            
            if 'rename' in menuActions.keys() and choice == menuActions['rename'] :
                self.renameStep(name)                
            elif 'remove' in menuActions.keys() and choice == menuActions['remove'] :
                self.gui.configManager.delRecipeStep(name)
            elif 'setvalue' in menuActions.keys() and choice == menuActions['setvalue'] :
                self.setStepValue(name)

        
        
    def renameStep(self,name):
        
        newName,state = QtWidgets.QInputDialog.getText(self.gui, name, f"Set {name} new name",
                                                 QtWidgets.QLineEdit.Normal, name)
        
        newName = cleanString(newName)
        if newName != '' :
            self.gui.configManager.renameRecipeStep(name,newName)
            
   
            
    def setStepValue(self,name):
        
        element = self.gui.configManager.getRecipeStepElement(name)
        value = self.gui.configManager.getRecipeStepValue(name)
        
        if element.type in [str] :
            defaultValue = f'{value}'
        else :
            defaultValue = f'{value:g}'
        
        value,state = QtWidgets.QInputDialog.getText(self.gui, 
                                                     name, 
                                                     f"Set {name} value",
                                                     QtWidgets.QLineEdit.Normal, defaultValue)
        
        if value != '' :
            
            try :   
            
                if element.type in [int]:
                    value = int(value)
                elif element.type in [float] :
                    value = float(value)
                elif element.type in [str] :
                    value = str(value)
                elif element.type in [bool]:
                    value = int(value)
                    assert value in [0,1]
                    value = bool(value)
                
                self.gui.configManager.setRecipeStepValue(name,value)
                
            except :
                pass
            
            
            
            

        
        
    def itemDoubleClicked(self,item,column):
        name = item.text(0)
        
        stepType = self.gui.configManager.getRecipeStepType(name)
        
        if column == 0 : 
            self.renameStep(name)
        if column == 3 and stepType == 'set' :
            self.setStepValue(name)
    
    
    
    
    

    def setStepProcessingState(self,name,state):
        
        item = self.tree.findItems(name, QtCore.Qt.MatchExactly, 0)[0]
        
        if state is None :
            item.setBackground(0,self.defaultItemBackground)
        if state == 'started' :
            item.setBackground(0, QtGui.QColor('#ff8c1a'))
        elif state == 'finished' :
            item.setBackground(0, QtGui.QColor('#70db70'))
                                               
        
    def resetStepsProcessingState(self):
        for name in self.gui.configManager.getNames(option='recipe'):
            self.setStepProcessingState(name,None)
            



def cleanString(name):
    for character in '*."/\[]:;|, ' :
        name = name.replace(character,'')
    return name        
        



class RangeManager : 
    
    def __init__(self,gui):
        
        self.gui = gui
        
                
        self.gui.scanLog_checkBox.stateChanged.connect(self.scanLogChanged)
        self.gui.nbpts_lineEdit.returnPressed.connect(self.nbptsChanged)
        self.gui.step_lineEdit.returnPressed.connect(self.stepChanged)
        self.gui.start_lineEdit.returnPressed.connect(self.startChanged)
        self.gui.end_lineEdit.returnPressed.connect(self.endChanged)
        self.gui.mean_lineEdit.returnPressed.connect(self.meanChanged)
        self.gui.width_lineEdit.returnPressed.connect(self.widthChanged)
        
        self.gui.nbpts_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.nbpts_lineEdit,'edited'))
        self.gui.step_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.step_lineEdit,'edited'))
        self.gui.start_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.start_lineEdit,'edited'))
        self.gui.end_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.end_lineEdit,'edited'))
        self.gui.mean_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.mean_lineEdit,'edited'))
        self.gui.width_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.width_lineEdit,'edited'))
        
        self.gui.fromFigure_pushButton.clicked.connect(self.fromFigureButtonClicked)
        
        
        self.refresh()
                        
        
    def fromFigureButtonClicked(self):
        
        xrange = self.gui.figureManager.getRange('x')
        self.gui.configManager.setRange(xrange)
        
        log = self.gui.figureManager.isLogScaleEnabled('x')
        self.gui.configManager.setLog(log)
        
        
        
    def refresh(self):
        
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
        
        value = self.gui.nbpts_lineEdit.text()
        
        try :
            value = int(float(value))
            assert value > 2
            self.gui.configManager.setNbPts(value)
        except :
            self.refresh()
        
        
    def stepChanged(self) :
        
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
                











class ParameterManager :
    
    def __init__(self,gui):
        
        self.gui = gui
        
        self.gui.parameterName_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.parameterName_lineEdit,'edited'))
        self.gui.parameterName_lineEdit.returnPressed.connect(self.nameChanged)
        self.gui.parameterName_lineEdit.setEnabled(False)
        
        self.refresh()
        
        
    def refresh(self):
                
        # Paramater name, address and unit
        parameter = self.gui.configManager.getParameter()
        
        if parameter is not None :
            name = self.gui.configManager.getParameterName()
            self.gui.parameterName_lineEdit.setEnabled(True)
            address = parameter.getAddress()
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
        
        newName = self.gui.parameterName_lineEdit.text()
        newName = cleanString(newName)
        if newName != '' : 
            self.gui.configManager.setParameterName(newName)

     



        




                        
        
        
        
class FigureManager :
    
    
    
    
    def __init__(self,gui):
        
        self.gui = gui
        
        self.curves = []
        
        # Configure and initialize the figure in the GUI
        self.fig = Figure()
        matplotlib.rcParams.update({'font.size': 12})
        self.ax = self.fig.add_subplot(111)  
        self.ax.grid()
        self.ax.set_xlim((0,10))
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
        
        for axe in ['x','y'] :
            
            getattr(self.gui,f'logScale_{axe}_checkBox').stateChanged.connect(lambda b, axe=axe:self.logScaleChanged(axe))
            getattr(self.gui,f'autoscale_{axe}_checkBox').stateChanged.connect(lambda b, axe=axe:self.autoscaleChanged(axe))
            getattr(self.gui,f'autoscale_{axe}_checkBox').setChecked(True)
            getattr(self.gui,f'zoom_{axe}_pushButton').clicked.connect(lambda b,axe=axe:self.zoomButtonClicked('zoom',axe))
            getattr(self.gui,f'unzoom_{axe}_pushButton').clicked.connect(lambda b,axe=axe:self.zoomButtonClicked('unzoom',axe))
                    
        self.gui.goUp_pushButton.clicked.connect(lambda:self.moveButtonClicked('up'))
        self.gui.goDown_pushButton.clicked.connect(lambda:self.moveButtonClicked('down'))
        self.gui.goLeft_pushButton.clicked.connect(lambda:self.moveButtonClicked('left'))
        self.gui.goRight_pushButton.clicked.connect(lambda:self.moveButtonClicked('right'))
        
        self.fig.canvas.mpl_connect('button_press_event', self.onPress)
        self.fig.canvas.mpl_connect('scroll_event', self.onScroll)
        self.fig.canvas.mpl_connect('motion_notify_event', self.onMotion)
        self.fig.canvas.mpl_connect('button_release_event', self.onRelease)
        self.press = None
        
        self.movestep = 0.05


        
        
        self.nbtraces = 5
        self.gui.nbTraces_lineEdit.setText(f'{self.nbtraces:g}')
        self.gui.nbTraces_lineEdit.returnPressed.connect(self.nbTracesChanged)
        self.gui.nbTraces_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.nbTraces_lineEdit,'edited'))
        self.gui.setLineEditBackground(self.gui.nbTraces_lineEdit,'synced')
        self.gui.variable_comboBox.currentIndexChanged.connect(self.variableChanged)
        
        self.ax.autoscale(enable=False)
        
    
        
    # AUTOSCALING
    ###########################################################################
    
    def autoscaleChanged(self,axe):
        state = self.isAutoscaleEnabled(axe)
        getattr(self.ax,f'set_autoscale{axe}_on')(state)
        if state is True :
            self.doAutoscale(axe)
            self.redraw()
            
    def isAutoscaleEnabled(self,axe):
        return getattr(self.gui,f'autoscale_{axe}_checkBox').isChecked()
    
    def doAutoscale(self,axe):
        datas = [getattr(curve,f'get_{axe}data')() for curve in self.curves]
        if len(datas)>0 :
            minValue = min([min(data) for data in datas])
            maxValue = max([max(data) for data in datas])
            if (minValue,maxValue) != self.getRange(axe) :
                self.setRange(axe,(minValue,maxValue))

#
#    
#    def doAutoscale(self,axe):
##        ranges_inf = [curve.getRange(axe)[0] for curve in self.curves]
##        ranges_sup = [curve.getRange(axe)[0] for curve in self.curves]
##        
#        
##        if len(self.curves) > 0 :
##            for 
#        self.ax.relim()
#        if axe == 'x':self.ax.autoscale_view(scaley=False)
#        elif axe == 'y':self.ax.autoscale_view(scalex=False)
#        print('autoscale done',axe)
            
            
            
            
    # LOGSCALING
    ###########################################################################

    def logScaleChanged(self,axe):
        
        state = getattr(self.gui,f'logScale_{axe}_checkBox').isChecked()
        self.setLogScale(axe,state)
        self.redraw()
        
    
    def isLogScaleEnabled(self,axe):
        return getattr(self.ax,f'get_{axe}scale')() == 'log'

            
    def setLogScale(self,axe,state):
        
        if state is True :
            scaleType = 'log'
        else :
            scaleType = 'linear'
        
        self.checkLimPositive(axe)
        self.ax.grid(state,which='minor',axis=axe)
        getattr(self.ax,f'set_{axe}scale')(scaleType)
        
        
    def checkLimPositive(self,axe):
        
        axeRange = list(self.getRange(axe))
            
        change = False
        if axeRange[1] <= 0 : 
            axeRange[1] = 1
            change = True
        if axeRange[0] <= 0 : 
            axeRange[0] = 10**(m.log10(axeRange[1])-1)
            change = True
            
        if change is True :
            self.setRange(axe,axeRange)
        
        
        
    # AXE LABEL
    ###########################################################################
        
    def setLabel(self,axe,value):
        getattr(self.ax,f'set_{axe}label')(value)

    def xLabelChanged(self):
        label = self.gui.configManager.getParameterName()
        self.setLabel('x',str(label))
        self.redraw()
        
        


    # PLOT DATA
    ###########################################################################
            
    
    def clearData(self):
        for curve in self.curves :
            curve.remove()
        self.curves = []
        self.redraw()
            
        
    def reloadData(self):
        
        ''' Full reset '''
        
        self.clearData()
        
        resultName = self.gui.variable_comboBox.currentText()
        self.setLabel('y',resultName)
        
        data = self.gui.dataManager.getPlotData(self.nbtraces,resultName)        
        
        for i in range(len(data)) :
                            
            # Data
            subdata = data[i]
            x = pd.to_numeric(subdata.x,errors='coerce')
            y = pd.to_numeric(subdata.y,errors='coerce')
            
            # Apprearance:    
            if i == (len(data)-1) :      
                color = 'r'
                alpha = 1
            else:
                color = 'k'
                alpha = (self.nbtraces-(len(data)-1-i))/self.nbtraces
            
            # Plot
            curve = self.ax.plot(x,y,color=color,alpha=alpha)[0]
            self.curves.append(curve)
            
        if self.isAutoscaleEnabled('x') is True : self.doAutoscale('x')
        if self.isAutoscaleEnabled('y') is True : self.doAutoscale('y')
        
        self.redraw()
        
        
        
    def reloadLastData(self):
        
        ''' Update just last curve '''
        
        resultName = self.gui.variable_comboBox.currentText()
        data = self.gui.dataManager.getPlotData(1,resultName)
        
        self.curves[-1].set_xdata(pd.to_numeric(data[0].x,errors='coerce'))
        self.curves[-1].set_ydata(pd.to_numeric(data[0].y,errors='coerce'))
        
        if self.isAutoscaleEnabled('x') is True : self.doAutoscale('x')
        if self.isAutoscaleEnabled('y') is True : self.doAutoscale('y')
        
        self.redraw()
        
        
    def variableChanged(self,index):
        
        self.clearData()
        
        if index != -1: 
            self.reloadData()

            
        
    # TRACES
    ###########################################################################      
        
    def nbTracesChanged(self):
                
        value = self.gui.nbTraces_lineEdit.text()
        
        check = False
        try :
            value = int(float(value))
            assert value > 0
            self.nbtraces = value
            check = True
        except :
            pass
        
        self.gui.nbTraces_lineEdit.setText(f'{self.nbtraces:g}')
        self.gui.setLineEditBackground(self.gui.nbTraces_lineEdit,'synced')
        
        if check is True and self.gui.variable_comboBox.currentIndex() != -1 :
            self.reloadData()
        
        
    


    # ZOOM UNZOOM BUTTONS
    ###########################################################################

    def zoomButtonClicked(self,action,axe):

        logState = self.isLogScaleEnabled(axe)
            
        inf,sup = self.getRange(axe)
        
        if logState is False :
            if action == 'zoom' :
                inf_new = inf + (sup-inf)*self.movestep
                sup_new = sup - (sup-inf)*self.movestep
            elif action == 'unzoom' :
                inf_new = inf - (sup-inf)*self.movestep/(1-2*self.movestep)
                sup_new = sup + (sup-inf)*self.movestep/(1-2*self.movestep)
        else :
            log_inf = m.log10(inf)
            log_sup = m.log10(sup)
            if action == 'zoom' :
                inf_new = 10**(log_inf+(log_sup-log_inf)*self.movestep)
                sup_new = 10**(log_sup-(log_sup-log_inf)*self.movestep)
            elif action == 'unzoom' :
                inf_new = 10**(log_inf-(log_sup-log_inf)*self.movestep/(1-2*self.movestep))
                sup_new = 10**(log_sup+(log_sup-log_inf)*self.movestep/(1-2*self.movestep))
                
                
        self.setRange(axe,(inf_new,sup_new))
        self.redraw()



    # MOVE BUTTONS
    ###########################################################################
    
    
    def moveButtonClicked(self,action):
        
        if action in ['up','down'] :
            axe = 'y'
            if action == 'up' : action = 'increase'
            elif action == 'down' : action = 'decrease'
        elif action in ['left','right'] :
            axe = 'x'
            if action == 'left' : action = 'decrease'
            elif action == 'right' : action = 'increase'

        logState = self.isLogScaleEnabled(axe)
            
        inf,sup = self.getRange(axe)
        
        if logState is False :
            if action == 'increase' :
                inf_new = inf + (sup-inf)*self.movestep
                sup_new = sup + (sup-inf)*self.movestep
            elif action == 'decrease' :
                inf_new = inf - (sup-inf)*self.movestep
                sup_new = sup - (sup-inf)*self.movestep
        else :
            log_inf = m.log10(inf)
            log_sup = m.log10(sup)
            if action == 'increase' :
                inf_new = 10**(log_inf+(log_sup-log_inf)*self.movestep)
                sup_new = 10**(log_sup+(log_sup-log_inf)*self.movestep)
            elif action == 'decrease' :
                inf_new = 10**(log_inf-(log_sup-log_inf)*self.movestep)
                sup_new = 10**(log_sup-(log_sup-log_inf)*self.movestep)
            
        self.setRange(axe,(inf_new,sup_new))
        self.redraw()
   
    
    
    
        
    # MOUSE SCROLL
    ###########################################################################
     
    def onScroll(self,event):
        
        data = {'x':event.xdata,'y':event.ydata}
        
        for axe in ['x','y'] :
            
            logState = self.isLogScaleEnabled(axe)
            inf,sup = self.getRange(axe)
            
            if logState :
            
                if event.button == 'up' : 
                    inf_new = 10**(m.log10(data[axe]) * self.movestep + (1-self.movestep) * m.log10(inf)) 
                    sup_new = 10**(m.log10(data[axe]) * self.movestep + (1-self.movestep) * m.log10(sup)) 
                elif event.button == 'down' :
                    inf_new = 10**( ( - m.log10(data[axe]) * self.movestep + m.log10(inf) ) / (1 - self.movestep) )
                    sup_new = 10**( ( - m.log10(data[axe]) * self.movestep + m.log10(sup) ) / (1 - self.movestep) )
                    
            else :
            
                if event.button == 'up' : 
                    inf_new = data[axe] * self.movestep + (1-self.movestep) * inf 
                    sup_new = data[axe] * self.movestep + (1-self.movestep) * sup 
                elif event.button == 'down' :
                    inf_new = ( - data[axe] * self.movestep + inf ) / (1 - self.movestep)
                    sup_new = ( - data[axe] * self.movestep + sup ) / (1 - self.movestep)   
                
            self.setRange(axe,(inf_new,sup_new))
            self.redraw()
            
            
            
            
        
    # MOUSE DRAG
    ###########################################################################
        
    def onPress(self,event):
        
        xlim = self.getRange('x')
        ylim = self.getRange('y')
        
        if self.isLogScaleEnabled('x') is False :
            x_width_data = xlim[1]-xlim[0]
        else :
            x_width_data = m.log10(xlim[1])-m.log10(xlim[0])
        
        if self.isLogScaleEnabled('y') is False :
            y_width_data = ylim[1]-ylim[0]
        else :
            y_width_data = m.log10(ylim[1])-m.log10(ylim[0])
        
        leftInfCornerCoords = self.ax.transData.transform((xlim[0],ylim[0]))
        rightSupCornerCoords = self.ax.transData.transform((xlim[1],ylim[1]))       
        x_width_pixel = rightSupCornerCoords[0] - leftInfCornerCoords[0]
        y_width_pixel = rightSupCornerCoords[1] - leftInfCornerCoords[1]
    
        self.press = xlim,ylim,x_width_data,y_width_data,x_width_pixel,y_width_pixel,event.x,event.y

        

    def onMotion(self,event):
        
        if self.press is not None and event.inaxes is not None :
            
            xlim,ylim,x_width_data,y_width_data,x_width_pixel,y_width_pixel,x_press_pixel, y_press_pixel = self.press

            x_pixel,y_pixel = event.x,event.y
            
            xlim_new = list(xlim)
            ylim_new = list(ylim)
            
            dx_pixel = x_pixel - x_press_pixel
            dy_pixel = y_pixel - y_press_pixel
            
            dx_data = dx_pixel * x_width_data / x_width_pixel
            dy_data = dy_pixel * y_width_data / y_width_pixel
            
            if self.isLogScaleEnabled('x'):
                xlim_new[0] = 10**(m.log10(xlim[0])-dx_data)
                xlim_new[1] = 10**(m.log10(xlim[1])-dx_data)
            else :
                xlim_new[0] = xlim[0]-dx_data
                xlim_new[1] = xlim[1]-dx_data
  
            if self.isLogScaleEnabled('y'):
                ylim_new[0] = 10**(m.log10(ylim[0])-dy_data)
                ylim_new[1] = 10**(m.log10(ylim[1])-dy_data)
            else :
                ylim_new[0] = ylim[0]-dy_data
                ylim_new[1] = ylim[1]-dy_data
                
            
            self.setRange('x',xlim_new)
            self.setRange('y',ylim_new)
            self.redraw()
            
            
    def onRelease(self,event):
        self.press = None
        

        

    
    # SAVE FIGURE
    ###########################################################################
        
    def save(self,path):
        
        """ This function save the figure in the provided path """
        
        self.fig.savefig(os.path.join(path,'figure.jpg'),dpi=300)
        
        
        
        
        
    # redraw
    ###########################################################################

    def redraw(self):
        
        """ This function finalize the figure update in the GUI """
        
        try :
            self.fig.tight_layout()
        except :
            pass
        self.canvas.draw()
        
        
    # RANGE
    ###########################################################################
        
    def getRange(self,axe):
        return getattr(self.ax,f'get_{axe}lim')()
    
    def setRange(self,axe,r):
        getattr(self.ax,f'set_{axe}lim')(r)
        
        
        
class DataManager :
    
    def __init__(self,gui):
        
        self.gui = gui
        
        self.datasets = []
        self.queue = Queue()
        
        self.timer = QtCore.QTimer(self.gui)
        self.timer.setInterval(33) #30fps
        self.timer.timeout.connect(self.sync)
        
        self.gui.save_pushButton.clicked.connect(self.saveButtonClicked)
        self.gui.save_pushButton.setEnabled(False)
        
        self.initialized = False
        
        self.gui.clear_pushButton.clicked.connect(self.clear)
        
        
    def getPlotData(self,nbDataset,resultName):
        
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
        self.datasets = []
        self.initialized = False
        self.gui.variable_comboBox.clear()
        self.gui.save_pushButton.setEnabled(False)
        
        
    def getLastDataset(self):
        if len(self.datasets)>0 :
            return self.datasets[-1]
        
        
    def newDataset(self,config):
        
        dataset = Dataset(self.gui,config)
        self.datasets.append(dataset)
        self.gui.progressBar.setMaximum(config['nbpts'])
        return dataset
    
    
    def sync(self):
        
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
     
        self.data = pd.DataFrame()

        self.config = config
        
        self.tempFolderPath = tempfile.mkdtemp()
        
        # Save configuration config in this folder
        self.gui.configManager.export(os.path.join(self.tempFolderPath,'config.conf'))
        
        self.new = True
        
        
        

    def getData(self,resultName):
        data = self.data[[self.config['parameter']['name'],resultName]]
        data.rename(columns={self.config['parameter']['name']: 'x', resultName: 'y'},inplace=True)
        return data
    
    
    
    def save(self,path):
        distutils.dir_util.copy_tree(self.tempFolderPath,path)
        
    
    def addPoint(self,dataPoint):
        
        ID = len(self.data)+1
        
        simpledata =collections.OrderedDict()
        simpledata['id']=ID
        
        for resultName in dataPoint.keys():
            
            result = dataPoint[resultName]
            
            element = [step['element'] for step in self.config['recipe'] if step['name']==resultName][0]
            resultType = element.type
            
            if resultType in [np.ndarray,pd.DataFrame,str]:
                folderPath = os.path.join(self.tempFolderPath,resultName)
                if os.path.exists(folderPath) is False : os.mkdir(folderPath)
                filePath = os.path.join(folderPath,f'{ID}.txt')
                usit.core.devices.save(self.config.result,filePath)
            else : 
                simpledata[resultName] = result
            
        self.data = self.data.append(simpledata,ignore_index=True)
        if ID == 1 : 
            self.data = self.data[simpledata.keys()] # reorder columns
            header = True
        else :
            header = False
        self.data.tail(1).to_csv(os.path.join(self.tempFolderPath,f'data.txt'),index=False,mode='a',header=header)
        
            

        
    def __len__(self):
        return len(self.data)
    
    
    
    
    
    
class ScanManager :
    
    def __init__(self,gui):
        self.gui = gui
        
        self.gui.start_pushButton.clicked.connect(self.startButtonClicked)
        self.gui.pause_pushButton.clicked.connect(self.pauseButtonClicked)
        self.gui.pause_pushButton.setEnabled(False)
        
        self.gui.progressBar.setMinimum(0)
        self.gui.progressBar.setValue(0)
        
        self.thread = None
        

    # START AND STOP
    #############################################################################  

    def startButtonClicked(self):
        
        if self.isStarted() is False : 
            self.start()
        else :
            self.stop()

    def isStarted(self):
        return self.thread is not None

    def start(self) :
        
        test = False
        try : 
            config = self.gui.configManager.getConfig()
            assert config['parameter']['element'] is not None, "Parameter no set"
            assert len(config['recipe']) > 0, "Recipe is empty"
            test = True
        except Exception as e :
            self.gui.statusBar.showMessage(f'ERROR The scan cannot start with the current configuration : {str(e)}',10000)
            
        if test is True :
            
            # Prepare a new dataset in the datacenter
            self.gui.dataManager.newDataset(config)
            
            # Start a new thread
            ## Opening
            self.thread = ScanThread(self.gui.dataManager.queue, config)
            ## Signal connections
            self.thread.errorSignal.connect(self.error)
            self.thread.startStepSignal.connect(lambda stepName:self.gui.recipeManager.setStepProcessingState(stepName,'started'))
            self.thread.finishStepSignal.connect(lambda stepName:self.gui.recipeManager.setStepProcessingState(stepName,'finished'))
            self.thread.recipeCompletedSignal.connect(self.gui.recipeManager.resetStepsProcessingState)
            self.thread.finished.connect(self.finished)
            # Starting
            self.thread.start()
            
            # Start data center timer
            self.gui.dataManager.timer.start()
            
            # Update gui           
            self.gui.start_pushButton.setText('Stop')
            self.gui.pause_pushButton.setEnabled(True)
            self.gui.clear_pushButton.setEnabled(False)
            self.gui.progressBar.setValue(0)
            self.gui.configManager.importAction.setEnabled(False)
            self.gui.statusBar.showMessage(f'Scan started !',5000)
            

    def stop(self):
        self.disableContinuousMode()   
        self.thread.stopFlag.set()
        self.resume()
        self.thread.wait()
        
        
    # SIGNALS
    #############################################################################  
        
    def finished(self):
        
        """ Thread terminé """
        
        self.gui.start_pushButton.setText('Start')
        self.gui.pause_pushButton.setEnabled(False)
        self.gui.clear_pushButton.setEnabled(True)
        self.gui.configManager.importAction.setEnabled(False)
        self.gui.dataManager.timer.stop()
        self.gui.dataManager.sync() # once again to be sure we grabbed every data
        self.thread = None
        
        if self.isContinuousModeEnabled() : 
            self.start()
        
        
    def error(self,error):
        self.gui.statusBar.showMessage(f'Error : {error} ',10000)
        
        
        
        
        
    # CONTINUOUS MODE
    #############################################################################
    
    def isContinuousModeEnabled(self):
        return self.gui.continuous_checkBox.isChecked()
    
    
    def disableContinuousMode(self):
        self.gui.continuous_checkBox.setChecked(False)
        
        
    
    # PAUSE
    #############################################################################
    
    def pauseButtonClicked(self):
        
        if self.isStarted() :
            if self.isPaused() is False : 
                self.pause()
            else :
                self.resume()
    
    def isPaused(self):
        return self.thread is not None and self.thread.pauseFlag.is_set() is True 
    
               
    def pause(self):
        self.thread.pauseFlag.set()
        self.gui.dataManager.timer.stop()
        self.gui.pause_pushButton.setText('Resume')
        
    def resume(self):
        self.thread.pauseFlag.clear()
        self.gui.dataManager.timer.start()
        self.gui.pause_pushButton.setText('Pause')
        
        

        
        
class ScanThread(QtCore.QThread):
    
    """ This thread class is dedicated to read the variable, and send its data to GUI through a queue """
    
    errorSignal = QtCore.pyqtSignal(object) 
    startStepSignal = QtCore.pyqtSignal(object)
    finishStepSignal = QtCore.pyqtSignal(object)
    recipeCompletedSignal = QtCore.pyqtSignal()

    def __init__(self, queue, config):
        
        QtCore.QThread.__init__(self)
        self.config = config
        self.queue = queue
        
        self.pauseFlag = threading.Event()
        self.stopFlag = threading.Event()
        
        
        
    def run(self):
        
        parameter = self.config['parameter']['element']
        name = self.config['parameter']['name']
        startValue,endValue = self.config['range']
        nbpts = self.config['nbpts']
        logScale = self.config['log']
        
        if logScale is False : 
            paramValues = np.linspace(startValue,endValue,nbpts,endpoint=True)
        else : 
            paramValues = np.logspace(m.log10(startValue),m.log10(endValue),nbpts,endpoint=True)
            
        for paramValue in paramValues : 
                        
            if self.stopFlag.is_set() is False :
                
                try : 
                    
                    parameter(paramValue)
                    dataPoint = collections.OrderedDict()
                    dataPoint[name] = paramValue
                    dataPoint = self.processRecipe(dataPoint)
                    if self.stopFlag.is_set() is False : self.queue.put(dataPoint)

                except Exception as e :

                    self.errorSignal.emit(e)
                    self.stopFlag.set()
                    
                while self.pauseFlag.is_set() :
                    time.sleep(0.1)
                        
            else : 
                
                break
            
            
    def processRecipe(self,dataPoint):
        

        for stepInfos in self.config['recipe'] : 
            
            if self.stopFlag.is_set() is False :
                
                result = self.processElement(stepInfos)
                if result is not None :
                    dataPoint[stepInfos['name']] =  result
                    
                while self.pauseFlag.is_set() :
                    time.sleep(0.1)
            
            else : 
                break
            
        self.recipeCompletedSignal.emit()
            
        return dataPoint
                 
        
    def processElement(self,stepInfos):
        
        element = stepInfos['element']
        stepType = stepInfos['stepType']
        
        self.startStepSignal.emit(stepInfos['name'])
            
        result = None
        if stepType == 'measure' :
            result = element()
        if stepType == 'set' :
            element(stepInfos['value'])
        if stepType == 'action' :
            element()
            
        self.finishStepSignal.emit(stepInfos['name'])
        
        return result
    
    
    


                    

            
          
            
                
        
        
        