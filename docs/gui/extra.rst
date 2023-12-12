.. _extra:

Experimental features
=====================

Executing Python codes in GUI
#############################

A function for executing python code directly in the GUI can be used to change a variable based on other device variables or purely mathematical equations.

To use this function both in the control panel and in a scan recipe, use the special ``$eval:`` tag before defining your code in the corresponding edit box.
This name was chosen in reference to the python function eval used to perform the operation and also to be complex enough not to be used by mistake and produce an unexpected result.
The eval function only has access to all instantiated devices and to the pandas and numpy packages.

.. code-block:: none

	>>> # Usefull to have a recipe taking the loop number
	>>> $eval:system.parameter_buffer()

	>>> # Useful to define a recipe according to a measured data
	>>> $eval:laser.wavelength()

	>>> # Useful to define the recipe according to an analyzed value
	>>> $eval:plotter.bandwitdh.x_left()
	>>> $eval:np.max(mydummy.array_1D())

	>>> # Usefull to define a filename which changes during an analysis
	>>> $eval:"data_wavelength="+f"{laser.wavelength()}"+".txt"

	>>> # Usefull to add a dataframe to a device variable (for example to add data using the action plotter.data.add_data)
	>>> $eval:mydummy.array_1D()

It is also useful in a scan to set the frequency of a signal analyzer relative to the frequency of a signal generator. Here is a example of the recipe using ``$eval:`` to do so.

.. image:: recipe_eval_example.png


Adding extra recipes
####################

This feature allows to add multiple recipes to a scan.
Click on 'Add recipe' at the bottom of the scanner to add a new recipe.
It is possible to add elements to a recipe by dragging and dropping a variable form the control panel to the corresponding recipe in the scanner.
A variable from one recipe can be drag and drop to another recipe.
With this feature, it is possible within one config file to have init and end recipe to start instruments, set all the constant variables before the scan, do a scan, and turn off the instruments.
It is also possible to sweep one parameter with a specific recipe and another parameter with a different recipe in a single scan.
It may be possible in the future to execute a recipe inside a recipe to do 2D scan.

.. image:: multiple_recipes.png
