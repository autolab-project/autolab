# -*- coding: utf-8 -*-
"""
Created on Mon Jul 19 22:39:47 2021

@author: jonathan
"""

import os
import time

import numpy as np
import pandas as pd

from scipy.signal import argrelextrema



class Data:
    pass


class Interface():  # TODO: delete or merge with Autolab plotting.analyze which is the improved version of Interface

    def __init__(self, dev):

        self.dev = dev
        self._x_label = "L"
        self._y_label = "1"
        self._init_variables()

        self.verbose = True
        self._remove_zero = True


    def _init_variables(self):
        self._results = {"wl_3db_left": 0, "power_3db_left": -99,
                         "wl_3db_right": 0, "power_3db_right": -99,
                         "wl_max": 0, "power_max": -99}

    def getNames(self):
        return list(self.dev.data.keys())

    def get_data_name(self):
        return str(self.dev._last_data_name)

    def set_data_name(self, name):
        self.dev._last_data_name = str(name)


    def get_3db_wavelength_left(self):
        return self._results["wl_3db_left"]

    def get_3db_wavelength_right(self):
        return self._results["wl_3db_right"]

    def get_wavelength_max(self):
        return self._results["wl_max"]


    def search_3db_wavelength(self, wl_max="default", data_name=None):

        try:
            self._results = self.sweep_analyse(
                wl_max=wl_max, data_name=data_name)

        except Exception as error:
            print("Couldn't find the 3dB wavelength:", error)
            self._init_variables()


    def delete(self, data_name):
        data_name = str(data_name)

        if data_name == self.dev._last_data_name:
            self.dev._last_data_name = ""

        check_item_exist = self.dev.data.get(data_name)

        if check_item_exist is None:
            available_data = self.getNames()
            raise AttributeError(f"No data find for the name: '{data_name}'. " \
                      f"Here is the list of available data: {available_data}")

        self.dev.data.pop(data_name)


    def format_data_name(self, filename):

        """ Format the filename and also returns the corresponding the data_name """

        if not os.path.exists(filename):
            raw_name, extension = os.path.splitext(filename)

            if os.path.exists(raw_name):
                filename = raw_name
            elif extension != ".txt":
                filename += ".txt"

        raw_name, extension = os.path.splitext(filename)

        if extension == ".txt":
            data_name = os.path.basename(raw_name)
        else:
            data_name = os.path.basename(filename)

        return filename, data_name

    def getUniqueName(self,basename):

        """ This function adds a number next to basename in case this basename is already taken """

        names = self.getNames()
        name = basename

        compt = 0
        while True :
            if name in names :
                compt += 1
                name = basename+'_'+str(compt)
            else :
                break
        return name


    def open(self, filename):

        """  Open sweep data from file """

        filename, data_name = self.format_data_name(filename)

        sweep_data = pd.read_csv(filename, delimiter=" ")

        if list(sweep_data.keys()) != ["L", "O", "1"]:
            sweep_data = pd.read_csv(filename, delimiter=",")

            if list(sweep_data.keys()) != ["L", "O", "1"]:
                sweep_data = pd.read_csv(filename, delimiter=";")

                if list(sweep_data.keys()) != ["L", "O", "1"]:
                    sweep_data = pd.read_csv(filename, delimiter="\t")
                    assert list(sweep_data.keys()) == ["L", "O", "1"], "Bad data format. Need labels: 'L O 1'"

        data_name = self.getUniqueName(data_name)

        self.dev._last_data_name = data_name
        self.dev.data[data_name] = sweep_data


    def save(self, filename=None, data_name=None, save_interp=True):

        """  Save sweep data in txt file """

        if data_name is None:
            data_name = self.dev._last_data_name

        data_name, extension = os.path.splitext(data_name)
        if extension == ".txt":
            extension = ""
        data_name = data_name + extension
        data_name = os.path.basename(data_name)

        data = self.dev.data.get(data_name, None)

        if data is None:
            available_data = self.getNames()
            message = f"No data find for the name: '{data_name}'. " \
                      f"Here is the list of available data: {available_data}"
            raise KeyError(message)

        if filename is None or filename == "":
            filename = self.dev._last_data_name+".txt"

        extension = os.path.splitext(filename)[1]

        if extension != ".txt":
            filename = filename + ".txt"

        file_exist = os.path.exists(filename)
        raw_name, extension = os.path.splitext(filename)

        if file_exist:
            t = time.strftime("%Y%m%d-%H%M%S")
            t = f"_{t}"
            filename = raw_name + t + extension

        df = pd.DataFrame(data)

        df_data = df.copy() # used to change format rounding in saved file
        df_data['L'] = df_data['L'].map(lambda x: '%1.3f' % x)
        df_data['O'] = df_data['O'].map(lambda x: '%1.2f' % x)
        df_data['1'] = df_data['1'].map(lambda x: '%1.2f' % x)

        df_data.to_csv(filename, index=False, sep=" ")

        if self.verbose:
            print("Sweep data saved:", filename)

        # try to also save interp data  " OBSOLETE: if want interp data, must uncomment in _get_data_sweep in yenista_CT400.py
        data_name_interp = data_name+"_interp"
        data_interp = self.dev.data.get(data_name_interp, None)

        if save_interp and data_interp is not None:

            if file_exist:
                filename_interp = raw_name + t + "_interp" + extension
            else:
                filename_interp = raw_name + "_interp" + extension

            df = pd.DataFrame(data_interp)

            df_data = df.copy()
            df_data['L'] = df_data['L'].map(lambda x: '%1.3f' % x)
            df_data['O'] = df_data['O'].map(lambda x: '%1.2f' % x)
            df_data['1'] = df_data['1'].map(lambda x: '%1.2f' % x)

            df_data.to_csv(filename_interp, index=False, sep=" ")

            if self.verbose:
                print("Interpolated sweep data saved:", filename_interp)


    def sweep_analyse(self, wl_max="default", data_name=None):

        """ wl_max : wavelength close to the desired maximum power """

        if data_name is None:
            data_name = self.dev._last_data_name

        data = self.dev.data.get(data_name, None)

        if data is None:
            raise IndexError("Could not find the asked data_name: '%s'.\nAvailable data: %s" % (data_name, self.getNames()))

        data = data.dropna()
        # wl, ref, power = np.array(data["L"]), np.array(data["O"]), np.array(data["1"])
        wl, power = np.array(data[self._x_label]), np.array(data[self._y_label])
        if self._remove_zero:
            keep_data = power != 0  # used to remove unwanted data if loading interpolated sweep
            power = power[keep_data]
            wl = wl[keep_data]
        # ref = ref[keep_data]

        if wl_max != "default":

            order_array = np.array([1, 10, 20, 50, 100, 200])
            data = list()

            for order in order_array:  # search local maximum with different filter setting
                maximum_filter = self.find_local_maximum(wl, power, wl_max, order=order)

                point = {"wl": maximum_filter.wl, "power": maximum_filter.power}
                data.append(point)

            df = pd.DataFrame(data)

            wl_candidates = df['wl'].mode().values  # wavelength with the most occurences (could have several wavelength with same occurance)

            condition = np.abs(wl_candidates - wl_max)  # take wavelength closer to target if several wl found
            index = np.where(condition == np.min(condition))[0][0]

            maximum = Data()
            maximum.wl = wl_candidates[index]

            index2 = np.where(wl == maximum.wl)[0][0]
            maximum.power = power[index2]

        else:
            # get maximum power and change it only if user want a different wl_max
            maximum = Data()
            maximum.power = np.max(power)
            maximum.index = np.where(power == maximum.power)[0][0]
            maximum.wl = wl[maximum.index]

        # df.hist()  # used to see the selection process
        quadrature_left, quadrature_right = self.find_3db(wl, power, maximum, interp=True)

        self._results = {"wl_3db_left": quadrature_left.wl, "power_3db_left": quadrature_left.power,
                         "wl_3db_right": quadrature_right.wl, "power_3db_right": quadrature_right.power,
                         "wl_max": maximum.wl, "power_max": maximum.power}

        return self._results


    def find_local_maximum(self, wl, power, wl_max, order=10):

        """ Find local maximum with wl close to wl_max.
            order is used to filter local maximum. """

        maximum_array = Data()
        maximum_array.index = argrelextrema(power, np.greater, order=order)[0]

        if maximum_array.index.shape[0] != 0:

            maximum_array.wl = wl[maximum_array.index]
            maximum_array.power = power[maximum_array.index]

            condition = np.abs(maximum_array.wl - wl_max)

            index = np.where(condition == np.min(condition))[0][0]

            maximum_filter = Data()
            maximum_filter.index = index
            maximum_filter.wl = maximum_array.wl[index]  # maximum wavelength from filter maximum list
            maximum_filter.power = maximum_array.power[index]

            maximum = self.find_maximum_from_maximum_filter(wl, power, maximum_filter)
        else:
            maximum_raw = Data()
            maximum_raw.power = np.max(power)
            maximum_raw.index = np.argmax(power)
            # maximum_raw.index = np.where(power == maximum_raw.power)[0][0]
            maximum_raw.wl = wl[maximum_raw.index]
            maximum = maximum_raw

        return maximum

    def find_maximum_from_maximum_filter(self, wl, power, maximum_filter):
        quadrature_filter_left, quadrature_filter_right = self.find_3db(wl, power, maximum_filter)

        interval_low_index = np.where(wl <= quadrature_filter_left.wl)[0][-1]
        interval_high_index = np.where(wl >= quadrature_filter_right.wl)[0][0]

        if interval_high_index == 0:
            interval_high_index = None  # To avoid removing all the data

        new_interval = Data()
        new_interval.wl = wl[interval_low_index: interval_high_index]
        new_interval.power = power[interval_low_index: interval_high_index]

        maximum = Data()
        maximum.index = np.argmax(new_interval.power)
        # maximum.index = np.where(new_interval.power == np.max(new_interval.power))[0][0]
        maximum.wl = new_interval.wl[maximum.index]
        maximum.power = new_interval.power[maximum.index]

        return maximum

    def find_3db(self, wl, power, maximum, interp=False):

        condition = np.abs(wl - maximum.wl)
        index = np.argmin(condition)

        # index = np.where(condition == np.min(condition))[0][0]
        wl_left = wl[:index][::-1]  # Reverse order to start at maximum
        wl_right = wl[index:]
        power_left = power[:index][::-1]
        power_right = power[index:]

        quadrature_target = Data()
        quadrature_target.power = maximum.power - 3

        # left 3db
        index = np.where(power_left <= quadrature_target.power)[0]
        quadrature_target.index = -1 if index.shape[0] == 0 else index[0]

        if len(wl_left) != 0:
            quadrature_target.wl = wl_left[quadrature_target.index]

            condition = np.abs(wl - quadrature_target.wl)
            index = np.where(condition == np.min(condition))[0][0]

            quadrature_left = self.interp_3db(wl, power, index, quadrature_target.power, "left", interp=interp)
        else:
            quadrature_left = Data()
            quadrature_left.wl = None
            quadrature_left.power = None


        # right 3db
        index = np.where(power_right <= quadrature_target.power)[0]
        quadrature_target.index = -1 if index.shape[0] == 0 else index[0]

        if len(wl_right) != 0:
            quadrature_target.wl = wl_right[quadrature_target.index]

            condition = np.abs(wl - quadrature_target.wl)
            index = np.where(condition == np.min(condition))[0][0]

            quadrature_right = self.interp_3db(wl, power, index, quadrature_target.power, "right", interp=interp)
        else:
            quadrature_right = Data()
            quadrature_right.wl = None
            quadrature_right.power = None


        return quadrature_left, quadrature_right


    def interp_3db(self, wl, power, index, target, direction, interp=False):

        x1 = wl[index]
        y1 = power[index]

        if interp and y1 <= target:

            assert direction in ("left", "right")

            if direction == "right":
                next_index = index-1
            elif direction == "left":
                next_index = index+1


            x2 = wl[next_index]
            y2 = power[next_index]

            a = (y2 - y1) / (x2 - x1)
            b = y1 - a*x1
            y = target
            x = (y - b) / a
        else:
            x = x1
            y = y1

        quadrature = Data()
        quadrature.wl = x
        quadrature.power = y

        return quadrature


    def get_driver_model(self):

        config = []

        config.append({'element':'variable','name':'data_name',
                       'read':self.get_data_name,'write':self.set_data_name,
                       'type':str,
                       'help':'Set the data name'})

        config.append({'element':'action','name':'save',
                       'do':self.save,
                       'param_type':str,
                       'help':'Save sweep data with the provided filename'})

        config.append({'element':'action','name':'open',
                       'do':self.open,
                       "param_type":str,
                       'help':'Open sweep data with the provided filename'})

        config.append({'element':'action','name':'delete',
                       'do':self.delete,
                       "param_type":str,
                       'help':'Delete sweep data with the provided data name'})

        config.append({'element':'action','name':'search_3db_wavelength_max',
                       'do':self.search_3db_wavelength,
                       'help':'Find the 3dB wavelength around the global maximum peak'})

        config.append({'element':'action','name':'search_3db_wavelength',
                        'do':self.search_3db_wavelength,
                        "param_type":float,
                        'help':'Find the 3dB wavelengths around the local peak closed to the defined wavelength'})

        config.append({'element':'variable','name':'get_3db_wavelength_left',
                       'read':self.get_3db_wavelength_left,
                       'type':float,'unit':'nm',
                       'help':'Return the previously calculated left 3dB wavelength in nm'})

        config.append({'element':'variable','name':'get_3db_wavelength_right',
                       'read':self.get_3db_wavelength_right,
                       'type':float,'unit':'nm',
                       'help':'Return the previously calculated right 3dB wavelength in nm'})

        config.append({'element':'variable','name':'get_wavelength_max',
                       'read':self.get_wavelength_max,
                       'type':float,'unit':'nm',
                       'help':'Return the previously calculated maximum wavelength in nm'})
        return config
