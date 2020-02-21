# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 22:13:21 2019

@author: qchat
"""


import os
import shutil






def checkForbiddenCharacters(value):
    try : 
        assert '/' not in value
        assert '<' not in value
        assert '>' not in value
        assert ':' not in value
        assert '?' not in value
        assert '!' not in value
        assert '\\' not in value
        assert '*' not in value
        assert '|' not in value
        return True
    except :
        return False  
    
    
    
    
class Recorder :
    
    def __init__(self,name,customPath=None,verbose=True):
        
        if isinstance(name,str) is False or checkForbiddenCharacters(name) is False:
            raise ValueError(f'The name "{name}" is not valid')           
            		
        print(f'Starting Recorder with name "{name}"')
                
        self.verbose = verbose 
        
        self.name = name
        self.path = None
        
        self.var = {}
        self.varList= []
        self.started = False
        self.count = 0
        self.mainFile = None
        
        
        if customPath is None :
            self.setPath(os.getcwd())
        else :
            self.createFolder(customPath)
            self.setPath(customPath)
        
    #--------------------------------------------------------------------------
    # Path
    #--------------------------------------------------------------------------
        
    def createFolder(self,path):
        if os.path.exists(path) is False :
            parentFolder = os.path.realpath(os.path.dirname(path))
            if os.path.exists(parentFolder) is False :
                self.createFolder(parentFolder)
            os.mkdir(path)
                
    
    def getPath(self):
        return self.path
    
    def setPath(self,folderPath):
        if self.started is False :
            
            if os.path.exists(folderPath) is False :
                raise ValueError(f'The path "{os.path.dirname(folderPath)}" does not exists')
    
            path = os.path.join(folderPath,self.name)
            compt = 0
            while True :
                if os.path.exists(path):
                    compt += 1
                    path = os.path.join(folderPath,self.name+'_'+str(compt))
                else :
                    break
            self.path = path
            print(f'Recorder "{self.name}" will save its data at "{self.path}"')
            
        else : 
            raise ValueError('You cannot change the path after having started to save your data')
        
        
        
    #--------------------------------------------------------------------------
    # Variables
    #--------------------------------------------------------------------------    
    
    def setValue(self,varName,value):
        if isinstance(varName,str) is False :
            raise ValueError(f'"{varName}" is not a valid name for a variable')
        if self.started and varName not in self.getVariableList() :
            raise ValueError('You cannot add a new variable after having started to save your data')
        if varName not in self.getVariableList():
            self.varList.append(varName)
        self.var[varName] = value
        
        
    def getValue(self,varName):
        if varName not in self.getVariableList():
            raise ValueError(f'Variable unknown "{varName}"')
        return self.var[varName]
        
        
    def getVariableList(self):
        return tuple(self.varList)

    
    def getValueType(self,varName):
        if varName not in self.getVariableList():
            raise ValueError(f'Variable unknown "{varName}"')
        return type(self.var[varName])
        
    
    #--------------------------------------------------------------------------
    # Data file
    #--------------------------------------------------------------------------     

    def initialize(self):
        
        import pandas as pd
        self.started = True
        
        os.mkdir(self.path)
        
        # Sauvegarde script
        try :
            scriptPath = os.path.realpath(__file__)
            shutil.copyfile(scriptPath,os.path.join(self.path,'script_backup.py'))
        except :
            pass
        
        # Création datafile        
        headerLine = '# MeasID - Variable'
        for varName in self.getVariableList() :
            if self.getValueType(varName) != pd.DataFrame :
                headerLine += f',{varName}'
            else :
                os.mkdir(os.path.join(self.path,varName.replace(' ','_')))
                        
        self.mainFile = open(os.path.join(self.path,'data.txt'), 'w')
        self.mainFile.write(headerLine+'\n')
        
        
    def save(self):
        
        import pandas as pd
        
        if self.started is False :
            self.initialize()
            
        self.count += 1
        
        valueLine = f'{self.count}'

        for varName in self.getVariableList() :
            if self.getValueType(varName) != pd.DataFrame :
                valueLine += f',{self.getValue(varName)}'
            else :
                varValue = self.getValue(varName)
                varValue.to_csv(os.path.join(self.path,varName.replace(' ','_'),f'{self.count}.txt'),index=False)

                        
        self.mainFile.write(valueLine+'\n')
        
        if self.verbose is True :
            print()
            print(f'Recorder "{self.name}" saving data point #{self.count} :')
            for varName in self.getVariableList() :
                print(f' - {varName} = {self.getValue(varName)}')
            print()
        

    def close(self):
        if self.started is True :
            self.mainFile.close()
        print(f'Recorder "{self.name}" closed')
    
            
            
            
class Recorder_V2 :
    
    def __init__(self,name,customPath=None,verbose=True):
        
        import pandas as pd
        
        if isinstance(name,str) is False or checkForbiddenCharacters(name) is False:
            raise ValueError(f'The name "{name}" is not valid')           
            
        print(f'Starting Recorder with name "{name}"')
            		
        self.verbose = verbose 
        
        self.name = name
        self.path = None
        
        self.var = {}
        self.varNameHistory = []
        self.dataframe = pd.DataFrame()
        self.started = False
        self.count = 0
        
        
        if customPath is None :
            self.setPath(os.getcwd())
        else :
            self.createFolder(customPath)
            self.setPath(customPath)
        
    #--------------------------------------------------------------------------
    # Path
    #--------------------------------------------------------------------------
        
    def createFolder(self,path):
        if os.path.exists(path) is False :
            parentFolder = os.path.realpath(os.path.dirname(path))
            if os.path.exists(parentFolder) is False :
                self.createFolder(parentFolder)
            os.mkdir(path)
                
    
    def getPath(self):
        return self.path
    
    def setPath(self,folderPath):
        if self.started is False :
            
            if os.path.exists(folderPath) is False :
                raise ValueError(f'The path "{os.path.dirname(folderPath)}" does not exists')
    
            path = os.path.join(folderPath,self.name)
            compt = 0
            while True :
                if os.path.exists(path):
                    compt += 1
                    path = os.path.join(folderPath,self.name+'_'+str(compt))
                else :
                    break
            self.path = path
            print(f'Recorder "{self.name}" will save its data at "{self.path}"')
            
        else : 
            raise ValueError('You cannot change the path after having started to save your data')
        
        
        
    #--------------------------------------------------------------------------
    # Variables
    #--------------------------------------------------------------------------    
    
    def getVariableList(self):
        return tuple(self.var.keys())
    
    def setValue(self,varName,value):
        if isinstance(varName,str) is False :
            raise ValueError(f'"{varName}" is not a valid name for a variable')
        if self.started and varName not in self.getVariableList() :
            raise ValueError('You cannot add a new variable after having started to save your data')
        assert type(value) in [str, int, float, bool]
        if varName not in self.getVariableList() :
            self.varNameHistory.append(varName)
        self.var[varName] = value
        
    def getValue(self,varName):
        if varName not in self.getVariableList():
            raise ValueError(f'Variable unknown "{varName}"')
        return self.var[varName]
        

    def getValueType(self,varName):
        if varName not in self.getVariableList():
            raise ValueError(f'Variable unknown "{varName}"')
        return type(self.var[varName])
        
    
    #--------------------------------------------------------------------------
    # Data file
    #--------------------------------------------------------------------------     

    def initialize(self):
        self.started = True
        
        os.mkdir(self.path)        

        
        
    def save(self):
        
        if self.started is False :
            self.initialize()
        
        # Ajout du set de variable à la fin du dataframe
        self.dataframe = self.dataframe.append(self.var, ignore_index=True)

        # Copie de la dernière ligne dans le fichier
        filePath = os.path.join(self.getPath(),'data.csv')
        if len(self.dataframe) == 1 :
            self.dataframe=self.dataframe[self.varNameHistory]
            self.dataframe.iloc[[-1]].to_csv(filePath,sep=';')
        else :
            self.dataframe.iloc[[-1]].to_csv(filePath,sep=';', mode='a', header=False)
            
        # Log
        if self.verbose is True :
            print()
            print(f'Recorder "{self.name}" saving data point #{self.count} :')
            print(self.dataframe.iloc[-1])
        

    
