.. _configuration:

Save a Driver configuration
===========================

To avoid having to provide each time the full driver configuration to load a **Driver**, Autolab proposes to store it locally for further use. The configuration of a **Driver** is stored locally in a configuration file named ``local_config.ini``. This file is located in the local directory of Autolab, which is automatically created in your home directory the first time you use the package (import it or run the GUI). The following messages will then be displayed, indicating the exact paths of the local folder and of the configuration file is needed.

.. code-block:: python

	INFORMATION: The local folder AUTOLAB has been created : C:\Users\<USER>\autolab
	INFORMATION: The configuration file local_config.ini has been created : C:\Users\<USER>\autolab\local_config.ini
		
.. warning ::

	Do not move or rename the local folder nor the configuration file.
	
A driver configuration is composed of several parameters:

* The **name** of the driver configuration, which is usually the nickname of your instrument in Autolab.
* The name of the associated Autolab **driver**.
* The **connection** to be used to communicate with your instrument (ex: VISA, TELNET,...). 
* **Other driver-dependent parameters** (an address, a communication port, a slot configuration, etc...)

To know what parameters have to be provided for a particular **Driver**, use the function `help_driver` (see :ref:`userguide_low`).

This section describes the procedure to create or modify a local driver configuration either through Autolab, or by editing directly a configuration file on your computer.

Python commands
-----------------

The first way to create or modify a local driver configuration is to use the dedicated functions in Autolab. To create a new driver configuration, call the function ``set_driver_config`` with the name of the driver configuration (usually the nickname you want to give to your instrument in Autolab), and the parameters and values as keywords arguments (``driver`` and ``connection`` are mandatory). 

.. code-block:: python

	>>> autolab.set_driver_config('my_tunics',driver='yenista_TUNICS',connection='VISA',address='GPIB0::12::INSTR')

The function ``set_driver_config`` can also be used to update an existing driver configuration. As above, provides the name of the driver configuation and the parameters and values you want to update, with the additional keyword ``modify=True`` to confirm the local changes. Any parameter can be changed in this way.

.. code-block:: python

	>>> autolab.set_driver_config('my_tunics',address='GPIB0::4::INSTR')
	
You can display the content of a driver configuration by calling the function ``show_driver_config`` with the name of the driver configuration.

.. code-block:: python

	>>> autolab.show_driver_config('my_tunics')
	
Finally, to remove a parameter from a driver configuration, call the function ``remove_driver_config_parameter`` with the name of the driver configuration and of the parameter.

.. code-block:: python

	>>> autolab.set_driver_driver('my_tunics',fake_parameter=8)
	>>> autolab.remove_driver_config_parameter('my_tunics','fake_parameter')

If you want to remove completely a driver configuration, call the function ``remove_driver_config`` with the name of the driver configuration.

.. code-block:: python

	>>> autolab.remove_driver_config('my_tunics')

**To sum up, you can either provide the full driver configuration in the function** ``get_driver`` **, or save it locally for further use through the function** ``get_driver_by_config``.

.. code-block:: python

	>>> laserSource = autolab.get_driver('yenista_TUNICS','VISA',address='GPIB0::12::INSTR')

.. code-block:: python

	>>> autolab.set_driver_config('my_tunics',driver='yenista_TUNICS',connection='VISA',address='GPIB0::12::INSTR')
	>>> laserSource = autolab.get_driver('my_tunics')
	
	
Edit the configuration file
---------------------------------
 
You can also edit directly the local configuration file. This file is structured in blocks, each of them containing the driver configuration which is automatically passed in the function ``get_driver`` when calling the function ``get_driver_by_config`` (see :ref:`userguide_low`).

Each block is represented by a header, which is the name of the driver configuration in square brackets ``[ ]``. Then, the parameters and values are separated by an equal sign ``=`` and listed line by line.

.. code-block:: none

	[<NICKNAME_OF_YOUR_DEVICE>]			
	driver = <DRIVER_NAME>
	connection = <CONNECTION_TYPE>
	address = <ADDRESS>
	slot1 = <MODULE_NAME>
	slot1_name = <MY_MODULE_NAME>

To see a concrete example of the block you have to append in the configuration file, call the function ``driver_help`` of the corresponding driver. You can copy and paste this exemple into the configuration file, and customize the value of the parameters to suit those of your instrument. Here is an example for the Yenista Tunics light source:

.. code-block:: none

	[my_tunics]
	driver = yenista_TUNICS
	connection = VISA
	address = GPIB0::2::INSTR
	
Save the configuration file, and go back to Autolab. You don't need to restart Autolab, the configuration file will be read automatically at the next request.

.. code-block:: python

	>>> laserSource = autolab.get_driver('my_tunics')
