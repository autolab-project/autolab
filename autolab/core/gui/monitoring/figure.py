# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:22:35 2019

@author: qchat
"""

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import os
            
class FigureManager :
    
    def __init__(self,gui):
        
        self.gui = gui
        
        # Configure and initialize the figure in the GUI
        self.fig = Figure()
        matplotlib.rcParams.update({'font.size': 12})
        self.ax = self.fig.add_subplot(111)        
        self.ax.set_xlabel('Time [s]')
        ylabel = f'{self.gui.variable.address()}'
        if self.gui.variable.unit is not None :
            ylabel += f' ({self.gui.variable.unit})'
        self.ax.set_ylabel(ylabel)
        self.ax.grid()
        self.plot=self.ax.plot([0],[0],'x-',color='r')[0]
        # The first time we open a monitor it doesn't work, I don't know why..
        # There is no current event loop in thread 'Thread-7'.
        # More accurately, FigureCanvas doesn't find the event loop the first time it is called
        # The second time it works..
        # Seems to be only in Spyder..
        try : 
            self.canvas = FigureCanvas(self.fig) 
        except :
            self.canvas = FigureCanvas(self.fig)
        self.gui.graph.addWidget(self.canvas)
        self.fig.tight_layout()
        self.canvas.draw()

    
    def update(self,xlist,ylist):
        
        """ This function update the figure in the GUI """ 
        
        # Data retrieval
        self.plot.set_xdata(xlist)
        self.plot.set_ydata(ylist)

        # X axis update
        xlist = self.plot.get_xdata()
        xmin = min(xlist)
        xmax = max(xlist)
        if xmin != xmax :
            self.ax.set_xlim(xmin,xmax+0.15*(xmax-xmin))
        else :
            self.ax.set_xlim(xmin-0.1,xmin+0.1)
        
        # Y axis update
        ylist = self.plot.get_ydata()
        ymin = min(ylist)
        ymax = max(ylist)
        if ymin != ymax :
            self.ax.set_ylim(ymin-0.1*(ymax-ymin),ymax+0.1*(ymax-ymin))
        else :
            self.ax.set_ylim(ymin-0.1,ymin+0.1)
            
        # Figure finalization  
        self.redraw()
        #self.canvas.draw()

            
            
        
    def redraw(self):
        
        """ This function finalize the figure update in the GUI """
        
        try :
            self.fig.tight_layout()
        except :
            pass
        self.canvas.draw()
        
        
        
        
                
    def save(self,path):
        
        """ This function save the figure in the provided path """
        
        self.fig.savefig(os.path.join(path,'figure.jpg'),dpi=300)
        
        
        
        