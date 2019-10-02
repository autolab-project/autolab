#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import pandas as pd
import numpy as np





class Device():    
    
    def __init__(self):
                        
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
    
    
    
    def getDriverConfig(self):
        config = []
        config.append({'element':'variable','name':'exposureTime','unit':'s','type':float,'read':self.getExposureTime,'write':self.setExposureTime,'help':'Exposure time of the camera'})
        config.append({'element':'variable','name':'autoExposureTime','type':bool,'read':self.isAutoExposureTimeEnabled,'write':self.setAutoExposureTimeEnabled,'help':'Enable or not the auto exposure time mode'})
        config.append({'element':'variable','name':'autoBackgroundRemoval','type':bool,'read':self.isAutoBackgroundRemovalEnabled,'write':self.setAutoBackgroundRemovalEnabled,'help':'Enable or not the auto background removal mode'})
        config.append({'element':'variable','name':'spectrum','read':self.getSpectrum,'type':pd.DataFrame,'help':'Spectrum acquired'})
        config.append({'element':'variable','name':'temperature','type':float,'unit':'°C','read':self.getTemperature,'help':'Temperature of the camera'})
        config.append({'element':'variable','name':'mainPeakWavelength','type':float,'unit':'nm','read':self.getMainPeakWavelength,'help':'Wavelength of the main peak in the spectrum'})
        config.append({'element':'variable','name':'mainPeakFWHM','type':float,'unit':'nm','read':self.getMainPeakFWHM,'help':'FWHM of the main peak in the spectrum'})
        config.append({'element':'variable','name':'maxPower','type':float,'read':self.getMaxPower,'help':'Maximum power of the main peak in the spectrum'})
        config.append({'element':'variable','name':'integratedPower','type':float,'read':self.getIntegratedPower,'help':'Integrated power of the spectrum'})
        config.append({'element':'action','name':'acquire','do':self.acquireSpectrum,'help':'Acquire a spectrum'})
        return config
    
    
    
#################################################################################
############################## Connections classes ##############################
class Device_SOCKET(Device) :
    
    def __init__(self,address='192.168.0.8',**kwargs):
        
        import socket 
        
        self.ADDRESS = address
        self.PORT = 5005
        self.BUFFER_SIZE = 40000
        
        self.controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controller.connect((self.ADDRESS,self.PORT))   
        
        Device.__init__(self)
        
    def write(self,command):
        self.controller.send(command.encode())
        self.controller.recv(self.BUFFER_SIZE)
        
    def query(self,command):
        self.controller.send(command.encode())
        data = self.controller.recv(self.BUFFER_SIZE)
        return data.decode()
        
    def close(self):
        try :
            self.controller.close()
        except :
            pass
        self.controller = None



class Device_LOCAL(Device) : #not used

    def __init__(self,**kwargs):
        
        from winspec_utilities.winspec_gui_driver import Winspec
        self.controller = Winspec()

        Device.__init__(self)
        
              
    def write(self,command):
        self.controller.command(command)
        
    def query(self,command):
        return self.controller.command(command)
        
    def close(self):
        self.controller = None
############################## Connections classes ##############################
#################################################################################



#ADDRESS = '192.168.0.3'

    



