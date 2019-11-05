#!/usr/bin/python  
# -*- coding: utf-8 -*-

"""Loot at 2D dynamic or static data"""
from matplotlib.pyplot import axes, plot, figure, draw, show, rcParams
from matplotlib.widgets import Slider, Cursor
from numpy import array, roll, arange, sin, concatenate,\
        fromfile, int8, reshape, memmap, zeros, fromstring,copy,roll
from tempfile import TemporaryFile
from numpy.random import randn
import time
import sys
import commands as C
import matplotlib as mpl
from optparse import OptionParser
import vxi11 as vxi
import gobject
from matplotlib.font_manager import FontProperties

mpl.style.use('classic')
mpl.pyplot.switch_backend('GTkAgg')

class Scope(object):
    def __init__(self, chan, host, fold=19277, nmax=100,NORM=True,sequence=False,encoding='BYTE'):
        self.UPDATE = True
        self.color  = True
        self.CMAP   = ['jet','seismic','Greys','plasma']
        self.COLORS = ['b','g','r']
        
        self.channel   = chan
        self.t         = time.time()
        self.NORM      = NORM
        self.shear     = 0.
        self.sequence  = sequence
        self.vmin      = -125
        self.vmax      = 125
        self.HORIZ_VAL = 0.05
        self.fold      = fold
        self.NMAX      = nmax
        
        ### To set the first name that has to be recorded ###
        try:
            L = C.getoutput('ls Image_*_DSA'+self.channel[0]+' | sort -n').splitlines()
            temp = array([eval(L[i].split('_')[1]) for i in range(len(L))])
            self.flag_save = max(temp) + 1
        except:                      # nothing in the folder already
            self.flag_save = 1
        
        for i in range(len(self.channel)):
            exec("self.remove_len1%d = 0" %i)
            exec("self.remove_len2%d = 1" %i)
        
        ### Establish the communication with the scope ###
        try:
            self.sock = vxi.Instrument(host)
            self.sock.write('CFMT DEF9,'+encoding+',BIN')
            self.sock.write('CHDR SHORT')
            
        except:
            print "\nWrong IP, Listening port or bad connection =>  Check cables first\n"
            sys.exit()
        
        ### Verify all channell provided are active ###
        for i in range(len(self.channel)):
            temp = self.query(self.channel[i]+':TRA?')
            if temp.find('ON') == -1:
                print '\nWARNING:  Channel',self.channel[i], 'is not active  ===>  exiting....\n'
                sys.exit()
        
        ##################################################################
        ################## Start creating the figure #####################
        self.fig = figure(figsize=(16,7))
        
        ### trigger the scope for the first time ###
        self.single()
        self.load_data()
        if not(self.NMAX):
            self.NMAX = int(len(self.data0)/self.fold)
        self.update_tabs()
        self.Y0 = 0
        
        if len(self.channel)==1:
            self.declare_axis_1channel()
        elif len(self.channel)==2:
            self.declare_axis_2channel()
        elif len(self.channel)==3:
            self.declare_axis_3channel()
            
        for i in range(len(self.channel)):
            if not self.NORM:
                exec("self.im%d = self.ax%d.imshow(self.folded_data%d, interpolation='nearest', aspect='auto',origin='lower', vmin=self.vmin, vmax=self.vmax)" %(i,i,i))
            else:
                exec("self.im%d = self.ax%d.imshow(self.folded_data%d, interpolation='nearest', aspect='auto',origin='lower', vmin=self.folded_data%d.min(), vmax=self.folded_data%d.max())" %(i,i,i,i,i))

        for i in range(len(self.channel)):
            exec("self.cursor%d = Cursor(self.ax%d, useblit=True, color='red', linewidth=2)" %(i,i))
        
        self.axhh = axes([0.02,0.25,0.12,0.62])
        for i in range(len(self.channel)):
            exec("self.hline%d, = self.axh%d.plot(self.folded_data%d[self.Y0,:])" %(i,i,i))
            exec("self.axh%d.set_xlim(0,len(self.folded_data%d[0,:]))" %(i,i))
            exec("self.hhline%d, = self.axhh.plot(self.folded_data%d.mean(1),arange(self.NMAX),self.COLORS[i])" %(i,i))
        self.axhh.set_ylim(0,self.NMAX-1)
        if not self.NORM:
            for i in range(len(self.channel)):
                exec("self.axh%d.set_ylim(self.vmin, self.vmax)" %i)
            self.axhh.set_xlim(self.vmin, self.vmax)
        else:
            for i in range(len(self.channel)):
                 exec("self.axh%d.set_ylim(self.folded_data%d.min(), self.folded_data%d.max())" %(i,i,i))
            if len(self.channel)==1:
                LIM_MIN = self.folded_data0.mean(1).min()
                LIM_MAX = self.folded_data0.mean(1).max()
            elif len(self.channel)==2:
                LIM_MIN = min(self.folded_data0.mean(1).min(),self.folded_data1.mean(1).min())
                LIM_MAX = max(self.folded_data0.mean(1).max(),self.folded_data1.mean(1).max())
            elif len(self.channel)==3:
                LIM_MIN = min(self.folded_data0.mean(1).min(),self.folded_data1.mean(1).min(),self.folded_data2.mean(1).min())
                LIM_MAX = max(self.folded_data0.mean(1).max(),self.folded_data1.mean(1).max(),self.folded_data2.mean(1).max())
            self.axhh.set_xlim(LIM_MIN-1,LIM_MAX+1)
        
        # create 'remove_len1' slider
        for i in range(len(self.channel)):
            exec("self.remove_len1%d_slider   = Slider(self.remove_len1%d_sliderax,'beg',0.,self.fold,self.remove_len1%d,'%s')" %(i,i,i,'%d'))
            exec("self.remove_len1%d_slider.on_changed(self.update_tab)" %i)
        
        # create 'remove_len2' slider
        for i in range(len(self.channel)):
            exec("self.remove_len2%d_slider   = Slider(self.remove_len2%d_sliderax,'end',1.,self.fold,self.remove_len2%d,'%s')" %(i,i,i,'%d'))
            exec("self.remove_len2%d_slider.on_changed(self.update_tab)" %i)
        
        # create 'shear' slider
        self.shear_sliderax = axes([0.175,0.96,0.775,0.02])
        self.shear_slider   = Slider(self.shear_sliderax,'Shear',-0.5,0.5,self.shear,'%1.2f')
        self.shear_slider.on_changed(self.update_shear)
        
        #if self.sequence:
        VERT_VAL = -6
        font0 = FontProperties()
        font1 = font0.copy()
        font1.set_weight('bold')
        
        mpl.pyplot.text(-0.71,7+VERT_VAL,'Sequence mode:',fontsize=18,fontproperties=font1)
        mpl.pyplot.text(-0.71,3+VERT_VAL,'"b" to toggle it then:\n      "y" to save\n      "n" to next',fontsize=18)
        mpl.pyplot.text(-0.71,-32+VERT_VAL,'Useful keys:',fontsize=18,fontproperties=font1)
        mpl.pyplot.text(-0.71,-40+VERT_VAL,'"c" to change colormap\n "v" to change vertical\n      /colorscale\n " " to pause\n "S" to save trace\n       and picture\n "q" to exit',fontsize=18)
        #mpl.pyplot.text(-0.5,-27+VERT_VAL,'Sequence mode:',fontsize=18,fontproperties=font1)
        #mpl.pyplot.text(-0.37,-29.5+VERT_VAL,'"b" to toggle it then:\n      "y" to save\n      "n" to next',fontsize=18)
        #mpl.pyplot.text(0.15,-27+VERT_VAL,'Useful keys:',fontsize=18,fontproperties=font1)
        #mpl.pyplot.text(0.25,-31.5+VERT_VAL,'"c" to change colormap\n "v" to change vertical/colorscale\n " " to pause\n "S" to save trace and picture\n "q" to exit',fontsize=18)
        
        cid  = self.fig.canvas.mpl_connect('motion_notify_event', self.mousemove)
        cid2 = self.fig.canvas.mpl_connect('key_press_event', self.keypress)

        self.axe_toggledisplay  = self.fig.add_axes([0.,0.,1.0,0.02])
        self.plot_circle(0,0,2,fc='#00FF7F')
        mpl.pyplot.axis('off')
        
        gobject.idle_add(self.update_plot)
        show()
    
    ### BEGIN main loop ###
    def update_plot(self):
        while self.UPDATE: 
            self.t = time.time()
            if len(self.data0)<self.NMAX*self.fold:
                print '\nNumber of point asked for the plot must not exceed the length of datas got from the scope \n\nExiting...\n'
                sys.exit()
            
            ### Compute the array to plot ###
            self.load_data()
            if not self.sequence:
                self.single()
            self.update_tabs()
            print '\nDATA ARE LEN:', len(self.data0)
            print 'data loaded, update plot:',time.time()-self.t
            self.t = time.time()
            
            ### Update picture ###
            for i in range(len(self.channel)):
                exec("self.im%d.set_data(self.folded_data%d)" %(i,i))
                exec("self.hline%d.set_ydata(self.folded_data%d[self.Y0,:])" %(i,i))
                exec("self.hhline%d.set_xdata(self.folded_data%d.mean(1))" %(i,i))
            
            self.fig.canvas.draw()
            print 'plot updated:',time.time()-self.t
            
            if self.sequence:
                self.toggle_update()
            return True
        return False
    ### END main loop ###

    def process_data(self,val,i):
        """ Redress data in the space/time diagram """
        exec("dd = self.folded_data%d.copy()" %i)
        for k in range(0,dd.shape[0]):
            exec("dd[k,:] = roll(self.folded_data%d[k,:], int(k*val))" %i)
        exec("self.folded_data%d = dd" %i)
    
    def is_scope_stopped(self):
        ### Verify that the scope has triggered ###
        val = 0.05
        while self.query('TRMD?') != "TRMD STOP\n":
            print self.query('TRMD?')
            print 'Waiting for triggering:',val
            val = val+0.05
            time.sleep(val)

    def load_data(self):
        self.is_scope_stopped()
        for i in range(len(self.channel)):
            self.sock.write(self.channel[i]+':WF? DAT1')
            data = self.sock.read_raw()
            self.bin_data = data[data.find('#')+11:-1]
            exec("self.data%d = fromstring(self.bin_data, dtype=int8)" %i)

    #def load_data(self):
        #self.is_scope_stopped()
        #for i in range(len(self.channel)):
            #self.sock.write(':WAVEFORM:SOURCE ' + self.channel[i])
            #self.sock.write(':WAV:DATA?')
            #self.bin_data = self.sock.read_raw()[10:]
            #exec("self.data%d = fromstring(self.bin_data, dtype=int8)" %i)
        
    def update_tabs(self):
        for i in range(len(self.channel)):
            exec("self.folded_data%d = self.data%d[:self.NMAX*self.fold].reshape(self.NMAX,self.fold)" %(i,i))
            exec("self.process_data(self.shear,%d)" %i)
            exec("self.folded_data%d = self.folded_data%d[:,self.remove_len1%d:-self.remove_len2%d]" %(i,i,i,i))  

    def norm_fig(self):
        if len(self.channel)==1:
            LIM_MIN = self.folded_data0.mean(1).min()
            LIM_MAX = self.folded_data0.mean(1).max()
        elif len(self.channel)==2:
            LIM_MIN = min(self.folded_data0.mean(1).min(),self.folded_data1.mean(1).min())
            LIM_MAX = max(self.folded_data0.mean(1).max(),self.folded_data1.mean(1).max())
        elif len(self.channel)==3:
            LIM_MIN = min(self.folded_data0.mean(1).min(),self.folded_data1.mean(1).min(),self.folded_data2.mean(1).min())
            LIM_MAX = max(self.folded_data0.mean(1).max(),self.folded_data1.mean(1).max(),self.folded_data2.mean(1).max())
        self.axhh.clear()
        if not self.NORM:
            for i in range(len(self.channel)):
                exec("self.ax%d.clear()" %i)
                exec("self.im%d = self.ax%d.imshow(self.folded_data%d,cmap=self.CMAP[0], interpolation='nearest', aspect='auto',origin='lower', vmin=self.vmin, vmax=self.vmax)" %(i,i,i))
                exec("self.axh%d.clear()" %i)
                exec("self.hline%d, = self.axh%d.plot(self.folded_data%d[self.Y0,:])" %(i,i,i))
                exec("self.axh%d.set_ylim(self.vmin, self.vmax)" %i)
                exec("self.axh%d.set_xlim(0, len(self.folded_data%d[0]))" %(i,i))
                exec("self.hhline%d, = self.axhh.plot(self.folded_data%d.mean(1),arange(self.NMAX),self.COLORS[i])" %(i,i))
            self.axhh.set_ylim(0,self.NMAX-1)
            self.axhh.set_xlim(self.vmin, self.vmax)
        else:
            for i in range(len(self.channel)):
                exec("self.ax%d.clear()" %i)
                exec("self.im%d = self.ax%d.imshow(self.folded_data%d,cmap=self.CMAP[0], interpolation='nearest', aspect='auto',origin='lower', vmin=self.folded_data%d.min(), vmax=self.folded_data%d.max())" %(i,i,i,i,i))
                exec("self.axh%d.clear()" %i)
                exec("self.hline%d, = self.axh%d.plot(self.folded_data%d[self.Y0,:])" %(i,i,i))
                exec("self.axh%d.set_ylim(self.folded_data%d.min(), self.folded_data%d.max())" %(i,i,i))
                exec("self.axh%d.set_xlim(0, len(self.folded_data%d[0]))" %(i,i))
                exec("self.hhline%d, = self.axhh.plot(self.folded_data%d.mean(1),arange(self.NMAX),self.COLORS[i])" %(i,i))
            self.axhh.set_ylim(0,self.NMAX-1)
            self.axhh.set_xlim(LIM_MIN-1,LIM_MAX+1)
        self.fig.canvas.draw()
        
    def update_cut(self):
        for i in range(len(self.channel)):
            exec("self.hline%d.set_ydata(self.folded_data%d[self.Y0,:])" %(i,i))
        self.fig.canvas.draw()
        
    ### BEGIN Slider actions ###
    def update_shear(self,val):
        self.shear = round(self.shear_slider.val,2)
        self.update_tabs()
        self.norm_fig()
        self.fig.canvas.draw()
        
    def update_tab(self,val):
        for i in range(len(self.channel)):
            exec("self.remove_len1%d = int(self.remove_len1%d_slider.val)" %(i,i))
            exec("self.remove_len2%d = int(self.remove_len2%d_slider.val)" %(i,i))
        self.Y0 = 0
        self.update_tabs()
        self.norm_fig()
        self.fig.canvas.draw()
    ### END Slider actions ###
        
    def toggle_update(self):
            self.UPDATE = not(self.UPDATE)
            if self.UPDATE:
                self.single()
                self.is_scope_stopped()
                gobject.idle_add(self.update_plot)
            else:
                self.stop()
            self.color  = not(self.color)
            if not(self.color):
                self.patch.remove()
                self.axe_toggledisplay  = self.fig.add_axes([0.,0.,1.0,0.02])
                self.axe_toggledisplay.clear()
                self.plot_circle(0,0,2,fc='#FF4500')
                mpl.pyplot.axis('off')
                self.fig.canvas.draw()
            else:
                self.patch.remove()
                self.axe_toggledisplay  = self.fig.add_axes([0.,0.,1.0,0.02])
                self.axe_toggledisplay.clear()
                self.plot_circle(0,0,2,fc='#00FF7F')
                mpl.pyplot.axis('off')
                self.fig.canvas.draw()
        
    def Save(self):
        if self.UPDATE: self.toggle_update()
        ### Verify that the scope is stopped ###
        self.is_scope_stopped()
        ### Verify that the figure is plotted ###
        self.fig.canvas.draw()
        
        l = []
        ### Iddentify all active channels ###
        for i in [1,2,3,4]:
            if self.query(':CHAN'+str(i)+':DISP?')=='1\n':
                l.append(i)
        ### Save all active channels ###
        for i in l:
            filename = 'Image_'+str(self.flag_save)+'_DSACHAN'+str(i)
            self.sock.write(':WAVEFORM:SOURCE CHAN' + str(i))
            self.sock.write(':WAV:DATA?')
            data = self.sock.read_raw()[10:]
            print 'Saving to files ', filename
            ff = open(filename,'w')
            ff.write(data)
            ff.close()
            self.sock.write(':WAVEFORM:PREAMBLE?')
            self.preamble = self.sock.read()
            f = open(filename+'_log','w')
            f.write(self.preamble)
            f.close()
        temp = ''
        temp = temp.join([i for i in self.channel])
        filename = 'Image_'+str(self.flag_save)+'_DSA'+temp
        self.fig.savefig(filename+'.png')
        self.flag_save = self.flag_save + 1   
        if not(self.UPDATE):self.toggle_update()
    
    ### BEGIN actions to the window ###
    def keypress(self, event):
        if event.key == 'q': # eXit
            del event
            self.run()
            sys.exit()
        elif event.key == 'b': # switch sequence mode on/off
            self.sequence = not(self.sequence)
            self.toggle_update()
            time.sleep(0.15)
            del event
        elif event.key == 'y':
            if self.sequence:
                self.fig.canvas.draw()
                self.UPDATE = False
                self.Save()
                time.sleep(0.15)
            del event
        elif event.key == 'n':
            if self.sequence:
                self.fig.canvas.draw()
                self.toggle_update()
                time.sleep(0.15)
            del event
        elif event.key=='v':
            del event
            self.NORM = not(self.NORM)
            self.norm_fig()
        elif event.key=='c':
            del event
            self.CMAP = roll(self.CMAP,-1)
            self.norm_fig()
            self.fig.canvas.draw()
        elif event.key == ' ': # play/pause
            if not self.sequence:
                self.load_data()
                self.update_tabs()
                self.norm_fig()
                self.toggle_update()
            del event
        elif event.key == 'S':
            if not self.sequence:
                self.load_data()
                self.update_tabs()
                self.norm_fig()
                self.Save()
            del event
        else:
            print 'Key '+str(event.key)+' not known'
            
    def mousemove(self, event):
        # called on each mouse motion to get mouse position
        if len(self.channel)==1:
            if event.inaxes!=self.ax0: return
        elif len(self.channel)==2:
            if event.inaxes!=self.ax0 and event.inaxes!=self.ax1: return
        elif len(self.channel)==3:
            if event.inaxes!=self.ax0 and event.inaxes!=self.ax1 and event.inaxes!=self.ax2: return
        self.X0 = int(round(event.xdata,0))
        self.Y0 = int(round(event.ydata,0))
        self.update_cut()
    ### END actions to the window ###
    
    def declare_axis_1channel(self):
        self.ax0                   = axes([0.125+self.HORIZ_VAL,0.25,0.81,0.62])
        self.axh0                  = axes([0.125+self.HORIZ_VAL,0.05,0.81,0.15])
        self.remove_len10_sliderax = axes([0.125+self.HORIZ_VAL,0.91,0.78,0.02])
        self.remove_len20_sliderax = axes([0.125+self.HORIZ_VAL,0.88,0.78,0.02])
    def declare_axis_2channel(self):
        self.ax0                   = axes([0.125+self.HORIZ_VAL,0.25,0.395,0.62])
        self.ax1                   = axes([0.54+self.HORIZ_VAL,0.25,0.395,0.62])
        self.axh0                  = axes([0.125+self.HORIZ_VAL,0.05,0.395,0.15])
        self.axh1                  = axes([0.54+self.HORIZ_VAL,0.05,0.395,0.15])
        self.remove_len10_sliderax = axes([0.125+self.HORIZ_VAL,0.91,0.37,0.02])
        self.remove_len11_sliderax = axes([0.54+self.HORIZ_VAL,0.91,0.37,0.02])
        self.remove_len20_sliderax = axes([0.125+self.HORIZ_VAL,0.88,0.37,0.02])
        self.remove_len21_sliderax = axes([0.54+self.HORIZ_VAL,0.88,0.37,0.02])
    def declare_axis_3channel(self):
        self.ax0                   = axes([0.125+self.HORIZ_VAL,0.25,0.25,0.62])
        self.ax1                   = axes([0.405+self.HORIZ_VAL,0.25,0.25,0.62])
        self.ax2                   = axes([0.685+self.HORIZ_VAL,0.25,0.25,0.62])
        self.axh0                  = axes([0.125+self.HORIZ_VAL,0.05,0.25,0.15])
        self.axh1                  = axes([0.405+self.HORIZ_VAL,0.05,0.25,0.15])
        self.axh2                  = axes([0.685+self.HORIZ_VAL,0.05,0.25,0.15])
        self.remove_len10_sliderax = axes([0.125+self.HORIZ_VAL,0.91,0.25,0.02])
        self.remove_len11_sliderax = axes([0.405+self.HORIZ_VAL,0.91,0.25,0.02])
        self.remove_len12_sliderax = axes([0.685+self.HORIZ_VAL,0.91,0.25,0.02])
        self.remove_len20_sliderax = axes([0.125+self.HORIZ_VAL,0.88,0.25,0.02])
        self.remove_len21_sliderax = axes([0.405+self.HORIZ_VAL,0.88,0.25,0.02])
        self.remove_len22_sliderax = axes([0.685+self.HORIZ_VAL,0.88,0.25,0.02])
        
    def plot_circle(self,x,y,r,fc='r'):
        """Plot a circle of radius r at position x,y"""
        cir = mpl.patches.Circle((x,y), radius=r, fc=fc)
        self.patch = mpl.pyplot.gca().add_patch(cir)


    def query(self,com):
        self.sock.write(com)
        return self.sock.read_raw()
    
    def stop(self):
        self.sock.write("TRMD STOP")
    def single(self):
        self.sock.write("TRMD SINGLE")
    def run(self):
        self.sock.write("TRMD AUTO")
            
if __name__=='__main__':

    IP = '169.254.77.34'
    
    usage = """usage: %prog [options] arg
               
               WARNING: Application has changed old version is still available using:
                   scope_DSA_BACKUP
               
               EXAMPLES:
                   scope_DSA -f 1000 -n 2000 1,2,4
               Show the interactive space/time diagram for 1000pts folding and 2000 rt of channel 1, channel 2 and channel 4
               
               
                   scope_DSA -s -i 169.254.108.196 -f 1000 -n 2000 1,2,4
                Same as before but changing the IP address used for the communication with the scope (option -i) and starting in sequence mode (option -s without any argument)

               """
    parser = OptionParser(usage)
    parser.add_option("-f", "--fold", type="int", dest="prt", default=364, help="Set the value to fold for yt diagram." )
    parser.add_option("-n", "--nmax", type="int", dest="nmax", default=None, help="Set the value to the number of roundtrip to plot." )
    parser.add_option("-i", "--address", type="str", dest="address", default=IP, help="Set the IP address to use for communication with the scope." )
    parser.add_option("-s", "--sequence", action = "store_true", dest ="sequence", default=False, help="Set saving mode")
    (options, args) = parser.parse_args()

    ### Compute channels to acquire ###
    if len(args) == 0:
        print '\nYou must provide at least one channel\n'
        sys.exit()
    elif len(args) == 1:
        chan = []
        temp_chan = args[0].split(',')                  # Is there a coma?
        if len(temp_chan) > 3:
            print "\nYou must enter 1, 2 or 3 channels separated with comas (if several)\n"
        for i in range(len(temp_chan)):
            try:
                eval(temp_chan[i])
            except:
                print '\nPlease provide existing channels (integer 1->4)\n'
                sys.exit()
            if eval(temp_chan[i]) not in [1,2,3,4]:
                print '\nPlease provide existing channels (integer 1->4)\n'
                sys.exit()
            chan.append('C' + temp_chan[i])
    else:
        print "\nYou must enter 1, 2 or 3 channels separated with comas (if several)\n"
    print chan
    
    
    ### begin TV ###
    Scope(chan, host=options.address, fold=options.prt, nmax=options.nmax,sequence=options.sequence)
    

