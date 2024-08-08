.. _shell_scripts:

OS shell
========

Most of the Autolab functions can also be used directly from a **Windows** or **Linux** terminal without opening explicitly a Python shell.

Just execute the command ``autolab`` or ``autolab -h`` or ``autolab --help`` in your terminal to see the available subcommands.

.. code-block:: none

	C:\Users\qchat>      autolab
	C:\Users\qchat>      autolab -h
	Hostname:/home/User$ autolab --help

The subcommands are:

* ``autolab gui``: a shortcut of the python function autolab.gui() to start the graphical interface of Autolab.
* ``autolab install_drivers``: a shortcut of the python function autolab.install_drivers() to install drivers from GitHub
* ``autolab driver``: a shortcut of the python interface Driver (see :ref:`os_driver`)
* ``autolab device``: a shortcut of the python interface Device (see :ref:`os_device`)
* ``autolab doc``: a shortcut of the python function autolab.doc() to open the present online documentation.
* ``autolab report``: a shortcut of the python function autolab.report() to open the present online documentation.
* ``autolab infos``: a shortcut of the python function autolab.infos() to list the drivers and the local configurations available on your system.

Table of contents:

.. toctree::
   :maxdepth: 1

   connection
   driver
   device
