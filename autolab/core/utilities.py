# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 23:09:51 2019

@author: qchat
"""
from typing import Any, List
import re
import ast
from io import StringIO
import platform
import os

import numpy as np
import pandas as pd


SUPPORTED_EXTENSION = "Text Files (*.txt);; Supported text Files (*.txt;*.csv;*.dat);; Any Files (*)"


def emphasize(txt: str, sign: str = '-') -> str:
    ''' Returns:    ---
                    txt
                    ---
    '''
    return sign*len(txt) + '\n' + txt + '\n' + sign*len(txt)


def underline(txt: str, sign: str = '-') -> str:
    ''' Returns:
                    txt
                    ---
    '''
    return txt + '\n' + sign*len(txt)


def clean_string(txt: str) -> str:
    """ Returns txt without special characters """
    for character in r'*."/\[]:;|, ':
        txt = txt.replace(character, '')

    return txt


def two_columns(txt_list: List[str]) -> str:
    ''' Returns a string of the form:
        txt[0]                         txt[1]
        with a minimal spacing between the first character of txt1 and txt2 '''
    spacing = max(len(txt[0]) for txt in txt_list) + 5

    return '\n'.join([txt[0] + ' '*(spacing-len(txt[0])) + txt[1]
                          for txt in txt_list])


def boolean(value: Any) -> bool:
    """ Convert value from "True" or "False" or float, int, bool to bool """
    if value == "True": value = True
    elif value == "False": value = False
    else: value = bool(int(float(value)))

    return value


def str_to_value(s: str) -> Any:
    ''' Tries to convert string to int, float, bool or None in this order '''
    try:
        int_val = int(s)
        if str(int_val) == s: return int_val
    except ValueError: pass

    try:
        float_val = float(s)
        return float_val
    except ValueError: pass

    if s.lower() in ('true', 'false'):
        return s.lower() == 'true'

    if s == 'None': s = None
    # If none of the above works, return the string itself
    return s


def create_array(value: Any) -> np.ndarray:
    ''' Format an int, float, list or numpy array to a numpy array with minimal one dimension '''
    # ndim=1 to avoid having float if 0D
    array = np.array(value, ndmin=1, dtype=float)  # check validity of array
    array = np.array(value, ndmin=1, copy=False)  # keep original dtype
    return array


def str_to_array(s: str) -> np.ndarray:
    ''' Convert string to a numpy array '''
    if "," in s: ls = re.sub(r'\s,+', ',', s)
    else: ls = re.sub(r'\s+', ',', s)
    test = ast.literal_eval(ls)

    return create_array(test)


def array_to_str(value: Any, threshold: int = None, max_line_width: int = None) -> str:
    ''' Convert a numpy array to a string '''
    return np.array2string(np.array(value), separator=',', suppress_small=True,
                           threshold=threshold, max_line_width=max_line_width)


def str_to_dataframe(s: str) -> pd.DataFrame:
    ''' Convert a string to a pandas DataFrame '''
    value_io = StringIO(s)
    # TODO: find sep (use \t to be compatible with excel but not nice to write by hand)
    df = pd.read_csv(value_io, sep="\t")
    return df


def dataframe_to_str(value: pd.DataFrame, threshold=1000) -> str:
    ''' Convert a pandas DataFrame to a string '''
    if isinstance(value, str) and value == '': value = None
    return pd.DataFrame(value).head(threshold).to_csv(index=False, sep="\t")  # can't display full data to QLineEdit, need to truncate (numpy does the same)


def str_to_data(s: str) -> Any:
    """ Convert str to data with special format for ndarray and dataframe """
    if '\t' in s and '\n' in s:
        try: s = str_to_dataframe(s)
        except: pass
    elif '[' in s:
        try: s = str_to_array(s)
        except: pass
    else:
        try: s = str_to_value(s)
        except: pass
    return s


def data_to_str(value: Any) -> str:
    """ Convert data to str with special format for ndarray and dataframe """
    if isinstance(value, np.ndarray):
        raw_value_str = array_to_str(value, threshold=1000000, max_line_width=9000000)
    elif isinstance(value, pd.DataFrame):
        raw_value_str = dataframe_to_str(value, threshold=1000000)
    else:
        raw_value_str = str(value)
    return raw_value_str


def open_file(filename: str):
    ''' Opens a file using the platform specific command '''
    system = platform.system()
    if system == 'Windows': os.startfile(filename)
    elif system == 'Linux': os.system(f'gedit "{filename}"')
    elif system == 'Darwin': os.system(f'open "{filename}"')


def data_to_dataframe(data: Any) -> pd.DataFrame:
    """ Format data to DataFrame """
    try: data = pd.DataFrame(data)
    except ValueError: data = pd.DataFrame([data])

    data.columns = data.columns.astype(str)
    data_type = data.values.dtype

    try:
        data[data.columns] = data[data.columns].apply(pd.to_numeric, errors="coerce")
    except ValueError:
        pass  # OPTIMIZE: This happens when there is identical column name

    if len(data) != 0:
        assert not data.isnull().values.all(), f"Datatype '{data_type}' not supported"
        if data.iloc[-1].isnull().values.all():  # if last line is full of nan, remove it
            data = data[:-1]

    if data.shape[1] == 1:
        data.rename(columns = {'0':'1'}, inplace=True)
        data.insert(0, "0", range(data.shape[0]))

    return data


def input_wrap(*args):
    """ Wrap input function to avoid crash with Spyder using Qtconsole=5.3 """
    input_allowed = True
    try:
        import spyder_kernels
        import qtconsole
    except ModuleNotFoundError:
        pass
    else:
        if hasattr(spyder_kernels, "console") and hasattr(qtconsole, "__version__"):
            if qtconsole.__version__.startswith("5.3"):
                print("Warning: Spyder crashes with input() if Qtconsole=5.3, skip user input.")
                input_allowed = False
    if input_allowed:
        ans = input(*args)
    else:
        ans = "yes"

    return ans
