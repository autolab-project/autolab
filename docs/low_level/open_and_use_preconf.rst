
Open and use a pre-configured Driver
----------------------------------

To see the list of the available driver configurations, call the function ``list_driver_configs``. It will returns the list of the blocks names (nicknames) in the configuration file.

.. code-block:: python

	>>> autolab.list_driver_configs()
	['my_tunics']

To communicate with an instrument whose the configuration has been stored in the Autolab configuration file, simply call the function ``get_driver_by_config`` with the nickname of your instrument.

.. code-block:: python

	>>> laserSource = autolab.get_driver_by_config('my_tunics')

You are now ready to use the functions implemented in the *Driver*:

.. code-block:: python

	>>> laserSource.set_wavelength(1550)
	>>> laserSource.get_wavelength()
	1550
