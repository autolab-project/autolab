# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 10:58:47 2023

@author: Jonathan
"""
import pandas as pd
from qtpy import QtCore, QtWidgets
# import pyqtgraph as pg
# TODO: need to choose between fast (QTableView+TableModel) or fancy (pg.TableWidget)


class DisplayValues(QtWidgets.QWidget):

    def __init__(self, gui: QtWidgets.QMainWindow,
                 name: str, size: QtCore.QSize = (250, 400)):
        """ Create a QWidget displaying the dataFrame input to the refresh method.
        size is of type QtCore.QSize or tuple of int """

        if type(size) in (tuple, list):
           size = QtCore.QSize(*size)

        self.gui = gui
        self.active = False

        QtWidgets.QWidget.__init__(self)

        self.setWindowTitle(name)
        self.resize(size)
        self.tableView = QtWidgets.QTableView()  # too basic (can't save/copy data)
        # self.tableView = pg.TableWidget(sortable=False)  # too slow

        layoutWindow = QtWidgets.QVBoxLayout()
        layoutWindow.addWidget(self.tableView)
        self.setLayout(layoutWindow)

    def refresh(self, data: pd.DataFrame):
        """ data is pd.DataFrame """
        tableModel = TableModel(data)
        self.tableView.setModel(tableModel)
        # self.tableView.setData(data.to_dict('records'))

    def show(self):
        if not self.active:
            super().show()
            self.active = True
        else:
            self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.activateWindow()

    def closeEvent(self, event):
        self.active = False


class TableModel(QtCore.QAbstractTableModel):
    "From https://www.pythonguis.com/tutorials/pyqt6-qtableview-modelviews-numpy-pandas/"
    def __init__(self, data: pd.DataFrame):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == QtCore.Qt.Orientation.Vertical:
                return str(self._data.index[section])
