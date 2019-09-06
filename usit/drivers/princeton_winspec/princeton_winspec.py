# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 20:06:08 2019

@author: quentin.chateiller
"""
import pandas as pd
import numpy as np

from connector import WinspecConnectorRemote

ADDRESS = '192.168.0.3'


class Device(WinspecConnectorRemote):    
    
    def __init__(self, address=ADDRESS):
        
        WinspecConnectorRemote.__init__(self,address)
                
        self.minCountsAllowed=5000
        self.maxCountsAllowed=61000
        self.nbPixelsFitBaseline=10 # en % du spectre à chaque extrémité
        
        # Defaults
        self.autoBackgroundRemoval = False
        self.autoExposureTime = True
		
        self.data = {'exposureTime':None,'spectrum':None}
        self.write('Initialize')
                
        
        
    def isConnected(self):
        try :
            return bool(int(self.query('STATE?')))
        except :
            return False

    


        
        


        
        
    def getExposureTime(self):
        if self.data['exposureTime'] is None :
            self.data['exposureTime'] = float(self.query('EXPTIME?'))
        return self.data['exposureTime']

    def setExposureTime(self,value):
        value=float(value)
        self.write(f'EXPTIME={value}')
        self.data['exposureTime'] = float(self.query('EXPTIME?'))
        
        
        
        
        
    
    def isAutoExposureTimeEnabled(self):
        return self.autoExposureTime
    
    def setAutoExposureTimeEnabled(self,value):
        assert isinstance(value,bool)
        self.autoExposureTime = value
        
        
        
        
        
        
    def getSpectrum(self):
        if self.data['spectrum'] is None :
            self.acquireSpectrum()
        return self.data['spectrum']
    
    
    def acquireSpectrum(self):
            
        if self.isAutoExposureTimeEnabled() :
            
            while True :
                
                # Mesure spectre
                spectrum = pd.read_json(self.query('SPECTRUM?'))
        
                # Récupération des données
                maxValue=max(spectrum['counts'])
                
                # Reduction du temps d'exposition
                if maxValue>self.maxCountsAllowed : 
                    exposureTime_save = self.getExposureTime()
                    self.setExposureTime(self.getExposureTime()/10)
                    if self.getExposureTime() == exposureTime_save :
                        break
                
                # Augmentation du temps d'exposition
                elif maxValue<self.minCountsAllowed : 
                    exposureTime_save = self.getExposureTime()
                    self.setExposureTime(self.getExposureTime()*self.maxCountsAllowed/maxValue*0.9)
                    if self.getExposureTime() == exposureTime_save :
                        break
                    
                else :
                    break
                
            self.data['spectrum'] = spectrum
            
        else :
            
            self.data['spectrum'] = pd.read_json(self.query('SPECTRUM?'))
            
		
        self.data['spectrum'].sort_index(inplace=True)
        
        if self.isAutoBackgroundRemovalEnabled():
            self.data['spectrum']['CountsWithoutBackground'] =(self.data['spectrum'].counts - self.getBackground())
            self.data['spectrum']['power']=self.data['spectrum']['CountsWithoutBackground']/self.getExposureTime()
        else:
            self.data['spectrum']['power']=self.data['spectrum']['counts']/self.getExposureTime()

            
            
    def getBackground(self):
        if self.data['spectrum'] is None :
            self.acquireSpectrum()
            self.data['spectrum'].sort_index(inplace=True)

        total_rows = len(self.data['spectrum'].index)
        mean_background_blue_wl = self.data['spectrum'].counts.head(int(np.floor(total_rows/10))).mean()
        mean_background_red_wl = self.data['spectrum'].counts.tail(int(np.floor(total_rows/10))).mean()
        mean_background = (mean_background_red_wl + mean_background_blue_wl)/2
        return mean_background
    
    
    def isAutoBackgroundRemovalEnabled(self):
        return self.autoBackgroundRemoval
    
    
    
    def setAutoBackgroundRemovalEnabled(self,value):
        assert isinstance(value,bool)
        self.autoBackgroundRemoval = value
    
    
    def getTemperature(self):
        return float(self.query('TEMP?'))
    
    
    
    
    

        
        
    def getMainPeakWavelength(self):
        if self.data['spectrum'] is None :
            self.acquireSpectrum()
        power = self.data['spectrum']['power']
        idx = (power-power.max()).abs().idxmin()
        return self.data['spectrum']['wavelength'].loc[idx]
        
    
    
    
    
    def getMaxPower(self):
        if self.data['spectrum'] is None :
            self.acquireSpectrum()
        return self.data['spectrum']['power'].max()
    
    
    
    
    
    def getIntegratedPower(self):
        if self.data['spectrum'] is None :
            self.acquireSpectrum()
        return np.trapz(self.data['spectrum']['power'],self.data['spectrum']['wavelength'])
    
    
    
    
    def getMainPeakFWHM(self):
        
        if self.data['spectrum'] is None :
            self.acquireSpectrum()
        
        power = self.data['spectrum']['power']
        
        # Recherche du max        
        idxMax=(power-power.max()).abs().idxmin()
        halfPower=self.getMaximumPower()/2
                      
        # Recherche autour du pic
        for i in np.arange(idxMax,min(power.index.values),-1):
            if power.loc[i] - halfPower<0 :
                fwhm_idxMin=i
                break
        for i in np.arange(idxMax,max(power.index.values),1):
            if power.loc[i] - halfPower <0 :
                fwhm_idxMax=i
                break
                
        wavelength = self.data['spectrum']['wavelength']
        return wavelength.loc[fwhm_idxMax] - wavelength.loc[fwhm_idxMin]
    
    
    
    
    
    



