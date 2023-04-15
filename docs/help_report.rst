Doc / Reports / Stats
-----------------------------------------

Documentation
=============

You can open directly this documentation from Python by calling the function ``doc`` of the package:

.. code-block:: python

	>>> autolab.doc()


.. code-block:: none

	>>> autolab doc


Bugs & suggestions reports
==========================

If you encounter some problems or bugs, or if you have any suggestion to improve this package, or one of its driver, please open an Issue on the GitHub page of this project
https://github.com/qcha41/autolab/issues/new

You can also directly call the function ``report`` of the package, which will open this page in your web browser:

.. code-block:: python

	>>> autolab.report()

.. code-block:: none

	>>> autolab report

Alternatively, you can send an email to the authors (see :ref:`about`).

Statistics of use
=================

At startup, Autolab is configured to send only once a completely anonymous signal (sha256 hashed ID) over internet for statistics of use. This helps the authors to have a better understanding of how the package is used worldwide. No personal data is transmitted during this process. Also, this is done in background, with no impact on the performance of Autolab. You can manage the state of this feature in the local configuration file ``autolab_config.ini``. You can use the function ``statistics`` to know its current state.

.. code-block:: python

	>>> autolab.statistics()
