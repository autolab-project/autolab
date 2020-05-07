# -*- coding: utf-8 -*-

import sys
import socket
import pickle
from . import config, devices


class Driver_SOCKET():

    prefix = b'<AUTOLAB_START>'
    suffix = b'<AUTOLAB_END>'

    def read(self, length=4096):

        ''' Read pickled object from autolab master and return python object '''

        # First read
        msg  = self.socket.recv(length)
        if not msg.startswith(self.prefix) : raise ValueError('Autolab communication structure not found in reply')

        # Continue reading up to suffix
        while not msg.endswith(self.suffix):
            msg += self.socket.recv(length)

        # Clean msg (remove prefix and suffix)
        msg = msg.lstrip(self.prefix).rstrip(self.suffix)

        # Return unpickled server answer
        return pickle.loads(msg)


    def write(self,object):

        ''' Send pickled object to autolab master '''

        msg = self.prefix+pickle.dumps(object)+self.suffix
        self.socket.send(msg)


class Server(Driver_SOCKET):

    def __init__(self,port=None):

        # Load server config in autolab_config.ini
        server_config = config.get_server_config()
        if not port: port = int(server_config['port'])
        self.port = port

        # Start the server
        self.start()

        # Start listening and executing remote commands
        self.listen()


    def listen(self):

        ''' Start listening and executing remote commands '''

        try:

            while True :

                # Wait incoming connection
                self.socket, self.client_address = self.main_socket.accept()

                # Handshaking
                if self.handshake() is True :
                    while True :

                        try: command = self.read()
                        except: break

                        if command == 'CLOSE_CONNECTION' : break
                        else : self.process_command(command)

                # Close socket (client)
                self.socket.close()


        except KeyboardInterrupt:
            self.close()
            sys.exit()



    def start(self):

        ''' Start the server (main socket) '''

        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_socket.bind(('', self.port))
        self.main_socket.listen(0)


    def close(self):

        ''' Close existing sockets (main and client if existing) '''

        try : self.socket.close()
        except : pass
        self.main_socket.close()



    def process_command(self,command):

        if command == 'DEVICES_STATUS?' :
            return self.write(devices.get_devices_status())



    def handshake(self):

        ''' Check that incoming connection comes from another Autolab program '''
        self.socket.settimeout(2)
        try :
            handshake_str = self.read()
            if handshake_str == 'AUTOLAB?' :
                self.write('YES')
                result = True
            else : result = False
        except :
            result = False
        self.socket.settimeout(None)
        return result






class Driver_REMOTE(Driver_SOCKET):

    def __init__(self,address='192.168.1.1',port=4001):
        from functools import partial

        self.address = address
        self.port    = port

        # Connection au serveur Autolab
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(2)
        self.socket.connect((address, int(port)))
        
        # Handshaking
        self.handshake()

        # Retourne la liste des devices
        self.devices_status = self.get_devices_status()
        print(self.devices_status)

    def close(self):

        self.socket.write('CLOSE_CONNECTION')
        self.socket.close()

    def handshake(self):

        ''' Check that distant partner is an Autolab server '''

        self.write('AUTOLAB?')
        try :
            answer = self.read()
            assert answer == 'YES', "This is not the good answer but anyway, this is never gonna be displayed ;)"
        except Exception as e :
            raise ValueError(f'Impossible to join autolab server at {self.address}:{self.port} \n {e}')


    def get_devices_status(self) : # Déjà instantié ou non
        self.write('DEVICES_STATUS?')
        return self.read()


    def get_driver_model(self):
        model = {}
        for dev_name in self.devices_status :
            model['element':'device', 'name':dev_name, 'instance': partial(self.get_device,dev_name)]
        return model

    def get_device(self,dev_name):
        pass

    def get_device_structure(self):
        pass
            # Pour un device de slave donné, retourne sa structure de (sous-devices, modules, action variable) à l’instant t
            # Device non instantité : ne renvoie rien
            # Device instantié : renvoie structure en (modules, action, variable)
