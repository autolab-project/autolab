# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 22:20:14 2019

@author: qchat
"""

import os
import sys
import inspect
from typing import Type, Tuple, List, Any

import numpy as np
import pandas as pd

from .paths import PATHS
from .utilities import emphasize, clean_string, SUPPORTED_EXTENSION


class Element():

    def __init__(self, parent: Type, element_type: str, name: str):

        self.name = name
        self._element_type = element_type
        self._parent = parent
        self._help = None

    def address(self) -> str:
        """ Returns the address of the given element.
        <module.submodule.variable> """
        if self._parent is not None:
            return self._parent.address() + '.' + self.name
        return self.name


class Variable(Element):

    def __init__(self, parent: Type, config: dict):

        super().__init__(parent, 'variable', config['name'])

        # Type
        assert 'type' in config, f"Variable {self.address()}: Missing variable type"
        assert config['type'] in [int, float, bool, str, bytes, tuple, np.ndarray, pd.DataFrame], f"Variable {self.address()} configuration: Variable type not supported in autolab"
        self.type = config['type']
        if self.type in [tuple]:
            self.value = ([], -1)

        # Read and write function
        assert 'read' in config or 'write' in config, f"Variable {self.address()} configuration: no 'read' nor 'write' functions provided"

        # Read function
        self.read_function = None
        self.read_init = False
        # if config['type'] in [tuple]: assert 'read' in config, f"Variable {self.address()} configuration: Must provide a read function"
        if 'read' in config:
            assert inspect.ismethod(config['read']), f"Variable {self.address()} configuration: Read parameter must be a function"
            self.read_function = config['read']
            if 'read_init' in config:
                assert isinstance(config['read_init'], bool), f"Variable {self.address()} configuration: read_init parameter must be a boolean"
                self.read_init = bool(config['read_init'])

        # Write function
        self.write_function = None
        if 'write' in config:
            assert inspect.ismethod(config['write']), f"Variable {self.address()} configuration: Write parameter must be a function"
            self.write_function = config['write']

        # Unit
        self.unit = None
        if 'unit' in config:
            assert isinstance(config['unit'], str), f"Variable {self.address()} configuration: Unit parameter must be a string"
            self.unit = config['unit']

        # Help
        if 'help' in config:
            assert isinstance(config['help'], str), f"Variable {self.address()} configuration: Info parameter must be a string"
            self._help = config['help']

        # Properties
        self.writable = self.write_function is not None
        self.readable = self.read_function is not None
        self.numerical = self.type in [int, float]
        self.parameter_allowed = self.writable and self.numerical

        # Signals for GUI
        self._read_signal = None
        self._write_signal = None

    def save(self, path: str, value: Any = None):
        """ This function measure the variable and saves its value in the provided path """

        assert self.readable, f"The variable {self.address()} is not configured to be measurable"

        if os.path.isdir(path):
            path = os.path.join(path, self.address()+'.txt')

        if value is None: value = self() # New measure if value not provided

        if self.type in [int, float, bool, str, tuple]:
            with open(path, 'w') as f: f.write(str(value))
        elif self.type == bytes:
            with open(path, 'wb') as f: f.write(value)
        elif self.type == np.ndarray:
            try:
                value = pd.DataFrame(value)  # faster and handle better different dtype than np.savetxt
                value.to_csv(path, index=False, header=None)
            except:
                # Avoid error if strange ndim, 0 or (1,2,3) ... was occuring in GUI scan when doing $eval:[1] instead of $eval:np.array([1]). Now GUI forces array to ndim=1
                print(f"Warning, can't save {value}")
        elif self.type == pd.DataFrame:
            value.to_csv(path, index=False)
        else:
            raise ValueError("The variable {self.address()} of type {self.type} cannot be saved.")

    def help(self):
        """ This function prints informations for the user about the current variable """
        print(self)

    def __str__(self) -> str:
        """ This function returns informations for the user about the current variable """
        display = '\n' + emphasize(f'Variable {self.address()}') + '\n'
        if self._help is not None: display += f'Help: {self._help}\n'
        display += '\n'

        display += 'Readable: '
        if self.readable: display += f"YES (driver function '{self.read_function.__name__}')\n"
        else: display += 'NO\n'

        display += 'Writable: '
        if self.writable: display += f"YES (driver function '{self.write_function.__name__}')\n"
        else: display += 'NO\n'

        display += f'Type: {self.type.__name__}\n'

        display += 'Unit: '
        if self.unit is not None: display += f'{self.unit}\n'
        else: display += 'None\n'

        return display

    def __call__(self, value: Any = None) -> Any:
        """ Measure or set the value of the variable """
        # GET FUNCTION
        if value is None:
            assert self.readable, f"The variable {self.address()} is not readable"
            answer = self.read_function()
            if self._read_signal is not None: self._read_signal.emit_read(answer)
            if self.type in [tuple]:  # OPTIMIZE: could be generalized to any variable but fear could lead to memory issue
                self.value = answer
            return answer

        # SET FUNCTION
        assert self.writable, f"The variable {self.address()} is not writable"

        if isinstance(value, np.ndarray) or self.type in [np.ndarray]:
            value = np.array(value, ndmin=1)  # ndim=1 to avoid having float if 0D
        else:
            value = self.type(value)
        if self.type in [tuple]:  # OPTIMIZE: could be generalized to any variable but fear could lead to memory issue
            self.value = value
        self.write_function(value)
        if self._write_signal is not None: self._write_signal.emit_write(value)
        return None


class Action(Element):

    def __init__(self, parent: Type, config: dict):

        super().__init__(parent, 'action', config['name'])

        # Do function
        assert 'do' in config, f"Action {self.address()}: Missing 'do' function"
        assert inspect.ismethod(config['do']), f"Action {self.address()} configuration: Do parameter must be a function"
        self.function = config['do']

        # Argument
        self.type = None
        self.unit = None
        if 'param_type' in config:
            assert config['param_type'] in [int, float, bool, str, bytes, tuple, np.ndarray, pd.DataFrame], f"Action {self.address()} configuration: Argument type not supported in autolab"
            self.type = config['param_type']
            if 'param_unit' in config:
                assert isinstance(config['param_unit'], str), f"Action {self.address()} configuration: Argument unit parameter must be a string"
                self.unit = config['param_unit']

        # Help
        if 'help' in config:
            assert isinstance(config['help'], str), f"Action {self.address()} configuration: Info parameter must be a string"
            self._help = config['help']

        self.has_parameter = self.type is not None

        if self.type in [tuple]:
            self.value = ([], -1)

        # Signals for GUI
        self._write_signal = None

    def help(self):
        """ This function prints informations for the user about the current variable """
        print(self)

    def __str__(self) -> str:
        """ This function returns informations for the user about the current variable """
        display = '\n' + emphasize(f'Action {self.address()}') + '\n'
        if self._help is not None: display+=f'Help: {self._help}\n'
        display += '\n'

        display += f"Driver function: '{self.function.__name__}'\n"

        if self.has_parameter:
            display += f'Parameter: YES (type: {self.type.__name__})'
            if self.unit is not None: display += f'(unit: {self.unit})'
            display += '\n'
        else:
            display += 'Parameter: NO\n'

        return display

    def __call__(self, value: Any = None) -> Any:
        """ Executes the action """
        # DO FUNCTION
        assert self.function is not None, f"The action {self.address()} is not configured to be actionable"
        if self.has_parameter:
            if value is not None:
                if isinstance(value, np.ndarray):
                    value = np.array(value, ndmin=1)  # ndim=1 to avoid having float if 0D
                else:
                    value = self.type(value)
                self.function(value)
            elif self.unit in ('open-file', 'save-file', 'filename'):
                if self.unit == 'filename':  # LEGACY (may be removed later)
                    print(f"Using 'filename' as unit is depreciated in favor of 'open-file' and 'save-file'" \
                          f"\nUpdate driver '{self.address().split('.')[0]}' to remove this warning",
                          file=sys.stderr)
                    self.unit = 'open-file'

                from qtpy import QtWidgets
                _ = QtWidgets.QApplication(sys.argv)  # Needed if started outside of GUI

                if self.unit == 'open-file':
                    filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                        caption=f"Open file - {self.address()}",
                        directory=PATHS['last_folder'],
                        filter=SUPPORTED_EXTENSION)
                elif self.unit == 'save-file':
                    filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                        caption=f"Save file - {self.address()}",
                        directory=PATHS['last_folder'],
                        filter=SUPPORTED_EXTENSION)

                if filename != '':
                    path = os.path.dirname(filename)
                    PATHS['last_folder'] = path
                    value = filename
                    self.function(value)
                else:
                    print(f"Action '{self.address()}' cancel filename selection")

            elif self.unit == "user-input":

                from qtpy import QtWidgets
                _ = QtWidgets.QApplication(sys.argv)  # Needed if started outside of GUI
                # OPTIMIZE: dialog closes on instantiation inside Spyder
                response, _ = QtWidgets.QInputDialog.getText(
                    None, self.address(), f"Set {self.address()} value",
                    QtWidgets.QLineEdit.Normal)

                if response != '':
                    value = response
                    self.function(value)
            else:
                assert value is not None, f"The action {self.address()} requires an argument"
        else:
            assert value is None, f"The action {self.address()} doesn't require an argument"
            self.function()

        if self.type in [tuple]:  # OPTIMIZE: could be generalized to any variable but fear could lead to memory issue
            self.value = value
        if self._write_signal is not None: self._write_signal.emit_write(value)


class Module(Element):

    def __init__(self, parent: Type, config: dict):

        super().__init__(parent, 'module', config['name'])

        self._mod = {}
        self._var = {}
        self._act = {}
        self._read_init_list = []

        # Object - instance
        assert 'object' in config, f"Module {self.address()}: missing module object"
        self.instance = config['object']

        # Help
        if 'help' in config:
            assert isinstance(config['help'], str), f"Module {self.address()} configuration: Help parameter must be a string"
            self._help = config['help']

        # Loading instance
        assert hasattr(self.instance, 'get_driver_model'), "There is no function 'get_driver_model' in the driver class"
        driver_config = self.instance.get_driver_model()
        assert isinstance(driver_config, list), f"Module {self.address()} configuration: 'get_driver_model' output must be a list of dictionnaries"

        for config_line in driver_config:
            # General check
            assert isinstance(config_line, dict), f"Module {self.address()} configuration: 'get_driver_model' output must be a list of dictionnaries"

            # Name check
            assert 'name' in config_line, f"Module {self.address()} configuration: missing 'name' key in one dictionnary"
            assert isinstance(config_line['name'], str), f"Module {self.address()} configuration: elements names must be a string"
            name = clean_string(config_line['name'])
            assert name != '', f"Module {self.address()}: elements names cannot be empty"

            # Element type check
            assert 'element' in config_line, f"Module {self.address()}, Element {name} configuration: missing 'element' key in the dictionnary"
            assert isinstance(config_line['element'], str), f"Module {self.address()}, Element {name} configuration: element type must be a string"
            element_type = config_line['element']
            assert element_type in ['module', 'variable', 'action'], f"Module {self.address()}, Element {name} configuration: Element type has to be either 'module','variable' or 'action'"

            if element_type == 'module':
                # Check name uniqueness
                assert name not in self.get_names(), f"Module {self.address()}, Submodule {name} configuration: '{name}' already exists"
                self._mod[name] = Module(self, config_line)

            elif element_type == 'variable':
                # Check name uniqueness
                assert name not in self.get_names(), f"Module {self.address()}, Variable {name} configuration: '{name}' already exists"
                self._var[name] = Variable(self, config_line)
                if self._var[name].read_init:
                    self._read_init_list.append(self._var[name])

            elif element_type == 'action':
                # Check name uniqueness
                assert name not in self.get_names(), f"Module {self.address()}, Action {name} configuration: '{name}' already exists"
                self._act[name] = Action(self, config_line)

    def get_module(self, name: str) -> Type:  # -> Module
        """ Returns the submodule of the given name """
        assert name in self.list_modules(), f"The submodule '{name}' does not exist in module {self.address()}"
        return self._mod[name]

    def list_modules(self) -> List[str]:
        """ Returns a list with the names of all existing submodules """
        return list(self._mod)

    def get_variable(self, name: str) -> Variable:
        """ Returns the variable with the given name """
        assert name in self.list_variables(), f"The variable '{name}' does not exist in module {self.address()}"
        return self._var[name]

    def list_variables(self) -> List[str]:
        """ Returns a list with the names of all existing variables attached to this module """
        return list(self._var)

    def get_action(self, name) -> Action:
        """ Returns the action with the given name """
        assert name in self.list_actions(), f"The action '{name}' does not exist in device {self.address()}"
        return self._act[name]

    def list_actions(self) -> List[str]:
        """ Returns a list with the names of all existing actions attached to this module """
        return list(self._act)

    def get_names(self) -> List[str]:
        """ Returns the list of the names of all the elements of this module """
        return self.list_modules() + self.list_variables() + self.list_actions()

    def __getattr__(self, attr: str) -> Element:
        if attr in self.list_variables(): return self.get_variable(attr)
        if attr in self.list_actions(): return self.get_action(attr)
        if attr in self.list_modules(): return self.get_module(attr)
        raise AttributeError(f"'{attr}' not found in module '{self.address()}'")

    def get_structure(self) -> List[Tuple[str, str]]:
        """ Returns the structure of the module as a list containing each element address associated with its type as
        [['address1', 'variable'], ['address2', 'action'],...] """
        structure = []

        for mod in self.list_modules():
            structure += self.get_module(mod).get_structure()
        for var in self.list_variables():
            structure.append((self.get_variable(var).address(), 'variable'))
        for act in self.list_actions():
            structure.append((self.get_action(act).address(), 'action'))

        return structure

    def sub_hierarchy(self, level: int = 0) -> List[Tuple[str, str, int]]:
        ''' Returns a list of the sub hierarchy of this module
        [[name: str, type: str, level: int]]
        '''
        h = []

        from .devices import Device  # import here to avoid ImportError circular import
        if isinstance(self, Device): h.append((self.name, 'Device/Module', level))
        else: h.append((self.name, 'Module', level))

        for mod in self.list_modules():
            h += self.get_module(mod).sub_hierarchy(level+1)
        for var in self.list_variables():
            h.append((var, 'Variable', level+1))
        for act in self.list_actions():
            h.append((act, 'Action', level+1))

        return h

    def help(self):
        """ This function prints informations for the user about the availables
        submodules, variables and action attached to the current module """
        print(self)

    def __str__(self) -> str:
        """ This function returns informations for the user about the availables
        submodules, variables and action attached to the current module """
        display ='\n' + emphasize(f'Module {self.address()}') + '\n'

        if self._help is not None:
            display += f'Help: {self._help}\n'

        display += '\nElement hierarchy:'
        hierarchy = self.sub_hierarchy()

        for i, h_step in enumerate(hierarchy):
            if i == 0: prefix = ''
            else: prefix = '|- '
            txt = ' '*3*h_step[2] + f'{prefix}{h_step[0]}'
            display += '\n' + txt + ' '*(30 - len(txt)) + f'({h_step[1]})'

        return display

    def __dir__(self):
        """ For auto-completion """
        return (self.list_modules() + self.list_variables()
                + self.list_actions() + ['help', 'instance'])
