#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


import time 
import os
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d

import numpy as np
import pandas as pd

class Device():
    
    slotNaming = 'slot<NUM> = <MODULE_NAME>,<SLOT_NAME>,<CALIBRATION_PATH>'
    
    def __init__(self,**kwargs):
        
        # Submodules
        self.slotnames = []
        prefix = 'slot'
        for key in kwargs.keys():
            if key.startswith(prefix):
                slot_num = key[len(prefix):]
                module = globals()[ 'Module_'+kwargs[key].split(',')[0].strip() ]
                name = kwargs[key].split(',')[1].strip()
                calibpath = kwargs[key].split(',')[2].strip()
                setattr(self,name,module(self,slot_num,name,calibpath))
                self.slotnames.append(name)
        
        
    def getDriverConfig(self):
        
        config = []
        for name in self.slotnames :
            config.append({'element':'module','name':name,'object':getattr(self,name)})
        return config
        
        
    
#################################################################################
############################## Connections classes ##############################
class Device_VISA(Device):
    def __init__(self, address='GPIB0::2::INSTR',**kwargs):
        import visa
        
        
        self.BAUDRATE = 115200
        
        # Initialisation
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)
        self.controller.baud_rate = self.BAUDRATE
        
        Device.__init__(self)
        
        
        
    def close(self):
        try : self.controller.close()
        except : pass

    def query(self,command):
        result = self.controller.query(command)
        result = result.strip('\r\n')
        return result
    
    def write(self,command):
        self.controller.write(command)
        
        
############################## Connections classes ##############################
#################################################################################

class Module_NSR1():
    
    def __init__(self,dev,slot,name,calibPath):
        
        self.dev = dev
        self.NAME = name
        self.SLOT = slot
        
        self.checkNOTREFstate()
    
        self.calibPath = calibPath
        assert os.path.exists(calibPath)
        self.calibrationFunction = None
        
        self.calib = None
        self.loadCalib()
        
        
        
    # Query write functions
    # =========================================================================  

    def query(self,command,unwrap=True) :
        result = self.dev.query(self.SLOT+command)
        if unwrap is True :
            try:
                prefix=self.SLOT+command[0:2]
                result = result.replace(prefix,'')
                result = result.strip()
                result = float(result)
            except:
                pass
        return result
        
    def write(self,command) :
        self.dev.write(self.SLOT+command)
    
       
    # Devices functions
    # =========================================================================
            
    def getID(self):
        return self.query('ID?')
    
    
    
    def getFilterState(self):
        ans = self.query('TS?',unwrap=False)[-2:]
        if ans[0] == '0' :
            return 'REF'
        elif ans == '14' :
            return 'CONF'
        elif ans == '1E' :
            return 'HOMING'
        elif ans == '28' :
            return 'MOVING'
        elif ans[0] == '3' and ( ans[1].isalpha() is False)  :
            return 'ENABLED'
        elif ans[0] == '3' and ( ans[1].isalpha() is True)  :
            return 'DISABLED'
        else :
            return 'UNKNOWN'


        
    def checkNOTREFstate(self):
        
        # On vérifie que l'on est pas dans le mode REF
        state=self.getFilterState()
        if state == 'REF' :
            self.write('OR') # Perfom Home search
            while self.getFilterState() == 'HOMING' :
                time.sleep(0.5)
        elif state == 'CONF' :    
            self.write('PW0') # Sortie du mode Configuration
            self.checkNOTREFstate()
            
    def waitMoveEnding(self):
        while self.getFilterState() == 'MOVING' :
            time.sleep(0.1)

    
    
    
    def setEnabled(self,value):
        assert isinstance(bool(value),bool)
        self.write('MM'+str(int(value)))
    
    def isEnabled(self):
        state=self.getFilterState()
        if state in ['ENABLED','MOVING'] :
            return True
        else :
            return False
        
        

        
        
    #--------------------------------------------------------------------------
    # Instrument variables
    #--------------------------------------------------------------------------
    
    
 
    
    def setVelocity(self,value):
        
        assert isinstance(int(value),int)
        value=int(value)
        
        if value != self.getVelocity():
            
            # Go to not ref mode
            self.write('RS')
            while self.getFilterState() != 'REF':
                time.sleep(0.1)
            
            # Go to config mode
            self.write('PW1')
            while self.getFilterState() != 'CONF':
                time.sleep(0.1)
            
            # Change value
            self.write('VA%i'%value)

            # Sortie du mode config
            self.write('PW0')
            while self.getFilterState() != 'REF':
                time.sleep(0.1)
            
            # Homing to get back to ready state
            self.write('OR')
            while self.getFilterState() != 'ENABLED':
                time.sleep(0.1)

            # On le désactive
            self.setEnabled(False)
            while self.getFilterState() != 'DISABLED':
                time.sleep(0.1)
    
    def getVelocity(self):
        return self.query('VA?')
    
    
    def setAcceleration(self,value):
        
        assert isinstance(int(value),int)
        value=int(value)
        
        if value != self.getVelocity():
            
            # Go to not ref mode
            self.write('RS')
            while self.getFilterState() != 'REF':
                time.sleep(0.1)
            
            # Go to config mode
            self.write('PW1')
            while self.getFilterState() != 'CONF':
                time.sleep(0.1)
            
            # Change value
            self.write('AC%i'%value)

            # Sortie du mode config
            self.write('PW0')
            while self.getFilterState() != 'REF':
                time.sleep(0.1)
            
            # Homing to get back to ready state
            self.write('OR')
            while self.getFilterState() != 'ENABLED':
                time.sleep(0.1)

            # On le désactive
            self.setEnabled(False)
            while self.getFilterState() != 'DISABLED':
                time.sleep(0.1)
    
        
    def getAcceleration(self):
        return self.query('AC?')
    
            
            
    
    
    
    def setAngle(self,value,forced=False):
        assert isinstance(float(value),float)
        value=float(value)
        
        if forced is False :
            currAngle = self.getAngle()
            if value > currAngle - 1.9 :
                self.setAngle(value+20,forced=True)
            
        self.setEnabled(True)
        self.write('PA'+str(value))
        self.waitMoveEnding()
        self.setEnabled(False)
        
    def getAngle(self):
        value = self.query('TP?')
        return value
       
    
    
    
    
    
    def setMin(self):
        self.setTransmission(0)
        
    def setMax(self):
        self.setTransmission(1)





    def setTransmission(self,value):
        assert isinstance(float(value),float)
        value = float(value)
        angle = self.getAngleFromTransmission(value)
        self.setAngle(angle)
    
    def getTransmission(self):
        angle = self.getAngle()
        return self.getTransmissionFromAngle(angle) 

    def getTransmissionMax(self):
        return self.calib.transmission.max()



    def getAngleFromTransmission(self,value):
        ind = abs(self.calib.transmission-value).idxmin()
        return float(self.calib.loc[ind,'angle'])   
    
    def getTransmissionFromAngle(self,value):
        ind = abs(self.calib.angle-value).idxmin()
        return float(self.calib.loc[ind,'transmission'])   


    
    def goHome(self):
                            
        # Go to not ref mode
        self.write('RS')
        while self.getFilterState() != 'REF':
            time.sleep(0.1)
        
        # Homing to get back to ready state
        self.write('OR')
        while self.getFilterState() != 'ENABLED':
            time.sleep(0.1)

        # On le désactive
        self.setEnabled(False)
        while self.getFilterState() != 'DISABLED':
            time.sleep(0.1)
            
            
            
    # Calibration functions
    # =========================================================================
    
    def loadCalib(self):
        try: self.calib = pd.read_csv(os.path.join(self.calibPath,'calib.csv'))
        except: pass
    
    def setCalibrationGetPowerFunction(self,calibrationFunction):
        self.calibrationFunction = calibrationFunction
        
    def calibrate(self):
        
        assert self.calibrationFunction is not None
        
        def scan(listAngle):
            
            df = pd.DataFrame()

            for angle_setpoint in listAngle :
                self.setAngle(angle_setpoint)
                angle=self.getAngle()
                power=self.calibrationFunction()
                df=df.append({'angle':angle,'power':power})
                   
            df.sort_values(by=['angle'],inplace=True)
            return df
        
        plt.ioff()
        fig = plt.figure()
        ax=fig.add_subplot(111)
        
        # Homing
        self.goHome()
        
        # Fabrication de la liste des angles à explorer
        listAngle = np.concatenate((np.arange(0,360,8),np.arange(4,360,8)))
        listAngle = np.flipud(listAngle)
        
        # Lancement du scan de mesure de puissance
        df=scan(listAngle)
        
        # Find transition
        derivative = np.diff(df.power)
        imax=np.argmax(derivative)
        
        # Recoupage
        df_shifted = pd.DataFrame()
        df_shifted['power'] = np.concatenate((df.power[imax:],df.power[0:imax]))
        df_shifted['angle'] = np.concatenate((df.angle[imax:]-360,df.angle[0:imax]))
        df = df_shifted
        
        # Suppression transition sur 10deg
        df = pd.DataFrame()
        df = df[df.angle>(df.angle.min()+10)]
        df = df[df.angle<(df.angle.max()-10)]
        
        # Normalisation
        df['transmission']=df.power/df.power.max()
        ax.plot(df.angle,df.transmission,'x',label='raw')
        
        # Lissage
        df['transmission']=savgol_filter(df.transmission, 7, 3)
        
        # Interpolation
        interpolFunc=interp1d(df.angle, df.transmission, kind='cubic')
        df['angle']=np.linspace(df.angle.min(),df.angle.max(),1000)
        df['transmission']=interpolFunc(df.angle)
        
        # EXTRACT On ne garde que entre 0% et 95% car trop bruité au dessus
        df = df[df.transmission<0.95]
        
        # Sauvegarde plot
        date=time.strftime("%Y%m%d_%H%M%S")
        ax.plot(df.angle,df.transmission,'r-',label='Final')
        ax.set_title(f'{self.NAME} filter {date}')
        ax.grid()
        ax.set_xlabel('Angle [deg]')
        ax.set_ylabel('Power [a.u.]')
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, loc=0)
        filepath=os.path.join(self.calibPath,f'{date}_{self.NAME}_calib.jpg')
        fig.savefig(filepath,bbox_inches='tight',dpi=300)
        fig.close()
           
        # Enregistrement des données 
        df.to_csv(os.path.join(self.calibPath,'calib.csv'))
        
        # Raffraichissement des donnees
        self.loadCalib()
     
        
    def getDriverConfig(self):
        
        config = []
        config.append({'element':'variable','name':'velocity','type':float,'read':self.getVelocity,'write':self.setVelocity,'help':'Velocity of the filter during move'})
        config.append({'element':'variable','name':'acceleration','type':float,'read':self.getAcceleration,'write':self.setAcceleration,'help':'Acceleration of the filter during move'})
        config.append({'element':'variable','name':'angle','type':float,'read':self.getAngle,'write':self.setAngle,'help':'Current angle position'})
        config.append({'element':'variable','name':'transmission','type':float,'read':self.getTransmission,'write':self.setTransmission,'help':'Current transmission of the filter'})
        config.append({'element':'action','name':'setMin','do':self.setMin,'help':'Go to minimum transmission'})
        config.append({'element':'action','name':'setMax','do':self.setMax,'help':'Go to maximum transmission'})
        config.append({'element':'action','name':'goHome','do':self.goHome,'help':'Go to home position'})
        return config
    
    
        
        
    
