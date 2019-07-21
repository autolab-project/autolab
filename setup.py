# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:30:03 2019

@author: qchat
"""

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'usit',
    version = '0.1',  # Ideally should be same as your GitHub release tag varsion
    author = 'Quentin Chateiller',
    author_email = 'q.chateiller@gmail.com',
    description = 'Universal Scanning Interface : Python automation package for scientific laboratory experiments',
    long_description = long_description,
    long_description_content_type="text/markdown",
    url = 'https://github.com/qcha41/usit'
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
            
    data_files = [('usit', ['config/*'])],
    
    author = 'Quentin Chateiller',
    author_email = 'q.chateiller@gmail.com',
    url = 'https://upload.pypi.org/legacy/',
    download_url = 'https://github.com/qcha41/usit/archive/0.1.tar.gz',
    keywords = ['Universal','Scanning','Interface','automation','scientific','laboratory','experiments','measures']
)

