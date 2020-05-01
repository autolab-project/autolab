# -*- coding: utf-8 -*-
class Server():

    def __init(self)



class Driver_REMOTE():
    def __init__(self,address=’192.168.1.1’,port=5000):
        import socket
        from functools import partial

        # Connection au PC slave
        self.controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Retourne la liste des devices
        self.devices_list = self.get_devices_list()

    def get_devices_list(self) : # Déjà instantié ou non
        pass

    def get_driver_model(self):
        model = {}
        for dev_name in self.devices_list :
                model['element':'device', 'name':dev_name, 'instance': partial(self.get_device,dev_name)]
        return model

    def get_device(self,dev_name):
        pass

    def get_device_structure(self):
            # Pour un device de slave donné, retourne sa structure de (sous-devices, modules, action variable) à l’instant t
            # Device non instantité : ne renvoie rien
            # Device instantié : renvoie structure en (modules, action, variable)
    IL FAUDRA IMPLEMENTER CA DANS OBJET DEVICE (fonction qui retourne sa structure)


    def send_command(self,element_address,value=None):
        # Send the command to the autolab_slave server instance and return the answer.
        command = {'element_address':element_address,'value':None}
        msg = picke.dumps(command}
        socket.send(msg)
        ans = socket.read()
        return pickle.loads(ans)

    def send...(self):
        pass
    def fake_function(self):
        pass



######################################################################################
######################################################################################
#!/usr/bin/env python3

import sys
import socket
import threading

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
LISTENING_PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

class Driver_DLL():
    def __init__(self):
        setattr(self,'module',Module_TEST())
        pass

    def set_fonc(self,val):
        self.b = val

    def set_fonc_with_return(self,val):
        self.b = val
        return self.b

    def get_fonc(self):
        self.b = 'work?'
        return self.a

class Module_TEST():
    def __init__(self):
        self.module_a = 2
    def module_function(self,b):
        self.module_b = b
        return self.module_b



class Server(Driver_DLL):

    def list_devices(self):
        # build the list of attributes
        return  autolab.list_devices()
    def list_callable(self):
        list_attr = self.list_attr()
        return [name for name in list_attr if callable(getattr(self,name))]
    def list_callable_with_args(self):
        list_callable = self.list_callable()
        return [name for name in list_callable if getattr(self,name).__code__.co_argcount > 1]

    def interpreter(self,command):
        command = yaml.load(command, Loader=yaml.FullLoader)
        if isinstance(command,dict):
            if command['name'] in ['list_attr','list_callable','list_callable_with_args']:
                attr = getattr(self,command['name'])
                called = attr()
                if 'value' in command.keys():
                    setattr(self,command['name'],called)
                command['value'] = called
                return command

            elif command['name'] in self.list_callable():
                attr = getattr(self,command['name'])
                if 'value' in command.keys():
                    command['value'] = attr(command['value'])
                else:
                    command['value'] = attr()
                return command
            elif command['name'] in self.list_attr():
                if 'value' in command.keys():
                    setattr(self,command['name'],command['value'])
                temp = getattr(self,command['name'])
                command['value'] = temp
                return command
        else:
            # first called to lists
            if command in self.list_callable_with_args():
                pass
            if command in self.list_callable():
                attr = getattr(self,f'{command}')
                return attr()
            if command in self.list_attr():
                attr = getattr(self,f'{command}')
                return attr

    def __init__(self):

        self.a = 1

        Driver_DLL.__init__(self)

        ### Start the server ###
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, LISTENING_PORT))
        self.socket.listen(1)

        self.thread = None
        while True :
            try:
                conn, addr = self.socket.accept()
                if self.thread is not None :
                    self.thread.stopFlag.set()
                self.thread = ClientThread(conn,self)
                self.thread.start()
                print('Incoming connection from '+str(addr))
            except KeyboardInterrupt:
                try: self.thread.join()
                except: pass
                self.socket.close()
                print(" You cancelled the program!")
                sys.exit(1)


class ClientThread(threading.Thread):
    def __init__(self, clientsocket,Instance):
        self.end_char = '\n'

        self.Instance = Instance

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
            print('\nReceived (server):',command)

            data = self.Instance.interpreter(command)
            print('####Sent (server):', data)

            self.clientsocket.sendall((str(data)+self.end_char).encode('utf-8'))

            #if isinstance(answer,str) and len(answer) > 50 :
                #log('Sent: '+answer[:50]+'...')
            #elif not(answer):
                #log('Sent: '+str(answer))
            #else :
                #log('Sent: '+str(answer)[:50]+' ...')

        self.clientsocket.close()


server = Server()
