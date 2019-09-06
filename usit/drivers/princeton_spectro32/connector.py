# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 16:55:18 2019

@author: qchat
"""

class Spectro32ConnectorRemote():
    
    def __init__(self,address):
        
        import socket 
        
        self.ADDRESS = address
        self.PORT = 5005
        self.BUFFER_SIZE = 10000
        
        self.controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controller.connect((self.ADDRESS,self.PORT))
        
    def write(self,command):
        self.controller.send(command.encode())
        self.recv_end(self.controller)
        
    def query(self,command):
        self.controller.send(command.encode())
        data = self.recv_end(self.controller)
        return data
    
    def recv_end(self,the_socket,end='\n'):
        total_data=[];data=''
        while True:
                data=the_socket.recv(self.BUFFER_SIZE).decode()
                if end in data:
                    total_data.append(data[:data.find(end)])
                    break
                total_data.append(data)
                if len(total_data)>1:
                    #check if end_of_data was split
                    last_pair=total_data[-2]+total_data[-1]
                    if end in last_pair:
                        total_data[-2]=last_pair[:last_pair.find(end)]
                        total_data.pop()
                        break
        return ''.join(total_data)

        
    def close(self):
        try :
            self.controller.close()
        except :
            pass
        self.controller = None



class Spectro32ConnectorLocal : #not used

    
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
