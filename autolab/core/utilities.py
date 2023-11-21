# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 23:09:51 2019

@author: qchat
"""

def emphasize(txt,sign='-'):

    ''' Returns:    ---
                    txt
                    ---
    '''

    return sign*len(txt) + '\n' + txt + '\n' + sign*len(txt)


def underline(txt,sign='-'):

    ''' Returns:
                    txt
                    ---
    '''

    return txt + '\n' + sign*len(txt)


def clean_string(txt):

    """ Returns txt without special characters """

    for character in '*."/\[]:;|, ' :
        txt = txt.replace(character,'')

    return txt



def two_columns(txt_list) :

    ''' Returns a string of the form:
        txt[0]                         txt[1]
        with a minimal spacing between the first character of txt1 and txt2 '''

    spacing = max([len(txt[0]) for txt in txt_list]) + 5

    return '\n'.join([ txt[0] + ' '*(spacing-len(txt[0])) + txt[1]
            for txt in txt_list])


def boolean(value):
    """ Convert value from "True" or "False" or float, int, bool to bool """

    if value == "True":
        value = True
    elif value == "False":
        value = False
    else:
        value = bool(int(float(value)))
    return value


def formatData(data):
    """ Format data to DataFrame """
    import pandas as pd
    try:
        data = pd.DataFrame(data)
    except ValueError:
        data = pd.DataFrame([data])
    data.columns = data.columns.astype(str)
    data_type = data.values.dtype

    try:
        data[data.columns] = data[data.columns].apply(pd.to_numeric, errors="coerce")
    except ValueError:
        pass  # OPTIMIZE: This happens when their is identical column name
    if len(data) != 0:
        assert not data.isnull().values.all(), f"Datatype '{data_type}' not supported"
        if data.iloc[-1].isnull().values.all():  # if last line is full of nan, remove it
            data = data[:-1]
    if data.shape[1] == 1:
        data.rename(columns = {'0':'1'}, inplace=True)
        data.insert(0, "0", range(data.shape[0]))
    return data
