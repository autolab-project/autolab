#!/usr/bin/env python
import socket
import threading
import datetime as dt
import spectro32_server as spectro


IP_LOCAL_PREFIX = '192.168.0'
LISTENING_PORT = 5005

def log(message):
    print(str(dt.datetime.now())+': '+message)

def get_local_ip():
    ip_list = [ a[4][0] for a in socket.getaddrinfo(socket.gethostname(), None) ]
    ip_list_local = [ ip for ip in ip_list if ip.startswith(IP_LOCAL_PREFIX) ]
    assert len(ip_list_local) > 0, "Local interface not found"
    assert len(ip_list_local) < 2, "More than one local interface found"
    ip = ip_list_local[0]
    return ip


class Server():
    def __init__(self):
		
		### Initiate spectro and camera ###
        self.spectro = spectro.remote_Device()
		
        ### Start the server ###
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
        log('Ok ! Server running')
        
        log('')            
        log('Waiting for an incoming connection...')
        self.thread = None
        while True :
            conn, addr = self.s.accept()
            if self.thread is not None : 
                self.thread.stopFlag.set()
            self.thread = ClientThread(conn,self.spectro)
            self.thread.start()
            log('Incoming connection from '+str(addr))
    

class ClientThread(threading.Thread):
    def __init__(self, clientsocket, spectro):
        self.end_char = '\n'
        
        self.spectro = spectro
	
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
            
            answer = self.spectro.command(command)
            
            if isinstance(answer,str) and len(answer) > 50 : 
                log('Sent: '+answer[:50]+'...')
            elif not(answer):
                log('Sent: '+str(answer))
            else : 
                log('Sent: '+str(answer)[:50]+' ...')
            
            self.clientsocket.send((str(answer)+self.end_char).encode())  # echo

        self.clientsocket.close()
        log('Current connection closed')


server = Server()
