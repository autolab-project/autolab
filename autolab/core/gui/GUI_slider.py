# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 23:23:51 2023

@author: jonathan
"""
from typing import Any, Union
import sys

import numpy as np
from qtpy import QtCore, QtWidgets

from .icons import icons
from .GUI_utilities import get_font_size, setLineEditBackground
from .GUI_instances import clearSlider
from ..config import get_control_center_config
from ..elements import Variable as Variable_og
from ..variables import Variable

if hasattr(QtCore.Qt.LeftButton, 'value'):
    LeftButton = QtCore.Qt.LeftButton.value
else:
    LeftButton = QtCore.Qt.LeftButton


class ProxyStyle(QtWidgets.QProxyStyle):
    """ https://stackoverflow.com/questions/67299834/pyqt-slider-not-come-to-a-specific-location-where-i-click-but-move-to-a-certain """
    def styleHint(self, hint, opt=None, widget=None, returnData=None):
        res = super().styleHint(hint, opt, widget, returnData)
        if hint == QtWidgets.QStyle.SH_Slider_AbsoluteSetButtons:
            res |= LeftButton
        return res


class Slider(QtWidgets.QMainWindow):

    changed = QtCore.Signal()  # Used by scanner to update filter when slider value changes

    def __init__(self,
                 variable: Union[Variable, Variable_og],
                 gui: QtWidgets.QMainWindow = None,
                 item: QtWidgets.QTreeWidgetItem = None):
        """ https://stackoverflow.com/questions/61717896/pyqt5-qslider-is-off-by-one-depending-on-which-direction-the-slider-is-moved """
        self.gui = gui  # gui can have setStatus, threadManager
        self.variable = variable
        self.item = item
        super().__init__()
        self.resize(self.minimumSizeHint())
        self.setWindowTitle(self.variable.address())
        self.setWindowIcon(icons['slider'])

        # Load configuration
        control_center_config = get_control_center_config()
        self.precision = int(float(control_center_config['precision']))

        self._font_size = get_font_size()

        # Slider
        self.slider_instantaneous = True
        self._last_moved = False  # Prevent double setting/readding after a slider has been moved with the slider_instantaneous=True

        if self.is_writable():
            self.true_min = self.variable.type(0)
            self.true_max = self.variable.type(10)
            self.true_step = self.variable.type(1)
        else:
            self.true_min = 0
            self.true_max = 10
            self.true_step = 1

        centralWidget = QtWidgets.QWidget()
        layoutWindow = QtWidgets.QVBoxLayout()
        layoutTopValue = QtWidgets.QHBoxLayout()
        layoutSlider = QtWidgets.QHBoxLayout()
        layoutBottomValues = QtWidgets.QHBoxLayout()

        centralWidget.setLayout(layoutWindow)
        layoutWindow.addLayout(layoutTopValue)
        layoutWindow.addLayout(layoutSlider)
        layoutWindow.addLayout(layoutBottomValues)

        self.instantCheckBox = QtWidgets.QCheckBox()
        self.instantCheckBox.setToolTip(
            "True: Changes instantaneously the value.\n" \
            "False: Changes the value when click released.")
        self.instantCheckBox.setCheckState(QtCore.Qt.Checked)
        self.instantCheckBox.stateChanged.connect(self.instantChanged)

        layoutTopValue.addWidget(QtWidgets.QLabel("Instant"))
        layoutTopValue.addWidget(self.instantCheckBox)

        self.valueWidget = QtWidgets.QLineEdit()
        self.valueWidget.setAlignment(QtCore.Qt.AlignCenter)
        self.valueWidget.setReadOnly(True)
        self.valueWidget.setText(f'{self.true_min}')
        setLineEditBackground(self.valueWidget, 'edited', self._font_size)

        layoutTopValue.addStretch()
        layoutTopValue.addWidget(QtWidgets.QLabel("Value"))
        layoutTopValue.addWidget(self.valueWidget)
        layoutTopValue.addStretch()
        layoutTopValue.addSpacing(40)

        self.sliderWidget = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sliderWidget.setValue(0)
        self.sliderWidget.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.sliderWidget.valueChanged.connect(self.valueChanged)
        self.sliderWidget.sliderReleased.connect(self.sliderReleased)
        self.sliderWidget.setStyle(ProxyStyle())

        button_minus = QtWidgets.QToolButton()
        button_minus.setArrowType(QtCore.Qt.LeftArrow)
        button_minus.clicked.connect(self.minusClicked)

        button_plus = QtWidgets.QToolButton()
        button_plus.setArrowType(QtCore.Qt.RightArrow)
        button_plus.clicked.connect(self.plusClicked)

        layoutSlider.addWidget(button_minus)
        layoutSlider.addWidget(self.sliderWidget)
        layoutSlider.addWidget(button_plus)

        self.minWidget = QtWidgets.QLineEdit()
        self.minWidget.setAlignment(QtCore.Qt.AlignLeft)
        self.minWidget.returnPressed.connect(self.minWidgetValueChanged)
        self.minWidget.textEdited.connect(lambda: setLineEditBackground(
            self.minWidget, 'edited', self._font_size))

        layoutBottomValues.addWidget(QtWidgets.QLabel("Min"))
        layoutBottomValues.addWidget(self.minWidget)
        layoutBottomValues.addSpacing(10)
        layoutBottomValues.addStretch()

        self.stepWidget = QtWidgets.QLineEdit()
        self.stepWidget.setAlignment(QtCore.Qt.AlignCenter)
        self.stepWidget.returnPressed.connect(self.stepWidgetValueChanged)
        self.stepWidget.textEdited.connect(lambda: setLineEditBackground(
            self.stepWidget, 'edited', self._font_size))

        layoutBottomValues.addWidget(QtWidgets.QLabel("Step"))
        layoutBottomValues.addWidget(self.stepWidget)
        layoutBottomValues.addStretch()
        layoutBottomValues.addSpacing(10)

        self.maxWidget = QtWidgets.QLineEdit()
        self.maxWidget.setAlignment(QtCore.Qt.AlignRight)
        self.maxWidget.returnPressed.connect(self.maxWidgetValueChanged)
        self.maxWidget.textEdited.connect(lambda: setLineEditBackground(
            self.maxWidget, 'edited', self._font_size))

        layoutBottomValues.addWidget(QtWidgets.QLabel("Max"))
        layoutBottomValues.addWidget(self.maxWidget)

        self.setCentralWidget(centralWidget)

        self.updateStep()

        self.resize(self.minimumSizeHint())

    def displayError(self, e: str):
        """ Wrapper to display errors """
        self.gui.setStatus(e, 10000, False) if self.gui and hasattr(
            self.gui, 'setStatus') else print(e, file=sys.stderr)

    def setVariableValue(self, value: Any):
        """ Wrapper to change variable value """
        if self.gui and hasattr(self.gui, 'threadManager') and self.item:
            self.gui.threadManager.start(
                self.item, 'write', value=value)
        else:
            self.variable(value)

    def is_writable(self):
        return self.variable.writable and self.variable.type in (int, float)

    def updateStep(self):

        if self.is_writable():
            slider_points = 1 + int(
                np.floor((self.true_max - self.true_min) / self.true_step))
            self.true_max = self.variable.type(
                self.true_step*(slider_points - 1) + self.true_min)

            self.minWidget.setText(f'{self.true_min}')
            setLineEditBackground(self.minWidget, 'synced', self._font_size)
            self.maxWidget.setText(f'{self.true_max}')
            setLineEditBackground(self.maxWidget, 'synced', self._font_size)
            self.stepWidget.setText(f'{self.true_step}')
            setLineEditBackground(self.stepWidget, 'synced', self._font_size)

            temp = self.slider_instantaneous
            self.slider_instantaneous = False
            self.sliderWidget.setMinimum(0)
            self.sliderWidget.setSingleStep(1)
            self.sliderWidget.setTickInterval(1)
            self.sliderWidget.setMaximum(slider_points - 1)
            self.slider_instantaneous = temp
        else: self.badType()

    def updateTrueValue(self, old_true_value: Any):

        if self.is_writable():
            new_cursor_step = round(
                (old_true_value - self.true_min) / self.true_step)
            slider_points = 1 + int(
                np.floor((self.true_max - self.true_min) / self.true_step))
            if new_cursor_step > (slider_points - 1):
                new_cursor_step = slider_points - 1
            elif new_cursor_step < 0:
                new_cursor_step = 0

            temp = self.slider_instantaneous
            self.slider_instantaneous = False
            self.sliderWidget.setSliderPosition(new_cursor_step)
            self.slider_instantaneous = temp

            true_value = self.variable.type(
                new_cursor_step*self.true_step + self.true_min)
            self.valueWidget.setText(f'{true_value:.{self.precision}g}')
            setLineEditBackground(self.valueWidget, 'edited', self._font_size)
        else: self.badType()

    def stepWidgetValueChanged(self):

        if self.is_writable():
            old_true_value = self.variable.type(self.valueWidget.text())
            try:
                true_step = self.variable.type(self.stepWidget.text())
                assert true_step != 0, "Can't have step=0"
                self.true_step = true_step
            except Exception as e:
                e = f"Variable {self.variable.address()}: {e}"
                self.displayError(e)
            else:
                self.updateStep()
                self.updateTrueValue(old_true_value)
        else: self.badType()

    def minWidgetValueChanged(self):

        if self.is_writable():
            old_true_value = self.variable.type(self.valueWidget.text())
            try:
                self.true_min = self.variable.type(self.minWidget.text())
            except Exception as e:
                e = f"Variable {self.variable.address()}: {e}"
                self.displayError(e)
            else:
                self.updateStep()
                self.updateTrueValue(old_true_value)
        else: self.badType()

    def maxWidgetValueChanged(self):

        if self.is_writable():
            old_true_value = self.variable.type(self.valueWidget.text())
            try:
                self.true_max = self.variable.type(self.maxWidget.text())
            except Exception as e:
                e = f"Variable {self.variable.address()}: {e}"
                self.displayError(e)
            else:
                self.updateStep()
                self.updateTrueValue(old_true_value)
        else: self.badType()

    def sliderReleased(self):
        """ Do something when the cursor is released """
        if self.is_writable():
            if self.slider_instantaneous and self._last_moved:
                self._last_moved = False
                return None
            self._last_moved = False
            value = self.sliderWidget.value()
            true_value = self.variable.type(
                value*self.true_step + self.true_min)
            self.valueWidget.setText(f'{true_value:.{self.precision}g}')
            setLineEditBackground(self.valueWidget, 'synced', self._font_size)
            self.setVariableValue(true_value)
            self.changed.emit()
            self.updateStep()
        else:
            self.badType()

    def valueChanged(self, value: Any):
        """ Do something with the slider value when the cursor is moved """
        if self.is_writable():
            self._last_moved = True
            true_value = self.variable.type(
                value*self.true_step + self.true_min)
            self.valueWidget.setText(f'{true_value:.{self.precision}g}')
            if self.slider_instantaneous:
                setLineEditBackground(self.valueWidget, 'synced', self._font_size)
                self.setVariableValue(true_value)
                self.changed.emit()
            else:
                setLineEditBackground(self.valueWidget, 'edited', self._font_size)
            # self.updateStep()  # Don't use it here, infinite loop leading to crash if set min > max
        else: self.badType()

    def instantChanged(self, value):
        self.slider_instantaneous = self.instantCheckBox.isChecked()

    def minusClicked(self):
        self.sliderWidget.setSliderPosition(self.sliderWidget.value()-1)
        self._last_moved = False
        if not self.slider_instantaneous: self.sliderReleased()

    def plusClicked(self):
        self.sliderWidget.setSliderPosition(self.sliderWidget.value()+1)
        self._last_moved = False
        if not self.slider_instantaneous: self.sliderReleased()

    def badType(self):
        setLineEditBackground(self.valueWidget, 'edited', self._font_size)
        setLineEditBackground(self.minWidget, 'edited', self._font_size)
        setLineEditBackground(self.stepWidget, 'edited', self._font_size)
        setLineEditBackground(self.maxWidget, 'edited', self._font_size)

        e = f"Variable {self.variable.address()}: Variable should be writable int or float"
        self.displayError(e)

    def closeEvent(self, event):
        """ This function does some steps before the window is really killed """
        clearSlider(self.variable)

        if self.gui is None:
            QtWidgets.QApplication.quit()  # close the slider app
