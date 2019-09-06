# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 20:06:08 2019

@author: quentin.chateiller
"""


import socket
import time



ADDRESS = '192.168.0.16'



class Device():

    def __init__(self,address=ADDRESS):
                
        self.BUFFER_SIZE = 40000
        
        self.controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controller.connect((address,50000))        






        
    def write(self,command):
        self.controller.send(command.encode())
        self.controller.recv(self.BUFFER_SIZE)
        
        
    def query(self,command):
        self.controller.send(command.encode())
        result = self.controller.recv(self.BUFFER_SIZE).decode()
        result = result.strip('\n\x00)\x00')
        if '=' in result : result = result.split('=')[1]
        try : result = float(result)
        except: pass
        return result
    
        
    def close(self):
        try :
            self.controller.close()
        except :
            pass
        self.controller = None
        
        
        
        
        
        
        
        
        
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
    
    
    