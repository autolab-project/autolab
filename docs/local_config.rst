.. _localconfig:

Local configuration
===================

To avoid having to provide each time the full configuration of an instrument (connection type, address, port, slots, ...) to load a **Driver** or a **Device**, Autolab proposes to store it locally for further use. 

More precisely, this configuration is stored in a local configuration file named ``local_config.ini``, which is located in the local directory of Autolab. Both this directory and this file are created automatically in your home directory the first time you use the package (the following messages will be displayed, indicating their exact paths).

.. code-block:: python

	INFORMATION: The local folder AUTOLAB has been created : C:\Users\<USER>\autolab
	INFORMATION: The configuration file local_config.ini has been created : C:\Users\<USER>\autolab\local_config.ini
		
.. warning ::

	Do not move or rename the local directory nor the configuration file.
	
A local configuration is composed of several parameters:

* The name of the local configuration, which is usually the nickname of your instrument in Autolab.
* The name of the associated Autolab **driver**.
* All the connection parameters (connection, address, port, slots, ...)

To see the list of the available local configurations, call the function ``list_local_configs``. 

.. code-block:: python

	>>> autolab.list_local_configs()

To know what parameters have to be provided for a particular **Driver** or **Device**, use the function `config_help` with the name of corresponding driver.

.. code-block:: python

	>>> autolab.config_help('yenista_TUNICS')

This section describes the procedure to create or modify a local configuration either through Autolab, or by editing directly the configuration file on your computer.

Python commands
-----------------

The first way to create or modify a local configuration is to use the dedicated functions in Autolab. To create a new local configuration, call the function ``set_local_config`` with the configuration name, the driver name, and the parameters with their values. (Note that ``driver`` and ``connection`` keywords are mandatory). 

.. code-block:: python

	>>> autolab.set_local_config('my_tunics', driver='yenista_TUNICS', connection='VISA', address='GPIB0::12::INSTR')

The function ``set_local_config`` can also be used to update an existing local configuration. As above, provide configuration name followed by the parameters and values you want to update, with the additional keyword ``modify=True`` to confirm the local changes. Any parameter can be changed in this way.

.. code-block:: python

	>>> autolab.set_local_config('my_tunics', address='GPIB0::4::INSTR')
	
You can display the content of a local configuration by calling the function ``show_local_config`` with the name of the local configuration.

.. code-block:: python

	>>> autolab.show_local_config('my_tunics')
	
Finally, to remove a parameter from a local configuration, call the function ``remove_local_config_parameter`` with the configuration name and the name of the parameter to remove.

.. code-block:: python

	>>> autolab.set_driver_driver('my_tunics', fake_parameter=8)
	>>> autolab.remove_local_config_parameter('my_tunics', 'fake_parameter')

If you want to remove completely a local configuration, call the function ``remove_local_config`` with the name of the configuration to remove.

.. code-block:: python

	>>> autolab.remove_local_config('my_tunics')

**To sum up, you can either provide the full configuration of an instrument in the function ** ``get_driver`` ** or ** ``get_device`` **, or save it locally with a nickname, and just provide that nickname in the two previous functions.

.. code-block:: python

	>>> laserSource = autolab.get_driver('yenista_TUNICS', connection='VISA', address='GPIB0::12::INSTR')
	>>> laserSource = autolab.get_device('yenista_TUNICS', connection='VISA', address='GPIB0::12::INSTR')

.. code-block:: python

	>>> autolab.set_local_config('my_tunics',driver='yenista_TUNICS',connection='VISA',address='GPIB0::12::INSTR')
	>>> laserSource = autolab.get_driver('my_tunics')
	>>> laserSource = autolab.get_device('my_tunics')
	
	
Edit the configuration file
---------------------------------
 
You can also edit directly the local configuration file ``local_config.ini``. 

This file is structured in blocks, each of them containing the configuration of an instrument. Each block contains a header (the configuration name / nickname of the instrument in square brackets ``[ ]``). The parameters and values are then listed below line by line, separated by an equal sign ``=``.

.. code-block:: none

	[<NICKNAME_OF_YOUR_DEVICE>]			
	driver = <DRIVER_NAME>
	connection = <CONNECTION_TYPE>
	address = <ADDRESS>
	slot1 = <MODULE_NAME>
	slot1_name = <MY_MODULE_NAME>

To see a concrete example of the block you have to append in the configuration file for a given driver, call the function ``config_help`` with the name of the driver. You can then directly copy and paste this exemple into the configuration file, and customize the value of the parameters to suit those of your instrument. Here is an example for the Yenista Tunics light source:

.. code-block:: none

	[my_tunics]
	driver = yenista_TUNICS
	connection = VISA
	address = GPIB0::2::INSTR
	
Save the configuration file, and go back to Autolab. You don't need to restart Autolab, the configuration file will be read automatically at the next request.

.. code-block:: python

	>>> laserSource = autolab.get_driver('my_tunics')
	>>> laserSource = autolab.get_device('my_tunics')
