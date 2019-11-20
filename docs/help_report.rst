Docs and bugs/suggestions report
-----------------------------------------

Documentation
=============

You can open directly this documentation  from Python by calling the function ``doc`` of the package:

.. code-block:: python

	>>> autolab.doc()

	
Bugs & suggestions reports
==========================

If you encounter some problems or bugs, or if you have any suggestion to improve this package, or one of its driver, please open an Issue on the GitHub page of this project
https://github.com/qcha41/autolab/issues/new

You can also directly call the function ``report`` of the package, which will open this page in your web browser:

.. code-block:: python

	>>> autolab.report()

You can also send us an email (see :ref:`about`).

Statistics of use
=================
	
At startup, Autolab is configured to send just only once a completely anonymous signal (sha256 hashed ID) over internet for statistics of use. This helps us to have a better understanding of how our package is used worldwide. No personal data is transmitted during this process. Also, this is done in background, with no impact on the performance of Autolab. You can manage the state of this feature in Autolab through these functions:

.. code-block:: python

	>>> autolab.set_stats_enabled(True/False)
	>>> state = autolab.is_stats_enabled()

