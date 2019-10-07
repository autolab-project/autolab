.. _configuration:

Device configuration
========================

We will here describe the procedure to configure a new instrument.

	1. Check if a driver is available for your instrument.
	2. Update the Autolab configuration file.
	3. Test the communication with your instrument.
	
Driver availability
-------------------

The first thing to do is to check whether a driver is available in Autolab for your instrument. Call the function ``help`` of the object ``autolab.drivers`` to get the list of available drivers:

.. code-block:: python

	>>> import autolab
	>>> autolab.drivers.help()

If a driver is available for your instrument, go to the next step. If not, please visit the section :ref:`drivers` to create a compatible driver and thus contribute to the Autolab package.


Autolab configuration file
--------------------------

The Autolab package requires a local folder on your computer, to store its configuration file. These two elements are created automatically in your home directory, either when you import the package for the first time in a Python shell, or when you launch the GUI for the first time. The following messages will then be displayed, indicating the exact paths of the local folder and of the configuration file.

.. code-block:: python

	INFORMATION: The local folder AUTOLAB has been created : C:\Users\<USER>\autolab
	INFORMATION: The configuration file devices_index.ini has been created : C:\Users\<USER>\autolab\devices_index.ini
		

.. warning ::

	Do not modify the location and the name of this local folder and of the configuration file.
	
The configuration of a new device in Autolab simply consists in adding a small block of informations in the configuration file. This block contains a header that indicates the local name of the instrument (as it will be displayed in Autolab), and several options that indicates its driver name, its connection informations (connection type, address, port,...) and optionally its module configuration. These options are passed as arguments when the driver is instantiated.

Example of the structure of a block in the configuration file ``devices_index.ini``:

.. code-block:: 

	[<LOCAL_NAME_OF_YOUR_DEVICE>]
	driver = <DRIVER_NAME>
	connection = <CONNECTION_TYPE>
	address = <ADDRESS>
	slot1 = <MODULE_NAME>,<SLOT_NAME>

To see a concrete example of the block you have to add in the configuration file to use your instrument, call the function ``help`` of the driver object ``autolab.drivers.<DRIVER_NAME>`` by replacing <DRIVER_NAME> with the name of the driver associated to your instrument. 

Example for the Yenista Tunics light source:

.. code-block:: python

	>>> autolab.drivers.yenista_tunics.help()
