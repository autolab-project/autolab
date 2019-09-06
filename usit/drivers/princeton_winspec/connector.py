# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 16:55:18 2019

@author: qchat
"""

class WinspecConnectorRemote :
    
    def __init__(self,address):
        
        import socket 
        
        self.ADDRESS = address
        self.PORT = 5005
        self.BUFFER_SIZE = 40000
        
        self.controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controller.connect((self.ADDRESS,self.PORT))        
        
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





class WinspecConnectorLocal : #not used

    
    def __init__(self):
        from .winspec_gui_driver import Winspec
        self.controller = Winspec()
        print('passffbhdfhdfh')
              
    def write(self,command):
        self.controller.command(command)
        
    def query(self,command):
        return self.controller.command(command)
        
    def close(self):
        self.controller = None
