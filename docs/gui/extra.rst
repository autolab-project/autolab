.. _extra:

Extra function
==============

An experimental function for executing python code directly in the GUI can be used to change a variable based on other device variables or purely mathematical equations.

To use this function both in the control panel and in a scan recipe, use the special ``$eval:`` tag before defining your code in the corresponding edit box.
This name was chosen in reference to the python function eval used to perform the operation and also to be complex enough not to be used by mistake and produce an unexpected result.
The eval function only has access to all instantiated devices and to the pandas and numpy packages.

.. code-block:: none

	>>> # Usefull to have a recipe taking the loop number
	>>> $eval:system.parameter_buffer()

	>>> # Useful to define a recipe according to a measured data
	>>> $eval:laser.wavelength()

	>>> # Useful to define the recipe according to an analyzed value
	>>> $eval:plotter.analyze.bandwitdh.x_left()
	>>> $eval:np.max(mydummy.array_1D())

	>>> # Usefull to define a filename which changes during an analysis
	>>> $eval:"data_wavelength="+f"{laser.wavelength()}"+".txt"

	>>> # Usefull to add a dataframe to a device variable (for example to add data using the action plotter.data.add_data)
	>>> $eval:mydummy.array_1D()
