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
    author = 'Quentin Chateiller & Bruno Garbin, C2N-CNRS',
    description = 'Python package for scientific experiments interfacing and automation',
    long_description = long_description,
    long_description_content_type="text/markdown",
    url = 'https://github.com/qcha41/autolab',
    packages=find_packages(),
    classifiers=["Programming Language :: Python :: 3",
				"Programming Language :: Python :: 3.6",
				"Programming Language :: Python :: 3.7",
                 "Operating System :: OS Independent"],
    install_requires=[
            'numpy>=1.16',
            'pandas>=0.24',
            'pyvisa>=1.10',
            'python-vxi11>=0.9',
			'matplotlib>=3'
            ],
    entry_points={'console_scripts': ['autolab = scripts.autolab:main']},
	python_requires='>=3.6',
    include_package_data=True,
    package_data={'': ['*.ini','*.txt','*.ui']},# If any package contains *.ini files, include them:
    keywords = ['scanning','interface','automation','scientific','laboratory','devices','experiments','measures','interface','gui','scan']
)

