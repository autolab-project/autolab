# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 18:22:43 2019

@author: qchat
"""
from typing import Any, Tuple, List

import pandas as pd
import numpy as np
from qtpy import QtWidgets


class DataManager:

    def __init__(self, gui: QtWidgets.QMainWindow):

        self.gui = gui
        self.windowLength = 10
        self.xlist = []
        self.ylist = []

    def setWindowLength(self, value: float):
        """ This function set the value of the window length """
        self.windowLength = value

    def getWindowLength(self) -> float:
        """ This function returns the value of the window legnth """
        return self.windowLength

    def getData(self) -> Tuple[List, List]:
        """ This function update the data of the provided plot object """
        return self.xlist, self.ylist

    def save(self, filename: str):
        """ This function save the data in a file with the provided filename"""
        if self.xlist is not None:
            df = pd.DataFrame({self.gui.xlabel: self.xlist,
                               self.gui.ylabel: self.ylist})
            df.to_csv(filename, index=False)
        else: # Image
            np.savetxt(filename, self.ylist, sep=",")

    def addPoint(self, point: Tuple[Any, Any]):
        """ This function either replace list by array or add point to list depending on datapoint type """
        x, y = point
        try:
            float(y)
        except TypeError:
            if type(y) is np.ndarray:
                if len(y.T.shape) == 1 or y.T.shape[0] == 2:
                    self._addArray(y.T)
                else:
                    self._addImage(y)  # Defined which axe is major using pg.setConfigOption('imageAxisOrder', 'row-major') in gui start-up so no need to .T data
            elif type(y) is pd.DataFrame:
                self._addArray(y.values.T)
        else:
            self._addPoint(point)

    def _addImage(self, image: np.ndarray):
        """ Add image to ylist data as np.ndarray """
        self.xlist = None
        self.ylist = image

    def _addArray(self, array: np.ndarray):
        """ This function replace an dataset [x,y] x is time y is array"""

        if len(array.shape) == 1:
            y_array = array
            # Replace data
            self.xlist = np.arange(len(y_array))
            self.ylist = np.array(y_array)
        elif array.shape[0] >= 2:
            x_array = array[0]
            y_array = array[1] # OPTIMIZE: add button in gui to choose x and y like in scan

            # Replace data
            self.xlist = np.array(x_array)
            self.ylist = np.array(y_array)

    def _addPoint(self, point: Tuple[float, float]):
        """ This function append a datapoint [x,y] in the lists of data """
        x, y = point

        # Append data
        self.xlist.append(x)
        self.ylist.append(y)

        # Remove too old data (regarding the window length)
        while max(self.xlist)-min(self.xlist) > self.windowLength:
            self.xlist.pop(0)
            self.ylist.pop(0)

    def clear(self):
        try:
            self.xlist.clear()
            self.ylist.clear()
        except AttributeError:  # numpy array has no clear method
            self.xlist = []
            self.ylist = []
