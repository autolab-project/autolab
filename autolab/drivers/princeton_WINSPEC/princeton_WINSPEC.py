#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import pandas as pd
import numpy as np





class Driver():    
    
    def __init__(self):
                        
        self.min_counts_allowed=5000
        self.max_counts_allowed=61000
        
        # Defaults
        self.auto_background_removal = False
        self.auto_exposure_time = True
		
        self.data = {'exposure_time':None,'spectrum':None}
        self.write('Initialize')
                
        
        
    def is_connected(self):
        try :
            return bool(int(self.query('STATE?')))
        except :
            return False


    

        
        
    def get_exposure_time(self):
        if self.data['exposure_time'] is None :
            self.data['exposure_time'] = float(self.query('EXPTIME?'))
        return self.data['exposure_time']

    def set_exposure_time(self,value):
        value=float(value)
        self.write(f'EXPTIME={value}')
        self.data['exposure_time'] = float(self.query('EXPTIME?'))
        
        
        
        
        
    
    def is_auto_exposure_time_enabled(self):
        return self.auto_exposure_time
    
    def set_auto_exposure_time_enabled(self,value):
        assert isinstance(value,bool)
        self.auto_exposure_time = value
        
        
        
        
        
        
    def get_spectrum(self):
        if self.data['spectrum'] is None :
            self.acquire_spectrum()
        return self.data['spectrum']
    
    
    def acquire_spectrum(self):
            
        if self.is_auto_exposure_time_enabled() :
            
            while True :
                
                # Mesure spectre
                spectrum = pd.read_json(self.query('SPECTRUM?'))
        
                # Récupération des données
                max_value=max(spectrum['counts'])
                
                # Reduction du temps d'exposition
                if max_value>self.max_counts_allowed : 
                    exposure_time_save = self.get_exposure_time()
                    self.set_exposure_time(self.get_exposure_time()/10)
                    if self.get_exposure_time() == exposure_time_save :
                        break
                
                # Augmentation du temps d'exposition
                elif max_value<self.min_counts_allowed : 
                    exposure_time_save = self.get_exposure_time()
                    self.set_exposure_time(self.get_exposure_time()*self.max_counts_allowed/max_value*0.9)
                    if self.get_exposure_time() == exposure_time_save :
                        break
                    
                else :
                    break
                
            self.data['spectrum'] = spectrum
            
        else :
            
            self.data['spectrum'] = pd.read_json(self.query('SPECTRUM?'))
            
		
        self.data['spectrum'].sort_index(inplace=True)
        
        if self.is_auto_background_removal_enabled():
            self.data['spectrum']['CountsWithoutBackground'] =(self.data['spectrum'].counts - self.getBackground())
            self.data['spectrum']['power']=self.data['spectrum']['CountsWithoutBackground']/self.get_exposure_time()
        else:
            self.data['spectrum']['power']=self.data['spectrum']['counts']/self.get_exposure_time()

            
            
    def getBackground(self):
        if self.data['spectrum'] is None :
            self.acquire_spectrum()
            self.data['spectrum'].sort_index(inplace=True)

        total_rows = len(self.data['spectrum'].index)
        mean_background_blue_wl = self.data['spectrum'].counts.head(int(np.floor(total_rows/10))).mean()
        mean_background_red_wl = self.data['spectrum'].counts.tail(int(np.floor(total_rows/10))).mean()
        mean_background = (mean_background_red_wl + mean_background_blue_wl)/2
        return mean_background
    
    
    def is_auto_background_removal_enabled(self):
        return self.auto_background_removal
    
    
    
    def set_auto_background_removal_enabled(self,value):
        assert isinstance(value,bool)
        self.auto_background_removal = value
    
    
    def get_temperature(self):
        return float(self.query('TEMP?'))
    
    
    
    
    

        
        
    def get_main_peak_wavelength(self):
        if self.data['spectrum'] is None :
            self.acquire_spectrum()
        power = self.data['spectrum']['power']
        idx = (power-power.max()).abs().idxmin()
        return self.data['spectrum']['wavelength'].loc[idx]
        
    
    
    
    
    def get_max_power(self):
        if self.data['spectrum'] is None :
            self.acquire_spectrum()
        return self.data['spectrum']['power'].max()
    
    
    
    
    
    def get_integrated_power(self):
        if self.data['spectrum'] is None :
            self.acquire_spectrum()
        return np.trapz(self.data['spectrum']['power'],self.data['spectrum']['wavelength'])
    
    
    
    
    def get_main_peak_fwhm(self):
        
        if self.data['spectrum'] is None :
            self.acquire_spectrum()
        
        power = self.data['spectrum']['power']
        
        # Recherche du max        
        idxMax=(power-power.max()).abs().idxmin()
        halfPower=self.get_max_power()/2
                      
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
    
    
    
    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'exposure_time','unit':'s','type':float,'read':self.get_exposure_time,'write':self.set_exposure_time,'help':'Exposure time of the camera'})
        model.append({'element':'variable','name':'auto_exposure_time','type':bool,'read':self.is_auto_exposure_time_enabled,'write':self.set_auto_exposure_time_enabled,'help':'Enable or not the auto exposure time mode'})
        model.append({'element':'variable','name':'auto_background_removal','type':bool,'read':self.is_auto_background_removal_enabled,'write':self.set_auto_background_removal_enabled,'help':'Enable or not the auto background removal mode'})
        model.append({'element':'variable','name':'spectrum','read':self.get_spectrum,'type':pd.DataFrame,'help':'Spectrum acquired'})
        model.append({'element':'variable','name':'temperature','type':float,'unit':'°C','read':self.get_temperature,'help':'Temperature of the camera'})
        model.append({'element':'variable','name':'main_peak_wavelength','type':float,'unit':'nm','read':self.get_main_peak_wavelength,'help':'Wavelength of the main peak in the spectrum'})
        model.append({'element':'variable','name':'main_peak_peak_fwhm','type':float,'unit':'nm','read':self.get_main_peak_fwhm,'help':'FWHM of the main peak in the spectrum'})
        model.append({'element':'variable','name':'max_power','type':float,'read':self.get_max_power,'help':'Maximum power of the main peak in the spectrum'})
        model.append({'element':'variable','name':'integrated_power','type':float,'read':self.get_integrated_power,'help':'Integrated power of the spectrum'})
        model.append({'element':'action','name':'acquire','do':self.acquire_spectrum,'help':'Acquire a spectrum'})
        return model
    
    
    
#################################################################################
############################## Connections classes ##############################
class Driver_SOCKET(Driver) :
    
    def __init__(self,address='192.168.0.8',**kwargs):
        
        import socket 
        
        self.ADDRESS = address
        self.PORT = 5005
        self.BUFFER_SIZE = 40000
        
        self.controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controller.connect((self.ADDRESS,int(self.PORT)))   
        
        Driver.__init__(self)
        
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



class Driver_LOCAL(Driver) : #not used

    def __init__(self,**kwargs):
        
        from winspec_utilities.winspec_gui_driver import Winspec
        self.controller = Winspec()

        Driver.__init__(self)
        
              
    def write(self,command):
        self.controller.command(command)
        
    def query(self,command):
        return self.controller.command(command)
        
    def close(self):
        self.controller = None
############################## Connections classes ##############################
#################################################################################



