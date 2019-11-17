Installation
============

This package is working on Python version 3.6+.

Required packages:

* numpy
* pandas

Optional packages (depending on the drivers and connections types you will use):

* pyvisa
* python-vxi11

All these packages will be installed automatically, if not already present on your system.


Autolab
-------

This project is hosted in the global python repository PyPi at the following address : https://pypi.org/project/autolab/
To install the Autolab python package on your computer, we then advice you to use the Python package manager ``pip`` in a Python environnement:	
	
If the package is already installed, you can upgrade it to the last official version with the following command:

.. code-block:: none

	pip install autolab
	
To update the package:

.. code-block:: none

	pip install autolab --upgrade
	
Import the Autolab package in a Python shell to check that the installation is correct.

.. code-block:: python

	>>> import autolab
	
	
PyQt5 for the GUI
-----------------

The GUI requires the package PyQt5. But depending if you are using Anaconda or not, the installation is different:

With Anaconda:

.. code-block:: none

	conda install pyqt
	
Without:

.. code-block:: none

	pip install pyqt5
	
	
Development version
-------------------

You can install the latest development version (at your own risk) directly form GitHub:

.. code-block:: none

	pip install http://github.com/qcha41/autolab/zipball/master
	



