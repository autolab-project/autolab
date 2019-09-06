#!/usr/bin/env python3

from optparse import OptionParser
import sys,os
import time
from numpy import fromstring,int8,int16,float64,sign,savetxt
import connector

CAMERA  = 'Camera1'
ADDRESS = '192.168.0.2'


class Device(connector.Spectro32ConnectorRemote):
    def __init__(self,address=ADDRESS):
        
        ### Start the communication using socket ###
        connector.Spectro32ConnectorRemote.__init__(self,address)
        
    def set_camera(self,camera=CAMERA):
        self.write('CONNECT='+camera)
    def set_nb_frames(self,nb_frames):
        self.write('NBFRAMES='+str(nb_frames))
    def set_exposure(self,exposure):
        self.write('EXPTIME='+str(exposure))
        
    def get_data(self):
        self.data = eval(self.query('DATA?'))
    def get_exposure(self):
        return self.query('EXPTIME?')
    def get_nb_frames(self):
        self.write('NBFRAMES?')
    def list_cameras(self):
        return self.query('LISTCAMS?'+camera)
    
    def auto_exposure(self):
        self.write('AUTOEXP')
    def save_data_remote(self):
        self.write('SAVEDATA')
    def save_data(self,filename,FORCE=False,camera=CAMERA):
        # Verify file doesn't already exist
        temp_filename = filename + '_spectro32' + camera + '.txt'
        temp = os.listdir()
        for i in range(len(temp)):
           if temp[i] == temp_filename and not(FORCE):
               print('\nFile ', temp_filename, ' already exists, use -F option, change filename or remove old file\n')
               sys.exit()
        self.lambd=[list(range(len(self.data[0])))]
        assert self.lambd, 'You may want to get_data before saving ...'
        [self.lambd.append(self.data[i]) for i in range(len(self.data))]
        f = savetxt(temp_filename,self.lambd)  ## squeeze
        print('Spectro32 data saved')
    
    

class Device_fully_local():
    def __init__(self,camera=CAMERA):
        import pvcam_Manis
        
        self.pvcam = pvcam_Manis.Init_PVCam()
        
		### Initiate communication with the requested camera ###
        print('Trying to get: %s' %camera)
        self.CAM = self.get_camera(camera=camera)


    def get_data(self, nb_frames=1, exposure=None, region=None, binning=None):
        data = self.CAM.acq(frames=nb_frames, exposure=exposure, region=region, binning=binning)
        self.data = eval([list(data[i].squeeze()) for i in range(len(data))])
        #return data2

    def save_data(self,filename,camera=CAMERA,FORCE=False):
        # Verify file doesn't already exist
        temp_filename = filename + '_spectro32' + camera + '.txt'
        temp = os.listdir()
        for i in range(len(temp)):
           if temp[i] == temp_filename and not(FORCE):
               print('\nFile ', temp_filename, ' already exists, use -F option, change filename or remove old file\n')
               sys.exit()
        self.lambd=[list(range(len(self.data[0])))]
        assert self.lambd, 'You may want to get_data before saving ...'
        [self.lambd.append(self.data[i]) for i in range(len(self.data))]
        f = savetxt(temp_filename,self.lambd)  ## squeeze
        print(camera + ' saved')

    def get_camera(self,camera='Camera1'):
        CAM = self.pvcam.PVCam.getCamera(camera)
        print('Got: %s' %camera)
        return CAM

    def list_cameras(self):
        return self.pvcam.listCameras()
    
    def close(self):
        pass


if __name__=='__main__':

    usage = """usage: %prog [options] arg

               EXAMPLES:
                  
               

               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="command", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="query", default=None, help="Set the query to use." )
    parser.add_option("-i", "--address", type="string", dest="address", default=ADDRESS, help="Set the address to use for the communication" )
    parser.add_option("-n", "--nb_frames", type="int", dest="nb_frames", default=1, help="Set the number of frames" )
    parser.add_option("-e", "--exposure", type="float", dest="exposure", default=0.01, help="Set the time of exposure" )
    parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
    parser.add_option("-a", "--auto_exposure", action = "store_true", dest="auto_exposure", default=False, help="turn on auto exposition mode" )
    parser.add_option("-F", "--force",action = "store_true", dest="force", default=False, help="Allows overwriting file" )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    I = Device(address=options.address)
    
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
