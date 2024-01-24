.. _plotting:

Plotting
========

.. image:: plotting.png

.. caution::

    The plotter still need some work, feed-back are more than welcome (December 2023).

Import data
-----------

It is currently possible to plot data from previous experiments or any supported data type using the **Open** button.

Device connection
-----------------

It is also possible to get and plot data from a device variable with an automatic plot refresh option.

To do this, you need to provide a **device variable**, e.g. ``mydummy.array_1D`` to create a link between the plotter and the ``array_1D`` variable of the ``mydummy`` device (based on the ``dummy`` driver).

Once the variable is linked, use the **Get data** button to call the variable that returns the array to be plotted (will execute the mydummy.array_1D() command).

To automatically update the plot, check the **Auto get data** option.

Plugin tree
-----------

The **Plugin** tree can be used to connect any device to the plotter, either by dragging a device from the :ref:`control_panel` and dropping it the plugin tree, either using the configuration file ``plotter_config.ini`` to link a plugin to a device defined in ``device_config.ini``.

.. code-block:: none

	[plugin]
	<PLUGIN_NAME> = <DEVICE_NAME>

A plugin do not share the same instance as the original device in the controlcenter, meaning that variables of a device will not affect variables of a plugin and vis-versa.
Because a new instance is created for each plugin, you can add as many plugin from the same device as you want.

If a device uses the the argument ``gui`` in its ``__init__`` method, it will be able to access the plotter instance to get its data ot to modify the plot itself.

If a plugin has a method called ``refresh``, the plotter will call it with the argument ``data`` containing the plot data everytime the figure is updated, allowing for each plugin to get the lastest available data and do operations on it.

The plugin ``plotter`` is added by default to the Plotter, allowing to do basic analyzes on the plotted data.
Among them, getting the min, max values, but also computing the bandwidth around a local extremum.
Note that this plugin can be used as a device to process data in the control panel or directly in a scan recipe.
