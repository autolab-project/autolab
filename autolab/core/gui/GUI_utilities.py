# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 20:13:46 2024

@author: jonathan
"""

import re
import os
import sys
from typing import Tuple, List
from collections import defaultdict

import numpy as np
import pandas as pd
from qtpy import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

from ..config import get_GUI_config
from ..devices import DEVICES, get_element_by_address
from ..variables import has_eval, EVAL, VARIABLES

# Fixes pyqtgraph/issues/3018 for pg<=0.13.7 (before pyqtgraph/pull/3070)
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem

if hasattr(PlotDataItem, '_fourierTransform'):

    _fourierTransform_bugged = PlotDataItem._fourierTransform

    def _fourierTransform_fixed(self, x, y):
        if len(x) == 1: return np.array([0]), abs(y)
        return _fourierTransform_bugged(self, x, y)

    PlotDataItem._fourierTransform = _fourierTransform_fixed


ONCE = False


def get_font_size() -> int:
    GUI_config = get_GUI_config()
    if GUI_config['font_size'] != 'default':
        font_size = int(GUI_config['font_size'])
    else:
        font_size = QtWidgets.QApplication.instance().font().pointSize()
        return font_size


def setLineEditBackground(obj, state: str, font_size: int = None):
    """ Sets background color of a QLineEdit widget based on its editing state """
    if state == 'synced': color='#D2FFD2' # vert
    if state == 'edited': color='#FFE5AE' # orange

    if font_size is None:

        obj.setStyleSheet(
            "QLineEdit:enabled {background-color: %s}" % (
                color))
    else:
        obj.setStyleSheet(
            "QLineEdit:enabled {background-color: %s; font-size: %ipt}" % (
                color, font_size))


CHECK_ONCE = True


def qt_object_exists(QtObject) -> bool:
    """ Return True if object exists (not deleted).
    Check if use pyqt5, pyqt6, pyside2 or pyside6 to use correct implementation
    """
    global CHECK_ONCE
    QT_API = os.environ.get("QT_API")

    if not CHECK_ONCE: return True
    try:
        if QT_API in ("pyqt5", "pyqt6"):
            import sip
            return not sip.isdeleted(QtObject)
        if QT_API == "pyside2":
            import shiboken2
            return shiboken2.isValid(QtObject)
        if QT_API =="pyside6":
            import shiboken6
            return shiboken6.isValid(QtObject)
        raise ModuleNotFoundError(f"QT_API '{QT_API}' unknown")
    except ModuleNotFoundError as e:
        print(f"Warning: {e}. Skip check if Qt Object not deleted.")
        CHECK_ONCE = False
        return True


class MyGraphicsLayoutWidget(pg.GraphicsLayoutWidget):
    # OPTIMIZE: could merge with myImageView to only have one class handling both lines and images

    def __init__(self):
        super().__init__()

        self.img_active = False

        # for plotting 1D
        ax = self.addPlot()
        self.ax = ax

        ax.setLabel("bottom", ' ', **{'color':0.4, 'font-size': '12pt'})
        ax.setLabel("left", ' ', **{'color':0.4, 'font-size': '12pt'})

        # Set your custom font for both axes
        my_font = QtGui.QFont('Arial', 12)
        my_font_tick = QtGui.QFont('Arial', 10)
        ax.getAxis("bottom").label.setFont(my_font)
        ax.getAxis("left").label.setFont(my_font)
        ax.getAxis("bottom").setTickFont(my_font_tick)
        ax.getAxis("left").setTickFont(my_font_tick)
        ax.showGrid(x=True, y=True)
        ax.setContentsMargins(10., 10., 10., 10.)

        vb = ax.getViewBox()
        vb.enableAutoRange(enable=True)
        vb.setBorder(pg.mkPen(color=0.4))

        ## Text label for the data coordinates of the mouse pointer
        dataLabel = pg.LabelItem(color='k', parent=ax.getAxis('bottom'))
        dataLabel.anchor(itemPos=(1,1), parentPos=(1,1), offset=(0,0))

        def mouseMoved(point):
            """ This function marks the position of the cursor in data coordinates"""
            vb = ax.getViewBox()
            mousePoint = vb.mapSceneToView(point)
            l = f'x = {mousePoint.x():g},  y = {mousePoint.y():g}'
            dataLabel.setText(l)

        # data reader signal connection
        ax.scene().sigMouseMoved.connect(mouseMoved)

    def activate_img(self):
        """ Enable image feature """
        global ONCE
        # (py 3.6 -> pg 0.11.1, py 3.7 -> 0.12.4, py 3.8 -> 0.13.3, py 3.9 -> 0.13.7 (latest))
        # Disabled 2D plot if don't have pyqtgraph > 0.11
        pgv = pg.__version__.split('.')
        if int(pgv[0]) == 0 and int(pgv[1]) < 12:
            ONCE = True
            print("Can't use 2D plot for scan, need pyqtgraph >= 0.13.2", file=sys.stderr)
            # OPTIMIZE: could use ImageView instead?
            return None

        if not self.img_active:
            self.img_active = True

            # for plotting 2D
            img = pg.PColorMeshItem()
            self.ax.addItem(img)
            self.img = img

            # for plotting 2D colorbar
            if hasattr(self.ax, 'addColorBar') and hasattr(img, 'setLevels'):
                self.colorbar = self.ax.addColorBar(img, colorMap='viridis')  # pg 0.12.4
            else:
                if hasattr(pg, 'ColorBarItem'):
                    self.colorbar = pg.ColorBarItem(colorMap='viridis')  # pg 0.12.2
                else:
                    self.colorbar = pg.HistogramLUTItem()  # pg 0.11.0 (disabled)
                self.addItem(self.colorbar)

                if not ONCE:
                    ONCE = True
                    print('Skip colorbar update, need pyqtgraph >= 0.13.2', file=sys.stderr)

            self.colorbar.hide()

    def update_img(self, x, y, z):
        """ Update pcolormesh image """
        global ONCE
        z_no_nan = z[~np.isnan(z)]
        z[np.isnan(z)] = z_no_nan.min()-1e99  # OPTIMIZE: nan gives error, would prefer not to display empty values

        # Expand x and y arrays to define edges of the grid
        if len(x) == 1:
            x = np.append(x, x[-1]+1e-99)  # OPTIMIZE: first line too small and not visible if autoscale disabled, could use next x value instead but figure should not be aware of scan
        else:
            x = np.append(x, x[-1] + (x[-1] - x[-2]))

        if len(y) == 1:
            y = np.append(y, y[-1]+1e-99)
        else:
            y = np.append(y, y[-1] + (y[-1] - y[-2]))

        xv, yv = np.meshgrid(y, x)

        img = pg.PColorMeshItem()
        img.edgecolors = None
        img.setData(xv, yv, z.T)
        # OPTIMIZE: Changing log scale doesn't display correct axes
        if hasattr(img, 'setLevels'):  # pg 0.13.2 introduces setLevels in PColorMeshItem (py 3.8)
            self.colorbar.setImageItem(img)
        else:
            if not ONCE:
                ONCE = True
                print('Skip colorbar update, need pyqtgraph >= 0.13.2', file=sys.stderr)

        if isinstance(self.colorbar, pg.HistogramLUTItem):  # old
            self.colorbar.setLevels(z_no_nan.min(), z_no_nan.max())
        else:  # new
            self.colorbar.setLevels((z_no_nan.min(), z_no_nan.max()))

        # remove previous img and add new one (can't just refresh -> error if setData with nan and diff shape)
        self.ax.removeItem(self.img)
        self.img = img
        self.ax.addItem(self.img)


def pyqtgraph_fig_ax() -> Tuple[MyGraphicsLayoutWidget, pg.PlotItem]:
    """ Return a formated fig and ax pyqtgraph for a basic plot """
    fig = MyGraphicsLayoutWidget()
    return fig, fig.ax


class myImageView(pg.ImageView):
    ''' Wrap of pg.ImageView with additionnal functionalities '''
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # update tick background on gradient change
        self.ui.histogram.gradient.sigGradientChanged.connect(self.update_ticks)

        self.figLineROI, self.axLineROI = pyqtgraph_fig_ax()
        self.figLineROI.hide()
        self.plot = self.axLineROI.plot([], [], pen='k')

        self.lineROI = pg.LineSegmentROI([[0, 100], [100, 100]], pen='r')
        self.lineROI.sigRegionChanged.connect(self.updateLineROI)
        self.lineROI.hide()

        self.addItem(self.lineROI)

        # update slice when change frame number in scanner
        self.timeLine.sigPositionChanged.connect(self.updateLineROI)

        slice_pushButton = QtWidgets.QPushButton('Slice')
        slice_pushButton.state = False
        slice_pushButton.setMinimumSize(0, 23)
        slice_pushButton.setMaximumSize(75, 23)
        slice_pushButton.clicked.connect(self.slice_pushButtonClicked)
        self.slice_pushButton = slice_pushButton

        horizontalLayoutButton = QtWidgets.QHBoxLayout()
        horizontalLayoutButton.setSpacing(0)
        horizontalLayoutButton.setContentsMargins(0,0,0,0)
        horizontalLayoutButton.addStretch()
        horizontalLayoutButton.addWidget(self.slice_pushButton)

        widgetButton = QtWidgets.QWidget()
        widgetButton.setLayout(horizontalLayoutButton)

        verticalLayoutImageButton = QtWidgets.QVBoxLayout()
        verticalLayoutImageButton.setSpacing(0)
        verticalLayoutImageButton.setContentsMargins(0,0,0,0)
        verticalLayoutImageButton.addWidget(self)
        verticalLayoutImageButton.addWidget(widgetButton)

        widgetImageButton = QtWidgets.QWidget()
        widgetImageButton.setLayout(verticalLayoutImageButton)

        splitter = QtWidgets.QSplitter()
        splitter.setOrientation(QtCore.Qt.Vertical)
        splitter.addWidget(widgetImageButton)
        splitter.addWidget(self.figLineROI)
        splitter.setSizes([500,500])

        verticalLayoutMain = QtWidgets.QVBoxLayout()
        verticalLayoutMain.setSpacing(0)
        verticalLayoutMain.setContentsMargins(0,0,0,0)
        verticalLayoutMain.addWidget(splitter)

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(verticalLayoutMain)
        self.centralWidget = centralWidget

    def update_ticks(self):
        for tick in self.ui.histogram.gradient.ticks:
            tick.pen = pg.mkPen(pg.getConfigOption("foreground"))
            tick.currentPen = tick.pen
            tick.hoverPen = pg.mkPen(200, 120, 0)

    def slice_pushButtonClicked(self):
        self.slice_pushButton.state = not self.slice_pushButton.state
        self.display_line()

    def display_line(self):
        if self.slice_pushButton.state:
            self.figLineROI.show()
            self.lineROI.show()
            self.updateLineROI()
        else:
            self.figLineROI.hide()
            self.lineROI.hide()

    def show(self):
        self.centralWidget.show()

    def hide(self):
        self.centralWidget.hide()

    def roiChanged(self):
        pg.ImageView.roiChanged(self)
        for c in self.roiCurves:
            c.setPen(pg.getConfigOption("foreground"))

    def setImage(self, *args, **kwargs):
        pg.ImageView.setImage(self, *args, **kwargs)
        self.updateLineROI()

    def updateLineROI(self):
        if self.slice_pushButton.state:
            img = self.image if self.image.ndim == 2 else self.image[self.currentIndex]
            img = np.array([img])

            x,y = (0, 1) if self.imageItem.axisOrder == 'col-major' else (1, 0)
            d2 = self.lineROI.getArrayRegion(img, self.imageItem, axes=(x+1, y+1))
            self.plot.setData(d2[0])

    def close(self):
        self.figLineROI.deleteLater()
        super().close()


def pyqtgraph_image() -> Tuple[myImageView, QtWidgets.QWidget]:
    """ Return a formated ImageView and pyqtgraph widget for image plotting """
    imageView = myImageView()
    return imageView, imageView.centralWidget


class MyLineEdit(QtWidgets.QLineEdit):
    """https://stackoverflow.com/questions/28956693/pyqt5-qtextedit-auto-completion"""

    skip_has_eval = False
    use_variables = True
    use_devices = True
    use_np_pd = True
    completer: QtWidgets.QCompleter = None

    def __init__(self, *args):
        super().__init__(*args)

    def create_keywords(self) -> list[str]:
        """ Returns a list of all available keywords for completion """
        list_keywords = []

        if self.use_variables:
            list_keywords += list(VARIABLES)
            ## Could use this to see attributes of Variable like .raw .value
            # list_keywords += [f'{name}.{item}'
            #                     for name, var in VARIABLES.items()
            #                     for item in dir(var)
            #                     if not item.startswith('_') and not item.isupper()]
        if self.use_devices:
            list_keywords += [str(get_element_by_address(elements[0]).address())
                          for device in DEVICES.values()
                          if device.name not in list_keywords
                          for elements in device.get_structure()]

        if self.use_np_pd:
            if 'np' not in list_keywords:
                list_keywords += ['np']
                list_keywords += [f'np.{item}'
                                   for item in dir(np)
                                   if not item.startswith('_') and not item.isupper()]

            if 'pd' not in list_keywords:
                list_keywords += ['pd']
                list_keywords += [f'pd.{item}'
                                   for item in dir(pd)
                                   if not item.startswith('_') and not item.isupper()]
        return list_keywords

    def eventFilter(self, obj, event):
        """ Used when installEventFilter active """
        if (event.type() == QtCore.QEvent.KeyPress
                and event.key() == QtCore.Qt.Key_Tab):
            self.keyPressEvent(event)
            return True
        return super().eventFilter(obj, event)

    def setCustomCompleter(self):
        self.setCompleter(QtWidgets.QCompleter(self.create_keywords()))

    def setCompleter(self, completer: QtWidgets.QCompleter):
        """ Sets/removes completer """
        if self.completer:
            self.completer.popup().close()
            try:
                self.completer.disconnect()  # PyQT
            except TypeError:
                self.completer.disconnect(self) # Pyside

        if not completer:
            self.removeEventFilter(self)
            self.completer = None
            return None

        self.installEventFilter(self)
        completer.setWidget(self)
        completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.completer = completer
        self.completer.activated.connect(self.insertCompletion)

    def getCompletion(self) -> List[str]:
        model = self.completer.model()
        return model.stringList() if isinstance(
            model, QtCore.QStringListModel) else []

    def insertCompletion(self, completion: str, prefix: bool = True):
        cursor_pos = self.cursorPosition()
        text = self.text()

        prefix_length = (len(self.completer.completionPrefix())
                         if (prefix and self.completer) else 0)

        # Replace the current word with the completion
        new_text = (text[:cursor_pos - prefix_length]
                    + completion
                    + text[cursor_pos:])
        self.setText(new_text)
        self.setCursorPosition(cursor_pos - prefix_length + len(completion))

    def textUnderCursor(self) -> str:
        text = self.text()
        cursor_pos = self.cursorPosition()
        start = text.rfind(' ', 0, cursor_pos) + 1
        return text[start:cursor_pos]

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self)
        super().focusInEvent(event)

    def keyPressEvent(self, event):
        controlPressed = event.modifiers() == QtCore.Qt.ControlModifier
        tabPressed = event.key() == QtCore.Qt.Key_Tab
        specialTabPressed = tabPressed and controlPressed
        enterPressed = event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return)
        specialEnterPressed = enterPressed and controlPressed

        if specialTabPressed:
            self.insertCompletion('\t', prefix=False)
            return None

        if specialEnterPressed:
            self.insertCompletion('\n', prefix=False)
            return None

        if not self.completer or not tabPressed:
            if (self.completer and enterPressed and self.completer.popup().isVisible()):
                self.completer.activated.emit(
                    self.completer.popup().currentIndex().data())
            else:
                super().keyPressEvent(event)

        if self.skip_has_eval or has_eval(self.text()):
            if not self.completer: self.setCustomCompleter()
        else:
            if self.completer: self.setCompleter(None)

        if not self.completer or not tabPressed:
            if self.completer: self.completer.popup().close()
            return None

        completion_prefix = self.format_completion_prefix(self.textUnderCursor())

        new_keywords = self.create_new_keywords(
            self.create_keywords(), completion_prefix)
        keywords = self.getCompletion()

        if new_keywords != keywords:
            keywords = new_keywords
            self.setCompleter(QtWidgets.QCompleter(keywords))

        if completion_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completion_prefix)
            self.completer.popup().setCurrentIndex(
                self.completer.completionModel().index(0, 0))

        if self.completer.completionModel().rowCount() == 1:
            self.completer.setCompletionMode(
                QtWidgets.QCompleter.InlineCompletion)
            self.completer.complete()

            self.completer.activated.emit(self.completer.currentCompletion())
            self.completer.setCompletionMode(
                QtWidgets.QCompleter.PopupCompletion)
        else:
            cr = self.cursorRect()
            cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                        + self.completer.popup().verticalScrollBar().sizeHint().width())
            self.completer.complete(cr)

    @staticmethod
    def format_completion_prefix(completion_prefix: str) -> str:
        """ Returns a simplified prefix for completion """
        if has_eval(completion_prefix):
            completion_prefix = completion_prefix[len(EVAL):]

        pattern = r'[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*'
        temp = [var for var in re.findall(pattern, completion_prefix)]

        if len(temp) > 0:
            position = completion_prefix.rfind(temp[-1])
            if position != -1:
                completion_prefix = completion_prefix[position:]

        special_char = ('(', '[', ',', ':', '-', '+', '^', '*', '/', '|')
        if completion_prefix.endswith(special_char):
            completion_prefix = ''

        return completion_prefix

    @staticmethod
    def create_new_keywords(list_keywords: List[str],
                            completion_prefix: str) -> List[str]:
        """ Returns a list with all available keywords and possible decomposition """
        # Create ordered list with all attributes and sub attributes
        master_list = []
        master_list.append(list_keywords)
        list_temp = list_keywords
        while len(list_temp) > 1:
            list_temp = list(set(
                [var[:-len(var.split('.')[-1])-1]
                 for var in list_temp if len(var.split('.')) != 0]))
            if '' in list_temp: list_temp.remove('')
            master_list.append(list_temp)

        # Filter attributes that contained completion_prefix and remove doublons
        flat_list = list(set(item
                             for sublist in master_list
                             for item in sublist
                             if item.startswith(completion_prefix)))

        # Group items by the number of dots
        dot_groups = defaultdict(list)
        for item in flat_list:
            dot_count = item.count('.')
            dot_groups[dot_count].append(item)

        # Sort the groups by the number of dots
        sorted_groups = sorted(
            dot_groups.items(), key=lambda x: x[0], reverse=True)

        # Extract items from each group and return as a list with sorted sublist
        sorted_list = [sorted(group) for _, group in sorted_groups]

        # Create list of all available keywords and possible decomposition
        new_keywords = []
        good = False
        for level in reversed(sorted_list):
            for item in level:
                if completion_prefix in item:
                    new_keywords.append(item)
                    good = True
            if good: break

        return new_keywords
