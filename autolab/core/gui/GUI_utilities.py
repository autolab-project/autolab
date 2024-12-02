# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 20:13:46 2024

@author: jonathan
"""

import re
import os
import sys
from typing import Tuple, List, Union, Callable
from collections import defaultdict
import inspect

import numpy as np
import pandas as pd
from qtpy import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

from .icons import icons
from ..paths import PATHS
from ..config import get_GUI_config
from ..devices import DEVICES, get_element_by_address
from ..variables import has_eval, EVAL, VARIABLES
from ..utilities import SUPPORTED_EXTENSION

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

    return (int(float(GUI_config['font_size']))
                 if GUI_config['font_size'] != 'default'
                 else QtWidgets.QApplication.instance().font().pointSize())


def setLineEditBackground(obj, state: str, font_size: int = None):
    """ Sets background color of a QLineEdit widget based on its editing state """
    if state == 'synced': color='#D2FFD2' # vert
    if state == 'edited': color='#FFE5AE' # orange

    if font_size is None:
        obj.setStyleSheet(
            "QLineEdit:enabled {background-color: %s; color: #000000;}" % (
                color))
    else:
        obj.setStyleSheet(
            "QLineEdit:enabled {background-color: %s; font-size: %ipt; color: #000000;}" % (
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
        if QT_API == "pyqt5":
            import sip
            return not sip.isdeleted(QtObject)
        if QT_API == "pyqt6":
            from PyQt6 import sip
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

        ax.setLabel("bottom", ' ', **{'color': pg.getConfigOption("foreground"),
                                      'font-size': '12pt'})
        ax.setLabel("left", ' ', **{'color': pg.getConfigOption("foreground"),
                                    'font-size': '12pt'})

        # Set your custom font for both axes
        my_font = QtGui.QFont('Arial', 12)
        my_font_tick = QtGui.QFont('Arial', 10)
        ax.getAxis("bottom").label.setFont(my_font)
        ax.getAxis("left").label.setFont(my_font)
        ax.getAxis("bottom").setTickFont(my_font_tick)
        ax.getAxis("left").setTickFont(my_font_tick)
        ax.showGrid(x=True, y=True)

        vb = ax.getViewBox()
        vb.enableAutoRange(enable=True)
        vb.setBorder(pg.mkPen(color=pg.getConfigOption("foreground")))

        ## Text label for the data coordinates of the mouse pointer
        dataLabel = pg.LabelItem(color=pg.getConfigOption("foreground"),
                                 parent=ax.getAxis('bottom'))
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

    def dragLeaveEvent(self, event):
        # Pyside6 triggers a leave event resuling in error:
        # QGraphicsView::dragLeaveEvent: drag leave received before drag enter
        pass
        # super().dragLeaveEvent(event)



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

        # update slice when change frame number in scanner
        self.timeLine.sigPositionChanged.connect(lambda: self.updateLineROI())

        # Create a checkbox for aspect ratio
        self.aspect_ratio_checkbox = QtWidgets.QCheckBox("Lock aspect ratio")
        self.aspect_ratio_checkbox.setChecked(True)
        self.aspect_ratio_checkbox.stateChanged.connect(self.toggle_aspect_ratio)

        # Store shapes in a list with visibility and remove information
        self.shapes = []
        self.shapes_plot = []

        # Create menu bar
        shape_toolbutton = QtWidgets.QToolButton(self)
        shape_toolbutton.setText(" Custom ROI ")
        shape_toolbutton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        menu_bar = QtWidgets.QMenu(self)
        menu_bar.aboutToShow.connect(self.update_shape_properties_menu)
        shape_toolbutton.setMenu(menu_bar)

        add_menu = menu_bar.addMenu("Add")

        add_line_action = QtWidgets.QAction("Line", add_menu)
        add_line_action.triggered.connect(self.add_line)
        add_menu.addAction(add_line_action)

        add_rectangle_action = QtWidgets.QAction("Rectangle", add_menu)
        add_rectangle_action.triggered.connect(self.add_rectangle)
        add_menu.addAction(add_rectangle_action)

        add_ellipse_action = QtWidgets.QAction("Ellipse", add_menu)
        add_ellipse_action.triggered.connect(self.add_ellipse)
        add_menu.addAction(add_ellipse_action)

        # Create a container for shape visibility toggles and delete buttons
        self.shape_properties_menu = menu_bar.addMenu("Properties")

        horizontalLayoutButton = QtWidgets.QHBoxLayout()
        horizontalLayoutButton.setSpacing(0)
        horizontalLayoutButton.setContentsMargins(0,0,0,0)
        horizontalLayoutButton.addWidget(self.aspect_ratio_checkbox)
        horizontalLayoutButton.addStretch()
        horizontalLayoutButton.addWidget(shape_toolbutton)

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

        for splitter in (splitter, ):
            for i in range(splitter.count()):
                handle = splitter.handle(i)
                handle.setStyleSheet("background-color: #DDDDDD;")
                handle.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            obj.setStyleSheet("background-color: #AAAAAA;")  # Hover color
        elif event.type() == QtCore.QEvent.Leave:
            obj.setStyleSheet("background-color: #DDDDDD;")  # Normal color
        return super().eventFilter(obj, event)

    def update_ticks(self):
        for tick in self.ui.histogram.gradient.ticks:
            tick.pen = pg.mkPen(pg.getConfigOption("foreground"))
            tick.currentPen = tick.pen
            tick.hoverPen = pg.mkPen(200, 120, 0)

    def toggle_aspect_ratio(self):
        self.getView().setAspectLocked(
            self.aspect_ratio_checkbox.isChecked())

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

    def updateLineROI(self, shape: pg.ROI = None):
        shapes_to_plot = self.shapes_plot if shape is None else [shape]

        img = self.image if self.image.ndim == 2 else self.image[self.currentIndex]
        img = np.array([img])
        x,y = (0, 1) if self.imageItem.axisOrder == 'col-major' else (1, 0)

        for shape in shapes_to_plot:
            if shape not in self.shapes_plot:
                continue

            # OPTIMIZE: This behavior might not be ideal in all case, some user would prefer to have the average over the full range instead of the x line.
            if isinstance(shape, pg.LineSegmentROI):
                d2 = shape.getArrayRegion(img, self.imageItem, axes=(x+1, y+1))
                data = d2[0]
            elif isinstance(shape, pg.RectROI):
                d2 = shape.getArrayRegion(img, self.imageItem, axes=(y+1, x+1))
                data = np.mean(d2[0], axis=0)
            elif isinstance(shape, pg.EllipseROI):
                d2 = shape.getArrayRegion(img, self.imageItem, axes=(y+1, x+1))
                data = np.mean(d2[0], axis=0)
            else:
                d2 = shape.getArrayRegion(img, self.imageItem, axes=(x+1, y+1))
                data = d2[0]

            shape.plot.setData(data)

        self.figLineROI.setVisible(len(self.shapes_plot) != 0)

    def on_roi_clicked(self, roi: pg.ROI, ev: QtCore.QEvent):
        if ev.button() == QtCore.Qt.RightButton:
            roi.menu.actions_list['visible'].setChecked(roi.isVisible())
            global_pos = self.mapToGlobal(roi.getSceneHandlePositions()[0][1].toPoint())
            _ = roi.menu.exec_(global_pos)
            ev.accept()

    def toggle_all_plot(self, state: bool):
        for shape in self.shapes:
            if state:
                self.show_plot(shape)
            else:
                self.hide_plot(shape)

    def show_all_shapes(self):
        for shape in self.shapes:
            self.show_plot(shape)

    def hide_all_shapes(self):
        for shape in self.shapes:
            self.hide_plot(shape)

    def toggle_plot(self, shape: pg.ROI, state: bool):
        if state:
            self.show_plot(shape)
        else:
            self.hide_plot(shape)

    def show_plot(self, shape: pg.ROI):
        self.shapes_plot.append(shape)
        shape.plot.show()
        shape.menu.actions_list['plot'].setChecked(True)
        self.updateLineROI(shape)

    def hide_plot(self, shape: pg.ROI):
        self.shapes_plot.remove(shape)
        shape.plot.hide()
        shape.menu.actions_list['plot'].setChecked(False)
        self.figLineROI.setVisible(len(self.shapes_plot) != 0)

    def add_shape(self, shape: pg.ROI):

        if isinstance(shape, pg.LineSegmentROI):
            basename = 'Line'
        elif isinstance(shape, pg.RectROI):
            basename = 'Rectangle'
        elif isinstance(shape, pg.EllipseROI):
            basename = 'Ellipse'
        else:
            basename = 'Unknown'

        name = basename
        names = [shape.name for shape in self.shapes]
        compt = 0
        while True:
            if name in names:
                compt += 1
                name = basename + '_' + str(compt)
            else:
                break

        # Define shape menu
        shape_menu = QtWidgets.QMenu()
        shape_menu.setTitle(name)

        shape_actions = {}
        shape_menu.actions_list = shape_actions

        visibility_action = shape_menu.addAction("Show")
        visibility_action.setCheckable(True)
        visibility_action.setChecked(shape.isVisible())
        visibility_action.triggered.connect(shape.setVisible)
        shape_actions['visible'] = visibility_action

        plot_action = shape_menu.addAction("Plot")
        plot_action.setCheckable(True)
        plot_action.triggered.connect(lambda state: self.toggle_plot(shape, state))
        shape_actions['plot'] = plot_action

        delete_action = shape_menu.addAction("Remove")
        delete_action.triggered.connect(lambda: self.delete_shape(shape))
        shape_actions['delete'] = delete_action

        # Add attributes to ROI
        shape.name = name
        shape.menu = shape_menu
        shape.setAcceptedMouseButtons(QtCore.Qt.RightButton)
        shape.sigClicked.connect(self.on_roi_clicked)  # Connect sigClicked to the handler
        shape.sigRegionChanged.connect(lambda: self.updateLineROI(shape))
        shape.plot = self.axLineROI.plot([], [], pen=shape.pen)
        shape.plot.hide()

        self.addItem(shape)
        self.shapes.append(shape)
        self.shape_properties_menu.addMenu(shape.menu)

    def add_line(self):
        position_point = ((10, 10), (50, 10))  # Start and end position
        center_point = (0, 0)  # center point (x, y)

        line = pg.LineSegmentROI(position_point, center_point)
        line.setPen(pg.mkPen(QtGui.QColor(0, 255, 0), width=2))  # green

        self.add_shape(line)

    def add_rectangle(self):
        rect = pg.RectROI([10, 20], [30, 20])  # Position (x, y), size (width, height)
        rect.setPen(pg.mkPen(QtGui.QColor(255, 0, 0), width=2))  # red

        rect.addRotateHandle([0, 0], [0.5, 0.5])  # position at top-left corner, center at center of ROI

        self.add_shape(rect)

    def add_ellipse(self):
        ellipse = pg.EllipseROI([10, 50], [20, 20])  # Position (x, y), size (width, height)
        ellipse.setPen(pg.mkPen(QtGui.QColor(0, 0, 255), width=2))  # blue

        self.add_shape(ellipse)

    def delete_shape(self, shape: pg.ROI):
        """Delete a shape from the scene and update the shapes list and visibility menu."""
        self.shapes.remove(shape)
        self.getView().scene().removeItem(shape)
        if shape in self.shapes_plot:
            self.hide_plot(shape)
            self.axLineROI.removeItem(shape.plot)

    def delete_all_shapes(self):
        for shape in self.shapes.copy():
            self.delete_shape(shape)

    def toggle_all_visibility(self, checked: bool):
        for shape in self.shapes:
            shape.setVisible(checked)

    def update_shape_properties_menu(self):
        """Update the visibility menu to show only existing shapes."""
        self.shape_properties_menu.clear()  # Clear old entries

        all_menu = self.shape_properties_menu.addMenu('All')

        all_show = all_menu.addAction('Show')
        all_show.setCheckable(True)
        all_show.setChecked(all([shape.isVisible() for shape in self.shapes])
                                and len(self.shapes) != 0)
        all_show.triggered.connect(
            lambda: self.toggle_all_visibility(all_show.isChecked()))

        all_plot = all_menu.addAction('Plot')
        all_plot.setCheckable(True)
        all_plot.setChecked(len(self.shapes_plot) == len(self.shapes)
                                and len(self.shapes) != 0)
        all_plot.triggered.connect(
            lambda: self.toggle_all_plot(all_plot.isChecked()))

        all_delete = all_menu.addAction('Remove')
        all_delete.triggered.connect(self.delete_all_shapes)

        self.shape_properties_menu.addSeparator()

        for shape in self.shapes:
            self.shape_properties_menu.addMenu(shape.menu)

    def close(self):
        self.figLineROI.deleteLater()
        self.delete_all_shapes()
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

    def create_keywords(self) -> List[str]:
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

    def setCompleter(self, completer: QtWidgets.QCompleter):
        """ Sets/removes completer """
        if self.completer:
            if self.completer.popup().isVisible(): return None
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

        # Fixe issue if press control after an eval (issue appears if do self.completer = None)
        if self.completer and controlPressed:
            super().keyPressEvent(event)
            return None

        if not self.completer or not tabPressed:
            if (self.completer and enterPressed and self.completer.popup().isVisible()):
                self.completer.activated.emit(
                    self.completer.popup().currentIndex().data())
            else:
                super().keyPressEvent(event)

        if self.skip_has_eval or has_eval(self.text()):
            if not self.completer:
                self.setCompleter(QtWidgets.QCompleter(self.create_keywords()))
        else:
            if self.completer:
                self.setCompleter(None)

        if self.completer and not tabPressed:
            self.completer.popup().close()

        if not self.completer or not tabPressed:
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


class MyInputDialog(QtWidgets.QDialog):

    def __init__(self, parent: QtWidgets.QMainWindow, name: str):

        super().__init__(parent)
        self.setWindowTitle(name)

        lineEdit = MyLineEdit()
        lineEdit.setMaxLength(10000000)
        self.lineEdit = lineEdit

        # Add OK and Cancel buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            self)

        # Connect buttons
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel(f"Set {name} value"))
        layout.addWidget(lineEdit)
        layout.addWidget(button_box)
        layout.addStretch()
        layout.setContentsMargins(10, 5, 10, 10)

        self.textValue = lineEdit.text
        self.setTextValue = lineEdit.setText
        self.resize(self.minimumSizeHint())

    def showEvent(self, event):
        """Focus and select the text in the lineEdit."""
        super().showEvent(event)
        self.lineEdit.setFocus()
        self.lineEdit.selectAll()

    def closeEvent(self, event):
        for children in self.findChildren(QtWidgets.QWidget):
            children.deleteLater()
        super().closeEvent(event)


class MyFileDialog(QtWidgets.QDialog):

    def __init__(self, parent: QtWidgets.QMainWindow, name: str,
                 mode: QtWidgets.QFileDialog):

        super().__init__(parent)
        if mode == QtWidgets.QFileDialog.AcceptOpen:
            self.setWindowTitle(f"Open file - {name}")
        elif mode == QtWidgets.QFileDialog.AcceptSave:
            self.setWindowTitle(f"Save file - {name}")

        file_dialog = QtWidgets.QFileDialog(self, QtCore.Qt.Widget)
        file_dialog.setAcceptMode(mode)
        file_dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog)
        file_dialog.setWindowFlags(file_dialog.windowFlags() & ~QtCore.Qt.Dialog)
        file_dialog.setDirectory(PATHS['last_folder'])
        file_dialog.setNameFilters(SUPPORTED_EXTENSION.split(";;"))

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(file_dialog)
        layout.addStretch()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        self.exec_ = file_dialog.exec_
        self.selectedFiles = file_dialog.selectedFiles

    def closeEvent(self, event):
        for children in self.findChildren(QtWidgets.QWidget):
            children.deleteLater()

        super().closeEvent(event)


class MyQCheckBox(QtWidgets.QCheckBox):

    def __init__(self, parent):
        self.parent = parent
        super().__init__()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.parent.valueEdited()
        try:
            inspect.signature(self.parent.write)
        except ValueError: pass  # For built-in method (occurs for boolean for action parameter)
        else:
            self.parent.write()


class MyQComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.readonly = False
        self.wheel = True
        self.key = True

    def mousePressEvent(self, event):
        if not self.readonly:
            super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if not self.readonly and self.key:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        if not self.readonly and self.wheel:
            super().wheelEvent(event)


class CustomMenu(QtWidgets.QMenu):
    """ Menu with action containing sub-menu for recipe and parameter selection """
    def __init__(self,
                 gui: QtWidgets.QMainWindow,
                 main_combobox: QtWidgets.QComboBox = None,
                 second_combobox: QtWidgets.QComboBox = None,
                 update_gui: Callable[[None], None] = None):

        super().__init__()
        self.gui = gui  #  gui is scanner
        self.main_combobox = main_combobox
        self.second_combobox = second_combobox
        self.update_gui = update_gui

        self.current_menu = 1
        self.selected_action = None

        self.recipe_names = [self.main_combobox.itemText(i)
                             for i in range(self.main_combobox.count())
                             ] if self.main_combobox else []

        self.HAS_RECIPE = len(self.recipe_names) > 1

        self.HAS_PARAM = (self.second_combobox.count() > 1
                          if self.second_combobox
                          else False)

        # To only show parameter if only one recipe
        if not self.HAS_RECIPE and self.HAS_PARAM:
            self.main_combobox = second_combobox
            self.second_combobox = None

            self.recipe_names = [self.main_combobox.itemText(i)
                                 for i in range(self.main_combobox.count())
                                 ] if self.main_combobox else []


    def addAnyAction(self, action_text='', icon_name='',
                     param_menu_active=False) -> Union[QtWidgets.QWidgetAction,
                                                       QtWidgets.QAction]:

        if self.HAS_RECIPE or (self.HAS_PARAM and param_menu_active):
            action = self.addCustomAction(action_text, icon_name,
                                          param_menu_active=param_menu_active)
        else:
            action = self.addAction(action_text)
            if icon_name != '':
                action.setIcon(icons[icon_name])

        return action

    def addCustomAction(self, action_text='', icon_name='',
                        param_menu_active=False) -> QtWidgets.QWidgetAction:
        """ Create an action with a sub menu for selecting a recipe and parameter """

        def close_menu():
            self.selected_action = action_widget
            self.close()

        def handle_hover():
            """ Fixe bad hover behavior and refresh radio_button """
            self.setActiveAction(action_widget)
            recipe_name = self.main_combobox.currentText()
            action = recipe_menu.actions()[self.recipe_names.index(recipe_name)]
            radio_button = action.defaultWidget()

            if not radio_button.isChecked():
                radio_button.setChecked(True)

        def handle_radio_click(name):
            """ Update parameters available, open parameter menu if available
            and close main menu to validate the action """
            if self.current_menu == 1:
                self.main_combobox.setCurrentIndex(self.recipe_names.index(name))
                if self.update_gui:
                    self.update_gui()
                recipe_menu.close()

                if param_menu_active:
                    param_items = [self.second_combobox.itemText(i)
                                   for i in range(self.second_combobox.count())
                                   ] if self.second_combobox else []

                    if len(param_items) > 1:
                        self.current_menu = 2
                        setup_menu_parameter(param_menu)
                        return None
            else:
                update_parameter(name)
                param_menu.close()
                self.current_menu = 1
                action_button.setMenu(recipe_menu)

            close_menu()

        def reset_menu(button: QtWidgets.QToolButton):
            QtWidgets.QApplication.sendEvent(
                button, QtCore.QEvent(QtCore.QEvent.Leave))
            self.current_menu = 1
            action_button.setMenu(recipe_menu)

        def setup_menu_parameter(param_menu: QtWidgets.QMenu):
            param_items = [self.second_combobox.itemText(i)
                           for i in range(self.second_combobox.count())]
            param_name = self.second_combobox.currentText()

            param_menu.clear()
            for param_name_i in param_items:
                add_radio_button_to_menu(param_name_i, param_name, param_menu)

            action_button.setMenu(param_menu)
            action_button.showMenu()

        def update_parameter(name: str):
            param_items = [self.second_combobox.itemText(i)
                           for i in range(self.second_combobox.count())]
            self.second_combobox.setCurrentIndex(param_items.index(name))
            if self.update_gui:
                self.update_gui()

        def add_radio_button_to_menu(item_name: str, current_name: str,
                                     target_menu: QtWidgets.QMenu):
            widget = QtWidgets.QFrame()
            radio_button = QtWidgets.QRadioButton(item_name, widget)
            action = QtWidgets.QWidgetAction(self.gui)
            action.setDefaultWidget(radio_button)
            target_menu.addAction(action)

            if item_name == current_name:
                radio_button.setChecked(True)

            radio_button.clicked.connect(
                lambda: handle_radio_click(item_name))

        # Add custom action
        action_button = QtWidgets.QToolButton()
        action_button.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        action_button.setText(f"   {action_text}")
        action_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        action_button.setAutoRaise(True)
        action_button.clicked.connect(close_menu)
        action_button.enterEvent = lambda event: handle_hover()
        if icon_name != '':
            action_button.setIcon(icons[icon_name])

        action_widget = QtWidgets.QWidgetAction(action_button)
        action_widget.setDefaultWidget(action_button)
        self.addAction(action_widget)

        recipe_menu = QtWidgets.QMenu()
        # recipe_menu.aboutToShow.connect(lambda: self.set_clickable(False))
        recipe_menu.aboutToHide.connect(lambda: reset_menu(action_button))

        if param_menu_active:
            param_menu = QtWidgets.QMenu()
            # param_menu.aboutToShow.connect(lambda: self.set_clickable(False))
            param_menu.aboutToHide.connect(lambda: reset_menu(action_button))

        recipe_name = self.main_combobox.currentText()

        for recipe_name_i in self.recipe_names:
            add_radio_button_to_menu(recipe_name_i, recipe_name, recipe_menu)

        action_button.setMenu(recipe_menu)

        return action_widget


class RecipeMenu(CustomMenu):

    def __init__(self, gui: QtWidgets.QMainWindow):  # gui is scanner

        main_combobox = gui.selectRecipe_comboBox if gui else None
        second_combobox = gui.selectParameter_comboBox if gui else None
        update_gui = gui._updateSelectParameter if gui else None

        super().__init__(gui, main_combobox, second_combobox, update_gui)
