# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:30:03 2019

@author: qchat
"""

from setuptools import setup,find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'usit',
    version = '0.2.3',  # Ideally should be same as your GitHub release tag varsion
    author = 'Quentin Chateiller',
    author_email = 'q.chateiller@gmail.com',
    description = 'Universal Scanning Interface : python package for scientific experiments automation',
    long_description = long_description,
    long_description_content_type="text/markdown",
    url = 'https://github.com/qcha41/usit',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    package_data={'': ['*.ini']},# If any package contains *.ini files, include them:
    keywords = ['Universal','Scanning','Interface','automation','scientific','laboratory','experiments','measures']
)

