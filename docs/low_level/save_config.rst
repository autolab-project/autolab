.. _configuration:

Save a driver configuration
===========================

To communicate more easily with your instrument, the full configuration that has to be provided in the ``get_driver`` function can be stored locally and read automatically by Autolab. This page describe the procedure to configure a new instrument locally, and how to use it after in Autolab.
	
Driver availability
-------------------

The first thing to do is to check whether a driver is available in Autolab for your instrument. Call the function ``driver_help`` of Autolab to get the list of available drivers:

.. code-block:: python

	>>> import autolab
	>>> autolab.list_drivers()

If a driver is available for your instrument, go to the next step. If not, please visit the section :ref:`create_driver` to create a compatible driver and thus contribute to the Autolab package.

Autolab configuration file
--------------------------

The configuration of a *Driver* is stored locally in a configuration file named ``local_config.ini``. This file is located in the local directory of Autolab, which is automatically created in your home directory the first time you use the package (import the package or run the GUI). The following messages will then be displayed, indicating the exact paths of the local folder and of the configuration file.

.. code-block:: python

	INFORMATION: The local folder AUTOLAB has been created : C:\Users\<USER>\autolab
	INFORMATION: The configuration file local_config.ini has been created : C:\Users\<USER>\autolab\local_config.ini
		
.. warning ::

	Do not move or rename the local folder nor the configuration file.
	
This configuration file is structured in blocks, each of them containing the configuration that you usually pass in the function ``get_driver`` to instantiate a *Driver*. 

.. code-block:: 

	[<NICKNAME_OF_YOUR_DEVICE>]			
	driver = <DRIVER_NAME>
	connection = <CONNECTION_TYPE>
	address = <ADDRESS>
	slot1 = <MODULE_NAME>
	slot1_name = <MY_MODULE_NAME>
	
Each block is represented by a header, which is the nickname of your instrument in Autolab, and several options that indicates its driver name, its connection type and other driver-dependent parameters. 

Configuration elements:

* *Device nickname* (mandatory): In squared brackets, indicate the local name of your instrument, as it will be displayed in Autolab.
* *Parameter "driver"* (mandatory): Name of the associated Autolab driver.
* *Parameter "connection"* (mandatory): Type of the connection use to communicate with your instrument (ex: VISA, TELNET,...). 
* *Other driver-dependent parameters*: Depending on the driver, you may have to provide an address (Visa or IP address,...), a communication port, a slot configuration, or others options.

To see a concrete example of the block you have to append in the configuration file, call the function ``driver_help`` of the corresponding driver. You can copy and paste this exemple into the configuration file ``local_config.ini``, and customize the value of the parameters to suit those of your instrument. Here is an example for the Yenista Tunics light source:

.. code-block:: 

	[my_tunics]
	driver = yenista_TUNICS
	connection = VISA
	address = GPIB0::2::INSTR
	
Save the configuration file, and go back to Autolab. You don't need to restart Autolab, the configuration file will be read automatically.

Load a pre-configured Driver
----------------------------

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
