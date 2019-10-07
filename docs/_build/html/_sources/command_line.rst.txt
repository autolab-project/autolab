.. _commandline:

Command-line operation
======================

To start using Autolab, open a Python shell and import the package:

.. code-block:: python

	>>> import autolab

Devices
-------

To see which devices are currently configured locally in your system, call the function ``help`` of the object ``autolab.devices``:

.. code-block:: python

	>>> autolab.devices.help()

To configure a new device on your system, see the section :ref:`configuration`.


Help and bugs/suggestions report
--------------------------------

In case you need some help to use Autolab, you can open directly this documentation in your web browser by calling the function ``help`` of the package:

.. code-block:: python

	>>> autolab.help()

	
If you encounter some problems or bugs, or if you have any suggestion to improve this package, or one of its driver, please open an Issue on the GitHub page of this project: 
https://github.com/qcha41/autolab/issues/new

You can also directly call the function ``report`` of the package, which will open this page on your web browser:

.. code-block:: python

	>>> autolab.report()
