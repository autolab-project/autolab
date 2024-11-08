# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 10:58:47 2023

@author: Jonathan
"""
import pandas as pd
from qtpy import QtCore, QtWidgets
import pyqtgraph as pg


class DisplayValues(QtWidgets.QWidget):

    def __init__(self, name: str, size: QtCore.QSize = (250, 400)):
        """ Create a QWidget displaying the dataFrame input to the refresh method.
        size is of type QtCore.QSize or tuple of int """

        if isinstance(size, (tuple, list)): size = QtCore.QSize(*size)

        self.active = False

        super().__init__()

        self.setWindowTitle(name)
        self.resize(size)
        # I choose pg.TableWidget to have more features at the cost of slower execution than QTableView+TableModel
        # self.tableView = QtWidgets.QTableView()  # basic (can't save/copy data)
        self.tableView = pg.TableWidget()  # slow
        self.tableView.setFormat('%.16g')

        layoutWindow = QtWidgets.QVBoxLayout()
        layoutWindow.addWidget(self.tableView)
        self.setLayout(layoutWindow)

    def refresh(self, data: pd.DataFrame):
        """ data is pd.DataFrame """
        # tableModel = TableModel(data)
        # self.tableView.setModel(tableModel)
        self.tableView.setData(data.to_dict('records'))

    def show(self):
        if not self.active:
            super().show()
            self.active = True
        else:
            self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.activateWindow()

    def closeEvent(self, event):
        self.active = False

    def close(self):
        for children in self.findChildren(QtWidgets.QWidget):
            children.deleteLater()

        super().close()


# OBSOLETE
class TableModel(QtCore.QAbstractTableModel):
    "From https://www.pythonguis.com/tutorials/pyqt6-qtableview-modelviews-numpy-pandas/"
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data

    def data(self, index, role):
        if hasattr(QtCore.Qt.ItemDataRole, 'DisplayRole'):
            role_check = QtCore.Qt.ItemDataRole.DisplayRole
        else:
            role_check = 0  # Compatibility py3.6
        if role == role_check:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if hasattr(QtCore.Qt.ItemDataRole, 'DisplayRole'):
            role_check = QtCore.Qt.ItemDataRole.DisplayRole
        else:
            role_check = 0
        if role == role_check:
            if orientation == QtCore.Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == QtCore.Qt.Vertical:
                return str(self._data.index[section])
