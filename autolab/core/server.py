# -*- coding: utf-8 -*-

import socket
import pickle
import threading
import datetime as dt
from functools import partial

from .config import get_server_config
from .devices import get_devices_status, get_device


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

    def write(self, object):
        ''' Send pickled object to autolab master '''
        msg = self.prefix + pickle.dumps(object) + self.suffix
        self.socket.send(msg)


class ClientThread(threading.Thread, Driver_SOCKET):

    def __init__(self, client_socket, server):
        super().__init__()
        self.socket = client_socket
        self.server = server
        self.stop_flag = threading.Event()
        self.hostname = None

    def run(self):

        # Handshaking
        if self.handshake():
            # Start listening client commands
            self.listen()

        # Close client socket
        self.close()

    def handshake(self) -> bool:

        ''' Check that incoming connection comes from another Autolab program,
            and that no thread is already controlling autolab '''

        self.socket.settimeout(2)

        try :
            # Read first command from client
            handshake_str = self.read()

            # Check that first client command is 'AUTOLAB?'
            if handshake_str.startswith('AUTOLAB?'):

                self.hostname = handshake_str.split('=')[1]

                # There is no main thread currently running, accepting communication
                if self.server.active_connection_thread is None:
                    self.server.active_connection_thread = self
                    self.server.log(f'Host "{self.hostname}" connected')
                    self.write('YES')
                    result = True

                # Another client is controlling autolab, reply that the server is busy, refusing communication
                else :
                    self.server.log(f'Host "{self.hostname}" trying to connect but a connection is already established from host "{self.server.active_connection_thread.hostname}"')
                    self.write(f'A connection to the Autolab server is already established from host "{self.server.active_connection_thread.hostname}".')
                    result = False

            # The client did not ask the right first command, refusing communication
            else: result = False

        except Exception as e:
            print(e)
            result = False

        self.socket.settimeout(None)

        return result

    def listen(self):
        ''' Listen and answer client commands '''
        while not self.stop_flag.is_set():
            try:
                command = self.read()
                self.process_command(command)
            except:
                self.stop_flag.set()

    def process_command(self, command):
        ''' Process given client command '''
        if isinstance(command, str):
            if command == 'CLOSE_CONNECTION':
                self.stop_flag.set()
            elif command == 'DEVICES_STATUS?':
                return self.write(get_devices_status())
        else:
            if command['command'] == 'get_device_model':
                device_name = command['device_name']
                structure = get_device(device_name).get_structure()
                self.write(structure)
            elif command['command'] == 'request':
                get_device(device_name).get_by_adress(command['element_adress'])
                # element_address --> my_yenista::submodule::wavelength
                wavelength()

#command_dict = {'command':'get_driver_model','name':self.name}

    def close(self):

        # In case the close call come from outside of the threading
        self.socket.close()

        # If this thread is the main client thread, remove declaration
        if self.server.active_connection_thread == self:
            self.server.log(f'Host "{self.hostname}" disconnected')
            self.server.active_connection_thread = None

    def request_close(self):

        self.stop_flag.set()
        self.socket.shutdown(socket.SHUT_RDWR)
        self.join()


class Server():

    def __init__(self, port=None):

        self.client_threads = []
        self.active_connection_thread = None

        # Load server config in autolab_config.ini
        server_config = get_server_config()
        if not port: port = int(server_config['port'])
        self.port = port

        # Start the server
        self.start()

        # Start listening
        try: self.listen()
        except: print('You excited the server (TO CHANGE)')
        self.close()


    def start(self):
        ''' Start the server '''
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.main_socket.bind(('', self.port))
        self.main_socket.listen(0)
        self.log(f'Autolab server running, waiting for incoming connections on port {self.port}')


    def listen(self):

        while True:

            # Wait incoming connection
            client_socket, _ = self.main_socket.accept()

            # Clean terminated threads
            self.clean_client_threads()

            # Start new client thread
            client_thread = ClientThread(client_socket, self)
            client_thread.start()
            self.client_threads.append(client_thread)


    def clean_client_threads(self):
        ''' Remove finshed client threads from the list '''
        self.client_threads = [t for t in self.client_threads if t.is_alive()]

    def close_client_threads(self):
        ''' Close any existing client thread '''
        self.clean_client_threads()

        for thread in self.client_threads:
            thread.request_close()

        self.client_threads = []


    def log(self, log):
        ''' Display a log on the server '''
        timestamp = dt.datetime.now().isoformat()
        print(f'{timestamp}: {log}')


    def close(self):
        ''' Close the server and client threads'''
        self.close_client_threads()
        self.main_socket.shutdown(socket.SHUT_RDWR)
        self.main_socket.close()


class Driver_REMOTE(Driver_SOCKET):

    def __init__(self, address='192.168.1.1', port=4001):
        from functools import partial

        self.address = address
        self.port = int(port)

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
        self.socket.settimeout(None)


    def handshake(self):
        ''' Check that distant partner is an Autolab server '''
        self.write(f'AUTOLAB?HOSTNAME={socket.gethostname()}')
        try:
            answer = self.read()
            assert answer == 'YES', answer
        except Exception as e:
            raise ValueError(f'Impossible to join autolab server at {self.address}:{self.port} \n {e}')

    def disconnect(self):
        ''' Close autolab server connection '''
        self.socket.write('CLOSE_CONNECTION')
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def get_devices_status(self): # Déjà instantié ou non
        self.write('DEVICES_STATUS?')
        return self.read()

    def get_driver_model(self):
        model = []
        for dev_name in self.devices_status.keys():
            a = FakeDriver(self, dev_name, status)
            model.append({'element': 'module', 'name': dev_name, 'object': a})
            a.get_driver_model()
            partial(devices.Device, dev_name)
        return model

    def get_device(self, dev_name):
        pass

    def get_device_structure(self):
        pass
            # Pour un device de slave donné, retourne sa structure de (sous-devices, modules, action variable) à l’instant t
            # Device non instantité : ne renvoie rien
            # Device instantié : renvoie structure en (modules, action, variable)


class FakeDriver():

    def __init__(self, driver_remote, name, status):

        self.driver_remote = driver_remote
        self.name = name
        self.status = status

    def get_driver_model(self):
        model = []
        if status is False:
            return model
        else:
            command_dict = {'command': 'get_device_structure', 'name': self.name}
            remote_device_structure = self.driver_remote.write(command_dict)

            for key in remote_device_structure.keys():
                if remote_device_structure[key] == 'variable':
                    arg = {'command': 'request', address: 'yenista::wavelength'}
                    #model.append({'element':remote_device_structure[key], 'name':key, 'read': partial(self.interact,'read',address) .., 'write'})
                elif remote_device_structure[key] == 'action':
                    pass
                elif remote_device_structure[key] == 'module':
                    pass

            return remote_driver_model

    def interact(interaction_type, address):
        pass


#{'slot1': {'power': 'variable', 'wavelength': 'variable'},
# 'amplitude': 'variable',
# 'something': 'action'}

#def get_driver_model(self):

 #    model = []
#    model.append({'element':'variable','name':'amplitude','write':self.amplitude,'read':self.get_amplitude,'unit':'V','type':float,'help':'Amplitude'})
#    model.append({'element':'variable','name':'offset','write':self.offset,'read':self.get_offset,'unit':'V','type':float,'help':'Offset'})
#    model.append({'element':'variable','name':'frequency','write':self.frequency,'read':self.get_frequency,'unit':'Hz','type':float,'help':'Frequency'})

#    return model
