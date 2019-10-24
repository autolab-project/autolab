.. _userguide_low:

Load and use a Driver
=====================

The low-level interface provides a raw access to the drivers implemented in Autolab, through a **Driver** object, which contains functions that perform particular operations in your instrument.

.. warning::

	The Autolab drivers may contains internal functions, that are not dedicated to be called by the user, and some functions requires particular types of inputs. The authors declines any responsibility for the consequences of an incorrect use of the drivers. To avoid any problems, make sure you have a real understanding of what you are doing, or prefer the :ref:`highlevel`.
	
To see the list of available drivers in Autolab, sorted by categories, simply use the function ``show_drivers``. If you just want the list, call the ``list_drivers`` function.

.. code-block:: python

	>>> import autolab
	>>> autolab.show_drivers()
	>>> autolab.list_drivers()

.. note::

	The driver of your instrument is missing ? Please contribute to Autolab by creating yourself a new driver, following the provided guidelines : :ref:`create_driver`
	
To get more information about one particular driver (connection types, modules, required configuration, ...), call the function ``driver_help`` of Autolab, with the name of the driver.

.. code-block:: python

	>>> autolab.driver_help('yenista_TUNICS')

Generally, a **Driver** need a particular configuration to be loaded. As we will see now, this configuration can be provided directly, or loaded from a local configuration file.

Load a Driver
-------------

The instantiation of a *Driver* object is done through the function ``get_driver`` of Autolab, and requires a particular configuration: 

* The name of the driver: one of the name appearing in the ``list_drivers`` function (ex: 'yenista_TUNICS').
* The connection type: it indicates the library to use to communicate with the instrument. The available connection types are listed in the help function ``driver_help`` (ex: 'VISA', 'TELNET', ...).
* Driver-dependent arguments: they are listed in the help function ``driver_help`` (ex: address, port, number of channel, module configuration, ...).

.. code-block:: python

	>>> laserSource = autolab.get_driver('yenista_TUNICS','VISA',address='GPIB0::12::INSTR')
	
Load a Driver with local configuration
--------------------------------------

To avoid having to provide each time the full configuration to load a **Driver** (as above), Autolab proposes to store locally this configuration. To learn more about this, please see the section :ref:`configuration`.

To see the list of the available local drivers configurations, call the function ``list_driver_configs``. 

.. code-block:: python

	>>> autolab.list_driver_configs()
	['my_tunics']

Then, to load a **Driver** based on a given local driver configuration, call the function ``get_driver_by_config`` with the name of the driver configuration (usually the nickname of your instrument). The associated driver configuration will be passed automatically in the function ``get_driver``.

.. code-block:: python

	>>> laserSource = autolab.get_driver_by_config('my_tunics')
	
.. note::

	You can overwrite some of the parameters values of a driver configuration by simply providing them as keywords arguments in the ``get_driver_by_config`` function:
	
	.. code-block:: python	
		>>> laserSource = autolab.get_driver_by_config('my_tunics',address='GPIB::9::INSTR')
			

Use a Driver
------------

You are now ready to use the functions implemented in the **Driver**:

.. code-block:: python

	>>> laserSource.set_wavelength(1550)
	>>> laserSource.get_wavelength()
	1550

