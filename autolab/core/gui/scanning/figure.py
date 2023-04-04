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

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# matplotlib.rcParams.update({'figure.autolayout': True})  # good but can raise LinAlgError. alternative is to emit signal when change windows


class FigureManager :

    def __init__(self,gui):

        self.gui = gui

        self.curves = []

        # Configure and initialize the figure in the GUI
        self.fig = Figure()
        matplotlib.rcParams.update({'font.size': 12})
        self.ax = self.fig.add_subplot(111)

        self.add_grid(True)

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

        self.toolbar = NavigationToolbar(self.canvas, self.gui)
        self.gui.graph.addWidget(self.toolbar)

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


        self.MOVESTEP = 0.05

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
        if len(datas) > 0 :
            minValue = min([min(data) for data in datas])
            maxValue = max([max(data) for data in datas])
            if (minValue,maxValue) != self.getRange(axe) :
                self.setRange(axe,(minValue,maxValue))

            self.toolbar.update()


    def add_grid(self, state):
        if state:
            self.ax.minorticks_on()
        else:
            self.ax.minorticks_off()

        self.ax.grid(b=state, which='major')
        self.ax.grid(b=state, which='minor', alpha=0.4)



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
        getattr(self.ax,f'set_{axe}scale')(scaleType)  # BUG: crash python if ct400 is openned -> issue between matplotlib and ctypes from ct400 dll lib
        self.add_grid(True)
        # update for bug -> np.log crash python if a dll lib is openned: https://stackoverflow.com/questions/52497031/python-kernel-crashes-if-i-use-np-log10-after-loading-a-dll
        # could change log in matplotlib but not a good solution
        # I added this:
            # if 0 in a: # OPTIMIZE: used to fix the python crash with dll lib openned
            #     a[a == 0] += 1e-200
        # in matplotlib.scale.transform_non_affine at line 210 to fixe the crash

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
            self.setRange(axe,tuple(axeRange))






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
        data_id = int(self.gui.data_comboBox.currentIndex()) + 1
        data_len = len(self.gui.dataManager.datasets)
        selectedData = data_len - data_id

        # Label update
        self.setLabel('x',variable_x)
        self.setLabel('y',variable_y)

        # Load the last results data
        try :
            data = self.gui.dataManager.getData(self.nbtraces,[variable_x,variable_y], selectedData=selectedData)
        except :
            data = None

        # Plot them
        if data is not None :

            for i in range(len(data)) :

                # Data
                subdata = data[i]
                if subdata is None:
                    continue

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
        if data is not None:
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
                inf_new = inf + (sup-inf)*self.MOVESTEP
                sup_new = sup - (sup-inf)*self.MOVESTEP
            elif action == 'unzoom' :
                inf_new = inf - (sup-inf)*self.MOVESTEP/(1-2*self.MOVESTEP)
                sup_new = sup + (sup-inf)*self.MOVESTEP/(1-2*self.MOVESTEP)
        else :
            log_inf = m.log10(inf)
            log_sup = m.log10(sup)
            if action == 'zoom' :
                inf_new = 10**(log_inf+(log_sup-log_inf)*self.MOVESTEP)
                sup_new = 10**(log_sup-(log_sup-log_inf)*self.MOVESTEP)
            elif action == 'unzoom' :
                inf_new = 10**(log_inf-(log_sup-log_inf)*self.MOVESTEP/(1-2*self.MOVESTEP))
                sup_new = 10**(log_sup+(log_sup-log_inf)*self.MOVESTEP/(1-2*self.MOVESTEP))

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
                inf_new = inf + (sup - inf)*self.MOVESTEP
                sup_new = sup + (sup - inf)*self.MOVESTEP
            elif action == 'decrease' :
                inf_new = inf - (sup - inf)*self.MOVESTEP
                sup_new = sup - (sup - inf)*self.MOVESTEP
        else :
            log_inf = m.log10(inf)
            log_sup = m.log10(sup)
            if action == 'increase' :
                inf_new = 10**(log_inf + (log_sup - log_inf)*self.MOVESTEP)
                sup_new = 10**(log_sup + (log_sup - log_inf)*self.MOVESTEP)
            elif action == 'decrease' :
                inf_new = 10**(log_inf - (log_sup - log_inf)*self.MOVESTEP)
                sup_new = 10**(log_sup - (log_sup - log_inf)*self.MOVESTEP)

        self.setRange(axe,(inf_new,sup_new))
        self.redraw()




    # SAVE FIGURE
    ###########################################################################

    def save(self,filename):
        """ This function save the figure with the provided filename """

        raw_name, extension = os.path.splitext(filename)
        new_filename = raw_name+".png"
        self.fig.savefig(new_filename, dpi=300)


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

        if r[0] != r[1]:
            getattr(self.ax,f'set_{axe}lim')(r)
        else:
            if r[0] != 0:
                getattr(self.ax,f'set_{axe}lim')(r[0]-r[0]*5e-3, r[1]+r[1]*5e-3)
            else:
                getattr(self.ax,f'set_{axe}lim')(-5e-3, 5e-3)
