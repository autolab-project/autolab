#!/usr/bin/python  
# -*- coding: utf-8 -*-

"""Look at 2D static data"""
from matplotlib.pyplot import axes, plot, figure, draw, show, rcParams, clf
from matplotlib.widgets import Slider, Cursor
from numpy import array, roll, arange, sin, concatenate,\
        fromfile, uint8, int8, reshape, memmap, zeros, fromstring, where,linspace
from tempfile import TemporaryFile
from numpy.random import randn
import time
import sys
import commands as C
import matplotlib as mpl
from optparse import OptionParser
import vxi11 as vxi
import gobject
import matplotlib.pyplot as plt
from scipy import interpolate
from matplotlib.font_manager import FontProperties

plt.style.use('classic')
mpl.pyplot.switch_backend('GTkAgg')

class ytViewer(object):
    def __init__(self, filenames, fold=19277, nmax=100,NORM=True,dtype=int8,DEB=0,shear=0.):
        self.UPDATE = False
        self.color  = False
        self.CMAP   = ['jet','seismic','Greys','plasma']
        self.COLORS = ['b','g','r']
        
        self.filenames   = filenames
        self.NORM        = NORM
        self.NMAX        = nmax
        self.fold        = fold
        self.increment   = 5
        self.index       = 0
        self.shear       = shear
        self.vmin        = -125
        self.vmax        = 125
        self.HORIZ_VAL   = 0.05
        
        for i in range(len(self.filenames)):
            exec("self.remove_len1%d = 0" %i)
            exec("self.remove_len2%d = 1" %i)

        self.Y0 = 0
        
        ### To set the data arrays ###
        for i in range(len(self.filenames)):
            exec("self.data%d = fromfile(filenames[i],dtype=dtype)" %i)
            try:
                pass
            except:
                print '\nYou must provide existing filenames\n'
                sys.exit()
                
        self.max_index = int(len(self.data0)/self.fold)
        if not(self.NMAX):
            self.NMAX = self.max_index
        
        for i in range(len(self.filenames)):
            exec("self.folded_data_orig2%d = self.data%d[:self.max_index*self.fold].reshape(self.max_index,self.fold)" %(i,i))
            exec("self.folded_data_orig%d  = array(self.folded_data_orig2%d)" %(i,i))
            exec("self.folded_data_orig3%d = array(self.folded_data_orig%d)" %(i,i))
            exec("self.folded_data%d       = self.folded_data_orig3%d[:self.NMAX]" %(i,i))
        
        ##################################################################
        ################## Start creating the figure #####################
        self.fig = figure(figsize=(16,7))
        
        if len(self.filenames)==1:
            self.declare_axis_1channel()
        elif len(self.filenames)==2:
            self.declare_axis_2channel()
        elif len(self.filenames)==3:
            self.declare_axis_3channel()
            
        for i in range(len(self.filenames)):
            if not self.NORM:
                exec("self.im%d = self.ax%d.imshow(self.folded_data%d, interpolation='nearest', aspect='auto',origin='lower', vmin=self.vmin, vmax=self.vmax)" %(i,i,i))
            else:
                exec("self.im%d = self.ax%d.imshow(self.folded_data%d, interpolation='nearest', aspect='auto',origin='lower', vmin=self.folded_data%d.min(), vmax=self.folded_data%d.max())" %(i,i,i,i,i))

        for i in range(len(self.filenames)):
            exec("self.cursor%d = Cursor(self.ax%d, useblit=True, color='red', linewidth=2)" %(i,i))

        self.axhh = axes([0.02,0.25,0.12,0.62])
        for i in range(len(self.filenames)):
            exec("self.hline%d, = self.axh%d.plot(self.folded_data%d[self.Y0,:])" %(i,i,i))
            exec("self.axh%d.set_xlim(0,len(self.folded_data%d[0,:]))" %(i,i))
            exec("self.hhline%d, = self.axhh.plot(self.folded_data%d.mean(1),arange(self.NMAX),self.COLORS[i])" %(i,i))
        self.axhh.set_ylim(0,self.NMAX-1)
        if not self.NORM:
            for i in range(len(self.filenames)):
                exec("self.axh%d.set_ylim(self.vmin, self.vmax)" %i)
            self.axhh.set_xlim(self.vmin, self.vmax)
        else:
            for i in range(len(self.filenames)):
                 exec("self.axh%d.set_ylim(self.folded_data%d.min(), self.folded_data%d.max())" %(i,i,i))
            if len(self.filenames)==1:
                LIM_MIN = self.folded_data0.mean(1).min()
                LIM_MAX = self.folded_data0.mean(1).max()
            elif len(self.filenames)==2:
                LIM_MIN = min(self.folded_data0.mean(1).min(),self.folded_data1.mean(1).min())
                LIM_MAX = max(self.folded_data0.mean(1).max(),self.folded_data1.mean(1).max())
            elif len(self.filenames)==3:
                LIM_MIN = min(self.folded_data0.mean(1).min(),self.folded_data1.mean(1).min(),self.folded_data2.mean(1).min())
                LIM_MAX = max(self.folded_data0.mean(1).max(),self.folded_data1.mean(1).max(),self.folded_data2.mean(1).max())
            self.axhh.set_xlim(LIM_MIN-1,LIM_MAX+1)
        
        # create 'remove_len1' slider
        for i in range(len(self.filenames)):
            exec("self.remove_len1%d_slider   = Slider(self.remove_len1%d_sliderax,'beg',0.,self.fold,self.remove_len1%d,'%s')" %(i,i,i,'%d'))
            exec("self.remove_len1%d_slider.on_changed(self.update_tab)" %i)
        
        # create 'remove_len2' slider
        for i in range(len(self.filenames)):
            exec("self.remove_len2%d_slider   = Slider(self.remove_len2%d_sliderax,'end',1.,self.fold,self.remove_len2%d,'%s')" %(i,i,i,'%d'))
            exec("self.remove_len2%d_slider.on_changed(self.update_tab)" %i)
        # create 'index' slider
        self.index_sliderax = axes([0.175,0.975,0.775,0.02])
        self.index_slider   = Slider(self.index_sliderax,'index',0,self.max_index-self.increment,0,'%d')
        self.index_slider.on_changed(self.update_tab)
        # create 'nmax' slider
        self.nmax_sliderax = axes([0.175,0.955,0.775,0.02])
        self.nmax_slider   = Slider(self.nmax_sliderax,'nmax',0,self.max_index,self.NMAX,'%d')
        self.nmax_slider.on_changed(self.update_tab)
        # create 'shear' slider
        self.shear_sliderax = axes([0.175,0.935,0.775,0.02])
        self.shear_slider   = Slider(self.shear_sliderax,'Shear',-0.5,0.5,self.shear,'%1.2f')
        self.shear_slider.on_changed(self.update_shear)
        
        cid  = self.fig.canvas.mpl_connect('motion_notify_event', self.mousemove)
        cid2 = self.fig.canvas.mpl_connect('key_press_event', self.keypress)

        VERT_VAL = -4
        font0 = FontProperties()
        font1 = font0.copy()
        font1.set_weight('bold')
        mpl.pyplot.text(-0.72,-32+VERT_VAL,'Useful keys:',fontsize=18,fontproperties=font1)
        mpl.pyplot.text(-0.72,-41+VERT_VAL,'"c" to change colormap\n "v" to change vertical\n      /colorscale\n " " to pause\n "w"/"x" set Ch1 REMOVE\n       sliders values to Ch2/3\n "t" Retrigger mode\n (NOT TOO MUCH POINTS) \n "q" to exit',fontsize=18)
        
        self.axe_toggledisplay  = self.fig.add_axes([0.,0.,1.0,0.02])
        if self.UPDATE:
            self.plot_circle(0,0,2,fc='#00FF7F')
        else:
            self.plot_circle(0,0,2,fc='#FF4500')
        mpl.pyplot.axis('off')
        
        gobject.idle_add(self.update_plot)
        show()
        
    ### BEGIN main loop ###
    def update_plot(self):
        while self.UPDATE:
            ### Compute the array to plot ###
            for i in range(len(self.filenames)):
                exec("self.folded_data%d = self.folded_data_orig3%d[self.index:(self.index+self.NMAX)]" %(i,i))
            
            ### Update picture ###
            for i in range(len(self.filenames)):
                exec("self.im%d.set_data(self.folded_data%d)" %(i,i))
                exec("self.hline%d.set_ydata(self.folded_data%d[self.Y0,:])" %(i,i))
                exec("self.hhline%d.set_xdata(self.folded_data%d.mean(1))" %(i,i))
            self.index = self.index + self.increment
            self.index_slider.set_val(self.index)
            self.fig.canvas.draw()

            return True
        return False
    ### END main loop ###
        
    def update_tab(self,val):
        for i in range(len(self.filenames)):
            exec("self.remove_len1%d = int(self.remove_len1%d_slider.val)" %(i,i))
            exec("self.remove_len2%d = int(self.remove_len2%d_slider.val)" %(i,i))
        self.index = int(round(self.index_slider.val,0))
        self.NMAX  = int(round(self.nmax_slider.val,0))
        self.Y0 = 0
        self.update_tabs()
        self.norm_fig()
        self.fig.canvas.draw()
        
    def update_tabs(self):
        for i in range(len(self.filenames)):
            exec("self.folded_data_orig3%d = array(self.folded_data_orig%d[:,self.remove_len1%d:-self.remove_len2%d])" %(i,i,i,i))
            exec("self.process_data(self.shear,%d)" %i)
            exec("self.folded_data%d = self.folded_data_orig3%d[self.index:(self.index+self.NMAX)]" %(i,i))
            
    def process_data(self,val,i):
        """ Redress data in the space/time diagram """
        exec("dd = self.folded_data_orig2%d.copy()" %i)
        for k in range(0,dd.shape[0]):
            exec("dd[k,:] = roll(self.folded_data_orig2%d[k,:], int(k*val))" %i)
        exec("self.folded_data_orig%d = dd" %i)
        
    def norm_fig(self):
        if len(self.filenames)==1:
            LIM_MIN = self.folded_data0.mean(1).min()
            LIM_MAX = self.folded_data0.mean(1).max()
        elif len(self.filenames)==2:
            LIM_MIN = min(self.folded_data0.mean(1).min(),self.folded_data1.mean(1).min())
            LIM_MAX = max(self.folded_data0.mean(1).max(),self.folded_data1.mean(1).max())
        elif len(self.filenames)==3:
            LIM_MIN = min(self.folded_data0.mean(1).min(),self.folded_data1.mean(1).min(),self.folded_data2.mean(1).min())
            LIM_MAX = max(self.folded_data0.mean(1).max(),self.folded_data1.mean(1).max(),self.folded_data2.mean(1).max())
        self.axhh.clear()
        if not self.NORM:
            for i in range(len(self.filenames)):
                exec("self.ax%d.clear()" %i)
                exec("self.im%d = self.ax%d.imshow(self.folded_data%d,cmap=self.CMAP[0], interpolation='nearest', aspect='auto',origin='lower', vmin=self.vmin, vmax=self.vmax)" %(i,i,i))
                exec("self.axh%d.clear()" %i)
                exec("self.hline%d, = self.axh%d.plot(self.folded_data%d[self.Y0,:])" %(i,i,i))
                exec("self.axh%d.set_ylim(self.vmin, self.vmax)" %i)
                exec("self.axh%d.set_xlim(0, len(self.folded_data%d[0]))" %(i,i))
                exec("self.hhline%d, = self.axhh.plot(self.folded_data%d.mean(1),arange(len(self.folded_data%d.mean(1))),self.COLORS[i])" %(i,i,i))
            self.axhh.set_ylim(0,self.max_index-self.index-1)
            self.axhh.set_xlim(self.vmin, self.vmax)
        else:
            for i in range(len(self.filenames)):
                exec("self.ax%d.clear()" %i)
                exec("self.im%d = self.ax%d.imshow(self.folded_data%d,cmap=self.CMAP[0], interpolation='nearest', aspect='auto',origin='lower', vmin=self.folded_data%d.min(), vmax=self.folded_data%d.max())" %(i,i,i,i,i))
                exec("self.axh%d.clear()" %i)
                exec("self.hline%d, = self.axh%d.plot(self.folded_data%d[self.Y0,:])" %(i,i,i))
                exec("self.axh%d.set_ylim(self.folded_data%d.min(), self.folded_data%d.max())" %(i,i,i))
                exec("self.axh%d.set_xlim(0, len(self.folded_data%d[0]))" %(i,i))
                exec("self.hhline%d, = self.axhh.plot(self.folded_data%d.mean(1),arange(len(self.folded_data%d.mean(1))),self.COLORS[i])" %(i,i,i))
            self.axhh.set_ylim(0,len(self.folded_data0.mean(1)))
            self.axhh.set_xlim(LIM_MIN-1,LIM_MAX+1)
        self.fig.canvas.draw()

    ### BEGIN Slider actions ###
    def update_shear(self,val):
        self.shear = round(self.shear_slider.val,2)
        self.update_tabs()
        self.update_tab(0)
        self.norm_fig()
        self.fig.canvas.draw()

    def update_cut(self):
        for i in range(len(self.filenames)):
            exec("self.hline%d.set_ydata(self.folded_data%d[self.Y0,:])" %(i,i))
        self.fig.canvas.draw()
    ### END Slider actions ###
    
    ### BEGIN actions to the window ###
    def toggle_update(self):
            self.UPDATE = not(self.UPDATE)
            if self.UPDATE:
                gobject.idle_add(self.update_plot)
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
                
    def keypress(self, event):
        if event.key == 'q': # eXit
            del event
            sys.exit()
        elif event.key=='c':
            del event
            self.CMAP = roll(self.CMAP,-1)
            self.norm_fig()
            self.fig.canvas.draw()
        elif event.key=='v':
            del event
            self.NORM = not(self.NORM)
            self.norm_fig()
        elif event.key == ' ': # play/pause
            self.toggle_update()
        elif event.key == 'w':
            if len(self.filenames)>=2:
                print 'Set REMOVE values of channel 1 to channel 2'
                self.remove_len11_slider.set_val(self.remove_len10)
                self.remove_len21_slider.set_val(self.remove_len20)
        elif event.key == 'x':
            if len(self.filenames)>=3:
                print 'Set REMOVE values of channel 1 to channel 3'
                self.remove_len12_slider.set_val(self.remove_len10)
                self.remove_len22_slider.set_val(self.remove_len20)
        elif event.key == 't':
            print 'Trying to smooth from index',self.index
            self.smooth_array()
            print 'Done MF'
        else:
            print 'Key '+str(event.key)+' not known'
    
    def mousemove(self, event):
        # called on each mouse motion to get mouse position
        if len(self.filenames)==1:
            if event.inaxes!=self.ax0: return
        elif len(self.filenames)==2:
            if event.inaxes!=self.ax0 and event.inaxes!=self.ax1: return
        elif len(self.filenames)==3:
            if event.inaxes!=self.ax0 and event.inaxes!=self.ax1 and event.inaxes!=self.ax2: return
        self.X0 = int(round(event.xdata,0))
        self.Y0 = int(round(event.ydata,0))
        self.update_cut()
    ### END actions to the window ###
    
    ### Divers useful functions ###
    def plot_circle(self,x,y,r,fc='r'):
        """Plot a circle of radius r at position x,y"""
        cir = mpl.patches.Circle((x,y), radius=r, fc=fc)
        self.patch = mpl.pyplot.gca().add_patch(cir)
    
    def smooth_array(self):
        if len(self.filenames)>=2 and self.UPDATE==False:
            self.fig2 = figure(5,figsize=(16,7))
            clf()
            for i in range(len(self.filenames)):
                exec("self.folded_data%d = self.folded_data_orig3%d[self.index:(self.index+self.NMAX)]" %(i,i))
            if len(self.filenames)==2:
                self.folded_data_retriggered1,self.folded_data_retriggered0 = self.trig_by_interpolation_pola(self.folded_data1,self.folded_data0)
                self.fig2ax0 = self.fig2.add_subplot(111)
                self.fig2ax0.clear()
                self.fig2ax0.imshow(self.folded_data_retriggered0,cmap=self.CMAP[0], interpolation='nearest', aspect='auto',origin='lower', vmin=self.folded_data_retriggered0.min(), vmax=self.folded_data_retriggered0.max())
            elif len(self.filenames)==3:
                self.folded_data_retriggered2,self.folded_data_retriggered0,self.folded_data_retriggered1 = self.trig_by_interpolation_pola(self.folded_data2,self.folded_data0,self.folded_data1)
                self.fig2ax1 = self.fig2.add_subplot(121)
                self.fig2ax1.clear()
                self.fig2ax1.imshow(self.folded_data_retriggered0,cmap=self.CMAP[0], interpolation='nearest', aspect='auto',origin='lower', vmin=self.folded_data_retriggered0.min(), vmax=self.folded_data_retriggered0.max())
                self.fig2ax2 = self.fig2.add_subplot(122)
                self.fig2ax2.clear()
                self.fig2ax2.imshow(self.folded_data_retriggered1,cmap=self.CMAP[0], interpolation='nearest', aspect='auto',origin='lower', vmin=self.folded_data_retriggered1.min(), vmax=self.folded_data_retriggered1.max())
            show(False)
            self.fig2.canvas.draw()
        else:
            print 'This function REQUIRES a trigger'
            
    
    def trig_by_interpolation_pola(self,data,pola1,pola2=None,thr=30,FACT=25,num_trig=0,DOWN=False):
        if DOWN:
            pos   = self.find_down(data,thr)
        else:
            pos   = self.find_up(data,thr)
        l     = data    # for a first trigg  ->  #array([data[pos[i]-100:pos[i]+100] for i in xrange(len(pos)-1)])
        lp1      = pola1
        if pola2 is not None: lp2 = pola2
        ll       = []
        trace    = []
        trace_p1 = []
        if pola2 is not None: trace_p2 = []
        for i in range(len(l)):
                b     = interpolate.interp1d(linspace(0,len(l[i]),len(l[i])),l[i])
                bp1   = interpolate.interp1d(linspace(0,len(lp1[i]),len(lp1[i])),lp1[i])
                if pola2 is not None: bp2   = interpolate.interp1d(linspace(0,len(lp2[i]),len(lp2[i])),lp2[i])
                xnew2 = linspace(0, len(l[i]),FACT*len(l[i]))
                xnew  = linspace(0, len(lp1[i]),FACT*len(lp1[i]))
                xnew3 = linspace(0, len(lp2[i]),FACT*len(lp2[i]))
                try:
                    temp2    = b(xnew2)
                    temp2_p1 = bp1(xnew)
                    if pola2 is not None: temp2_p2 = bp2(xnew3)
                    if DOWN:
                        temp = self.find_down(temp2,thr)
                    else:
                        temp = self.find_up(temp2,thr)
                    ll.append(temp[num_trig])     # If several downward event found for the trigger
                    trace.append(temp2)
                    trace_p1.append(temp2_p1)
                    if pola2 is not None: trace_p2.append(temp2_p2)
                except:
                    print '%d WARNING: Error repering => skiping a line'%i
        lll   = []
        lllp1 = []
        if pola2 is not None: lllp2 = []
        ll = array(ll)-array(ll).min()
        for i in range(len(ll)):
            lll.append(roll(trace[i],-ll[i]))
            lllp1.append(roll(trace_p1[i],-ll[i]))
            if pola2 is not None: lllp2.append(roll(trace_p2[i],-ll[i]))
        return (array(lll),array(lllp1),array(lllp2)) if pola2 is not None else (array(lll),array(lllp1))
    
    def find_down(self,d, threshold):
        digitized = zeros(shape=d.shape, dtype=uint8)
        digitized[where(d < threshold)] = 255
        derivative = digitized[1:]-digitized[0:-1]
        indices = where(derivative == 255)[0]
        return indices
    def find_up(self,d, threshold):
        digitized = zeros(shape=d.shape, dtype=uint8)
        digitized[where(d > threshold)] = 255
        derivative = digitized[1:]-digitized[0:-1]
        indices = where(derivative == 255)[0]
        return indices
        
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
        
        
if __name__=='__main__':

    usage = """usage: %prog [options] arg
               
               EXAMPLES:
                   ytExp_DSA -f 1000 -n 2000 1_DSACHAN1
               Show the interactive space/time diagram for 1000pts folding and 2000 rt acquired from the file


               """
    parser = OptionParser(usage)
    parser.add_option("-f", "--fold", type="int", dest="prt", default=364, help="Set the value to fold for yt diagram." )
    parser.add_option("-n", "--nmax", type="int", dest="nmax", default=None, help="Set the value to the number of roundtrip to plot." )
    parser.add_option("-d", "--deb", type="int", dest="deb", default=0, help="Change the beginning of data." )
    parser.add_option("-s", "--shear", type="float", dest="shear", default=0., help="Set initial value of the shear." )
    (options, args) = parser.parse_args()

    ### Compute filenames to open ###
    if len(args) == 0:
        print '\nYou must provide at least one filename\n'
        sys.exit()
    elif len(args) == 1:
        filenames = []
        temp_filenames = args[0].split(',')                  # Is there a coma?
        if len(temp_filenames) > 3:
            print "\nYou must enter 1, 2 or 3 filenames separated with comas (if several)\n"
        for i in range(len(temp_filenames)):
            filenames.append(temp_filenames[i])
    else:
        print "\nYou must enter 1, 2 or 3 filenames separated with comas (if several)\n"
    print filenames
    
    ### begin TV ###
    ytViewer(filenames, fold=options.prt, nmax=options.nmax,DEB=options.deb,shear=options.shear)



