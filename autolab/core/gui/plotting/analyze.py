# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 21:26:10 2022

@author: jonathan
"""

import os
import time

import numpy as np
import pandas as pd

from .data import DataManager


class Data:
    pass

# TODO: merge data.py and analyze.py
# Currently set some data.py functions as staticmethod and imported them here

class AnalyzeManager :

    def __init__(self):

        self.data = DataModule()
        self.analyze = AnalyzeModule(self.data)

    def get_driver_model(self):

        config = []

        config.append({'element':'variable','name':'available_data',
                       'read':self.data.getNames,
                       'type':str,
                       'help':'List of stored data'})

        config.append({'element':'action','name':'open_prompt',
                       'do':self.data.import_data,
                       'help':'Open GUI prompt to add DataFrame'})

        config.append({'element':'action','name':'open',
                       'do':self.data.open,
                       "param_type":str,
                       'help':'Open data with the provided filename'})

        config.append({'element':'action','name':'delete',
                       'do':self.data.delete,
                       "param_type":str,
                       'help':'Delete data with the provided data_name'})

        config.append({'element':'module','name':'data','object':getattr(self,'data')})
        config.append({'element':'module','name':'analyze','object':getattr(self,'analyze')})


        return config



class AnalyzeModule:

    def __init__(self, data):
        self.data = data

        self.min = MinModule(self.data)
        self.max = MaxModule(self.data)
        self.mean = MeanModule(self.data)
        self.std = StdModule(self.data)
        self.bandwidth = BandwidthModule(self.data)


    def get_driver_model(self):

        config = []

        config.append({'element':'module','name':'min','object':getattr(self,'min')})
        config.append({'element':'module','name':'max','object':getattr(self,'max')})
        config.append({'element':'module','name':'mean','object':getattr(self,'mean')})
        config.append({'element':'module','name':'std','object':getattr(self,'std')})
        config.append({'element':'module','name':'bandwidth','object':getattr(self,'bandwidth')})

        return config



class DataModule:

    def __init__(self):

        self._sep = ","
        self._extension = ".txt"
        self._x_label = ""
        self._y_label = ""

        self._verbose = True
        self._remove_zero = True

        self._last_data_name = str()
        self._data = dict()


    def get_x_label(self):
        return self._x_label

    def set_x_label(self, value):
        key = str(value)
        keys = self.get_keys()
        if key in keys:
            self._x_label = key
        else:
            self._x_label = ""


    def get_y_label(self):
        return self._y_label

    def set_y_label(self, value):
        key = str(value)
        keys = self.get_keys()
        if key in keys:
            self._y_label = key
        else:
            self._y_label = ""


    def get_keys(self):
        data = self._data.get(self._last_data_name)
        if data is not None:
            return str(list(data.keys()))

    def getNames(self):
        return str(list(self._data.keys()))


    def get_data_name(self):
        return str(self._last_data_name)

    def set_data_name(self, name):
        self._last_data_name = str(name)


    def get_data(self):
        return pd.DataFrame(self._data.get(self._last_data_name))


    def delete(self, data_name):
        data_name = str(data_name)

        if self._data.get(data_name) is None:
            raise KeyError(f"No data find for the name: '{data_name}'. " \
                      f"Here is the list of available data: {self.getNames()}")

        self._data.pop(data_name)

        if data_name == self._last_data_name:
            self._last_data_name = ""

    def import_data(self):

        """ This function prompts the user for a configuration filename,
        and import the current scan configuration from it """

        from PyQt5 import QtWidgets
        # BUG: if open this prompt before Plotter, Scanner.., bad backend for GUI (old looking one) and can crash if not close immediately. Second time openned is ok
        filename = QtWidgets.QFileDialog.getOpenFileName(caption="Import DataFrame file",
                                                         filter="Text Files (*.txt);; Supported text Files (*.txt;*.csv;*.dat);; All Files (*)")[0]
        if filename != '':
            self.open(filename)


    def add_data(self, value):
        """  Open data from DataFrame """

        df = pd.DataFrame(value)
        self._open(df)


    def open(self, filename):
        """  Open data from file """

        data = DataManager._importData(filename)

        data_name = os.path.basename(filename)
        names_list = self.getNames()
        data_name = DataManager.getUniqueName(data_name, names_list)

        self._last_data_name = data_name

        self._open(data)

    def _open(self, df):
        """  Add data to dict """

        self._data[self._last_data_name] = df

        try:
            self.set_x_label(df.keys()[0])
        except:
            pass

        try:
            self.set_y_label(df.keys()[-1])
        except:
            pass

    def save(self, filename=None, data_name=None):

        """  Save data in txt file """

        if data_name is None:
            data_name = self._last_data_name

        data = self._data.get(data_name, None)

        if data is None:
            message = f"No data find for the name: '{data_name}'. " \
                      f"Here is the list of available data: {self.getNames()}"
            raise KeyError(message)

        if filename is None or filename == "":
            filename = self._last_data_name

        extension = os.path.splitext(filename)[1]

        if extension == "":
            filename += self._extension

        file_exist = os.path.exists(filename)

        if file_exist:
            raw_name, extension = os.path.splitext(filename)
            t = f"_{time.strftime('%Y%m%d-%H%M%S')}"
            filename = raw_name + t + extension


        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, sep=self._sep)

        if self._verbose:
            print(f"DataFrame {data_name} saved at {filename}")


    def get_driver_model(self):

        config = []

        config.append({'element':'variable','name':'data_name',
                       'read':self.get_data_name,'write':self.set_data_name,
                       'type':str,
                       'help':'Set data name'})

        config.append({'element':'variable','name':'data_keys',
                       'read':self.get_keys,
                       'type':str,
                       'help':'Data keys'})

        config.append({'element':'variable','name':'x_label',
                       'read':self.get_x_label,'write':self.set_x_label,
                       'type':str,
                       'help':'Set x_label to consider in analyze functions'})

        config.append({'element':'variable','name':'y_label',
                       'read':self.get_y_label,'write':self.set_y_label,
                       'type':str,
                       'help':'Set y_label to consider in analyze functions'})


        config.append({'element':'variable','name':'data','type':pd.DataFrame,
                       'read':self.get_data,
                       "help": "Return data stored at data_name"})

        config.append({'element':'action','name':'add_data',
                       'do':self.add_data,
                       'param_type':pd.DataFrame,
                       'help':'Add DataFrame to dict using data_name as key'})

        config.append({'element':'action','name':'save',
                       'do':self.save,
                       'param_type':str,
                       'help':'Save data with the provided filename'})

        return config



class MinModule:

    def __init__(self, data):
        self.data = data

    def x(self):
        index = np.argmin(self.data._data[self.data._last_data_name][self.data._y_label])
        return self.data._data[self.data._last_data_name][self.data._x_label][index]

    def y(self):
        return np.min(self.data._data[self.data._last_data_name][self.data._y_label])


    def get_driver_model(self):

        config = []

        config.append({'element':'variable','name':'x',
                       'read':self.x,
                       "type":float,
                       'help':'Returns the x value at which y is min'})

        config.append({'element':'variable','name':'y',
                        'read':self.y,
                        "type":float,
                        'help':'Returns the min y value'})

        return config


class MaxModule:

    def __init__(self, data):
        self.data = data

    def x(self):
        index = np.argmax(self.data._data[self.data._last_data_name][self.data._y_label])
        return self.data._data[self.data._last_data_name][self.data._x_label][index]

    def y(self):
        return np.max(self.data._data[self.data._last_data_name][self.data._y_label])


    def get_driver_model(self):

        config = []

        config.append({'element':'variable','name':'x',
                       'read':self.x,
                       "type":float,
                       'help':'Returns the x value at which y is max'})

        config.append({'element':'variable','name':'y',
                        'read':self.y,
                        "type":float,
                        'help':'Returns the max y value'})

        return config


class MeanModule:

    def __init__(self, data):
        self.data = data

    def x(self):
        return np.mean(self.data._data[self.data._last_data_name][self.data._x_label])

    def y(self):
        return np.mean(self.data._data[self.data._last_data_name][self.data._y_label])


    def get_driver_model(self):

        config = []

        config.append({'element':'variable','name':'x',
                        'read':self.x,
                        "type":float,
                        'help':'Returns the mean value of x array'})

        config.append({'element':'variable','name':'y',
                        'read':self.y,
                        "type":float,
                        'help':'Returns the mean value of y array'})


        return config


class StdModule:

    def __init__(self, data):
        self.data = data

    def x(self):
        return np.std(self.data._data[self.data._last_data_name][self.data._x_label])

    def y(self):
        return np.std(self.data._data[self.data._last_data_name][self.data._y_label])


    def get_driver_model(self):

        config = []

        config.append({'element':'variable','name':'x',
                        'read':self.x,
                        "type":float,
                        'help':'Returns the standard deviation of x array'})

        config.append({'element':'variable','name':'y',
                        'read':self.y,
                        "type":float,
                        'help':'Returns the standard deviation of y array'})

        return config


class BandwidthModule:

    def __init__(self, data):

        self.data = data
        self.results = self.init_variables()
        self._remove_zero = True
        self.comparator = True
        self._comparator = np.greater
        self.depth = 1
        self.level = -3.


    def init_variables(self):
        return {"x_left": 0, "y_left": -99,
               "x_right": 0, "y_right": -99,
                "x_max": 0, "y_max": -99}


    def get_x_left(self):
        return self.results["x_left"]

    def get_x_right(self):
        return self.results["x_right"]

    def get_x_max(self):
        return self.results["x_max"]

    def get_y_left(self):
        return self.results["y_left"]

    def get_y_right(self):
        return self.results["y_right"]

    def get_y_max(self):
        return self.results["y_max"]


    def get_depth(self):
        """ This function returns the value of the algorithm depth to find the local maximum """

        return int(self.depth)

    def set_depth(self,value):
        """ This function set the value of the algorithm depth to find the local maximum """

        self.depth = int(value)

    def get_level(self):
        """ This function returns the value of the drop in dB for the bandwitdh """

        return float(self.level)

    def set_level(self,value):
        """ This function set the value of the drop in dB for the bandwitdh """

        self.level = float(value)


    def get_comparator(self):
        """ This function returns the comparator state """

        return bool(int(float(self.comparator)))

    def set_comparator(self,value):
        """ This function set the comparator state """

        self.comparator = bool(int(float(value)))
        self._comparator = np.greater if self.comparator is True else np.less


    def search_bandwitdh(self, x_max="default", depth="default", level="default", comparator="default"):

        if depth == "default":
            depth = self.depth

        if level == "default":
            level = self.level

        if comparator == "default":
            comparator = self._comparator

        try:
            dataset = self.data._data
            data = dataset[self.data._last_data_name]

            variable_x = self.data._x_label
            variable_y = self.data._y_label

            x_data, y_data = np.array(data[variable_x]), np.array(data[variable_y])

            self.results = sweep_analyse(x_data, y_data,
                x_max=x_max, depth=depth, level=level, remove_zero=self._remove_zero, comparator=comparator)

        except Exception as error:
            print("Couldn't find the bandwitdh:", error)
            self.results = self.init_variables()

        return self.results


    def get_driver_model(self):

        config = []

        config.append({'element':'action','name':'search_bandwitdh_global',
                       'do':self.search_bandwitdh,
                       'help':'Find the bandwitdh around the global maximum peak'})

        config.append({'element':'action','name':'search_bandwitdh_local',
                        'do':self.search_bandwitdh,
                        "param_type":float,
                        'help':'Find the bandwitdh around the local peak closed to the defined wavelength'})

        config.append({'element':'variable','name':'x_left',
                       'read':self.get_x_left,
                       'type':float,
                       'help':'Return x_left value'})

        config.append({'element':'variable','name':'x_right',
                       'read':self.get_x_right,
                       'type':float,
                       'help':'Return x_right value'})

        config.append({'element':'variable','name':'x_max',
                       'read':self.get_x_max,
                       'type':float,
                       'help':'Return x_max value'})

        config.append({'element':'variable','name':'y_left',
                       'read':self.get_y_left,
                       'type':float,
                       'help':'Return y_left value'})

        config.append({'element':'variable','name':'y_right',
                       'read':self.get_y_right,
                       'type':float,
                       'help':'Return y_right value'})

        config.append({'element':'variable','name':'y_max',
                       'read':self.get_y_max,
                       'type':float,
                       'help':'Return y_max value'})

        config.append({'element':'variable','name':'depth',
                       'read':self.get_depth,
                       'write':self.set_depth,
                       'type':int,
                       'help':'Set algorithm depth to find the local maximum'})

        config.append({'element':'variable','name':'comparator',
                       'read':self.get_comparator,
                       'write':self.set_comparator,
                       'type':bool,
                       'help':'Set comparator state. True for greater and False for less'})

        config.append({'element':'variable','name':'level',
                       'read':self.get_level,
                       'write':self.set_level,
                       'type':float,
                       'help':'Set drop level in dB for the bandwidth'})

        return config


def sweep_analyse(x_data, y_data, x_max="default", depth=1, level=-3, remove_zero=True, comparator=np.greater):
    """ x_max : x value close to the desired maximum y """
    # OPTIMIZE: put back this line -> data = data.dropna()  # BUG: crash python if ct400 dll loaded
    # x_data, y_data = np.array(data[variable_x]), np.array(data[variable_y])
    if remove_zero:
        keep_data = y_data != 0  # used to remove unwanted data if loading interpolated sweep
        y_data = y_data[keep_data]
        x_data = x_data[keep_data]

    if x_max != "default":

        order = lambda x: (((x-1) % 3)**2 + 1)*10**abs((x-1)//3)
        order_array = order(np.arange(1, depth+1))
        # order_array = np.array([1, 2, 5, 10, 20, 50, 100, 200])  # result if depth=6
        data = list()

        for order in order_array:  # search local maximum with different filter setting
            maximum_filter = find_local_maximum(x_data, y_data, x_max, order=order, level=level, comparator=comparator)
            point = {"x": maximum_filter.x, "y": maximum_filter.y}
            data.append(point)

        df = pd.DataFrame(data)

        x_candidates = df['x'].mode().values  # wavelength with the most occurences (could have several wavelength with same occurance)

        condition = np.abs(x_candidates - x_max)  # take wavelength closer to target if several x points found
        index = np.where(condition == np.min(condition))[0][0]

        maximum = Data()
        maximum.x = x_candidates[index]

        index2 = np.where(x_data == maximum.x)[0][0]
        maximum.y = y_data[index2]

    else:
        # get maximum y_data and change it only if user want a different x_max
        maximum = Data()
        if comparator is np.greater:
            maximum.y = np.max(y_data)
            maximum.index = np.argmax(y_data)
        elif comparator is np.less:
            maximum.y = np.min(y_data)
            maximum.index = np.argmin(y_data)
        maximum.x = x_data[maximum.index]

    # df.hist()  # used to see the selection process
    quadrature_left, quadrature_right = find_3db(x_data, y_data, maximum, level=level, interp=True, comparator=comparator)

    results = {"x_left": quadrature_left.x, "y_left": quadrature_left.y,
               "x_right": quadrature_right.x, "y_right": quadrature_right.y,
               "x_max": maximum.x, "y_max": maximum.y}

    return results


def find_local_maximum(x_data, y_data, x_max, order=10, level=-3, comparator=np.greater):

    """ Find local maximum with wl close to x_max.
        order is used to filter local maximum. """

    from scipy.signal import argrelextrema

    maximum_array = Data()
    maximum_array.index = argrelextrema(y_data, comparator, order=order)[0]

    if len(y_data) > 1:
        if y_data[-1] > y_data[-2]:
            maximum_array.index = np.append(maximum_array.index, len(y_data)-1)

        if y_data[0] > y_data[1]:
            maximum_array.index = np.insert(maximum_array.index, 0, 0)

    if maximum_array.index.shape[0] != 0:

        maximum_array.x = x_data[maximum_array.index]
        maximum_array.y = y_data[maximum_array.index]

        condition = np.abs(maximum_array.x - x_max)

        index = np.where(condition == np.min(condition))[0][0]

        maximum_filter = Data()
        maximum_filter.index = index
        maximum_filter.x = maximum_array.x[index]  # maximum wavelength from filter maximum list
        maximum_filter.y = maximum_array.y[index]

        maximum = find_maximum_from_maximum_filter(x_data, y_data, maximum_filter, level=level, comparator=comparator)
    else:
        maximum_raw = Data()
        maximum_raw.y = np.max(y_data)
        maximum_raw.index = np.argmax(y_data)
        maximum_raw.x = x_data[maximum_raw.index]
        maximum = maximum_raw

    return maximum


def find_maximum_from_maximum_filter(x_data, y_data, maximum_filter, level=-3, comparator=np.greater):

    quadrature_filter_left, quadrature_filter_right = find_3db(x_data, y_data, maximum_filter, level=level, comparator=comparator)

    interval_low_index = np.where(x_data <= quadrature_filter_left.x)[0][-1]
    interval_high_index = np.where(x_data >= quadrature_filter_right.x)[0][0]

    if interval_high_index == 0:
        interval_high_index = None  # To avoid removing all the data

    new_interval = Data()
    new_interval.x = x_data[interval_low_index: interval_high_index+1]
    new_interval.y = y_data[interval_low_index: interval_high_index+1]

    maximum = Data()
    if comparator is np.greater:
        maximum.index = np.argmax(new_interval.y)
    elif comparator is np.less:
        maximum.index = np.argmin(new_interval.y)
    maximum.x = new_interval.x[maximum.index]
    maximum.y = new_interval.y[maximum.index]

    return maximum


def find_3db(x_data, y_data, maximum, interp=False, level=-3, comparator=np.greater):
    condition = np.abs(x_data - maximum.x)
    index = np.argmin(condition)

    x_left = x_data[:index+1][::-1]  # Reverse order to start at maximum
    x_right = x_data[index:]

    y_left = y_data[:index+1][::-1]
    y_right = y_data[index:]

    quadrature_target = Data()
    quadrature_target.y = maximum.y + level

    # left 3db
    if level <= 0:
        index = np.where(y_left <= quadrature_target.y)[0]
    else:
        index = np.where(y_left >= quadrature_target.y)[0]

    quadrature_target.index = -1 if index.shape[0] == 0 else index[0]

    if len(x_left) != 0:
        quadrature_target.x = x_left[quadrature_target.index]

        condition = np.abs(x_data - quadrature_target.x)
        index = np.where(condition == np.min(condition))[0][0]

        quadrature_left = interp_3db(x_data, y_data, index, quadrature_target.y, "left", interp=interp, comparator=comparator)
    else:
        quadrature_left = Data()
        try:
            quadrature_left.x = x_data[0]
            quadrature_left.y = y_data[0]
        except:
            quadrature_left.x = None
            quadrature_left.y = None

    # right 3db
    if level <= 0:
        index = np.where(y_right <= quadrature_target.y)[0]
    else:
        index = np.where(y_right >= quadrature_target.y)[0]

    quadrature_target.index = -1 if index.shape[0] == 0 else index[0]

    if len(x_right) != 0:
        quadrature_target.x = x_right[quadrature_target.index]

        condition = np.abs(x_data - quadrature_target.x)
        index = np.where(condition == np.min(condition))[0][0]

        quadrature_right = interp_3db(x_data, y_data, index, quadrature_target.y, "right", interp=interp, comparator=comparator)
    else:
        quadrature_right = Data()
        try:
            quadrature_left.x = x_data[-1]
            quadrature_left.y = y_data[-1]
        except:
            quadrature_right.x = None
            quadrature_right.y = None


    return quadrature_left, quadrature_right


def interp_3db(x_data, y_data, index, target, direction, interp=False, comparator=np.greater):

    x1 = x_data[index]
    y1 = y_data[index]

    if interp and ((y1 <= target and comparator is np.greater) or (y1 >= target and comparator is np.less)):

        assert direction in ("left", "right")

        if direction == "right":
            next_index = index-1
        elif direction == "left":
            next_index = index+1


        x2 = x_data[next_index]
        y2 = y_data[next_index]

        a = (y2 - y1) / (x2 - x1)
        b = y1 - a*x1
        y = target
        x = (y - b) / a
    else:
        x = x1
        y = y1

    quadrature = Data()
    quadrature.x = x
    quadrature.y = y

    return quadrature
