# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 13:42:52 2019

@author: quentin.chateiller
"""

import time 

class ILS100CC() :
    
    def __init__(self,dev,slot):
        
        self.dev = dev
        self.SLOT = str(slot)
        
        

        
        
    def query(self,command):
        return self.dev.query(self.SLOT+command)
    
    
    def write(self,command):
        self.dev.write(self.SLOT+command)
        
        
        
        
        
    

    def getState(self):
        ans = self.query('TS?',unwrap=False)[-2:]
        if ans[0] == '0' :
            return 'NOTREF'
        elif ans == '14' :
            return 'CONF'
        elif ans in ['1E','1F'] :
            return 'HOMING'
        elif ans == '28' :
            return 'MOVING'
        elif ans[0] == '3' and ( ans[1].isalpha() is False)  :
            return 'READY'
        elif ans[0] == '3' and ( ans[1].isalpha() is True)  :
            return 'DISABLED'
        elif ans in ['46','47']:
            return 'JOGGING'
        else :
            return 'UNKNOWN'
        
        
        
        
    def getReady(self):
        
        # On vérifie que l'on est pas dans le mode REF
        state=self.getState()
        if state == 'JOGGING' : 
            self.write('JD') # Sortie du mode Jogging   
        elif state == 'DISABLED' : 
            self.write('MM1') # Sortie du mode disabled  
        self.waitReady()

    def waitReady(self):
        while self.getState() != 'READY' :
            time.sleep(0.1)
            

            
            
    def getID(self):
        return self.query('ID?')





    def getPosition(self):
        return self.query('PA?')
    
    def setPosition(self,value):
        self.getReady()
        self.write('PA'+str(value))
        self.waitReady()


  
        

    def setAcceleration(self,value):
        self.getReady()
        self.write('AC'+str(value))


    def getAcceleration(self):
        return self.query('AC?')
