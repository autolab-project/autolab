.. _lowlevel:

Drivers (Low-level interface)
==============================

In Autolab, a **Driver** refers to a Python class dedicated to communicate with one particular instrument.
This class contains functions that perform particular operations, and may also contain subclasses in case some modules or channels are present in the instrument.
Autolab comes with a set of about 50 different **Drivers**, which are ready to use.
As of version 1.2, drivers are now in a seperate GitHub repository located at `github.com/autolab-project/autolab-drivers <https://github.com/autolab-project/autolab-drivers>`_.
When installing autolab, the user is asked if they wants to install all drivers from this repository.

The first part of this section explains how to configure and open a **Driver**, and how to use it to communicate with your instrument.
The, we present the guidelines to follow for the creation of new driver files, to contribute to the Autolab Python package.

Table of contents:

.. toctree::
   :maxdepth: 1

   open_and_use
   create_driver
