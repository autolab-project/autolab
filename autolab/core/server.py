# -*- coding: utf-8 -*-

import sys
import socket
import pickle
import threading
from . import config, devices


class Driver_SOCKET():

    prefix = b'<AUTOLAB_START>'
    suffix = b'<AUTOLAB_END>'

    def read(self, length=4096):

        ''' Read pickled object from autolab master and return python object '''

        # First read
        msg  = self.socket.recv(length)
        assert msg != b'', 'Connection closed by remote host'
        assert msg.startswith(self.prefix), 'Autolab communication structure not found in reply'

        # Continue reading up to suffix
        while not msg.endswith(self.suffix):
            msg += self.socket.recv(length)

        # Clean msg (remove prefix and suffix) and unpicke it
        msg = msg.lstrip(self.prefix).rstrip(self.suffix)
        obj = pickle.loads(msg)

        return obj


    def write(self,object):

        ''' Send pickled object to autolab master '''

        msg = self.prefix+pickle.dumps(object)+self.suffix
        self.socket.send(msg)





class ClientThread(threading.Thread,Driver_SOCKET):

    def __init__(self, client_socket, server):
        threading.Thread.__init__(self)
        self.socket = client_socket
        self.server = server
        self.stop_flag = threading.Event()


    def run(self):

        # Handshaking
        if self.handshake() is True :
            # Start listening client commands
            self.listen()

        # Close client socket
        self.close()


    def handshake(self):

        ''' Check that incoming connection comes from another Autolab program,
            and that no thread is already controlling autolab '''

        self.socket.settimeout(5)
        try :
            # Read first command from client
            handshake_str = self.read()

            # Check that first client command is 'AUTOLAB?'
            if handshake_str.startswith('AUTOLAB?') :

                # There is no main thread currently running, accepting communication
                if self.server.active_connection_thread is None :
                    self.server.active_connection_thread = self
                    self.server.active_connection_hostname = handshake_str.split('=')[1]
                    self.write('YES')
                    result = True

                # Another client is controlling autolab, reply that the server is busy, refusing communication
                else :
                    self.write(f'Autolab server on host {socket.gethostname()} already in use by host {self.server.active_connection_hostname}.')
                    result = False

            # The client did not ask the right first command, refusing communication
            else : result = False

        except Exception as e:
            print(e)
            result = False
        self.socket.settimeout(None)

        return result


    def listen(self):

        ''' Listen and answer client commands '''

        while self.stop_flag.is_set() is False :

            try:
                command = self.read()
                self.process_command(command)
            except:
                self.stop_flag.set()


    def process_command(self,command):

        ''' Process given client command '''

        if command == 'CLOSE_CONNECTION' :
            self.stop_flag.set()
        elif command == 'DEVICES_STATUS?' :
            return self.write(devices.get_devices_status())


    def close(self):

        # In case the close call come from outside of the threading
        self.stop_flag.set()

        # Close client socket
        self.socket.close()

        # If this thread is the main client thread, remove declaration
        if self.server.active_connection_thread == self :
            self.server.active_connection_thread = None
            self.server.active_connection_hostname = None









class Server():

    def __init__(self,port=None):

        self.client_threads = []

        self.active_connection_thread = None
        self.active_connection_hostname = None

        # Load server config in autolab_config.ini
        server_config = config.get_server_config()
        if not port: port = int(server_config['port'])
        self.port = port

        # Start the server
        self.start()

        # Start listening
        try :
            self.listen()
        except KeyboardInterrupt:
            self.close()
            sys.exit()


    def start(self):

        ''' Start the server '''

        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_socket.bind(('', self.port))
        self.main_socket.listen(0)


    def listen(self):

        while True :

            # Wait incoming connection
            client_socket, _ = self.main_socket.accept()

            # Clean terminated threads
            self.clean_client_threads()

            # Start new client thread
            client_thread = ClientThread(client_socket,self)
            client_thread.start()
            self.client_threads.append(client_thread)


    def clean_client_threads(self):

        ''' Remove finshed client threads from the list '''

        self.client_threads = [t for t in self.client_threads if not t.is_alive()]


    def close_client_threads(self):

        ''' Close any existing client thread '''

        self.clean_client_threads()
        for thread in self.client_threads :
            thread.close()
            thread.join()


    def close(self):

        ''' Close the server and client threads'''

        self.close_client_threads()
        self.main_socket.close()








class Driver_REMOTE(Driver_SOCKET):

    def __init__(self,address='192.168.1.1',port=4001):
        from functools import partial

        self.address = address
        self.port    = int(port)

        # Connection au serveur Autolab
        self.connect()

        # Handshaking
        self.handshake()

        # Retourne la liste des devices
        self.devices_status = self.get_devices_status()
        print(self.devices_status)


    def connect(self):

        ''' Initialize connection with autolab server '''

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(2)
        self.socket.connect((self.address, self.port))


    def handshake(self):

        ''' Check that distant partner is an Autolab server '''

        self.write(f'AUTOLAB?HOSTNAME={socket.gethostname()}')
        try :
            answer = self.read()
            assert answer == 'YES', answer
        except Exception as e :
            raise ValueError(f'Impossible to join autolab server at {self.address}:{self.port} \n {e}')


    def disconnect(self):

        ''' Close autolab server connection '''

        self.socket.write('CLOSE_CONNECTION')
        self.socket.close()




    def get_devices_status(self) : # Déjà instantié ou non
        self.write('DEVICES_STATUS?')
        return self.read()


    def get_driver_model(self):
        model = {}
        #for dev_name in self.devices_status :
            #model['element':'device', 'name':dev_name, 'instance': partial(self.get_device,dev_name)]
        return model

    def get_device(self,dev_name):
        pass

    def get_device_structure(self):
        pass
            # Pour un device de slave donné, retourne sa structure de (sous-devices, modules, action variable) à l’instant t
            # Device non instantité : ne renvoie rien
            # Device instantié : renvoie structure en (modules, action, variable)
