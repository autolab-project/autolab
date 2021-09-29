# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 15:11:17 2021

@author: Jonathan Peltier based on qchat
"""


class DataManager :

    def __init__(self,gui):

        self.gui = gui
        self.ct400 = self.gui.ct400

        self.targetWavelength = -1


    def setTargetWavelength(self,value):

        """ This function set the value of the target wavelength """

        self.targetWavelength = value


    def getTargetWavelength(self):

        """ This function returns the value of the target wavelength """

        return self.targetWavelength


    def deleteData(self, data_name):

        """ This function delete the data with the provided data name"""

        self.ct400.instance.interface.delete(data_name)  # raise error if don't exist


    def getAllData(self):
        return self.ct400.instance.data

    def getData_name(self):
        return self.ct400.instance._last_data_name

    def getData(self, data_name=None):

        """ This function returns the data with the provided data name """

        if data_name is None:
            data_name = self.ct400.instance._last_data_name
        else:
            self.ct400.instance._last_data_name = data_name


        data = self.ct400.instance.data.get(data_name, None)
        return data


    def save(self,filename):

        """ This function save the data with the provided filename"""

        self.ct400.instance.interface.save(filename)  # OPTIMIZE: could be better to save displayed data and not intern data in case intern data has changed


    def format_data_name(self, filename):
        return self.ct400.instance.interface.format_data_name(filename)


    def open(self, filename):

        """ This function open the data with the provided filename"""

        self.ct400.instance.interface.open(filename)


    def search_3db_wavelength(self, wl_max=-1):

        """ This function seachs and returns wavelength and power of FWHM markers """

        if wl_max == -1:
            wl_max = "default"

        results = dict(self.ct400.instance.interface.sweep_analyse(wl_max))
        wl_left = results["wl_3db_left"]
        wl_right = results["wl_3db_right"]
        wl_max = results["wl_max"]
        power_left = results["power_3db_left"]
        power_right = results["power_3db_right"]
        power_max = results["power_max"]

        wl = [wl_left, wl_max, wl_right]
        power = [power_left, power_max, power_right]
        return wl, power
