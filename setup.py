# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:30:03 2019

@author: qchat
"""

from setuptools import setup,find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
    
with open("./autolab/version.txt", "r") as fh:
    version = fh.read().strip()

setup(
    name = 'autolab',
    version = version,  # Ideally should be same as your GitHub release tag varsion
    author = 'Quentin Chateiller & Bruno Garbin',
    author_email = 'q.chateiller@gmail.com',
    description = 'Python package for scientific experiments interfacing and automation',
    long_description = long_description,
    long_description_content_type="text/markdown",
    url = 'https://github.com/qcha41/autolab',
    packages=find_packages(),
    classifiers=["Programming Language :: Python :: 3",
                 "Operating System :: OS Independent"],
    scripts=['autolab/scripts/autolab','autolab/scripts/autolab-device','autolab/scripts/autolab-driver'],
    install_requires=['pyqt5'],
    include_package_data=True,
    package_data={'': ['*.ini','*.txt','*.ui']},# If any package contains *.ini files, include them:
    keywords = ['scanning','interface','automation','scientific','laboratory','devices','experiments','measures','interface','gui','scan']
)

