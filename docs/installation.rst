Installation
============

Python
------

This package works on Python version 3.6+.

* On Windows, we recommend installing Python through the distribution Anaconda: https://www.anaconda.com/
* On older versions of Windows (before Windows 7), we recommend installing Python manually: https://www.python.org/
* On Linux, we recommend installing Python through the `apt-get` command.

Additional required packages (installed automatically with Autolab):

* numpy
* pandas
* pyvisa
* python-vxi11
* qtpy
* pyqtgraph
* requests
* tqdm
* comtypes

Autolab package
---------------

This project is hosted in the global Python repository PyPi at the following address: https://pypi.org/project/autolab/.
To install the Autolab python package on your computer, we then advise you to use the Python package manager ``pip`` in a Python environnement:

.. code-block:: none

	pip install autolab

If the package is already installed, you can check the current version installed and upgrade it to the latest official version with the following commands:

.. code-block:: none

	pip show autolab
	pip install autolab --upgrade

Import the Autolab package in a Python shell to check that the installation is correct.

.. code-block:: python

	>>> import autolab


Packages for the GUI
--------------------

The GUI requires several packages to work, but depending on whether you are using Anaconda or not, the installation is different:

With Anaconda:

.. code-block:: none

    conda install pyqtgraph
    conda install qtpy
    conda install pyqt

Without:

.. code-block:: none

    pip install pyqtgraph
    pip install qtpy
    pip install pyqt5

Note that thanks to qtpy, you can install a different Qt backend instead of pyqt5, such as pyqt6, pyside2, or pyside6

Development version
-------------------

You can install the latest development version (at your own risk) directly form GitHub:

.. code-block:: none

	pip install https://github.com/autolab-project/autolab/archive/master.zip
