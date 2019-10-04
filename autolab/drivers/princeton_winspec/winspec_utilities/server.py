#!/usr/bin/env python
import socket
import threading
import datetime as dt

from winspec_gui_driver import Winspec

IP_LOCAL_PREFIX = '192.168.0'
LISTENING_PORT = 5005

class Server :
    
    def __init__(self):

        log('')
        log(' *** WINSPEC SERVER by Q.C., March 2019 *** ')
        log('')
        log('1) Start Winspec')
        log('2) Close other windows')
        log('3) Start Winspec server as an administrator')
    
        
        
        log('')
        log('Looking for Winspec window...')
        self.winspec = Winspec()
        
        if self.winspec.isConnected() :
            
            log('Winspec window found !')
            self.winspec.minimizeWindow()
            
            log('')
            log('Looking for IP address...')
            self.ip = get_local_ip()
            log('Local IP : %s'%self.ip)
            log('Port : %i'%LISTENING_PORT)
                
            log('')
            log('Creating server...')
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((self.ip, LISTENING_PORT))
            self.s.listen(1)
            log('Ok ! Server running and Winspec ready.')
    
            self.thread = None
            
            log('')            
            log('Waiting for an incoming connection...')
        
            while True :
                conn, addr = self.s.accept()
                if self.thread is not None : 
                    self.thread.stopFlag.set()
                self.thread = ClientThread(conn,self)
                self.thread.start()
                log('Incoming connection from '+str(addr))

        else :
            log('') 
            log('Winspec not found...')
            log('Please check everything and try again !')


def log(message):
    print(str(dt.datetime.now())+': '+message)


def get_local_ip():
    ip_list = [ a[4][0] for a in socket.getaddrinfo(socket.gethostname(), None) ]
    ip_list_local = [ ip for ip in ip_list if ip.startswith(IP_LOCAL_PREFIX) ]
    assert len(ip_list_local) > 0, "Local interface not found"
    assert len(ip_list_local) < 2, "More than one local interface found"
    ip = ip_list_local[0]
    return ip
    

class ClientThread(threading.Thread):

    def __init__(self, clientsocket, server):

        self.winspec = server.winspec 
        
        threading.Thread.__init__(self)
        self.clientsocket = clientsocket
        self.stopFlag = threading.Event()
        

        
    def run(self): 
        while True :
            try : 
                data = self.clientsocket.recv(1024)
            except : 
                break 
            
            if not data or self.stopFlag.isSet() : break
            
            command = data.decode()
            log('Received: '+str(command))
            
            answer = self.winspec.command(command)
            
            if isinstance(answer,str) and len(answer) > 50 : 
                log('Sent: '+answer[:50]+'...')
            else : 
                log('Sent: '+str(answer))
            
            self.clientsocket.send(str(answer).encode())  # echo

        self.clientsocket.close()
        log('Current connection closed')




server = Server()
