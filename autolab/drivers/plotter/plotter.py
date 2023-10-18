# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 21:26:10 2022

@author: jonathan
"""

import csv

import numpy as np
import pandas as pd


try:
    from pandas._libs.lib import no_default
except:
    no_default = None


def find_delimiter(filename):
    sniffer = csv.Sniffer()
    with open(filename) as fp:
        try:
            text = fp.read(5000)
            if text.startswith("#"):
                text = text[len(text.split("\n")[0])+len("\n"):]
            delimiter = sniffer.sniff(text).delimiter
        except:
            # delimiter = ","  # only 1 column
            delimiter = no_default
        if delimiter in ("e", "."):  # sniffer got it wrong
            delimiter = no_default
    return delimiter


def _skiprows(filename):
    with open(filename) as fp:
        skiprows = 1 if fp.read(1) == "#" else None
    return skiprows


def find_header(filename, sep=no_default, skiprows=None):
    df = pd.read_csv(filename, sep=sep, header=None, nrows=5, skiprows=skiprows)
    try:
        first_row = df.iloc[0].values.astype("float")
        return "infer" if tuple(first_row) == tuple([i for i in range(len(first_row))]) else None
    except:
        pass
    df_header = pd.read_csv(filename, sep=sep, nrows=5)

    return "infer" if tuple(df.dtypes) != tuple(df_header.dtypes) else None


def formatData(data):
    """ Format data """

    try:
        data = pd.DataFrame(data)
    except ValueError:
        data = pd.DataFrame([data])
    data.columns = data.columns.astype(str)
    data_type = data.values.dtype
    data[data.columns] = data[data.columns].apply(pd.to_numeric, errors="coerce")
    assert not data.isnull().values.all(), f"Datatype '{data_type}' not supported"

    if data.shape[1] == 1:
        data.rename(columns = {'0':'1'}, inplace=True)
        data.insert(0, "0", range(data.shape[0]))
    return data


def importData(filename):
    """ This function open the data with the provided filename """

    skiprows = _skiprows(filename)
    sep = find_delimiter(filename)
    header = find_header(filename, sep, skiprows)
    try:
        data = pd.read_csv(filename, sep=sep, header=header, skiprows=skiprows)
    except:
        data = pd.read_csv(filename, sep="\t", header=header, skiprows=skiprows)

    data = formatData(data)
    return data


class AnalyzeManager :

    def __init__(self, gui=None):

        if gui:
            self.gui = gui
            self.ax = self.gui.figureManager.ax
            self.cursor_left_y = self.ax.plot([None],[None],'--',color='grey', label="Cursor left y")[0]
            self.cursor_right_y = self.ax.plot([None],[None],'--',color='grey', label="Cursor right y")[0]
            self.cursor_extremum = self.ax.plot([None],[None],'--',color='grey', label="Cursor max")[0]
            self.cursor_left_x = self.ax.plot([None],[None],'--',color='grey', label="Cursor left x")[0]
            self.cursor_right_x = self.ax.plot([None],[None],'--',color='grey', label="Cursor right x")[0]

        self.data = pd.DataFrame()
        self.x_label = ""
        self.y_label = ""
        self.isDisplayCursor = False

        self.info = DataModule(self)
        self.min = MinModule(self)
        self.max = MaxModule(self)
        self.mean = MeanModule(self)
        self.std = StdModule(self)
        self.bandwidth = BandwidthModule(self)

    def get_displayCursor(self):
        return bool(self.isDisplayCursor)

    def set_displayCursor(self, value):
        value = bool(int(float(value)))
        self.isDisplayCursor = value
        self.refresh(self.data)

    def get_x_label(self):
        return self.x_label

    def set_x_label(self, value):
        key = str(value)
        keys = self.get_keys()
        if key in keys:
            self.x_label = key
        else:
            self.x_label = ""


    def get_y_label(self):
        return self.y_label

    def set_y_label(self, value):
        key = str(value)
        keys = self.get_keys()
        if key in keys:
            self.y_label = key
        else:
            self.y_label = ""


    def get_keys(self):
        if self.data is not None:
            return str(list(self.data.keys()))

    def get_data(self):
        return pd.DataFrame(self.data)


    def set_data(self, value):
        """  Open data from DataFrame """

        df = formatData(value)
        self._open(df)


    def open(self, filename):
        """  Open data from file """

        data = importData(filename)

        self._open(data)

    def _open(self, df):
        """  Add data to dict """

        self.data = df

        try:
            self.set_x_label(df.keys()[0])
        except:
            pass

        try:
            self.set_y_label(df.keys()[-1])
        except:
            pass

    def refresh(self, data):
        """ Called by plotter"""

        if hasattr(self, "gui"):
            self.set_data(data)

            if self.isDisplayCursor:
                target_x = self.bandwidth.target_x
                level = self.bandwidth.level
                comparator = self.bandwidth._comparator
                depth = self.bandwidth.depth
                try:
                    self.bandwidth.search_bandwitdh(target_x, level=level, comparator=comparator, depth=depth)
                except Exception as error:
                    if str(error) == "Empty dataframe":
                        self.displayCursors([(None,None)]*3)
                    else:
                        self.gui.statusBar.showMessage(f"Can't display markers: {error}",10000)
            else:
                self.displayCursors([(None,None)]*3)

    def refresh_gui(self):
        if hasattr(self, "gui") and self.isDisplayCursor:
            results = self.bandwidth.results
            cursors_coordinate = (results["left"], results["extremum"], results["right"])

            try:
                self.displayCursors(cursors_coordinate)
            except Exception as error:
                self.gui.statusBar.showMessage(f"Can't display markers: {error}",10000)

    def displayCursors(self, cursors_coordinate):

        if hasattr(self, "gui"):
            assert len(cursors_coordinate) == 3, f"This function only works with 3 cursors, {len(cursors_coordinate)} were given"
            xmin, xmax = -1e99, 1e99
            ymin, ymax = -1e99, 1e99
            (left, extremum, right) = cursors_coordinate

            # left cursor
            self.cursor_left_y.set_xdata([left[0], left[0]])
            self.cursor_left_y.set_ydata([ymin, ymax])

            # right cursor
            self.cursor_right_y.set_xdata([right[0], right[0]])
            self.cursor_right_y.set_ydata([ymin, ymax])

            # extremum cursor
            self.cursor_extremum.set_xdata([xmin, xmax])
            self.cursor_extremum.set_ydata([extremum[1], extremum[1]])

            # left 3db marker
            self.cursor_left_x.set_xdata([xmin, xmax])
            self.cursor_left_x.set_ydata([left[1], left[1]])

            # right 3db marker
            self.cursor_right_x.set_xdata([xmin, xmax])
            self.cursor_right_x.set_ydata([right[1], right[1]])

            # remove right 3db marker if same as left
            if left[1] == right[1]:
                self.cursor_right_x.set_xdata([None, None])
                self.cursor_right_x.set_ydata([None, None])

            self.gui.figureManager.redraw()

    def get_driver_model(self):

        config = []

        if hasattr(self, "gui"):
            config.append({'element':'variable','name':'displayCursor','type':bool,
                           'read':self.get_displayCursor, 'write':self.set_displayCursor,
                           "help": "Select if want to display cursors"})
        else:
            config.append({'element':'module','name':'info','object':getattr(self,'info')})

            config.append({'element':'action','name':'open',
                           'do':self.open,
                           "param_type":str,
                           "param_unit":"filename",
                           'help':'Open data with the provided filename'})

            config.append({'element':'variable','name':'data','type':pd.DataFrame,
                           'read':self.get_data,
                           "help": "Return data stored at data_name"})

            config.append({'element':'action','name':'set_data',
                            'do':self.set_data,
                            'param_type':pd.DataFrame,
                            'help':'Add DataFrame to dict using data_name as key'})

        config.append({'element':'module','name':'min','object':getattr(self,'min')})
        config.append({'element':'module','name':'max','object':getattr(self,'max')})
        config.append({'element':'module','name':'mean','object':getattr(self,'mean')})
        config.append({'element':'module','name':'std','object':getattr(self,'std')})
        config.append({'element':'module','name':'bandwidth','object':getattr(self,'bandwidth')})

        return config

    def close(self):
        self.displayCursors([(None,None)]*3)


class Driver_DEFAULT(AnalyzeManager):
    def __init__(self, gui=None):

        AnalyzeManager.__init__(self, gui=gui)


class DataModule:

    def __init__(self, analyzer):

        self.analyzer = analyzer


    def get_driver_model(self):

        config = []

        config.append({'element':'variable','name':'keys',
                       'read':self.analyzer.get_keys,
                       'type':str,
                       'help':'Data keys'})

        config.append({'element':'variable','name':'x_label',
                       'read':self.analyzer.get_x_label,'write':self.analyzer.set_x_label,
                       'type':str,
                       'help':'Set x_label to consider in analyze functions'})

        config.append({'element':'variable','name':'y_label',
                       'read':self.analyzer.get_y_label,'write':self.analyzer.set_y_label,
                       'type':str,
                       'help':'Set y_label to consider in analyze functions'})


        return config



class MinModule:

    def __init__(self, analyzer):
        self.analyzer = analyzer

    def x(self):
        index = np.argmin(self.analyzer.data[self.analyzer.y_label])
        return self.analyzer.data[self.analyzer.x_label][index]

    def y(self):
        return np.min(self.analyzer.data[self.analyzer.y_label])


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

    def __init__(self, analyzer):
        self.analyzer = analyzer

    def x(self):
        index = np.argmax(self.analyzer.data[self.analyzer.y_label])
        return self.analyzer.data[self.analyzer.x_label][index]

    def y(self):
        return np.max(self.analyzer.data[self.analyzer.y_label])


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

    def __init__(self, analyzer):
        self.analyzer = analyzer

    def x(self):
        return np.mean(self.analyzer.data[self.analyzer.x_label])

    def y(self):
        return np.mean(self.analyzer.data[self.analyzer.y_label])


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

    def __init__(self, analyzer):
        self.analyzer = analyzer

    def x(self):
        return np.std(self.analyzer.data[self.analyzer.x_label])

    def y(self):
        return np.std(self.analyzer.data[self.analyzer.y_label])


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

    def __init__(self, analyzer):

        self.analyzer = analyzer
        self.results = self.init_variables()
        self.target_x = -1
        self.level = -3.
        self.depth = 1
        self.comparator = True
        self._comparator = np.greater
        self._remove_zero = False


    def init_variables(self):
        return {"left": (0, -99), "extremum": (0, -99), "right": (0, -99)}


    def get_x_left(self):
        return self.results["left"][0]

    def get_y_left(self):
        return self.results["left"][1]

    def get_x_extremum(self):
        return self.results["extremum"][0]

    def get_y_extremum(self):
        return self.results["extremum"][1]

    def get_x_right(self):
        return self.results["right"][0]

    def get_y_right(self):
        return self.results["right"][1]


    def get_target_x(self):
        """ This function returns the value of the target x value to find the local extremum """

        return float(self.target_x)

    def get_depth(self):
        """ This function returns the value of the algorithm depth to find the local extremum """

        return int(self.depth)

    def set_depth(self,value):
        """ This function set the value of the algorithm depth to find the local extremum """

        self.depth = int(value)
        self.analyzer.refresh(self.analyzer.data)

    def get_level(self):
        """ This function returns the value of the drop in dB for the bandwitdh """

        return float(self.level)

    def set_level(self,value):
        """ This function set the value of the drop in dB for the bandwitdh """

        self.level = float(value)
        self.analyzer.refresh(self.analyzer.data)


    def get_comparator(self):
        """ This function returns the comparator state """

        return bool(int(float(self.comparator)))

    def set_comparator(self,value):
        """ This function set the comparator state """

        self.comparator = bool(int(float(value)))
        self._comparator = np.greater if self.comparator is True else np.less
        self.analyzer.refresh(self.analyzer.data)


    def search_bandwitdh(self, target_x=-1, level="default", comparator="default", depth="default"):
        """ This function compute the bandwidth around target_x and return the x,y coordinate of the left, center and right"""

        self.target_x = target_x

        if depth == "default":
            depth = self.depth

        if level == "default":
            level = self.level

        if comparator == "default":
            comparator = self._comparator

        data = self.analyzer.data
        variable_x = self.analyzer.x_label
        variable_y = self.analyzer.y_label

        assert len(data) != 0, "Empty dataframe"

        try:
            if variable_x == variable_y:
                x_data = np.array(data.values[:,0])
                y_data = x_data
            else:
                x_data, y_data = np.array(data[variable_x]), np.array(data[variable_y])

            self.results = sweep_analyse(x_data, y_data, target_x=target_x, level=level, comparator=comparator, depth=depth, remove_zero=self._remove_zero)

        except Exception as error:
            print("Couldn't find the bandwitdh:", error)
            self.results = self.init_variables()

        self.analyzer.refresh_gui()

        return self.results


    def get_driver_model(self):

        config = []

        config.append({'element':'action','name':'search_bandwitdh',
                        'do':self.search_bandwitdh,
                        "param_type":float,
                        'help':'Find the bandwitdh around the local peak closed to the defined x value. Set -1 for global extremum'})

        config.append({'element':'variable','name':'x_left',
                       'read':self.get_x_left,
                       'type':float,
                       'help':'Return x_left value'})

        config.append({'element':'variable','name':'y_left',
                       'read':self.get_y_left,
                       'type':float,
                       'help':'Return y_left value'})

        config.append({'element':'variable','name':'x_extremum',
                       'read':self.get_x_extremum,
                       'type':float,
                       'help':'Return x_max value'})

        config.append({'element':'variable','name':'y_extremum',
                       'read':self.get_y_extremum,
                       'type':float,
                       'help':'Return y_max value'})

        config.append({'element':'variable','name':'x_right',
                       'read':self.get_x_right,
                       'type':float,
                       'help':'Return x_right value'})

        config.append({'element':'variable','name':'y_right',
                       'read':self.get_y_right,
                       'type':float,
                       'help':'Return y_right value'})


        config.append({'element':'variable','name':'depth',
                       'read':self.get_depth,
                       'write':self.set_depth,
                       'type':int,
                       'help':'Set algorithm depth to find the local extremum'})

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


def sweep_analyse(x_data, y_data, target_x=-1, level=-3, comparator=np.greater, depth=1, remove_zero=False):
    """ target_x : x value close to the desired local extremum y. If -1, consider default and choose global extremum y"""
    # OPTIMIZE: put back this line -> data = data.dropna()  # BUG: crash python if ct400 dll loaded
    if comparator is True:
       comparator = np.greater
    elif comparator is False:
       comparator = np.less

    x_data, y_data = np.array(x_data), np.array(y_data)

    if np.all(x_data[:-1] >= x_data[1:]):  # change decreasing order to increasing
        x_data = x_data[::-1]
        y_data = y_data[::-1]

    assert np.all(x_data[:-1] <= x_data[1:]), "x axis is not sorted"

    if remove_zero:
        if y_data.any():  # don't remove if have only 0
            keep_data = y_data != 0
            y_data = y_data[keep_data]
            x_data = x_data[keep_data]

    if target_x != -1:

        order = lambda x: (((x-1) % 3)**2 + 1)*10**abs((x-1)//3)
        order_array = order(np.arange(1, depth+1))
        # order_array = np.array([1, 2, 5, 10, 20, 50, 100, 200])  # result if depth=6
        data = list()

        for order in order_array:  # search local extremum with different filter setting
            extremum_filter = find_local_extremum(x_data, y_data, target_x, level, order, comparator=comparator)
            point = {"x": extremum_filter[0], "y": extremum_filter[1]}
            data.append(point)

        df = pd.DataFrame(data)

        x_candidates = df['x'].mode().values  # wavelength with the most occurences (could have several wavelength with same occurance)

        index = abs(x_candidates - target_x).argmin()  # take wavelength closer to target_x if several x points found
        extremum_x = x_candidates[index]

        index2 = np.where(x_data == extremum_x)[0][0]
        extremum = (extremum_x, y_data[index2])

    else:
        # get extremum y_data and change it only if user want a different x_max
        if comparator is np.greater:
            extremum_index = np.argmax(y_data)
        elif comparator is np.less:
            extremum_index = np.argmin(y_data)
        else:
            raise TypeError(f"Comparator must be of type np.greater or np.less or bool. Given {comparator} of type {type(comparator)}")

        extremum = (x_data[extremum_index], y_data[extremum_index])

    # df.hist()  # used to see the selection process
    bandwidth_left, bandwidth_right = find_bandwidth(x_data, y_data, level, extremum, interp=True, comparator=comparator)

    results = {"left": bandwidth_left, "extremum": extremum, "right": bandwidth_right}

    return results


def find_local_extremum(x_data, y_data, target_x, level, order, comparator=np.greater):

    """ Find local extremum with closest x value to target_x.
        order is used to filter local extremums. """

    from scipy.signal import argrelextrema

    extremum_array_index = argrelextrema(y_data, comparator, order=order)[0]

    if len(y_data) > 1:
        if y_data[-1] > y_data[-2]:
            extremum_array_index = np.append(extremum_array_index, len(y_data)-1)

        if y_data[0] > y_data[1]:
            extremum_array_index = np.insert(extremum_array_index, 0, 0)

    if extremum_array_index.shape[0] != 0:
        extremum_array_x = x_data[extremum_array_index]
        extremum_array_y = y_data[extremum_array_index]

        index = abs(extremum_array_x - target_x).argmin()
        extremum_filter = (extremum_array_x[index], extremum_array_y[index])  # data from filter extremum list
        extremum = find_extremum_from_extremum_filter(x_data, y_data, level, extremum_filter, interp=False, comparator=comparator)
    else:
        extremum_raw_index = np.argmax(y_data)
        extremum_raw = (x_data[extremum_raw_index], y_data[extremum_raw_index])
        extremum = extremum_raw

    return extremum


def find_extremum_from_extremum_filter(x_data, y_data, level, extremum_filter, interp, comparator=np.greater):

    bandwidth_left_filter, bandwidth_right_filter = find_bandwidth(x_data, y_data, level, extremum_filter, interp, comparator=comparator)

    interval_low_index = np.where(x_data <= bandwidth_left_filter[0])[0][-1]
    interval_high_index = np.where(x_data >= bandwidth_right_filter[0])[0][0]

    if interval_high_index == 0:
        new_interval_x = x_data[interval_low_index: None]
        new_interval_y = y_data[interval_low_index: None]
    else:
        new_interval_x = x_data[interval_low_index: interval_high_index+1]
        new_interval_y = y_data[interval_low_index: interval_high_index+1]

    if comparator is np.greater:
        extremum_index = np.argmax(new_interval_y)
    elif comparator is np.less:
        extremum_index = np.argmin(new_interval_y)

    extremum = (new_interval_x[extremum_index], new_interval_y[extremum_index])

    return extremum


def find_bandwidth(x_data, y_data, level, extremum, interp, comparator=np.greater):
    """ Find the bandwidth """
    x_data, y_data = np.array(x_data), np.array(y_data)

    if len(x_data) == 0:
        bandwidth_left = (None, None)
        return bandwidth_left, bandwidth_left
    elif len(x_data) == 1:
        bandwidth_left = (x_data[0], y_data[0])
        return bandwidth_left, bandwidth_left

    index_extremum = abs(x_data - extremum[0]).argmin()

    x_left = x_data[:index_extremum+1][::-1]  # Reverse order to start at extremum
    y_left= y_data[:index_extremum+1][::-1]

    x_right = x_data[index_extremum:]
    y_right = y_data[index_extremum:]

    target_y = extremum[1] + level

    bandwidth_left = find_bandwidth_side(x_left, y_left, target_y, level, extremum, interp)
    bandwidth_right = find_bandwidth_side(x_right, y_right, target_y, level, extremum, interp)

    return bandwidth_left, bandwidth_right


def find_bandwidth_side(x_side, y_side, target_y, level, extremum, interp):
    """ Find (x,y) coordinate of bandwith for the given side """
    if len(x_side) == 1:
        bandwidth_side = (x_side[0], y_side[0])
    else:
        if level == 0:
            bandwidth_side = extremum
        else:
            if level < 0:
                index_side_list1 = np.where(y_side <= target_y)[0]
            else:
                index_side_list1 = np.where(y_side >= target_y)[0]

            if index_side_list1.shape[0] == 0:
                bandwidth_side = (x_side[-1], y_side[-1])
            else:
                index_side1 = index_side_list1[0]
                x_side_cut1 = x_side[:index_side1+1][::-1]
                y_side_cut1 = y_side[:index_side1+1][::-1]

                if level < 0:
                    index_side_list2 = np.where(y_side_cut1 > target_y)[0]
                else:
                    index_side_list2 = np.where(y_side_cut1 < target_y)[0]

                if index_side_list2.shape[0] == 0 or len(x_side_cut1) == 1:
                    bandwidth_side = (x_side_cut1[0], y_side_cut1[0])
                else:
                    index_side2 = index_side_list2[0]
                    x_side_cut2 = x_side_cut1[:index_side2+1]
                    y_side_cut2 = y_side_cut1[:index_side2+1]

                    if interp:
                        bandwidth_side = interp_lin(x_side_cut2, y_side_cut2, target_y)
                    else:
                        bandwidth_side = (x_side_cut2[0], y_side_cut2[0])

    return bandwidth_side


def interp_lin(x_data, y_data, target_y):
    """ Interpolate between two points """
    assert len(x_data) == 2 and len(y_data) == 2, (f"Two points were expected for interpolation, {len(x_data)} were given")

    a = (y_data[-1] - y_data[0]) / (x_data[-1] - x_data[0])
    b = y_data[0] - a*x_data[0]
    y = target_y
    x = (y - b) / a

    return (x, y)
