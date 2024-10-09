# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 22:56:32 2024

@author: jonathan
"""

from typing import Dict
import sys

from qtpy import QtCore, QtWidgets

from .icons import icons
from .GUI_instances import clearPreferences
from ..utilities import boolean
from ..config import (check_autolab_config, change_autolab_config,
                      check_plotter_config, change_plotter_config,
                      load_config, modify_config, set_temp_folder)


class PreferencesWindow(QtWidgets.QMainWindow):

    def __init__(self, parent: QtWidgets.QMainWindow = None):

        super().__init__()
        self.mainGui = parent
        self.setWindowTitle('AUTOLAB - Preferences')
        self.setWindowIcon(icons['preference'])

        self.setFocus()
        self.activateWindow()
        self.statusBar = self.statusBar()

        self.init_ui()

        self.adjustSize()

        self.resize(500, 670)

    def init_ui(self):
        # Update config if needed
        check_autolab_config()
        check_plotter_config()

        autolab_config = load_config('autolab_config')
        plotter_config = load_config('plotter_config')

        centralWidget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(centralWidget)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setCentralWidget(centralWidget)

        scrollAutolab = QtWidgets.QScrollArea()
        scrollAutolab.setWidgetResizable(True)
        frameAutolab = QtWidgets.QFrame()
        scrollAutolab.setWidget(frameAutolab)
        layoutAutolab = QtWidgets.QVBoxLayout(frameAutolab)
        layoutAutolab.setAlignment(QtCore.Qt.AlignTop)

        scrollPlotter = QtWidgets.QScrollArea()
        scrollPlotter.setWidgetResizable(True)
        framePlotter = QtWidgets.QFrame()
        scrollPlotter.setWidget(framePlotter)
        layoutPlotter = QtWidgets.QVBoxLayout(framePlotter)
        layoutPlotter.setAlignment(QtCore.Qt.AlignTop)

        tab = QtWidgets.QTabWidget(self)
        tab.addTab(scrollAutolab, 'Autolab')
        tab.addTab(scrollPlotter, 'Plotter')

        layout.addWidget(tab)

        # Create a frame for each main key in the dictionary
        self.inputs_autolab = {}
        self.inputs_plotter = {}

        ### Autolab
        ## GUI
        main_key = 'GUI'
        group_box = QtWidgets.QGroupBox(main_key)
        layoutAutolab.addWidget(group_box)
        group_layout = QtWidgets.QFormLayout(group_box)
        self.inputs_autolab[main_key] = {}

        sub_key = 'qt_api'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QComboBox()
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Select the GUI Qt binding')
        input_widget.addItems(['default', 'pyqt5', 'pyqt6', 'pyside2', 'pyside6'])
        index = input_widget.findText(saved_value)
        input_widget.setCurrentIndex(index)
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(QtWidgets.QLabel(sub_key), input_widget)

        sub_key = 'theme'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QComboBox()
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Select the GUI theme')
        input_widget.addItems(['default', 'dark'])
        index = input_widget.findText(saved_value)
        input_widget.setCurrentIndex(index)
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(QtWidgets.QLabel(sub_key), input_widget)

        sub_key = 'font_size'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QSpinBox()
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Select the GUI text font size')
        input_widget.setValue(int(float(saved_value)))
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(QtWidgets.QLabel(sub_key), input_widget)

        sub_key = 'image_background'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QLineEdit()
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Select the plots background color (disabled if use dark theme)')
        input_widget.setText(str(saved_value))
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(QtWidgets.QLabel(sub_key), input_widget)

        sub_key = 'image_foreground'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QLineEdit()
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Select the plots foreground color (disabled if use dark theme)')
        input_widget.setText(str(saved_value))
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(QtWidgets.QLabel(sub_key), input_widget)

        ## control_center
        main_key = 'control_center'
        group_box = QtWidgets.QGroupBox(main_key)
        layoutAutolab.addWidget(group_box)
        group_layout = QtWidgets.QFormLayout(group_box)
        self.inputs_autolab[main_key] = {}

        sub_key = 'precision'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QSpinBox()
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Select the displayed precision for variables in the control panel')
        input_widget.setValue(int(float(saved_value)))
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(QtWidgets.QLabel(sub_key), input_widget)

        sub_key = 'print'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QCheckBox(sub_key)
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Select if print GUI information to console')
        input_widget.setChecked(boolean(saved_value))
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(input_widget)

        sub_key = 'logger'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QCheckBox(sub_key)
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Activate a logger to display GUI information')
        input_widget.setChecked(boolean(saved_value))
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(input_widget)

        sub_key = 'console'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QCheckBox(sub_key)
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Activate a console for debugging')
        input_widget.setChecked(boolean(saved_value))
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(input_widget)

        ## monitor
        main_key = 'monitor'
        group_box = QtWidgets.QGroupBox(main_key)
        layoutAutolab.addWidget(group_box)
        group_layout = QtWidgets.QFormLayout(group_box)
        self.inputs_autolab[main_key] = {}

        sub_key = 'precision'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QSpinBox()
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Select the displayed precision for variables in monitors')
        input_widget.setValue(int(float(saved_value)))
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(QtWidgets.QLabel(sub_key), input_widget)

        sub_key = 'save_figure'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QCheckBox(sub_key)
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Select if save figure image when saving monitor data')
        input_widget.setChecked(boolean(saved_value))
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(input_widget)

        ## scanner
        main_key = 'scanner'
        group_box = QtWidgets.QGroupBox(main_key)
        layoutAutolab.addWidget(group_box)
        group_layout = QtWidgets.QFormLayout(group_box)
        self.inputs_autolab[main_key] = {}

        sub_key = 'precision'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QSpinBox()
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Select the displayed precision for variables in the scanner')
        input_widget.setValue(int(float(saved_value)))
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(QtWidgets.QLabel(sub_key), input_widget)

        sub_key = 'save_config'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QCheckBox(sub_key)
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Select if save config file when saving scanner data')
        input_widget.setChecked(boolean(saved_value))
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(input_widget)

        sub_key = 'save_figure'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QCheckBox(sub_key)
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Select if save figure image when saving scanner data')
        input_widget.setChecked(boolean(saved_value))
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(input_widget)

        sub_key = 'save_temp'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QCheckBox(sub_key)
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Select if save temporary data. Should not be disable!')
        input_widget.setChecked(boolean(saved_value))
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(input_widget)

        sub_key = 'ask_close'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QCheckBox(sub_key)
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Set whether a warning message about unsaved data should be displayed when the scanner is closed.')
        input_widget.setChecked(boolean(saved_value))
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(input_widget)

        ## directories
        main_key = 'directories'
        group_box = QtWidgets.QGroupBox(main_key)
        layoutAutolab.addWidget(group_box)
        group_layout = QtWidgets.QFormLayout(group_box)
        self.inputs_autolab[main_key] = {}

        sub_key = 'temp_folder'
        saved_value = autolab_config[main_key][sub_key]
        input_widget = QtWidgets.QLineEdit()
        input_widget.setToolTip("Select the temporary folder. default correspond to os.environ['TEMP']")
        input_widget.setText(str(saved_value))
        self.inputs_autolab[main_key][sub_key] = input_widget
        group_layout.addRow(QtWidgets.QLabel(sub_key), input_widget)

        ## extra_driver_path
        main_key = 'extra_driver_path'
        group_box = QtWidgets.QFrame()
        group_layout = QtWidgets.QVBoxLayout(group_box)
        group_layout.setContentsMargins(0,0,0,0)
        layoutAutolab.addWidget(group_box)
        group_box_plugin = QtWidgets.QGroupBox(main_key)
        group_layout.addWidget(group_box_plugin)
        group_box.setToolTip('Add extra driver location')
        folder_layout = QtWidgets.QFormLayout(group_box_plugin)
        self.inputs_autolab[main_key] = {}

        addPluginButton = QtWidgets.QPushButton('Add driver folder')
        addPluginButton.setIcon(icons['add'])
        addPluginButton.clicked.connect(lambda: self.addOptionClicked(
            folder_layout, self.inputs_autolab, 'extra_driver_path',
            'onedrive',
            r'C:\Users\username\OneDrive\my_drivers'))
        group_layout.addWidget(addPluginButton)

        for sub_key, saved_value in autolab_config[main_key].items():
            self.addOptionClicked(
                folder_layout, self.inputs_autolab, main_key, sub_key, saved_value)

        ## extra_driver_url_repo
        main_key = 'extra_driver_url_repo'
        group_box = QtWidgets.QFrame()
        group_layout = QtWidgets.QVBoxLayout(group_box)
        group_layout.setContentsMargins(0,0,0,0)
        layoutAutolab.addWidget(group_box)
        group_box_plugin = QtWidgets.QGroupBox(main_key)
        group_layout.addWidget(group_box_plugin)
        group_box.setToolTip('Add extra url to download drivers from')
        url_layout = QtWidgets.QFormLayout(group_box_plugin)
        self.inputs_autolab[main_key] = {}

        addPluginButton = QtWidgets.QPushButton('Add driver url')
        addPluginButton.setIcon(icons['add'])
        addPluginButton.clicked.connect(lambda: self.addOptionClicked(
            url_layout, self.inputs_autolab, 'extra_driver_url_repo',
            r'C:\Users\username\OneDrive\my_drivers',
            r'https://github.com/my_repo/my_drivers'))
        group_layout.addWidget(addPluginButton)

        for sub_key, saved_value in autolab_config[main_key].items():
            self.addOptionClicked(
                url_layout, self.inputs_autolab, main_key, sub_key, saved_value)

        ### Plotter
        ## plugin
        main_key = 'plugin'
        group_box = QtWidgets.QFrame()
        group_layout = QtWidgets.QVBoxLayout(group_box)
        group_layout.setContentsMargins(0,0,0,0)
        group_layout.setSpacing(0)
        layoutPlotter.addWidget(group_box)
        group_box_plugin = QtWidgets.QGroupBox(main_key)
        group_layout.addWidget(group_box_plugin)
        group_box_plugin.setToolTip('Add plugins to plotter')
        plugin_layout = QtWidgets.QFormLayout(group_box_plugin)
        self.inputs_plotter[main_key] = {}

        addPluginButton = QtWidgets.QPushButton('Add plugin')
        addPluginButton.setIcon(icons['add'])
        addPluginButton.clicked.connect(lambda: self.addOptionClicked(
            plugin_layout, self.inputs_plotter, 'plugin', 'plugin', 'plotter'))
        group_layout.addWidget(addPluginButton)

        for sub_key, saved_value in plotter_config[main_key].items():
            self.addOptionClicked(
                plugin_layout, self.inputs_plotter, main_key, sub_key, saved_value)
            # To disable plotter modification
            input_key_widget, input_widget = self.inputs_plotter[main_key][sub_key]
            if sub_key == 'plotter':
                input_key_widget.setEnabled(False)
                input_widget.setEnabled(False)

        ## device
        main_key = 'device'
        group_box = QtWidgets.QGroupBox(main_key)
        layoutPlotter.addWidget(group_box)
        group_layout = QtWidgets.QFormLayout(group_box)
        self.inputs_plotter[main_key] = {}

        sub_key = 'address'
        saved_value = plotter_config[main_key][sub_key]
        input_widget = QtWidgets.QLineEdit()
        input_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_widget.setToolTip('Select the address of a device variable to be captured by the plotter.')
        input_widget.setText(str(saved_value))
        self.inputs_plotter[main_key][sub_key] = input_widget
        group_layout.addRow(QtWidgets.QLabel(sub_key), input_widget)

        ### Buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok
                | QtWidgets.QDialogButtonBox.Cancel
                | QtWidgets.QDialogButtonBox.Apply,
            self)

        layout.addWidget(button_box)
        button_box.setContentsMargins(6,6,6,6)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        apply_button = button_box.button(QtWidgets.QDialogButtonBox.Apply)
        apply_button.clicked.connect(self.apply)

    def addOptionClicked(self, main_layout: QtWidgets.QLayout,
                         main_inputs: dict, main_key: str, sub_key: str, val: str):
        """ Add new option layout """
        basename = sub_key
        names = main_inputs[main_key].keys()
        compt = 0
        while True:
            if sub_key in names:
                compt += 1
                sub_key = basename + '_' + str(compt)
            else:
                break

        layout = QtWidgets.QHBoxLayout()
        input_key_widget = QtWidgets.QLineEdit()
        input_key_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        input_key_widget.setText(sub_key)
        layout.addWidget(input_key_widget)
        input_widget = QtWidgets.QLineEdit()
        input_widget.setText(val)
        layout.addWidget(input_widget)
        button_widget = QtWidgets.QPushButton()
        button_widget.setIcon(icons['remove'])
        button_widget.clicked.connect(lambda: self.removeOptionClicked(
            layout, main_inputs, main_key, sub_key))
        layout.addWidget(button_widget)

        main_inputs[main_key][sub_key] = (input_key_widget, input_widget)
        main_layout.addRow(layout)

    def removeOptionClicked(self, layout: QtWidgets.QLayout,
                            main_inputs: dict, main_key: str,
                            sub_key: str):
        """ Remove optional argument layout """
        for j in reversed(range(layout.count())):
            layout.itemAt(j).widget().setParent(None)
        layout.setParent(None)
        main_inputs[main_key].pop(sub_key)

    def accept(self):
        try:
            self.generate_new_configs()
        except Exception as e:
            self.setStatus(f'Config error: {e}', 10000, False)
        else:
            self.close()

    def apply(self):
        try:
            self.generate_new_configs()
        except Exception as e:
            self.setStatus(f'Config error: {e}', 10000, False)

    def reject(self):
        self.close()

    @staticmethod
    def generate_new_dict(input_widgets: Dict[str, QtWidgets.QWidget]) -> dict:

        new_dict = {}
        for main_key, sub_dict in input_widgets.items():
            new_dict[main_key] = {}
            for sub_key, widget in sub_dict.items():
                if isinstance(widget, QtWidgets.QSpinBox):
                    new_dict[main_key][sub_key] = widget.value()
                elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                    new_dict[main_key][sub_key] = widget.value()
                elif isinstance(widget, QtWidgets.QCheckBox):
                    new_dict[main_key][sub_key] = widget.isChecked()
                elif isinstance(widget, QtWidgets.QComboBox):
                    new_dict[main_key][sub_key] = widget.currentText()
                elif isinstance(widget, tuple):
                    key_widget, value_widget = widget
                    new_dict[main_key][key_widget.text()] = value_widget.text()
                else:
                    new_dict[main_key][sub_key] = widget.text()

        return new_dict

    def generate_new_configs(self):
        new_autolab_dict = self.generate_new_dict(self.inputs_autolab)
        new_autolab_config = modify_config('autolab_config', new_autolab_dict)
        autolab_config = load_config('autolab_config')

        if new_autolab_config != autolab_config:
            change_autolab_config(new_autolab_config)

        new_plotter_dict = self.generate_new_dict(self.inputs_plotter)
        new_plotter_config = modify_config('plotter_config', new_plotter_dict)
        plotter_config = load_config('plotter_config')

        if new_plotter_config != plotter_config:
            change_plotter_config(new_plotter_config)

        if (new_autolab_config['directories']['temp_folder']
                != autolab_config['directories']['temp_folder']):
            set_temp_folder()

        if (new_autolab_config['control_center']['logger'] != autolab_config['control_center']['logger']
                and hasattr(self.mainGui, 'activate_logger')):
            self.mainGui.activate_logger(new_autolab_config['control_center']['logger'])

        if (new_autolab_config['control_center']['console'] != autolab_config['control_center']['console']
                and hasattr(self.mainGui, 'activate_console')):
            self.mainGui.activate_console(new_autolab_config['control_center']['console'])

        if (new_autolab_config['GUI']['qt_api'] != autolab_config['GUI']['qt_api']
                or new_autolab_config['GUI']['theme'] != autolab_config['GUI']['theme']
                or new_autolab_config['GUI']['font_size'] != autolab_config['GUI']['font_size']
                or new_autolab_config['GUI']['image_background'] != autolab_config['GUI']['image_background']
                or new_autolab_config['GUI']['image_background'] != autolab_config['GUI']['image_background']
                ):
            QtWidgets.QMessageBox.information(
                self,
                'Information',
                'One or more of the settings you changed requires a restart to be applied',
                QtWidgets.QMessageBox.Ok
                )

    def setStatus(self, message: str, timeout: int = 0, stdout: bool = True):
        """ Modify the message displayed in the status bar and add error message to logger """
        self.statusBar.showMessage(message, timeout)
        if not stdout: print(message, file=sys.stderr)

    def closeEvent(self, event):
        """ Does some steps before the window is really killed """
        clearPreferences()

        if not self.mainGui:
            QtWidgets.QApplication.quit()  # close the app
