# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 15:13:26 2019

@author: manip
"""

import os
import pywinauto as pwa
import time
import pandas as pd

class Winspec :
    
    def __init__(self):
        
        self.minExpTimeAllowed=2e-5 #s
        self.maxExpTimeAllowed=1    #s
        
        self.tempPath = os.path.join(os.path.dirname(os.path.realpath(__file__)),'temp')
        if os.path.exists(self.tempPath) is False : os.mkdir(self.tempPath)
        self.fileName = 'spectrum_temp.txt'
        self.dataPath = os.path.join(self.tempPath,self.fileName)
        
        self.windowBasename='WinSpec/32'
        
        self.nbPixelsBorder=5 # à chaque extrémité
        
        self.controller = None
        self.pwa = None
        
        self.connect()
        
    def connect(self):
         
        if self.isConnected() :
            self.close()
        try :
            self.pwa = pwa
            self.controller = pwa.Application()
            self.controller.connect(best_match=self.windowBasename,visible_only=False)
            self.initialize()
            return True
        except :
            self.controller = None
            return False
            
            
    def isConnected(self):
        try :
            self.getWindow('main').menu_select('File')
            result=True
        except :
            result=False
        return result
    
    
    def close(self):
        try :
            self.controller = None
        except :
            pass
        
        
    def command(self,command):
                
        if command == 'STATE?':
            return int(self.isConnected())
        elif command == 'CONNECT':
            self.connect()
        elif command == 'EXPTIME?':
            return self.getExposureTime()
        elif command == 'SPECTRUM?':
            return self.getSpectrum()
        elif command == 'TEMP?':
            return self.getTemperature()
        elif command.startswith('EXPTIME='):
            expTime = float(command.split('=')[1])
            self.setExposureTime(expTime)

    def minimizeWindow(self):
        self.getWindow('main').minimize()
        
    def getWindow(self,windowName):
        if windowName == 'main' :
            windowName = self.windowBasename
        window = getattr(self.controller,windowName)
        window.wait('exists',timeout=10)
        return window
        
    def stopAcquisitions(self):
        try :
            self.getWindow('main').menu_select('Acquisition -> Stop Acquisition')
            time.sleep(0.1)
        except:
            pass
        
    def initialize(self):
        self.stopAcquisitions()
            
        # Ouverture du menu de conversion
        self.getWindow('main').menu_select('Tools -> Convert To ASCII')
        window = self.getWindow('SPEToASCIIConversion')
        
        # Paramétrage du fichier
        if window.FileExtensionEdit.text_block() != 'txt' :
            window.FileExtensionEdit.set_edit_text('txt')
        if window.CommaRadioButton.get_check_state() == 0 :
            window.CommaRadioButton.check()
        if window.OneFilePerFrameRadioButton.get_check_state() == 0:
            window.OneFilePerFrameRadioButton.check()
        if window.PixelIntensityRadioButton.get_check_state() == 0:
            window.PixelIntensityRadioButton.check()
        if window.CarriageReturnCheckBox.get_check_state() == 0:
            window.CarriageReturnCheckBox.check()
        if window.LineFeedCheckBox.get_check_state() == 0:
            window.LineFeedCheckBox.check()
        if window.SingleColumnRadioButton.get_check_state() == 0:
            window.SingleColumnRadioButton.check()
        if window.SpaceComboBox.selected_text().strip() != 'nm' :
            window.SpaceComboBox.select('nm')           
        
        # Fermeture du menu
        window.DoneButton.click()
        self.closeWindow(window)
        
        
    def getExposureTime(self):
                    
        # Ouverture du menu
        self.getWindow('main').menu_select('Acquisition -> Experiment Setup...')
        self.getWindow('ExperimentSetup')

        # Récupération de la valeur
        value=float(self.getWindow('ExperimentSetup').ExposureTimeEdit.text_block())
                    
        # Récupération de l'unité
        unit=self.getWindow('ExperimentSetup').ExposureTimeComboBox.selected_text().strip()
        unitCoeff={'msec':1e-3,'usec':1e-6,'sec':1,'min':60}
        
        # Calcul vrai valeur
        realValue = value * unitCoeff[unit]
        
        # Fermeture du menu
        window = self.getWindow('ExperimentSetup')
        window.OK.click()
        self.closeWindow(window)
        
        return realValue
    
    
    
    
    def setExposureTime(self,value):
                
        assert isinstance(float(value),float)
            
        # Verif Valeurs limites
        if value<self.minExpTimeAllowed :
            value=self.minExpTimeAllowed
        elif value>self.maxExpTimeAllowed:
            value=self.maxExpTimeAllowed
            
        # Choix unité
        if self.maxExpTimeAllowed >= value >=0.1:
            valueStr=value
            unit='sec ' #the space is important
        elif 0.1 > value >= 0.1e-3:
            valueStr=value/1e-3
            unit = 'msec'
        elif 0.1e-3 > value >= self.minExpTimeAllowed:
            valueStr=value/1e-6
            unit = 'usec'
        
        # Ouverture du menu
        self.getWindow('main').menu_select('Acquisition -> Experiment Setup...')
        self.getWindow('ExperimentSetup')

        # Ecriture de la valeur
        self.getWindow('ExperimentSetup').ExposureTimeEdit.set_edit_text('%.2f'%valueStr)
                    
        # Ecriture de l'unité
        self.getWindow('ExperimentSetup').ExposureTimeComboBox.select(unit)           
        
        # Fermeture du menu
        window = self.getWindow('ExperimentSetup')
        window.OK.click()
        self.closeWindow(window)
        
        
        
    def closeWindow(self,window):
        try : 
            window.wait_not('exists',timeout=10)
        except:
            pass
    
    
    def getSpectrum(self):
                                    
        # On lance l'acquisition d'un spectre et on attend le temps de la mesure
        self.getWindow('main').menu_select('Acquisition -> Acquire')
        
        # Attente de la fin de la mesure
        data={}
        while True :
            try :
                data['expTime']=self.getExposureTime()
                break
            except :
               time.sleep(0.1)
               
        ''' Enregistre le spectre courant brut en un fichier csv 
        lisible et temporaire '''
                    
        # Clean du dossier de réception
        try :
            os.remove(self.dataPath)
        except:
            pass
        
        # Ouverture du menu de conversion
        self.getWindow('main').menu_select('Tools -> Convert To ASCII')
        window = self.getWindow('SPEToASCIIConversion')
        
        window.ChooseOutputDirectoryEdit.set_edit_text(self.tempPath)
    
        # Récupération du spectre qui vient de se faire
        window.GetActiveWindowButton.click()       

        # Lancement de l'enregistrement
        window.ConvertToASCIIButton.click()
        tini = time.time()
        while True :
            assert time.time() - tini < 10
            if 'Done' in window.GetActiveWindowEdit.text_block() :
                break
        
        # Fermeture du menu
        window.DoneButton.Click()
        self.closeWindow(window)
        
        # Rename txt file
        filename = os.listdir(self.tempPath)[0]
        os.rename(os.path.join(self.tempPath,filename),
                  self.dataPath)
                
        # Ouverture du fichier ASCII
        data = pd.read_csv(self.dataPath, names =  ["wavelength", "toremove", "counts"])
        data.drop(columns=['toremove'],inplace=True)

        return data.to_json()
    
    
    
    
    def getTemperature(self):
        self.getWindow('main').menu_select('Setup -> Detector Temperature...')
        window = self.getWindow('Detector Temperature')
        
        
        value = window.CurrentTemperature.window_text().split(':')[1].strip()
        if 'Locked' in value :
            temp = float(window.TargetTemperatureEdit.text_block())
        else :
            temp = float(value)
            
        window.OKButton.click()
        self.closeWindow(window)
        return temp
    
    
    
    
    
if __name__ == '__main__' : 
    
    __file__ = os.getcwd()
    winspec = Winspec()
    