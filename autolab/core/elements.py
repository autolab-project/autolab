# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 22:20:14 2019

@author: qchat
"""

import os
import sys
import inspect
from typing import Type, Tuple, List, Any

from . import paths
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
        else: return self.name


class Variable(Element):

    def __init__(self, parent: Type, config: dict):

        Element.__init__(self, parent, 'variable', config['name'])

        import numpy as np
        import pandas as pd

        # Type
        assert 'type' in config.keys(), f"Variable {self.address()}: Missing variable type"
        assert config['type'] in [int, float, bool, str, bytes, tuple, np.ndarray, pd.DataFrame], f"Variable {self.address()} configuration: Variable type not supported in autolab"
        self.type = config['type']

        # Read and write function
        assert 'read' in config.keys() or 'write' in config.keys(), f"Variable {self.address()} configuration: no 'read' nor 'write' functions provided"

        # Read function
        self.read_function = None
        self.read_init = False
        if config['type'] in [tuple]: assert 'read' in config.keys(), f"Variable {self.address()} configuration: Must provide a read function"
        if 'read' in config.keys():
            assert inspect.ismethod(config['read']), f"Variable {self.address()} configuration: Read parameter must be a function"
            self.read_function = config['read']
            if 'read_init' in config.keys():
                assert type(config['read_init']) is bool, f"Variable {self.address()} configuration: read_init parameter must be a boolean"
                self.read_init = bool(config['read_init'])
        # Write function
        self.write_function = None
        if 'write' in config.keys():
            assert inspect.ismethod(config['write']), f"Variable {self.address()} configuration: Write parameter must be a function"
            self.write_function = config['write']

        # Unit
        self.unit = None
        if 'unit' in config.keys():
            assert isinstance(config['unit'], str), f"Variable {self.address()} configuration: Unit parameter must be a string"
            self.unit = config['unit']

        # Help
        if 'help' in config.keys():
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

        import pandas as pd
        import numpy as np

        assert self.readable, f"The variable {self.name} is not configured to be measurable"

        if os.path.isdir(path):
            path = os.path.join(path, self.address()+'.txt')

        if value is None: value = self() # New measure if value not provided

        if self.type in [int, float, bool, str, tuple]:
            with open(path, 'w') as f: f.write(str(value))
        elif self.type == bytes:
            with open(path, 'wb') as f: f.write(value)
        elif self.type == np.ndarray:
            value = pd.DataFrame(value)  # faster and handle better different dtype than np.savetxt
            value.to_csv(path, index=False, header=None)
        elif self.type == pd.DataFrame:
            value.to_csv(path, index=False)
        else:
            raise ValueError("The variable {self.name} of type {self.type} cannot be saved.")

    def help(self):
        """ This function prints informations for the user about the current variable """
        print(self)

    def __str__(self):
        """ This function returns informations for the user about the current variable """
        display = '\n' + emphasize(f'Variable {self.name}') + '\n'
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

    def __call__(self, value: Any = None):
        """ Measure or set the value of the variable """
        # GET FUNCTION
        if value is None:
            assert self.readable, f"The variable {self.name} is not readable"
            answer = self.read_function()
            if self._read_signal is not None: self._read_signal.emit_read(answer)
            return answer

        # SET FUNCTION
        else:
            assert self.writable, f"The variable {self.name} is not writable"
            import numpy as np
            if isinstance(value, np.ndarray):
                value = np.array(value, ndmin=1)  # ndim=1 to avoid having float if 0D
            else:
                value = self.type(value)
            self.write_function(value)
            if self._write_signal is not None: self._write_signal.emit_write()


class Action(Element):

    def __init__(self, parent: Type, config: dict):

        Element.__init__(self, parent, 'action', config['name'])

        import pandas as pd
        import numpy as np

        # Do function
        assert 'do' in config.keys(), f"Action {self.address()}: Missing 'do' function"
        assert inspect.ismethod(config['do']), f"Action {self.address()} configuration: Do parameter must be a function"
        self.function = config['do']

        # Argument
        self.type = None
        self.unit = None
        if 'param_type' in config.keys():
            assert config['param_type'] in [int, float, bool, str, bytes, tuple, np.ndarray, pd.DataFrame], f"Action {self.address()} configuration: Argument type not supported in autolab"
            self.type = config['param_type']
            if 'param_unit' in config.keys():
                assert isinstance(config['param_unit'], str), f"Action {self.address()} configuration: Argument unit parameter must be a string"
                self.unit = config['param_unit']

        # Help
        if 'help' in config.keys():
            assert isinstance(config['help'], str), f"Action {self.address()} configuration: Info parameter must be a string"
            self._help = config['help']

        self.has_parameter = self.type is not None

    def help(self):
        """ This function prints informations for the user about the current variable """
        print(self)

    def __str__(self):
        """ This function returns informations for the user about the current variable """
        display = '\n' + emphasize(f'Action {self.name}') + '\n'
        if self._help is not None: display+=f'Help: {self._help}\n'
        display += '\n'

        display += f"Driver function: '{self.function.__name__}'\n"

        if self.has_parameter:
            display += f'Parameter: YES (type: {self.type.__name__})'
            if self.unit is not None: display += f'(unit: {self.unit})'
            display += '\n'
        else :
            display += 'Parameter: NO\n'

        return display

    def __call__(self, value: Any = None):
        """ Executes the action """
        # DO FUNCTION
        assert self.function is not None, f"The action {self.name} is not configured to be actionable"
        if self.has_parameter:
            if value is not None:
                value = self.type(value)
                self.function(value)
            elif self.unit in ('open-file', 'save-file', 'filename'):
                if self.unit == 'filename':  # LEGACY (may be removed later)
                    print(f"Using 'filename' as unit is depreciated in favor of 'open-file' and 'save-file'" \
                          f"\nUpdate driver {self.name} to remove this warning",
                          file=sys.stderr)
                    self.unit = 'open-file'

                from qtpy import QtWidgets
                app = QtWidgets.QApplication(sys.argv)  # Needed if started outside of GUI

                if self.unit == 'open-file':
                    filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                        caption="Open file",
                        directory=paths.USER_LAST_CUSTOM_FOLDER,
                        filter=SUPPORTED_EXTENSION)
                elif self.unit == 'save-file':
                    filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                        caption="Save file",
                        directory=paths.USER_LAST_CUSTOM_FOLDER,
                        filter=SUPPORTED_EXTENSION)

                if filename != '':
                    path = os.path.dirname(filename)
                    paths.USER_LAST_CUSTOM_FOLDER = path
                    self.function(filename)
                else:
                    print("Filename prompt cancelled")
            else:
                assert value is not None, f"The action {self.name} requires an argument"
        else:
            assert value is None, f"The action {self.name} doesn't require an argument"
            self.function()


class Module(Element):

    def __init__(self, parent: Type, config: dict):

        Element.__init__(self, parent, 'module', config['name'])

        self._mod = {}
        self._var = {}
        self._act = {}
        self._read_init_list = []

        # Object - instance
        assert 'object' in config.keys(), f"Module {self.name}: missing module object"
        self.instance = config['object']

        # Help
        if 'help' in config.keys():
            assert isinstance(config['help'], str), f"Module {self.address()} configuration: Help parameter must be a string"
            self._help = config['help']

        # Loading instance
        assert hasattr(self.instance, 'get_driver_model'), "There is no function 'get_driver_model' in the driver class"
        driver_config = self.instance.get_driver_model()
        assert isinstance(driver_config, list), f"Module {self.name} configuration: 'get_driver_model' output must be a list of dictionnaries"

        for config_line in driver_config:
            # General check
            assert isinstance(config_line, dict), f"Module {self.name} configuration: 'get_driver_model' output must be a list of dictionnaries"

            # Name check
            assert 'name' in config_line.keys(), f"Module {self.name} configuration: missing 'name' key in one dictionnary"
            assert isinstance(config_line['name'], str), f"Module {self.name} configuration: elements names must be a string"
            name = clean_string(config_line['name'])
            assert name != '', f"Module {self.name}: elements names cannot be empty"

            # Element type check
            assert 'element' in config_line.keys(), f"Module {self.name}, Element {name} configuration: missing 'element' key in the dictionnary"
            assert isinstance(config_line['element'], str), f"Module {self.name}, Element {name} configuration: element type must be a string"
            element_type = config_line['element']
            assert element_type in ['module', 'variable', 'action'], f"Module {self.name}, Element {name} configuration: Element type has to be either 'module','variable' or 'action'"

            if element_type == 'module':
                # Check name uniqueness
                assert name not in self.get_names(), f"Module {self.name}, Submodule {name} configuration: '{name}' already exists"
                self._mod[name] = Module(self, config_line)

            elif element_type == 'variable':
                # Check name uniqueness
                assert name not in self.get_names(), f"Module {self.name}, Variable {name} configuration: '{name}' already exists"
                self._var[name] = Variable(self, config_line)
                if self._var[name].read_init:
                    self._read_init_list.append(self._var[name])

            elif element_type == 'action':
                # Check name uniqueness
                assert name not in self.get_names(), f"Module {self.name}, Action {name} configuration: '{name}' already exists"
                self._act[name] = Action(self, config_line)

    def get_module(self, name: str) -> Type:  # -> Module
        """ Returns the submodule of the given name """
        assert name in self.list_modules(), f"The submodule '{name}' does not exist in module {self.name}"
        return self._mod[name]

    def list_modules(self) -> List[str]:
        """ Returns a list with the names of all existing submodules """
        return list(self._mod.keys())

    def get_variable(self, name: str) -> Variable:
        """ Returns the variable with the given name """
        assert name in self.list_variables(), f"The variable '{name}' does not exist in module {self.name}"
        return self._var[name]

    def list_variables(self) -> List[str]:
        """ Returns a list with the names of all existing variables attached to this module """
        return list(self._var.keys())

    def get_action(self, name) -> Action:
        """ Returns the action with the given name """
        assert name in self.list_actions(), f"The action '{name}' does not exist in device {self.name}"
        return self._act[name]

    def list_actions(self) -> List[str]:
        """ Returns a list with the names of all existing actions attached to this module """
        return list(self._act.keys())

    def get_names(self) -> List[str]:
        """ Returns the list of the names of all the elements of this module """
        return self.list_modules() + self.list_variables() + self.list_actions()

    def __getattr__(self, attr) -> Element:
        if attr in self.list_variables(): return self.get_variable(attr)
        elif attr in self.list_actions(): return self.get_action(attr)
        elif attr in self.list_modules(): return self.get_module(attr)
        else: raise AttributeError(f"'{attr}' not found in module '{self.name}'")

    def get_structure(self):
        """ Returns the structure of the module as a list containing each element address associated with its type as
        [['address1', 'variable'], ['address2', 'action'],...] """
        structure = []

        for mod in self.list_modules():
            structure += self.get_module(mod).get_structure()
        for var in self.list_variables():
            structure.append([self.get_variable(var).address(), 'variable'])
        for act in self.list_actions():
            structure.append([self.get_action(act).address(), 'action'])

        return structure

    def sub_hierarchy(self, level: int = 0) -> List[Tuple[str, str, int]]:
        ''' Returns a list of the sub hierarchy of this module
        [[name: str, type: str, level: int]]
        '''
        h = []

        from .devices import Device
        if isinstance(self, Device): h.append([self.name, 'Device/Module', level])
        else: h.append([self.name, 'Module', level])

        for mod in self.list_modules():
            h += self.get_module(mod).sub_hierarchy(level+1)
        for var in self.list_variables():
            h.append([var, 'Variable', level+1])
        for act in self.list_actions():
            h.append([act, 'Action', level+1])

        return h

    def help(self):
        """ This function prints informations for the user about the availables
        submodules, variables and action attached to the current module """
        print(self)

    def __str__(self) -> str:
        """ This function returns informations for the user about the availables
        submodules, variables and action attached to the current module """
        display ='\n' + emphasize(f'Module {self.name}') + '\n'

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
