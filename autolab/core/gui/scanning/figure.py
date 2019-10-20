# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:12:24 2019

@author: qchat
"""


import os
import math as m
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib

class FigureManager :    
    
    def __init__(self,gui):
        
        self.gui = gui
        
        self.curves = []
        
        # Configure and initialize the figure in the GUI
        self.fig = Figure()
        matplotlib.rcParams.update({'font.size': 12})
        self.ax = self.fig.add_subplot(111)  
        self.ax.grid()
        self.ax.set_xlim((0,10))
        self.ax.autoscale(enable=False)
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
        
        for axe in ['x','y'] :
            getattr(self.gui,f'logScale_{axe}_checkBox').stateChanged.connect(lambda b, axe=axe:self.logScaleChanged(axe))
            getattr(self.gui,f'autoscale_{axe}_checkBox').stateChanged.connect(lambda b, axe=axe:self.autoscaleChanged(axe))
            getattr(self.gui,f'autoscale_{axe}_checkBox').setChecked(True)
            getattr(self.gui,f'zoom_{axe}_pushButton').clicked.connect(lambda b,axe=axe:self.zoomButtonClicked('zoom',axe))
            getattr(self.gui,f'unzoom_{axe}_pushButton').clicked.connect(lambda b,axe=axe:self.zoomButtonClicked('unzoom',axe))
            getattr(self.gui,f'variable_{axe}_comboBox').currentIndexChanged.connect(self.variableChanged)
                    
        self.gui.goUp_pushButton.clicked.connect(lambda:self.moveButtonClicked('up'))
        self.gui.goDown_pushButton.clicked.connect(lambda:self.moveButtonClicked('down'))
        self.gui.goLeft_pushButton.clicked.connect(lambda:self.moveButtonClicked('left'))
        self.gui.goRight_pushButton.clicked.connect(lambda:self.moveButtonClicked('right'))
        
        self.fig.canvas.mpl_connect('button_press_event', self.onPress)
        self.fig.canvas.mpl_connect('scroll_event', self.onScroll)
        self.fig.canvas.mpl_connect('motion_notify_event', self.onMotion)
        self.fig.canvas.mpl_connect('button_release_event', self.onRelease)
        self.press = None
        
        self.movestep = 0.05

        # Number of traces
        self.nbtraces = 5
        self.gui.nbTraces_lineEdit.setText(f'{self.nbtraces:g}')
        self.gui.nbTraces_lineEdit.returnPressed.connect(self.nbTracesChanged)
        self.gui.nbTraces_lineEdit.textEdited.connect(lambda : self.gui.setLineEditBackground(self.gui.nbTraces_lineEdit,'edited'))
        self.gui.setLineEditBackground(self.gui.nbTraces_lineEdit,'synced')
        

        
        
        
    
        
    # AUTOSCALING
    ###########################################################################
    
    def autoscaleChanged(self,axe):
        
        """ Set or unset the autoscale mode for the given axis """
        state = self.isAutoscaleEnabled(axe)
        getattr(self.ax,f'set_autoscale{axe}_on')(state)
        if state is True :
            self.doAutoscale(axe)
            self.redraw()
            
            
            
    def isAutoscaleEnabled(self,axe):
        
        """ This function returns True or False whether the autoscale for the given axis
        is enabled """
        
        return getattr(self.gui,f'autoscale_{axe}_checkBox').isChecked()
    
    
    
    def doAutoscale(self,axe):
        
        """ This function proceeds to an autoscale operation of the given axis """
        
        datas = [getattr(curve,f'get_{axe}data')() for curve in self.curves]
        if len(datas)>0 :
            min([min(data) for data in datas])
            minValue = min([min(data) for data in datas])
            maxValue = max([max(data) for data in datas])
            if (minValue,maxValue) != self.getRange(axe) :
                self.setRange(axe,(minValue,maxValue))


            
            
            
    # LOGSCALING
    ###########################################################################

    def logScaleChanged(self,axe):
        
        """ This function is called when the log scale state is changed in the GUI. """
        
        state = getattr(self.gui,f'logScale_{axe}_checkBox').isChecked()
        self.setLogScale(axe,state)
        self.redraw()
        
        
    
    def isLogScaleEnabled(self,axe):
        
        """ This function returns True or False whether the log scale is enabled
        in the given axis """
        
        return getattr(self.ax,f'get_{axe}scale')() == 'log'

            
    
    def setLogScale(self,axe,state):
        
        """ This functions sets or not the log scale for the given axis """
        
        if state is True :
            scaleType = 'log'
        else :
            scaleType = 'linear'
        
        self.checkLimPositive(axe)
        self.ax.grid(state,which='minor',axis=axe)
        getattr(self.ax,f'set_{axe}scale')(scaleType)
        
        
        
    def checkLimPositive(self,axe):
        
        """ This function updates the current range of the given axis to be positive, 
        in case we enter in a log scale mode """
        
        axeRange = list(self.getRange(axe))
            
        change = False
        if axeRange[1] <= 0 : 
            axeRange[1] = 1
            change = True
        if axeRange[0] <= 0 : 
            axeRange[0] = 10**(m.log10(axeRange[1])-1)
            change = True
            
        if change is True :
            self.setRange(axe,axeRange)
        
        
        
        
        
        
    # AXE LABEL
    ###########################################################################
        
    def setLabel(self,axe,value):
        
        """ This function changes the label of the given axis """
        
        getattr(self.ax,f'set_{axe}label')(value)






    # PLOT DATA
    ###########################################################################

            
    def clearData(self):
        
        """ This function removes any plotted curves """
        
        for curve in self.curves :
            curve.remove()
        self.curves = []
        self.redraw()
            
        
        
    def reloadData(self):
        
        ''' This function removes any plotted curves and reload all required curves from 
        data available in the data manager'''
        
        # Remove all curves
        self.clearData()
        
        # Get current displayed result
        variable_x = self.gui.variable_x_comboBox.currentText()
        variable_y = self.gui.variable_y_comboBox.currentText()
        
        # Label update
        self.setLabel('x',variable_x)
        self.setLabel('y',variable_y)
        
        # Load the last results data
        try :
            data = self.gui.dataManager.getData(self.nbtraces,[variable_x,variable_y])       
        except :
            data = None
        
        # Plot them
        if data is not None :
            
            for i in range(len(data)) :
                                
                # Data
                subdata = data[i]
                subdata = subdata.astype(float)
                x = subdata.loc[:,variable_x]
                y = subdata.loc[:,variable_y]
                
                # Apprearance:    
                if i == (len(data)-1) :      
                    color = 'r'
                    alpha = 1
                else:
                    color = 'k'
                    alpha = (self.nbtraces-(len(data)-1-i))/self.nbtraces
                
                # Plot
                curve = self.ax.plot(x,y,'x-',color=color,alpha=alpha)[0]
                self.curves.append(curve)
            
            # Autoscale
            if self.isAutoscaleEnabled('x') is True : self.doAutoscale('x')
            if self.isAutoscaleEnabled('y') is True : self.doAutoscale('y')
            
            self.redraw()
        
        
        
    def reloadLastData(self):
        
        ''' This functions update the data of the last curve '''
        
        # Get current displayed result
        variable_x = self.gui.variable_x_comboBox.currentText()
        variable_y = self.gui.variable_y_comboBox.currentText()
        
        data = self.gui.dataManager.getData(1,[variable_x,variable_y])[0]
        data = data.astype(float)
        
        # Update plot data
        self.curves[-1].set_xdata(data.loc[:,variable_x])
        self.curves[-1].set_ydata(data.loc[:,variable_y])
        
        # Autoscale
        if self.isAutoscaleEnabled('x') is True : self.doAutoscale('x')
        if self.isAutoscaleEnabled('y') is True : self.doAutoscale('y')
        
        self.redraw()
        
        
        
    def variableChanged(self,index):
        
        """ This function is called when the displayed result has been changed in
        the combo box. It proceeds to the change. """
        
        self.clearData()        
        
        if self.gui.variable_x_comboBox.currentIndex() != -1 and self.gui.variable_y_comboBox.currentIndex() != -1 : 
            self.reloadData()
            
        if self.gui.variable_x_comboBox.currentText() == self.gui.configManager.getParameterName() :
            self.gui.fromFigure_pushButton.setEnabled(True)
        else :
            self.gui.fromFigure_pushButton.setEnabled(False)

            
            
        
    # TRACES
    ###########################################################################      
        
    def nbTracesChanged(self):
        
        """ This function is called when the number of traces displayed has been changed
        in the GUI. It proceeds to the change and update the plot. """
                
        value = self.gui.nbTraces_lineEdit.text()
        
        check = False
        try :
            value = int(float(value))
            assert value > 0
            self.nbtraces = value
            check = True
        except :
            pass
        
        self.gui.nbTraces_lineEdit.setText(f'{self.nbtraces:g}')
        self.gui.setLineEditBackground(self.gui.nbTraces_lineEdit,'synced')
        
        if check is True and self.gui.variable_y_comboBox.currentIndex() != -1 :
            self.reloadData()
        
        
    


    # ZOOM UNZOOM BUTTONS
    ###########################################################################

    def zoomButtonClicked(self,action,axe):
        
        """ This function is called when a zoom/unzoom button of a given axis has been pressed.
        It proceeds to the change to the figure range """

        logState = self.isLogScaleEnabled(axe)
        inf,sup = self.getRange(axe)
        
        if logState is False :
            if action == 'zoom' :
                inf_new = inf + (sup-inf)*self.movestep
                sup_new = sup - (sup-inf)*self.movestep
            elif action == 'unzoom' :
                inf_new = inf - (sup-inf)*self.movestep/(1-2*self.movestep)
                sup_new = sup + (sup-inf)*self.movestep/(1-2*self.movestep)
        else :
            log_inf = m.log10(inf)
            log_sup = m.log10(sup)
            if action == 'zoom' :
                inf_new = 10**(log_inf+(log_sup-log_inf)*self.movestep)
                sup_new = 10**(log_sup-(log_sup-log_inf)*self.movestep)
            elif action == 'unzoom' :
                inf_new = 10**(log_inf-(log_sup-log_inf)*self.movestep/(1-2*self.movestep))
                sup_new = 10**(log_sup+(log_sup-log_inf)*self.movestep/(1-2*self.movestep))
                
        self.setRange(axe,(inf_new,sup_new))
        self.redraw()




    # MOVE BUTTONS
    ###########################################################################
    
    def moveButtonClicked(self,action):
        
        """ This function is called when a move button of a given axis has been pressed.
        It proceeds to the change to the figure range """
        
        if action in ['up','down'] :
            axe = 'y'
            if action == 'up' : action = 'increase'
            elif action == 'down' : action = 'decrease'
        elif action in ['left','right'] :
            axe = 'x'
            if action == 'left' : action = 'decrease'
            elif action == 'right' : action = 'increase'

        logState = self.isLogScaleEnabled(axe)
            
        inf,sup = self.getRange(axe)
        
        if logState is False :
            if action == 'increase' :
                inf_new = inf + (sup-inf)*self.movestep
                sup_new = sup + (sup-inf)*self.movestep
            elif action == 'decrease' :
                inf_new = inf - (sup-inf)*self.movestep
                sup_new = sup - (sup-inf)*self.movestep
        else :
            log_inf = m.log10(inf)
            log_sup = m.log10(sup)
            if action == 'increase' :
                inf_new = 10**(log_inf+(log_sup-log_inf)*self.movestep)
                sup_new = 10**(log_sup+(log_sup-log_inf)*self.movestep)
            elif action == 'decrease' :
                inf_new = 10**(log_inf-(log_sup-log_inf)*self.movestep)
                sup_new = 10**(log_sup-(log_sup-log_inf)*self.movestep)
            
        self.setRange(axe,(inf_new,sup_new))
        self.redraw()
   
    
    
    
        
    # MOUSE SCROLL
    ###########################################################################
     
    def onScroll(self,event):
        
        """ This function is called when the scrolling button of the mouse has been
        actioned for a given axis has been pressed.
        It proceeds to the change to the figure range """
        
        data = {'x':event.xdata,'y':event.ydata}
        
        for axe in ['x','y'] :
            
            logState = self.isLogScaleEnabled(axe)
            inf,sup = self.getRange(axe)
            
            if logState :
            
                if event.button == 'up' : 
                    inf_new = 10**(m.log10(data[axe]) * self.movestep + (1-self.movestep) * m.log10(inf)) 
                    sup_new = 10**(m.log10(data[axe]) * self.movestep + (1-self.movestep) * m.log10(sup)) 
                elif event.button == 'down' :
                    inf_new = 10**( ( - m.log10(data[axe]) * self.movestep + m.log10(inf) ) / (1 - self.movestep) )
                    sup_new = 10**( ( - m.log10(data[axe]) * self.movestep + m.log10(sup) ) / (1 - self.movestep) )
                    
            else :
            
                if event.button == 'up' : 
                    inf_new = data[axe] * self.movestep + (1-self.movestep) * inf 
                    sup_new = data[axe] * self.movestep + (1-self.movestep) * sup 
                elif event.button == 'down' :
                    inf_new = ( - data[axe] * self.movestep + inf ) / (1 - self.movestep)
                    sup_new = ( - data[axe] * self.movestep + sup ) / (1 - self.movestep)   
                
            self.setRange(axe,(inf_new,sup_new))
            self.redraw()
            
            
            
            
        
    # MOUSE DRAG
    ###########################################################################
        
    def onPress(self,event):
        
        """ This function is called when the main button of the mouse is pressed on the figure.
        It saves information about this location, in order to use it in the onMotion function. """
        
        xlim = self.getRange('x')
        ylim = self.getRange('y')
        
        if self.isLogScaleEnabled('x') is False :
            x_width_data = xlim[1]-xlim[0]
        else :
            x_width_data = m.log10(xlim[1])-m.log10(xlim[0])
        
        if self.isLogScaleEnabled('y') is False :
            y_width_data = ylim[1]-ylim[0]
        else :
            y_width_data = m.log10(ylim[1])-m.log10(ylim[0])
        
        leftInfCornerCoords = self.ax.transData.transform((xlim[0],ylim[0]))
        rightSupCornerCoords = self.ax.transData.transform((xlim[1],ylim[1]))       
        x_width_pixel = rightSupCornerCoords[0] - leftInfCornerCoords[0]
        y_width_pixel = rightSupCornerCoords[1] - leftInfCornerCoords[1]
    
        self.press = xlim,ylim,x_width_data,y_width_data,x_width_pixel,y_width_pixel,event.x,event.y

        

    def onMotion(self,event):
        
        """ This function is called when the mouse if moved above the figure. If its button is pressed, 
        proceeds to the corresponding change in range with the help on the data saved with 
        the onPress function. """
        
        if self.press is not None and event.inaxes is not None :
            
            xlim,ylim,x_width_data,y_width_data,x_width_pixel,y_width_pixel,x_press_pixel, y_press_pixel = self.press

            x_pixel,y_pixel = event.x,event.y
            
            xlim_new = list(xlim)
            ylim_new = list(ylim)
            
            dx_pixel = x_pixel - x_press_pixel
            dy_pixel = y_pixel - y_press_pixel
            
            dx_data = dx_pixel * x_width_data / x_width_pixel
            dy_data = dy_pixel * y_width_data / y_width_pixel
            
            if self.isLogScaleEnabled('x'):
                xlim_new[0] = 10**(m.log10(xlim[0])-dx_data)
                xlim_new[1] = 10**(m.log10(xlim[1])-dx_data)
            else :
                xlim_new[0] = xlim[0]-dx_data
                xlim_new[1] = xlim[1]-dx_data
  
            if self.isLogScaleEnabled('y'):
                ylim_new[0] = 10**(m.log10(ylim[0])-dy_data)
                ylim_new[1] = 10**(m.log10(ylim[1])-dy_data)
            else :
                ylim_new[0] = ylim[0]-dy_data
                ylim_new[1] = ylim[1]-dy_data
            
            self.setRange('x',xlim_new)
            self.setRange('y',ylim_new)
            self.redraw()
            
            
    def onRelease(self,event):
        
        """ This function is called when the wiew change using the mouse is finshed.
        It clears the data of the initial press position """
        
        self.press = None
        

        

    
    # SAVE FIGURE
    ###########################################################################
        
    def save(self,path):
        
        """ This function save the figure in the provided path """
        
        self.fig.savefig(os.path.join(path,'figure.jpg'),dpi=300)
        
        
        
        
        
    # redraw
    ###########################################################################

    def redraw(self):
        
        """ This function make the previous changes appears in the GUI """
        
        try :
            self.fig.tight_layout()
        except :
            pass
        self.canvas.draw()
        
        
        
        
    # RANGE
    ###########################################################################
        
    def getRange(self,axe):
        
        """ This function returns the current range of the given axis """
        
        return getattr(self.ax,f'get_{axe}lim')()
    
    
    
    def setRange(self,axe,r):
        
        """ This function sets the current range of the given axis """
        
        if r[0] != r[1] :
            getattr(self.ax,f'set_{axe}lim')(r)
        