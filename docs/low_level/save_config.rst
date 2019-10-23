.. _configuration:

Save a driver configuration
===========================

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
	
The configuration of a new device in Autolab simply consists in adding a small block of informations in the configuration file. This block contains a header that indicates the local name of the instrument (as it will be displayed in Autolab), and several options that indicates its driver name, its connection informations and optionally its module configuration. These options are passed as arguments when the driver is instantiated.

Here is an example of the block structure in the configuration file ``devices_index.ini`` :

.. code-block:: 

	[<LOCAL_NAME_OF_YOUR_DEVICE>]			
	driver = <DRIVER_NAME>
	connection = <CONNECTION_TYPE>
	address = <ADDRESS>
	slot1 = <MODULE_NAME>,<SLOT_NAME>

Configuration elements:

	* *Device name* (mandatory): In squared brackets, indicate the local name of your instrument, as it will be displayed in Autolab.
	* *Option "driver"* (mandatory): Name of the associated Autolab driver.
	* *Option "connection"* (mandatory): Type of the connection use to communicate with your instrument (ex: VISA, TELNET,...). 
	* *Other options*: Depending on the driver, you may have to provide an address (Visa or IP address,...), a communication port, a slot configuration, or others options.

To see a concrete example of the block you have to append in the configuration file, call the function ``help`` of the corresponding driver object ``autolab.drivers.<DRIVER_NAME>`` by replacing <DRIVER_NAME> with the name of the driver associated to your instrument. Here is an example for the Yenista Tunics light source:

.. code-block:: python

	>>> autolab.drivers.yenista_tunics.help()
	
	========================================
	Driver "yenista_tunics" (Optical source)
	========================================

	Available connection(s):
	 - VISA

	Configuration example(s) for devices_index.ini:

	[myDeviceName]
	driver = yenista_tunics
	connection = VISA
	address = GPIB0::2::INSTR

You can then copy and paste this exemple to the configuration file ``devices_index.ini``, and customize the value of the options that suits your instrument.


Check your configuration
------------------------

To check your new configuration file, start a new Python shell and call the function ``help`` of the ``autolab.devices`` object. You should see a new line with the name of your instrument. 

.. code-block:: python

	>>> autolab.devices.help()
	
Now, try to instantiate a connection to the device by accessing the its attribute in ``autolab.devices``. Here is an example for the Yenista Tunics light source, named ``myTunics`` in the configuration file:

.. code-block:: python

	>>> autolab.devices.myTunics
	
If this doesn't raise any error, you are ready to use your new device in Autolab ! See sections :ref:`userguide_low` and :ref:`gui` to continue.