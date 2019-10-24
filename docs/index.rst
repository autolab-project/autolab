.. autolab documentation master file, created by
   sphinx-quickstart on Thu Oct  3 21:54:07 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Autolab's documentation!
===================================

Autolab is a Python package dedicated to laboratory instruments remote control and to scientific experiments automation.

This package provides a set of standardized drivers for more than 40 instruments, that can be used through three different interfaces: 

* A :ref:`lowlevel`, which provides a raw access to the package's drivers functions. The instantiation of a **Driver** requires some configuration information (ex `yenista_TUNICS` here) that can be saved locally to simplify the user scripts (ex `my_powermeter` here).

.. code-block:: python

	>>> import autolab
	
	>>> laserSource = autolab.get_driver('yenista_TUNICS','VISA',address='GPIB0::12::INSTR')
	>>> laserSource.set_wavelength(1550)
	>>> laserSource.get_wavelength()
	1550
	
	>>> powerMeter = autolab.get_driver_by_config('my_powermeter')
	>>> powerMeter.get_current_power()
	156.89e-6
	
	>>> stage = autolab.get_driver_by_config('my_stage')
	>>> stage.go_home()

* A :ref:`highlevel`, which is an abstraction layer of the low-level interface using local configurations, that provides a simple and straightforward way to communicate with an instrument through a **Device** object (a hierarchy of Modules, Variables and Actions objects). 
	
.. code-block:: python

	>>> import autolab

	>>> laserSource = autolab.get_device('my_tunics')	# Create the Device 'my_tunics'
	>>> laserSource.wavelength(1550)			# Set the Variable 'wavelength'
	>>> laserSource.wavelength()				# Read the Variable 'wavelength'
	1550
	
	>>> powerMeter = autolab.get_device('my_powermeter')	# Create the Device 'my_powermeter'
	>>> powerMeter.power()					# Read the Variable 'power'
	156.89e-6
	
	>>> stage = autolab.get_device('my_stage')		# Create the Device 'my_stage'
	>>> stage.home()					# Execute the Action 'home'

These interfaces are also usable through:

* A :ref:`gui`, a user-friendly GUI based on the high-level interface, that allows the user to interact even more easily with his instruments through three panels: A Control Panel (graphical equivalent of the high-level interface), a Monitor (to monitor the value of a Variable in time) and a Scanner (to scan a Parameter and execute a custom Recipe).
	
.. figure:: gui/scanning.png
	:scale: 50 %
	:figclass: align-center	
	
* :ref:`shell_scripts`, to perform a quick single-shot operation without opening explicitely a Python shell. This can be done through 3 different shell scripts.

.. code-block:: 

	>>> autolab-devices my_tunics.wavelength -v 1551

	
	
You find this package useful ? Please help us to improve its visibility by adding a star on the `GitHub page of this project <https://github.com/qcha41/autolab>`_ ! :-)
	
Table of contents:

.. toctree::
   :maxdepth: 1
   
   installation
   low_level/index
   high_level
   gui/index
   shell/index
   help_report
   about
   


