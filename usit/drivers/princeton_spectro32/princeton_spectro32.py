#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import sys,os
import time
from numpy import savetxt


class Device():
    def __init__(self,camera='Camera1'):
        self.camera = camera
        
    def set_camera(self,camera):
        self.write(f'CONNECT={camera}')
        self.camera = camera
    def set_nb_frames(self,nb_frames):
        self.write(f'NBFRAMES={nb_frames}')
    def set_exposure(self,exposure):
        self.write(f'EXPTIME={exposure}')
        
    def get_data(self):
        self.data = eval(self.query('DATA?'))
    def get_exposure(self):
        return float(self.query('EXPTIME?'))
    def get_nb_frames(self):
        self.write('NBFRAMES?')
    def list_cameras(self):
        return self.query('LISTCAMS?')
    
    def auto_exposure(self):
        self.write('AUTOEXP')
    def save_data_remote(self):
        self.write('SAVEDATA')
    def save_data(self,filename,FORCE=False):
        temp_filename = f'{filename}_spectro32{self.camera}.txt'
        if os.path.exists(os.path.join(os.getcwd(),temp_filename)) and not(FORCE):
            print('\nFile ', temp_filename, ' already exists, change filename or remove old file\n')
            return
        self.lambd=[list(range(len(self.data[0])))]
        assert self.lambd, 'You may want to get_data before saving ...'
        [self.lambd.append(self.data[i]) for i in range(len(self.data))]
        f = savetxt(temp_filename,self.lambd)  ## squeeze
        print('Spectro32 data saved')


#################################################################################
############################## Connections classes ##############################
class Device_SOCKET(Device):
    def __init__(self,address='192.168.0.2',camera='Camera1',**kwargs):
        import socket 
        
        self.PORT        = 5005
        self.BUFFER_SIZE = 10000
        
        self.controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controller.connect((address,self.PORT))
        
        Device.__init__(self,camera)
        
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

class Device_LOCAL(Device):
    def __init__(self,camera='Camera1',**kwargs):

        from spectro32_utilities.spectro32_driver import Device_driver
        self.controller = Device_driver()

        Device.__init__(self,camera)
              
    def write(self,command):
        self.controller.command(command)
    def query(self,command):
        return self.controller.command(command)
    def close(self):
        self.controller = None
############################## Connections classes ##############################
#################################################################################



if __name__=='__main__':
    
    from optparse import OptionParser
    import inspect
    
    usage = """usage: %prog [options] arg

               EXAMPLES:
                  
               

               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="command", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="query", default=None, help="Set the query to use." )
    parser.add_option("-i", "--address", type="string", dest="address", default='192.168.0.2', help="Set the remote computer address to use for communicating with the camera" )
    parser.add_option("-n", "--nb_frames", type="int", dest="nb_frames", default=1, help="Set the number of frames" )
    parser.add_option("-e", "--exposure", type="float", dest="exposure", default=0.01, help="Set the time of exposure" )
    parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
    parser.add_option("-a", "--auto_exposure", action = "store_true", dest="auto_exposure", default=False, help="turn on auto exposition mode" )
    parser.add_option("-F", "--force",action = "store_true", dest="force", default=False, help="Allows overwriting file" )
    parser.add_option("-l", "--link", type="string", dest="link", default='SOCKET', help="Set the connection type." )
    parser.add_option("-p", "--camera", type="string", dest="camera", default='Camera1', help="Set the camera to get the data from." )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    classes = [name for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass) if obj.__module__ is __name__]
    assert 'Device_'+options.link in classes , "Not in " + str([a for a in classes if a.startwith('Device_')])
    Device_LINK = getattr(sys.modules[__name__],'Device_'+options.link)
    I = Device_LINK(address=options.address,camera=options.camera)
    
    if options.query:
        print('\nAnswer to query:',options.query)
        rep = I.query(options.query)
        print(rep,'\n')
    elif options.command:
        print('\nExecuting command',options.command)
        I.write(options.command)
        print('\n')
    
    if options.exposure:
        I.set_exposure(options.exposure)
    if options.nb_frames:
        I.set_nb_frames(options.nb_frames)
    if options.auto_exposure:
        I.auto_exposure()
    if options.filename:
        I.get_data()
        I.save_data(options.filename,FORCE=options.force)
        
    I.close()
    sys.exit()
