.. _shell_scripts:

OS shell
=========

Most of the Autolab functions can also be used directly from a **Windows** or **Linux** terminal without opening explicitely a Python shell. 

Just enter the command ``autolab`` or ``autolab -h`` in your terminal to see the available commands.

.. code-block:: none

	C:\Users\qchat> autolab 
	C:\Users\qchat> autolab -h
	
The subcommands are :

* ``autolab infos`` : a shortcut of the python function autolab.infos() to list the drivers and the local configurations available on your system.
* ``autolab gui`` : a shortcut of the python function autolab.gui() to start the graphical interface of Autolab.
* ``autolab device`` : a shortcut of the python interface Device (see :ref:`os_device`)
* ``autolab driver`` : a shortcut of the python interface Driver (see :ref:`os_driver`)
* ``autolab doc`` : a shortcut of the python function autolab.doc() to open the present online documentation.
* ``autolab report`` : a shortcut of the python function autolab.report() to open the present online documentation.

Table of contents:

.. toctree::
   :maxdepth: 1
   
   driver
   device

