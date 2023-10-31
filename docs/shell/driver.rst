.. _os_driver:

Command driver
===============


See :ref:`name_shell_connection` for more informations about the connection. Once your driver is instantiated you will be able to perform **pre-configured operations** (see :ref:`name_driver_utilities.py` for how to configure operations) as well as **raw operations** (-m option). We will discuss both of them here as well as a quick (bash) **scripting example**.
In the rest of this sections we will assume that you have a driver (not device) named instrument that needs a connection named CONN.


Usage of pre-configured operations
##################################

You may access an extensive driver help, that will particularly **list the pre-defined options**, using:

.. code-block:: none

    >>> autolab driver -D instrument -C CONN -h

It includes the list of the implemented connections, the list of the available additional modules (classes **Channel**, **Trace**, **Module_MODEL**, etc.; see :ref:`create_driver`), the list of all the methods that are instantiated with the driver (for direct use with the command: autolab driver; see :ref:`os_driver`), and an extensive help for the usage of the pre-defined options. For instance if an option -a has been defined in the file driver_utilities.py (see :ref:`name_driver_utilities.py`), one may use it to perform the associated action, say to modify the amplitude, this way:

.. code-block:: none

    >>> autolab driver -D instrument -C CONN -a 2

This modifies the amplitude to 2 Volts (if the unit is set to Volt).

In addition, if the instrument has several channels, an channel option is most likely implemented and one can modify the amplitude of channel 4 and 6 to 2 Volts using:

.. code-block:: none

    >>> autolab driver -D instrument -C CONN -a 2 -c 4,6

.. warning::

    No space must be present within an argument or option (e.g. do not write ``- c`` or ``-c 4, 6``).

Furthermore, several operations may be perform in a single and compact script line. One can modify the amplitude of channel 4 and 6 to 2 Volts and the frequencies (of the same channel) to 50 Hz using:

.. code-block:: none

    >>> autolab driver -D instrument -C CONN -a 2 -c 4,6 -f 50

.. note::

    The arguments are non-positional, which means that the previous line is formally equivalent to:

    .. code-block:: none

        >>> autolab driver -D instrument -C CONN -c 4,6 -f 50 -a 2
        >>> autolab driver -D instrument -C CONN -f 50 -a 2 -c 4,6


Raw operations (-m option)
##########################

Independently of the user definition of options in the file driver_utilities.py, you may access any methods that are instantiated with the driver using the -m option.

.. important::

    This is not a *safe* environment, but it allows you to access all the functionnalities of a driver and doesn't rely on a user configuration.


You may access the **full list of instantiated methods** along with their argument definition, using:

.. code-block:: none

    >>> autolab driver -D instrument -C CONN -h

This allow you to simply copy and paste the method you want to use from the list into the following command, directly as *python code*:

.. code-block:: none

    >>> autolab driver -D instrument -C CONN -m get_amplitude()
    >>> autolab driver -D instrument -C CONN -m set_amplitude(value)

One may also call several methods separated with a space after -m option:

.. code-block:: none

    >>> autolab driver -D instrument -C CONN -m get_amplitude() set_amplitude(2) slot1.get_power()

.. note::

    It is possible to combine pre-defined options and -m option in a single script line.


Script example
##############


One may stack in a single file several script line in order to perform custom measurement (modify several control parameters, etc.). This is a bash counterpart to the python scripting example provided there :ref:`name_pythonscript_example`.

.. code-block:: none

    #!/bin/bash                   # Very first line of the file (this is bash code)

    i=1                           # Definition of a variable

    for volts in $(seq 0 0.1 5)   # Definition of a loop (variable volts goes from 0 to 5 with steps of 0.1)
    do

    echo $volts                   # Print the value of the volts variable

    autolab driver -D function_generator -C CONN -a $volts  # Increase the amplitude of function_generator
    autolab driver -D oscilloscope -C CONN -c 1,2,4 -o $i   # Get channels 1, 2 and 4 from oscilloscope and save the according files with a name starting with the number of iteration of the loop (i)

    i=$(($i+1))                   # Increment i variable of 1 at each loop iteration
    done                          # End of the for loop

.. note::

    1) Any time the command ``autolab driver`` is called it sets up the connection. It is then inherently slightly slower (instrument dependant for the amount of time that usually range from 0.1 to 0.5 seconds) than scripting in python.

    2) The whole script looks sightly simpler and shorter than its python counterpart.
