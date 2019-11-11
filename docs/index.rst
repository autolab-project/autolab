.. autolab documentation master file, created by
   sphinx-quickstart on Thu Oct  3 21:54:07 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Autolab's documentation!
===================================

**"With Autolab, forget your instruments, focus on your experiment!"**

Autolab is a Python package dedicated to control remotely any laboratory instruments and automate scientific experiments in the most user-friendly way. This package provides a set of standardized drivers for about 40 instruments (for now) which are ready to use, and is open to inputs from the community (new drivers or upgrades of existing ones). Autolab can be either used through a Python shell, an OS shell, or a graphical interface.

In this package, the interaction with a scientific instrument can be done through two different objects : the **Drivers**, or the **Devices**.

* The :ref:`lowlevel` provides a raw access to the package's drivers functions. The instantiation of a **Driver** requires some configuration information (ex `yenista_TUNICS` here) that can be saved locally to simplify the user scripts (ex `my_powermeter` here).

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

* The :ref:`highlevel`, are an abstraction layer of the low-level interface that provide a simple and straightforward way to communicate with an instrument, through a hierarchy of Modules, Variables and Actions objects. The configuration of the driver associated to the instrument has to be saved locally in order to interact with it through a **Device**.

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

The user can also interact even more easily with this high-level interface through a user-friendly :ref:`gui` which contains three panels: A Control Panel (graphical equivalent of the high-level interface), a Monitor (to monitor the value of a Variable in time) and a Scanner (to scan a Parameter and execute a custom Recipe).
	
	.. figure:: gui/scanning.png
		:scale: 50 %
		:figclass: align-center	
		
Autolab is also provided with an OS shell interface (Windows and Linux) that can be used to perform to perform a quick single-shot operation without opening explicitely a Python shell. 

	.. code-block:: 

		>>> autolab devices my_tunics.wavelength -v 1551
	
	
**You find this package useful?** Please help us to improve its visibility by adding a star on the `GitHub page of this project <https://github.com/qcha41/autolab>`_ !

A Google Slides presentation with examples is available here: `bit.ly/autolab-demo <bit.ly/autolab-demo>`_

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
   


