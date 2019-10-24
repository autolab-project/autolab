.. _userguide_low:

Open and use a Driver
=====================

The low-level interface provides a raw access to instantiate and use directly a driver implemented in Autolab, through a *Driver* object

To see the list of available drivers sorted by categories, simply use the function ``show_drivers`` of Autolab. If you just want the list, call the ``list_drivers`` function.

.. code-block:: python

	>>> import autolab
	>>> autolab.show_drivers()
	>>> autolab.list_drivers()

.. note::

	The driver of your instrument is missing ? Please contribute to Autolab by creating yourself a new driver, following the provided guidelines : :ref:`create_driver`
	
To get more information about one particular driver (connection types, modules, required configuration, ...), call the function ``driver_help`` of Autolab, with the name of the driver.

.. code-block:: python

	>>> autolab.driver_help('yenista_TUNICS')

The instantiation of a *Driver* object is done through the function ``get_driver`` of Autolab, and requires a particular configuration : 

* The name of the driver: one of the name appearing in the ``list_drivers`` function (ex: 'yenista_TUNICS').
* The connection type: it indicates the library to use to communicate with the instrument. The available connection types are listed in the help function ``driver_help`` (ex: 'VISA', 'TELNET', ...).
* Driver-dependent arguments: they are listed in the help function ``driver_help`` (ex: address, port, number of channel, module configuration, ...).

.. code-block:: python

	>>> laserSource = autolab.get_driver('yenista_TUNICS','VISA',address='GPIB0::12::INSTR')
	
You are now ready to use the functions implemented in the *Driver*:

.. code-block:: python

	>>> laserSource.set_wavelength(1550)
	>>> laserSource.get_wavelength()
	1550

