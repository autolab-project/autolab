# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 14:54:41 2024

@author: Jonathan
"""

import re
from typing import Any, List, Tuple

import numpy as np
import pandas as pd

from .devices import DEVICES
from .utilities import clean_string


# class AddVarSignal(QtCore.QObject):
#     add = QtCore.Signal(object, object)
#     def emit_add(self, name, value):
#         self.add.emit(name, value)


# class RemoveVarSignal(QtCore.QObject):
#     remove = QtCore.Signal(object)
#     def emit_remove(self, name):
#         self.remove.emit(name)


# class MyDict(dict):

#     def __init__(self):
#         self.addVarSignal = AddVarSignal()
#         self.removeVarSignal = RemoveVarSignal()

#     def __setitem__(self, item, value):
#         super(MyDict, self).__setitem__(item, value)
#         self.addVarSignal.emit_add(item, value)

#     def pop(self, item):
#         super(MyDict, self).pop(item)
#         self.removeVarSignal.emit_remove(item)


# VARIABLES = MyDict()
VARIABLES = {}

EVAL = "$eval:"


def update_allowed_dict() -> dict:
    global allowed_dict  # needed to remove variables instead of just adding new one
    allowed_dict = {"np": np, "pd": pd}
    allowed_dict.update(DEVICES)
    allowed_dict.update(VARIABLES)
    return allowed_dict


allowed_dict = update_allowed_dict()

# OPTIMIZE: Variable becomes closer and closer to core.elements.Variable, could envision a merge
# TODO: refresh menu display by looking if has eval (no -> can refresh)
# TODO add read signal to update gui (separate class for event and use it on itemwidget creation to change setText with new value)
class Variable():
    """ Class used to control basic variable """

    raw: Any
    value: Any

    def __init__(self, name: str, var: Any):
        """ name: name of the variable, var: value of the variable """
        self.unit = None
        self.writable = True
        self.readable = True
        self._rename(name)
        self.write_function(var)

    def _rename(self, new_name: str):
            self.name = new_name
            self.address = lambda: new_name

    def write_function(self, var: Any):
        if isinstance(var, Variable):
            self.raw = var.raw
            self.value = var.value
        else:
            self.raw = var
            self.value = 'Need update' if has_eval(self.raw) else self.raw

        # If no devices or variables with char '(' found in raw, can evaluate value safely
        if not has_variable(self.raw) or '(' not in self.raw:
            try: self.value = self.read_function()
            except Exception as e: self.value = str(e)

        self.type = type(self.raw)  # For slider

    def read_function(self):
        if has_eval(self.raw):
            value = str(self.raw)[len(EVAL): ]
            call = eval(str(value), {}, allowed_dict)
            self.value = call
        else:
            call = self.value

        return call

    def __call__(self, value: Any = None) -> Any:
        if value is None:
            return self.read_function()

        self.write_function(value)
        return None


def list_variables() -> List[str]:
    ''' Returns a list of Variables '''
    return list(VARIABLES)


def rename_variable(name: str, new_name: str):
    ''' Rename an existing Variable '''
    new_name = clean_string(new_name)
    var = VARIABLES.pop(name)
    VARIABLES[new_name] = var
    var._rename(new_name)
    update_allowed_dict()


def set_variable(name: str, value: Any) -> Variable:
    ''' Create or modify a Variable with provided name and value '''
    name = clean_string(name)

    if is_Variable(value):
        var = value
        var(value)
    else:
        if name in VARIABLES:
            var = get_variable(name)
            var(value)
        else:
            var = Variable(name, value)

    VARIABLES[name] = var
    update_allowed_dict()
    return var


def get_variable(name: str) -> Variable:
    ''' Return Variable with provided name '''
    assert name in VARIABLES, f"Variable name '{name}' not found in {list_variables()}"
    return VARIABLES[name]


def remove_variable(name: str) -> Variable:
    var = VARIABLES.pop(name)
    update_allowed_dict()
    return var


def remove_from_config(variables: List[Tuple[str, Any]]):
    for name, _ in variables:
        if name in VARIABLES:
            remove_variable(name)


def update_from_config(variables: List[Tuple[str, Any]]):
    for var in variables:
        set_variable(var[0], var[1])


def has_variable(value: str) -> bool:
    if not isinstance(value, str): return False
    if has_eval(value): value = value[len(EVAL): ]

    pattern = r'[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*'
    pattern_match = [var.split('.')[0] for var in re.findall(pattern, value)]

    for key in (list(DEVICES) + list(VARIABLES)):
        if key in pattern_match:
            return True
    return False


def has_eval(value: Any) -> bool:
    """ Checks if value is a string starting with '$eval:'"""
    return True if isinstance(value, str) and value.startswith(EVAL) else False


def is_Variable(value: Any):
    """ Returns True if value of type Variable """
    return isinstance(value, Variable)


def eval_variable(value: Any) -> Any:
    """ Evaluate the given python string. String can contain variables,
    devices, numpy arrays and pandas dataframes."""
    if has_eval(value): value = Variable('temp', value)

    if is_Variable(value): return value()
    return value


def eval_safely(value: Any) -> Any:
    """ Same as eval_variable but do not evaluate if contains devices or variables """
    if has_eval(value): value = Variable('temp', value)

    if is_Variable(value): return value.value
    return value
