.. _os_device:

Command device
==============

To read, write or save the value of a **Variable**, or to execute an **Action**, use the command ``autolab device`` in your terminal with the following general format:

.. code-block:: none

	autolab device -D <CONFIG_NAME> -e <ELEMENT_ADDRESS> <OPTIONS>

The **Element address** indicates the address of the desired **Variable** or **Action** in the Autolab Device hierarchy, using a point separator. This command will establish a connection to your instrument, perform the requested operation, and finally close properly the connection. See :ref:`name_shell_connection` for more informations about the connection.

The available operations are listed below:

	* **To read and print** the value of a readable **Variable** in the terminal, provide its address without any other options:

	.. code-block:: none

		>>> autolab device -D myTunics -e wavelength
		1550.00

	* **To read and save** the value of a readable **Variable** in a file, provide its address with the option ``-p`` or ``--path`` with the desired output file or folder path:

	.. code-block:: none

		>>> autolab device -D myPowerMeter -e line1.power -p .\data\power.txt

	* **To set** the value of a writable **Variable**, provide its address and the option ``-v`` or ``--value`` with the desired value:

	.. code-block:: none

		>>> autolab device -D myTunics -e wavelength -v 1551

	* **To execute** an **Action**, provide its address without any options (or with the option ``-v`` or ``--value`` with the desired value if the **Action** has a parameter):

	.. code-block:: none

		>>> autolab device -D myLinearStage -e goHome

	* **To display the help** of any **Element**, provide its address with the option ``-h`` or ``--help``:

	.. code-block:: none

		>>> autolab device -D myLinearStage -e goHome -h
