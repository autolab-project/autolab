# -*- coding: utf-8 -*-

import configparser
import os
import importlib
import inspect

from . import paths,utilities

drivers = {}

class DriverManager() :
    
    def __init__(self):
        self.refresh()
        
    def list_drivers(self):
        return list(drivers.keys())
    
    def list_categories(self):
        return list(set([d.category for d in drivers.keys()]))
    
    def refresh(self):
        global drivers
        drivers = {}
        for source_path in [paths.DRIVERS_OFFICIAL,paths.DRIVERS_LOCAL]:
            for item in os.listdir(source_path) :
                try : driver = Driver(os.path.join(source_path,item))
                except : driver = None
                if driver is not None and len(driver.list_versions())>0 :
                    assert driver.name not in drivers.keys(), f'At least two drivers found with the same name {driver.name}.'
                    drivers[driver.name] = driver
                    
    def summary(self):
        tab_content = [['Category','Manufacturer','Model','Driver name','Last version'],None]
        for category in sorted(self.list_categories()) :
            for driver_name in sorted([d.name for d in drivers.keys() if d.category==category]) :
                driver = drivers[driver_name]
                line_content = []
                if tab_content[-1] is not None and tab_content[-1][0] != category : line_content.append(category)
                else : line_content.append('')
                if tab_content[-1] is not None and tab_content[-1][1] != driver.manufacturer : line_content.append(driver.manufacturer)
                else : line_content.append('')
                line_content.append(driver.model)
                line_content.append(driver.name)
                line_content.append(driver.last_version())
                tab_content.append(None)
        if len(tab_content) == 2 : 
            print('No drivers yet, download them using the update() function.')
        else :
            utilities.print_tab(tab_content)
        
    def update(self):
        from . import repo
        repo.sync()   
        self.refresh()
        
    def get_driver(self,driver_name):
        assert driver_name in drivers.keys(), f'Driver {driver_name} does not exist' 
        return drivers[driver_name]

    def __getattr__(self,attr):
        return self.get_driver(attr)
    
    def __getitem__(self,attr):
        return self.get_driver(attr)
                    

class Driver():
    
    def __init__(self,path) :
        
        assert os.path.isdir(path)
        self.path = path
        
        # Load driver infos
        driver_infos_path = os.path.join(path,'driver_infos.ini')
        assert os.path.exists(driver_infos_path)
        driver_infos = configparser.ConfigParser()
        driver_infos.read(driver_infos_path)
        assert 'GENERAL' in driver_infos.sections()
        driver_infos = driver_infos['GENERAL']
        for key in ['name','category','manufacturer','model'] :
            assert key in driver_infos.keys(), f'Missing key "{key}" in {path}'
            setattr(self,key,driver_infos[key])
        
        # Load releases
        self.releases = {}
        for item in os.listdir(self.path) :
            try : release = Release(self,os.path.join(self.path,item))
            except : release = None
            if release is not None :
                assert release.name not in self.releases.keys()
                self.releases[release.version] = release
                
    def list_versions(self):
        return list(self.releases.keys())
    
    def last_version(self):
        return max(self.list_versions())
    
    def last_release(self):
        return self.get_release(self.last_version())
                    
    def connect(self,connection_infos,version=None) :
        if version is None: version = max(self.versions())
        release = self.get_release(version)
        return release.connect(connection_infos)
        
    def summary(self):
        print(f" Driver {self.name}")
        print(f" Instrument {self.manufacturer}, model {self.model}")
        print('')
        tab_content = [['Releases versions (date)','Releases notes'],None]
        for version in sorted(self.releases.keys()) :
            tab_content.append([f'{version} ({self.releases[version].date})',self.releases[version].notes])
        tab_content.append(None)
        utilities.print_tab(tab_content)
        
    def get_release(self,version):
        assert version in self.releases.keys(), f"Version {version} of driver {self.name} does not exist"
        return self.releases[version]
    
    def __getitem__(self,attr):
        return self.get_release(attr)
    
    
class Release():
    
    def __init__(self,driver,path):
        
        self.driver = driver
    
        assert os.path.isdir(path)
        self.path = path
        
        # Load release infos
        release_infos_path = os.path.join(path,'release_infos.ini')
        assert os.path.exists(release_infos_path)
        release_infos = configparser.ConfigParser()
        release_infos.read(release_infos_path)
        assert 'GENERAL' in release_infos.sections()
        release_infos = release_infos['GENERAL']
        for key in ['version','notes','date'] :
            assert key in release_infos.keys(), f'Missing key "{key}" in release_infos.ini'
            setattr(self,key,release_infos[key])
            
        # Check required files
        self.driver_path = os.path.join(self.path,'driver.py')
        self.autolab_config_path = os.path.join(self.path,'autolab_config.ini')
        assert os.path.exists(self.driver_path)  
        assert os.path.exists(self.autolab_config_path)
        
    
        
    def connect(self,connection_infos):
        connection_name = connection_infos.pop('connection')
        connection_class = DriverLibraryLoader(self.driver_path).get_connection_class(connection_name)
        return connection_class(connection_infos)
        
    def summary(self):
        print(f'Driver {self.driver.name}')
        print(f'Release {self.version} (self.date)')
        print(f'Releases notes: {self.notes}')
        

    def config_help(self, _print=True, _parser=False):

        ''' Display the help of a particular driver (connection types, modules, ...) '''
        
        library = DriverLibraryLoader(self.driver_path)
        
        # Load list of all parameters
        params = {}
        params['driver'] = self.driver.name
        params['connection'] = {}
        for connnection_name in library.get_connection_names() :
            params['connection'][connnection_name] = library.get_class_args(connnection_name)
        params['other'] = library.get_class_args('Driver')
        if hasattr(library.get_driver_class(),'slot_config') :
            params['other']['slot1'] = f'{library.get_driver_class().slot_config}'
            params['other']['slot1_name'] = 'my_<MODULE_NAME>'
    
        mess = '\n'
    
        # Name and category if available
        submess = f'Driver "{self.driver.name}" ({self.driver.category})'
        mess += utilities.emphasize(submess,sign='=') + '\n'
    
        # Connections types
        c_option=''
        if _parser: c_option='(-C option)'
        mess += f'\nAvailable connections types {c_option}:\n'
        for connection_name in params['connection'].keys() :
            mess += f' - {connection_name}\n'
        mess += '\n'
    
        # Modules
        if hasattr(library.get_driver_class(),'slot_config') :
            mess += 'Available modules:\n'
            for module_name in self.get_module_names() :
                mess += f' - {module_name}\n'
            mess += '\n'
    
        # Example of get_driver
        mess += '\n' + utilities.underline('Loading a Device manually (with arguments):') + '\n\n'
        for connection_name in params['connection'].keys() :
            if _parser is False :
                args_str = f"'{params['driver']}', connection='{connection_name}'"
                for arg,value in params['connection'][connection_name].items():
                    args_str += f", {arg}='{value}'"
                for arg,value in params['other'].items():
                    args_str += f", {arg}='{value}'"
                mess += f"   a = autolab.get_device({args_str})\n"
            else :
                args_str = f"-D {params['driver']} -C {connection_name} "
                for arg,value in params['connection'][connection_name].items():
                    if arg == 'address' : args_str += f"-A {value} "
                    if arg == 'port' : args_str += f"-P {value} "
                if len(params['other'])>0 : args_str += '-O '
                for arg,value in params['other'].items():
                    args_str += f"{arg}={value} "
                mess += f"   autolab device {args_str} \n"
    
        # Example of a devices_config.ini section
        mess += '\n\n' + utilities.underline('Saving a Device configuration in devices_config.ini:') + '\n'
        for connection_name in params['connection'].keys() :
            mess += f"\n   [my_{params['driver']}]\n"
            mess += f"   driver = {params['driver']}\n"
            mess += f"   connection = {connection_name}\n"
            for arg,value in params['connection'][connection_name].items():
                mess += f"   {arg} = {value}\n"
            for arg,value in params['other'].items():
                mess += f"   {arg} = {value}\n"
    
        # Example of get_driver_by_config
        mess += '\n\n' + utilities.underline('Loading a Device using a configuration in devices_config.ini:') + '\n\n'
        if _parser is False :
            mess += f"   a = autolab.get_device('my_{params['driver']}')"
        else :
            mess += f"   autolab device -D my_{params['driver']}\n"
    
        mess += "\n\nNote: provided arguments overwrite those found in devices_config.ini"
    
        if _print is True : print(mess)
        else : return mess
        
        
class DriverLibraryLoader() :
    
    def __init__(self,path):
        
        self.path = path
        
        # Save current working directory path and go to driver's directory
        curr_dir = os.getcwd()
        os.chdir(os.path.dirname(path))
    
        # Load the module
        spec = importlib.util.spec_from_file_location('driver.py', path)
        self.driver_lib = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.driver_lib)
    
        # Come back to previous working directory
        os.chdir(curr_dir)
    
    
    def list_classes(self):
        
        ''' Returns the list of the all driver's library class '''
        
        return [name.split('_')[1]
                for name, obj in inspect.getmembers(self.driver_lib, inspect.isclass)
                if obj.__module__ is self.driver_lib.__name__]
    
    
    def get_class_args(self,class_name):
    
        ''' Returns the dictionary of the optional arguments required by a class
        with their default values '''
        
        assert class_name in self.list_classes(), 'Class {class_name} does not exist'
        _class = getattr(self.driver_lib,class_name)
        signature = inspect.signature(_class)
        return {k: v.default for k, v in signature.parameters.items() if v.default is not inspect.Parameter.empty}
    
    
    def get_connection_names(self):
    
        ''' Returns the list of the driver's connection types (classes Driver_XXX) '''
    
        return [name.split('_')[1]
                for name, obj in inspect.getmembers(self.driver_lib, inspect.isclass)
                if obj.__module__ is self.driver_lib.__name__
                and name.startswith('Driver_')]
    
    
    def get_module_names(self):
    
        ''' Returns the list of the driver's Module(s) name(s) (classes Module_XXX) '''
    
        return [name.split('_')[1]
                for name, obj in inspect.getmembers(self.driver_lib, inspect.isclass)
                if obj.__module__ is self.driver_lib.__name__
                and name.startswith('Module_')]
    
    
    def get_driver_class(self):
    
        ''' Returns the class Driver of the provided driver library '''
    
        assert hasattr(self.driver_lib,'Driver'), f"Class Driver missing in driver {self.driver_lib.__name__}"
        assert inspect.isclass(self.driver_lib.Driver), f"Class Driver missing in driver {self.driver_lib.__name__}"
        return self.driver_lib.Driver
    
    
    def get_connection_class(self,connection_name):
    
        ''' Returns the class Driver_XXX of the provided driver library and connection type '''
    
        assert connection_name in self.get_connection_names(),f"Invalid connection type {connection_name} for driver {self.driver_lib.__name__}"
        return getattr(self.driver_lib,f'Driver_{connection_name}')
    
    
    def get_module_class(self,module_name):
    
        ''' Returns the class Module_XXX of the provided driver library and module_name'''
    
        assert module_name in self.get_module_names()
        return getattr(self.driver_lib,f'Module_{module_name}')
    
    
    

    
    # def explore_driver(instance,_print=True):
    
    #     ''' Displays the list of the methods available in this instance '''
    
    #     methods = get_instance_methods(instance)
    #     s = 'This instance contains the following functions:\n'
    #     for method in methods :
    #         s += f' - {method[0]}({",".join(method[1])})\n'
    
    #     if _print is True : print(s)
    #     else : return s
    
    
    # def get_instance_methods(instance):
    
    #     ''' Returns the list of all the methods (and their args) in that class '''
    
    #     methods = []
    
    #     # LEVEL 1
    #     for name,obj in inspect.getmembers(instance,inspect.ismethod) :
    #         if name != '__init__' :
    #             attr = getattr(instance,name)
    #             args = list(inspect.signature(attr).parameters.keys())
    #             methods.append([name,args])
    
    #     # LEVEL 2
    #     instance_vars = vars(instance)
    #     for key in instance_vars.keys():
    #         try :    # explicit to avoid visa and inspect.getmembers issue
    #             for name,obj in inspect.getmembers(instance_vars[key],inspect.ismethod):
    #                 if inspect.getmembers(instance_vars[key],inspect.ismethod) != '__init__' and inspect.getmembers(instance_vars[key],inspect.ismethod) and name!='__init__':
    #                     attr = getattr(getattr(instance,key),name)
    #                     args = list(inspect.signature(attr).parameters.keys())
    #                     methods.append([f'{key}.{name}',args])
    #         except : pass
    
    #     return methods
        
        
        
        
        
        