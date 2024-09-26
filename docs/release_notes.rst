Release notes
=============

2.0
###

Autolab 2.0 released in 2024 is the first major release since 2020.

General Features
----------------

- Configuration Enhancements:

  - Enhanced configuration options for driver management in autolab_config.ini, including extra paths and URLs for driver downloads.
  - Added install_driver() to download drivers.
  - Improved handling of temporary folders and data saving options.

- Driver Management:

  - Moved drivers to a dedicated GitHub repository: https://github.com/autolab-project/autolab-drivers.
  - Drivers are now located in the local "<username>/autolab/drivers/official" folder instead of the main package.
  - Added the ability to download drivers from GitHub using the GUI, allowing selective driver installation.

- Documentation:

  - Added documentation for new features and changes.

GUI Enhancements
----------------

- General Improvements:

  - Switched from matplotlib to pyqtgraph for better performance and compatibility.
  - Enhanced plotting capabilities in the monitor and scanner, including support for 1D and 2D arrays and images.
  - Added $eval: special tag to execute Python code in the GUI to perform custom operations.
  - Added autocompletion for variables using tabulation.
  - Added sliders to variables to tune values.

- Control Panel:

  - Added the ability to display and set arrays and dataframes in the control panel.
  - Added possibility to use variable with type bytes and action that have parameters with type bool, bytes, tuple, array or dataframe.
  - Added yellow indicator for written but not read elements.
  - Introduced a checkbox option to optionally display arrays and dataframes in the control panel.
  - Added sub-menus for selecting recipes and parameters.
  - Improved device connection management with options to modify or cancel connections.
  - Added right-click options for modifying device connections.

- Scanner:

  - Implemented multi-parameter and multi-recipe scanning, allowing for more complex scan configurations.
  - Enhanced recipe management with right-click options for enabling/disabling, renaming, and deleting.
  - Enabled plotting of scan data as an image, useful for 2D scans.
  - Added support for custom arrays and parameters in scans.
  - Enabled use of a default scan parameter not linked to any device.
  - Added data display filtering option.
  - Added scan config history with the last 10 configurations.
  - Added variables to be used in the scan, allowing on-the-fly analysis inside a recipe.
  - Changed the scan configuration file format from ConfigParser to json to handle new scan features.
  - Add shortcut for copy paste, undo redo, delete in scanner for recipe steps.

- Plotter:

  - Implementation of a plotter to open previous scan data, connect to instrument variables and perform data analysis.

- Usability Improvements:

  - Enabled drag-and-drop functionality in the GUI.
  - Added icons and various UI tweaks for better usability.
  - Enabled opening configuration files from the GUI.

- Standalone GUI Utilities:

  - Added autolab.about() for autolab information.
  - Added autolab.slider(variable) to change a variable value.
  - Added autolab.variables_menu() to control variables, monitor or use slider.
  - Added autolab.add_device() for adding devices to the config file.
  - Added autolab.monitor(variable) for monitoring variables.
  - Added autolab.plotter() to open the plotter directly.

Device and Variable Management
------------------------------

- Variable and Parameter Handling:

  - Added new action units ('user-input', 'open-file', 'save-file') to open dialog boxes.
  - Added 'read_init' argument to variable allowing to read a value on device instantiation in the control panel.
  - Added new type 'tuple' to create a combobox in the control panel.

Miscellaneous Improvements
--------------------------

- Code Quality and Compatibility:

  - Numerous bug fixes to ensure stability and usability across different modules and functionalities.
  - Compatibility from Python 3.6 up to 3.12.
  - Switched from PyQt5 to qtpy to enable extensive compatibility (Qt5, Qt6, PySide2, PySide6).
  - Extensive code cleanup, PEP8 compliance, and added type hints.

- Logger and Console Outputs:

  - Added an optional logger in the control center to display console outputs.
  - Added an optional console in the control center for debug/dev purposes.

- Miscellaneous:

  - Added an "About" window showing versions, authors, license, and project URLs.
  - Implemented various fixes for thread handling and error prevention.
  - Add dark theme option for GUI.

1.1.12
######

Last version developed by the original authors.
