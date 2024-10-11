# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 14:32:41 2024

@author: Jonathan
"""

import sys
import platform

import numpy as np
import pandas as pd
import qtpy
from qtpy import QtCore, QtWidgets
import pyqtgraph as pg

from .GUI_instances import clearAbout
from .icons import icons

from ..web import project_url, drivers_url, doc_url
from ... import __version__


def get_versions() -> dict:
    """Information about Autolab versions """

    # Based on Spyder about.py (https://github.com/spyder-ide/spyder/blob/3ce32d6307302a93957594569176bc84d9c1612e/spyder/plugins/application/widgets/about.py#L40)
    versions = {
        'autolab': __version__,
        'python': platform.python_version(),  # "2.7.3"
        'bitness': 64 if sys.maxsize > 2**32 else 32,
        'qt_api': qtpy.API_NAME,      # PyQt5
        'qt_api_ver': (qtpy.PYSIDE_VERSION if 'pyside' in qtpy.API
                       else qtpy.PYQT_VERSION),
        'system': platform.system(),   # Linux, Windows, ...
        'release': platform.release(),  # XP, 10.6, 2.2.0, etc.
        'pyqtgraph': pg.__version__,
        'numpy': np.__version__,
        'pandas': pd.__version__,
    }
    if sys.platform == 'darwin':
        versions.update(system='macOS', release=platform.mac_ver()[0])

    return versions


class AboutWindow(QtWidgets.QMainWindow):

    def __init__(self, parent: QtWidgets.QMainWindow = None):

        super().__init__()
        self.mainGui = parent
        self.setWindowTitle('AUTOLAB - About')
        self.setWindowIcon(icons['autolab'])

        self.init_ui()

        self.adjustSize()

        # Don't want to have about windows taking the full screen
        self.setWindowFlags(QtCore.Qt.Window
                            | QtCore.Qt.WindowMinimizeButtonHint
                            | QtCore.Qt.WindowCloseButtonHint
                            | QtCore.Qt.WindowTitleHint)

    def init_ui(self):
        versions = get_versions()

        # Main layout creation
        layoutWindow = QtWidgets.QVBoxLayout()
        layoutTab = QtWidgets.QHBoxLayout()
        layoutWindow.addLayout(layoutTab)
        layoutWindow.setContentsMargins(0,0,0,0)
        layoutWindow.setSpacing(0)

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(layoutWindow)
        self.setCentralWidget(centralWidget)

        frameOverview = QtWidgets.QFrame()
        layoutOverview = QtWidgets.QVBoxLayout(frameOverview)
        layoutOverview.setAlignment(QtCore.Qt.AlignTop)

        frameLegal = QtWidgets.QFrame()
        layoutLegal = QtWidgets.QVBoxLayout(frameLegal)
        layoutLegal.setAlignment(QtCore.Qt.AlignTop)

        tab = QtWidgets.QTabWidget(self)
        tab.addTab(frameOverview, 'Overview')
        tab.addTab(frameLegal, 'Legal')

        label_pic = QtWidgets.QLabel()
        label_pic.setPixmap(icons['autolab-pixmap'])

        label_autolab = QtWidgets.QLabel(f"<h2>Autolab {versions['autolab']}</h2>")
        label_autolab.setAlignment(QtCore.Qt.AlignCenter)

        frameIcon = QtWidgets.QFrame()
        layoutIcon = QtWidgets.QVBoxLayout(frameIcon)
        layoutIcon.addWidget(label_pic)
        layoutIcon.addWidget(label_autolab)
        layoutIcon.addStretch()

        layoutTab.addWidget(frameIcon)
        layoutTab.addWidget(tab)

        label_versions = QtWidgets.QLabel(
            f"""
            <h1>Autolab</h1>

            <h3>Python package for scientific experiments automation</h3>

            <p>
            {versions['system']} {versions['release']}
            <br>
            Python {versions['python']} - {versions['bitness']}-bit
            <br>
            {versions['qt_api']} {versions['qt_api_ver']} |
            PyQtGraph {versions['pyqtgraph']} |
            Numpy {versions['numpy']} |
            Pandas {versions['pandas']}
            </p>

            <p>
            <a href="{project_url}">Project</a> |
            <a href="{drivers_url}">Drivers</a> |
            <a href="{doc_url}"> Documentation</a>
            </p>
            """
        )
        label_versions.setOpenExternalLinks(True)
        label_versions.setWordWrap(True)

        layoutOverview.addWidget(label_versions)

        label_legal = QtWidgets.QLabel(
            f"""
            <p>
            Created by <b>Quentin Chateiller</b>, Python drivers originally from
            Quentin Chateiller and <b>Bruno Garbin</b>, for the C2N-CNRS
            (Center for Nanosciences and Nanotechnologies, Palaiseau, France)
            ToniQ team.
            <br>
            Project continued by <b>Jonathan Peltier</b>, for the C2N-CNRS
            Minaphot team and <b>Mathieu Jeannin</b>, for the C2N-CNRS
            Odin team.
            <br>
            <br>
            Distributed under the terms of the
            <a href="{project_url}/blob/master/LICENSE">GPL-3.0 licence</a>
            </p>"""
        )
        label_legal.setOpenExternalLinks(True)
        label_legal.setWordWrap(True)
        layoutLegal.addWidget(label_legal)

    def closeEvent(self, event):
        """ Does some steps before the window is really killed """
        clearAbout()

        if not self.mainGui:
            QtWidgets.QApplication.quit()  # close the about app
