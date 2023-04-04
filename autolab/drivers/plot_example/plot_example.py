# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 21:04:12 2022

@author: jonathan
"""

import queue

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PyQt5 import QtCore, QtWidgets


class MplCanvas(FigureCanvasQTAgg):
    """https://www.pythonguis.com/tutorials/plotting-matplotlib/"""

    def __init__(self, parent=None, width=13, height=6, dpi=100):
        with plt.style.context('ggplot'):  # to use your custom style only for your figure and not every other figures form Autolab
            fig = Figure(figsize=(width, height), dpi=dpi)
            self.fig = fig
            self.axes = fig.add_subplot(111)
            super(MplCanvas, self).__init__(fig)
            self.axes.set_ylabel('Amplitude (mV)')
            self.axes.set_xlabel('Frequency (Hz)')
            self.axes.set_title('Real-time acquisition')
            self.axes.minorticks_on()
            self.axes.grid(b=True, which='major')
            self.axes.grid(b=True, which='minor', alpha=0.4)
            self.data_line, = self.axes.plot([], [], alpha=0.8)#,'-',color='C0')  # not needed, data_line is just a way to extract data if needed and to keep a single line instance to avoid deleting and creating a new plot every plotting loop


class Monitor(QtWidgets.QMainWindow):

    def __init__(self):
        super(Monitor, self).__init__()

        self.setWindowTitle("FFT plotter")

        # Queue
        self.queue = queue.Queue()
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(16) # 16 ms (60fps)
        self.timer.timeout.connect(self.sync)

        self.figureManager = FigureManager(self)  # Create canvas
        self.activate()
        self.show()

    def activate(self):
        self.timer.start() # Start calling sync every setInterval (ms)
        self.active = True

    def deactivate(self):
        self.timer.stop()
        self.active = False
        self.figureManager.canvas.stop_event_loop()  # Don't think it is necessary

    def plot(self,xlist,ylist):
        """Send data to queue"""

        self.queue.put([xlist,ylist])
        """https://stackoverflow.com/questions/59199702/how-to-make-plt-pause-work-if-last-open-figure-is-closed"""
        self.figureManager.canvas.start_event_loop(0.001)  # Allow plotting from driver without crash

    def sync(self):
        """ This function updates the data and then the figure.
        Function called by the timer """

        count = 0
        while not self.queue.empty():
            data = self.queue.get()  # purge queue to only plot last data
            count += 1

        # Upload the plot if new data available
        if count > 0 :
            xlist,ylist = data
            self.figureManager.update(xlist,ylist)

    def closeEvent(self,event):
        """ This function does some steps before the window is really killed """

        self.deactivate()


class FigureManager:

    def __init__(self,gui):
        """https://www.pythonguis.com/tutorials/plotting-matplotlib/"""

        # self.gui = gui
        self.canvas = MplCanvas(gui)
        toolbar = NavigationToolbar(self.canvas, gui)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        gui.setCentralWidget(widget)  # Add canvas+toolbar to Monitor

    def update(self,xlist,ylist):
        """ This function update the figure in the GUI """

        # (self.data_line,) = self.canvas.axes.plot(xlist, ylist)  # Not optimized
        self.canvas.data_line.set_data(xlist,ylist)
        # self.canvas.data_line.set_ydata(ylist)  # OPTIMIZE: could just update ylist if xlist is always the same (Need to give xlist at least once). But not the limiting factor here so don't bother.

        # Rescale plot
        self.canvas.axes.relim()
        self.canvas.axes.autoscale_view(True,True,True)

        self.redraw()

    def redraw(self):
        """ This function finalize the figure update in the GUI """

        try :
            self.canvas.fig.tight_layout()
        except:
            pass
        self.canvas.fig.canvas.draw()


class Driver():

    def __init__(self):
        self.monitor = None
        self.gui_name = "Plotter fft"  # If not defined, Autolab will take 'Custom GUI'

    def measurement_once(self):
        if self.monitor is not None and self.monitor.active:
            Freq = np.logspace(3, 9, 1001)
            IntdBmV = np.random.random(1002)  # Measurement will come here
            self.monitor.plot(Freq,IntdBmV[:-1])
        else:
            print("Can't plot data if plotter is closed")

    def measurement_loop(self):
        if self.monitor is not None and self.monitor.active:
            while self.monitor.active:  # Monitor stay active untile its window or Autolab is closed
                Freq = np.logspace(3, 9, 1001)
                IntdBmV = np.random.random(1002)  # Measurement will come here
                self.monitor.plot(Freq,IntdBmV[:-1])
        else:
            print("Can't plot data if plotter is closed")


    def openGUI(self):
        """ This function create the canvas.
        openGUI is a special name so Autolab can linked to it. Don't change it.
        Can only be called from Autolab's top menu, once the driver has been initialized by clicking on it in the controlcenter. """

        # Create monitor if doesn't exist
        if self.monitor is None:
            self.monitor = Monitor()
            self.monitor.active = False
        # If the monitor is not active, open it
        if not self.monitor.active:
            self.monitor.show()
            self.monitor.activateWindow()
            self.monitor.activate()
        # If the monitor is already running, just put it on front
        else:
            self.monitor.setWindowState(self.monitor.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.monitor.activateWindow()

    def closeGUI(self):
        """ This function make sure the canvas is stopped when the driver is closed."""

        self.monitor.deactivate()
        del self.monitor
        self.monitor = None


    def get_driver_model(self):
        """
        Used by the GUI
        """

        model = []

        model.append({'element':'action','name':'Measurement_loop',\
                      'do':self.measurement_loop})
        model.append({'element':'action','name':'Measurement_once',\
                      'do':self.measurement_once})
        # model.append({'element':'action','name':'openGUI',\
        #               'do':self.openGUI})  # BUG: can't just open it here because not in good thread

        return model


class Driver_EXAMPLE(Driver):
    def __init__(self):

        Driver.__init__(self)

    def close(self):
        self.closeGUI()  # If close autolab but let monitor openned, will continue to call plotting function!!
        pass

if __name__ == "__main__":
    Board = Driver_EXAMPLE()
    Board.openGUI()
    Board.measurement_loop()
    # Board.measurement_once()
