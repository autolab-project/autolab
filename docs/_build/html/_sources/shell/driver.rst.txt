.. _os_driver:

Command driver
===============


Getting help
############
Three helps are configured (device or driver may be used equally in the lines bellow):
    
    An help message on ...
    
    .. code-block:: python
    
        >>> autolab driver -h
    
    Short message displaying the device category as well as the implemented connections to a device (VISA, etc).
    
    .. code-block:: python
    
        >>> autolab driver -h -D driver_name
    

    Full help message about the driver, including
    
    .. code-block:: python
    
        >>> autolab driver -D driver_name -C connection -A address -h
    
    
Connection arguments
####################

This command will establish a connection to your instrument, perform the requested operation, and finally close properly the connection.
    
    .. code-block:: python
    
        >>>   autolab driver <driver_name or config_name> -C <CONNECTION> -A <address> 

Recquired connection arguments (capital letters):
    -D driver_name: name of the driver to use (e.g.: agilent_33220A). driver_name can be either the driver_name or the defined nickname, as defined by the user in the local_config.ini. See lower for the list of available drivers.
    -C connection type to use to communicate with the device (e.g.: VISA, VXI11, SOCKET, TELNET, USB, GPIB, ...). You may access the available connections types with an help (see below helps section).
    -A address: full address to reach the device that depends on the connection type (e.g.: 192.168.0.2  [for VXI11]) and on how you configured the device.


Optional arguments:
  -P PORT, --port PORT  Argument used to address different things depending on
                        the connection type. SOCKET: the port number used to
                        communicate, GPIB: the gpib board index, DLL: the path
                        to the dll library.
  -O OTHER [OTHER ...], --other OTHER [OTHER ...]
                        Set other parameters (slots,...).

.. code-block:: python

    ======================
    Driver "driver_name"
    ======================

    Available connections types (-C option):
    - VISA
    - SOCKET


    Example(s) to load a Driver or a Device:
    ----------------------------------------

    autolab driver -D driver_name -C VISA
    autolab device -D driver_name -C VISA


    Example(s) to save a configuration by command-line:
    ---------------------------------------------------

    Available soon through OS shell


    Example(s) to save a configuration by editing the file local_config.ini:
    ------------------------------------------------------------------------

    [my_driver]
    driver = driver_name
    connection = VISA
    address = TCPIP::192.168.0.1::INSTR


    Example to instantiate a Driver or a Device with a local configuration:
    -----------------------------------------------------------------------

    autolab driver -D my_driver
    autolab device -D my_driver
    









