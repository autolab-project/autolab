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
        msg  = self.client_socket.recv(length)
        if not msg.startswith(self.prefix) : raise ValueError('Autolab communication structure not found in reply')

        # Continue reading up to suffix
        while not msg.endswith(self.suffix):
            msg += self.client_socket.recv(length)

        # Clean msg (remove prefix and suffix)
        msg = msg.lstrip(self.prefix).rstrip(self.suffix)

        # Return unpickled server answer
        return pickle.loads(msg)


    def write(self,object):

        ''' Send pickled object to autolab master '''

        msg = self.prefix+pickle.dumps(object)+self.suffix
        self.client_socket.send(msg)

        
class Server(Driver_SOCKET):

    def __init__(self):

        # Load server config in autolab_config.ini
        server_config = config.get_server_config()
        local_ip = server_config['local_ip']
        port = int(server_config['port'])

        # Start the server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((local_ip, port))
        self.socket.listen(1) # 0 to test

        # Start listening and executing remote commands
        while True :
            try:

                # Wait incoming connection
                self.client_socket, self.client_address = self.socket.accept()

                # Handshaking
                if self.handshake() is True :

                    while True :
                        command = self.read()
                        if command == 'CLOSE_CONNECTION' : break
                        else :
                            self.process_command(command)

                else :
                    self.client_socket.close()

            except KeyboardInterrupt:
                self.socket.close()
                print("You cancelled the program!")
                sys.exit(1)

    def process_command(self,command):

        if command == 'DEVICES_STATUS?' :
            return self.write(devices.get_devices_status())



    def handshake(self):

        ''' Check that incoming connection comes from another Autolab program '''
        self.client_socket.settimeout(2)
        try :
            handshake_str = self.read()
            if handshake_str == 'AUTOLAB?' :
                self.write('YES')
                result = True
            else : result = False
        except :
            result = False
        self.client_socket.settimeout(0)
        return result






class Driver_REMOTE(Driver_SOCKET):

    def __init__(self,address='192.168.1.1',port=5000):
        from functools import partial

        self.address = address
        self.port    = port

        # Connection au serveur Autolab
        self.controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controller.connect((address, int(port)))
        self.controller.settimeout(2)

        # Handshaking
        self.handshake()

        # Retourne la liste des devices
        self.devices_status = self.get_devices_status()

    def close(self):

        self.controller.write('CLOSE_CONNECTION')
        self.controller.close()

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
        for dev_name in self.devices_list :
            model['element':'device', 'name':dev_name, 'instance': partial(self.get_device,dev_name)]
        return model

    def get_device(self,dev_name):
        pass

    def get_device_structure(self):
        pass
            # Pour un device de slave donné, retourne sa structure de (sous-devices, modules, action variable) à l’instant t
            # Device non instantité : ne renvoie rien
            # Device instantié : renvoie structure en (modules, action, variable)
