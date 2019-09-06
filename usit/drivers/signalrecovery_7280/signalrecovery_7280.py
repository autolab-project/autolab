# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 20:06:08 2019

@author: quentin.chateiller
"""
import visa
import time

ADDRESS = 'GPIB0::12::INSTR'

class Device():

    def __init__(self,address=ADDRESS):
                
        rm = visa.ResourceManager()
        self.controller = rm.open_resource(address)

        
        
        
    def close(self):
        try : self.controller.close()
        except : pass

    def query(self,command):
        result = self.controller.query(command)
        result = result.strip('\n')
        if '=' in result : result = result.split('=')[1]
        try : result = float(result)
        except: pass
        return result
    
    def write(self,command):
        self.controller.write(command)
        
        
        

     
    def getID(self):
        return str(self.query('ID'))+' VER '+str(self.query('VER'))

    def waitFourTimeConstant(self): # see manual why
        time.sleep(4*self.getTimeConstant())






    def getMagnitude(self):
        return float(self.query("MAG."))

    def getPhase(self):
        return float(self.query("PHA."))
    
    def getRefFrequency(self):
        return float(self.query('FRQ.'))

    def getTimeConstant(self):
        return float(self.query('TC.'))
    
    def getSensitivity(self):
        return float(self.query('SEN.'))