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

	>>> # Usefull to set the value of a parameter to a step of a recipe
	>>> $eval:system.parameter_buffer()

	>>> # Useful to define a step according to a measured data
	>>> $eval:laser.wavelength()

	>>> # Useful to define a step according to an analyzed value
	>>> $eval:plotter.bandwitdh.x_left()
	>>> $eval:np.max(mydummy.array_1D())

	>>> # Usefull to define a filename which changes during an analysis
	>>> $eval:f"data_wavelength={laser.wavelength()}.txt"

	>>> # Usefull to add a dataframe to a device variable (for example to add data using the action plotter.data.add_data)
	>>> $eval:mydummy.array_1D()

It can also be useful in a scan for example to set the central frequency of a spectral analyzer according to the frequency of a signal generator. Here is a example to realize this measurement using ``$eval:``.

.. image:: recipe_eval_example.png


Multiple recipes
################

This feature allows to add multiple recipes to a scan.
Click on 'Add recipe' at the bottom of the scanner to add a new recipe.
It is possible to add elements to a recipe by dragging and dropping a variable form the control panel to the corresponding recipe in the scanner.
A variable from one recipe can be drag and drop to another recipe.
With this feature, it is possible within one config file to have init and end recipe to start instruments, set all the constant variables before the scan, do a scan, and turn off the instruments.
It is also possible to sweep one parameter with a specific recipe and another parameter with a different recipe in a single scan.

.. image:: multiple_recipes.png


Multiple parameters
###################
It it possible to add extra parameter to a recipe by right cliking on a recipe and selecting ``Add Parameter``
This feature allows to realize 2D scan or ND-scan.


Execute a recipe in a recipe
############################
It is possible to add a recipe as a step in another recipe by right clicking on a recipe tree and selecting ``Add Recipe_i``.
This feature allows to realize complex measurement scan.
Along with this feature, it is possible to disable a recipe to not execute it in a scan. It avoid executing a recipe on its own if it has been set as a step in another recipe.
