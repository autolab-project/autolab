.. _configuration:

Save a Driver configuration
===========================

To communicate more easily with your instrument, the full configuration that has to be provided to open a **Driver** can be stored locally and read automatically by Autolab. This page describes the procedure to configure a new instrument locally, and how to use it after in Autolab.

The configuration of a **Driver** is stored locally in a configuration file named ``local_config.ini``. This file is located in the local directory of Autolab, which is automatically created in your home directory the first time you use the package (import it or run the GUI). The following messages will then be displayed, indicating the exact paths of the local folder and of the configuration file.

.. code-block:: python

	INFORMATION: The local folder AUTOLAB has been created : C:\Users\<USER>\autolab
	INFORMATION: The configuration file local_config.ini has been created : C:\Users\<USER>\autolab\local_config.ini
		
.. warning ::

	Do not move or rename the local folder nor the configuration file.
	
This configuration file is structured in blocks, each of them containing the configuration that you usually pass in the function ``get_driver`` to instantiate a **Driver**. 

.. code-block:: none

	[<NICKNAME_OF_YOUR_DEVICE>]			
	driver = <DRIVER_NAME>
	connection = <CONNECTION_TYPE>
	address = <ADDRESS>
	slot1 = <MODULE_NAME>
	slot1_name = <MY_MODULE_NAME>
	
Each block is represented by a header, which is the nickname of your instrument in Autolab, and several options that indicates its driver name, its connection type and other driver-dependent parameters. 

Configuration elements:

* **Instrument nickname** (mandatory): In squared brackets, indicate the local name of your instrument, as it will be displayed in Autolab.
* **Parameter "driver"** (mandatory): Name of the associated Autolab driver.
* **Parameter "connection"** (mandatory): Type of the connection use to communicate with your instrument (ex: VISA, TELNET,...). 
* **Other driver-dependent parameters**: Depending on the driver, you may have to provide an address (Visa or IP address,...), a communication port, a slot configuration, or others options.

To see a concrete example of the block you have to append in the configuration file, call the function ``driver_help`` of the corresponding driver. You can copy and paste this exemple into the configuration file ``local_config.ini``, and customize the value of the parameters to suit those of your instrument. Here is an example for the Yenista Tunics light source:

.. code-block:: none

	[my_tunics]
	driver = yenista_TUNICS
	connection = VISA
	address = GPIB0::2::INSTR
	
Save the configuration file, and go back to Autolab. You don't need to restart Autolab, the configuration file will be read automatically.
