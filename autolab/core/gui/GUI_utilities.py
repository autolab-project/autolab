# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 20:13:46 2024

@author: jonathan
"""

from typing import Tuple
import os
import sys

import numpy as np
from qtpy import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

from ..config import get_GUI_config

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
