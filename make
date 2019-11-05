#!/bin/bash

# Compile the local source
python3 setup.py sdist bdist_wheel

# Uninstall autolab
pip3 uninstall autolab

# Install the compiled version
dir dist/*.whl | xargs pip3 install

# remove created folders 
rm -r build/ dist/ autolab.egg-info
