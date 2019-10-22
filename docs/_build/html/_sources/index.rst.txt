.. autolab documentation master file, created by
   sphinx-quickstart on Thu Oct  3 21:54:07 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Autolab's documentation!
===================================

Autolab is a Python package created to control easily your laboratory instruments and to quickly automate your scientific experiments.

This package provides a set of (>40) drivers, and three level of interfaces to use them: 

* **A low-level interface**: a raw access to the package's drivers.

.. code-block:: python

	>>> import autolab
	>>> laserSource = autolab.get_driver('yenista_TUNICS','VISA',address='GPIB0::12::INSTR')
	>>> powerMeter = autolab.get_driver('exfo_LTB1','TELNET',address='192.168.1.14')
	>>> laserSource.set_wavelength(1550)
	>>> laserSource.get_wavelength()
	1550
	>>> powerMeter.get_current_power()
	156.89e-6

Autolab can store locally the configuration informations required to instantiate a driver, to facilitate its further use.

.. code-block:: python

	>>> laserSource = autolab.get_driver_by_config('myTunics')
	>>> powerMeter = autolab.get_driver_by_config('powermeter_exfo')
	>>> laserSource.set_wavelength(1550)
	>>> laserSource.get_wavelength()
	1550
	>>> powerMeter.get_current_power()
	156.89e-6
	
* **A high-level interface**: a modelization of the instruments stored locally with Modules, Variables and Actions objects, for a user-friendly and straightforward way to communicate with the instrument.
	
.. code-block:: python

	>>> laserSource = autolab.get_device('myTunics')
	>>> powerMeter = autolab.get_device('powermeter_exfo')
	>>> laserSource.wavelength(1550)
	>>> laserSource.wavelength()
	1550
	>>> powerMeter.power()
	156.89e-6

* **A graphical interface**: a user-friendly GUI based on the high-level interface, that allows the user to interact even more easily with his instruments through three panels: A Control Panel, a Monitor and a Scanner.
	
.. figure:: gui/scanning.png
	:scale: 50 %
	:figclass: align-center	
	
	
You find this package useful ? Please help us to improve its visibility by adding a star on the `GitHub page of this project <https://github.com/qcha41/autolab>`_ ! :-)
	
Table of contents:

.. toctree::
   :maxdepth: 1
   
   installation
   low_level/index
   high_level/index
   gui/index
   help_report
   about
   


