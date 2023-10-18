# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 21:04:12 2022

@author: jonathan
"""

from custom_GUI import GUI
import numpy as np


class Driver(GUI):
    """ Use GUI to plot data """

    def __init__(self):
        GUI.__init__(self)
        self.gui_name = "Plotter fft"  # If not defined, Autolab will take 'Custom GUI'
        self.set_ylabel('Amplitude (mV)')
        self.set_xlabel('Frequency (Hz)')
        self.set_title('Real-time acquisition')

    def measurement_once(self):
        if self.monitor is not None and self.monitor.active:
            Freq = np.logspace(3, 9, 1001)
            IntdBmV = np.random.random(1002)  # Measurement will come here
            self.plot(Freq,IntdBmV[:-1])
        else:
            print("Can't plot data if plotter is closed")

    def measurement_loop(self):
        if self.monitor is not None and self.monitor.active:
            while self.monitor.active:  # Monitor stay active untile its window or Autolab is closed
                Freq = np.logspace(3, 9, 1001)
                IntdBmV = np.random.random(1002)  # Measurement will come here
                self.plot(Freq,IntdBmV[:-1])
        else:
            print("Can't plot data if plotter is closed")

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
    Board.openGUI(main=True)
    Board.measurement_loop()
    # Board.measurement_once()
