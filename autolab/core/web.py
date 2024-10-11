# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 17:11:57 2019

@author: qchat
"""

import webbrowser
import socket
import os
import inspect

from .utilities import open_file

project_url = 'https://github.com/autolab-project/autolab'
drivers_url = 'https://github.com/autolab-project/autolab-drivers'
doc_url = 'https://autolab.readthedocs.io'


def report():
    """ Open the github link to open an issue: https://github.com/autolab-project/autolab/issues """
    webbrowser.open(project_url+'/issues')


def doc(online: bool = "default"):
    """ By default try to open the online doc and if no internet connection, open the local pdf documentation.
    Can open online or offline documentation by using True or False."""

    if online == "default":
        if has_internet(False): webbrowser.open(doc_url)
        else:
            print("No internet connection found. Open local pdf documentation instead")
            doc_offline()
    elif online: webbrowser.open(doc_url)
    elif not online: doc_offline()


def doc_offline():
    dirname = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
    filename = os.path.join(dirname, "../autolab.pdf")
    if os.path.exists(filename): open_file(filename)
    else: print("No local pdf documentation found at {filename}")


def has_internet(_print=True) -> bool:
    """ https://stackoverflow.com/questions/20913411/test-if-an-internet-connection-is-present-in-python#20913928 """
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname("one.one.one.one")
        # connect to the host -- tells us if the host is actually reachable
        s = socket.create_connection((host, 80), 2)
        s.close()
        return True
    except Exception: pass # we ignore any errors, returning False

    if _print: print("No internet connection found")
    return False
