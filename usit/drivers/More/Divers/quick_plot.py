#!/usr/bin/env python3  
# -*- coding: utf-8 -*-

from optparse import OptionParser
from pylab import plot,draw,savefig,xlabel,ylabel,ylim,figure,show
import numpy

class quick_plot():
    def __init__(self,filename,SAVE=False):
        self.filename = filename
        self.SAVE     = SAVE
        self.fig      = figure(52)
        self.FIRST    = True
        
    def plot(self):
        self.filename = self.filename + '_YOKO'
        wl,amp = numpy.loadtxt(self.filename)
        
        if self.FIRST:
            self.a, = plot(wl,amp,linewidth=2)
            ylim(ymin=-80)
            xlabel('Wavelength',fontsize='xx-large')
            ylabel('Amplitude',fontsize='xx-large')
            show(False)
        else:
            self.a.set_data(wl,amp)
        self.fig.canvas.draw()
        
        if self.SAVE:
            savefig(self.filename+'.png')#,format='jpg')
        
        self.FIRST = False


if __name__ == "__main__":
    usage = """usage: %prog [options] arg
               
    EXAMPLES:
        quick_fig -s -o filename
        
        plot the spectrum corresponding to filename and save the figure (-s option)
        
    """
    
    parser = OptionParser(usage)
    parser.add_option("-o", "--filename", type="string", dest="filename", default='DEFAULT', help="Set the name of the output file" )
    parser.add_option("-s", "--save", action = "store_true", dest="save", default=False, help="Do you want to save?" )
    (options, args) = parser.parse_args()

    I = quick_plot(filename=options.filename,SAVE=options.save)
    I.plot()
