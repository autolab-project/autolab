# -*- coding: utf-8 -*-

import configparser
import os

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
        tab_content = [['Driver category','Driver name','Last version'],None]
        for category in sorted(self.list_categories()) :
            first_row_passed = False
            for driver_name in sorted([d.name for d in drivers.keys() if d.category==category]) :
                if first_row_passed == False : 
                    tab_content.append([category,driver_name,drivers[driver_name].last_version()])
                    first_row_passed = True
                else : 
                    tab_content.append(['',driver_name,drivers[driver_name].last_version()])
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
        assert driver_name in drivers.keys() 
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
        for key in ['name','category'] :
            assert key in driver_infos.keys(), f'Missing key "{key}" in driver_infos.ini'
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
        print('')
        tab_content = [['Releases versions (date)','Releases notes'],None]
        for version in sorted(self.releases.keys()) :
            tab_content.append([f'{version} ({self.releases[version].date})',self.releases[version].notes])
        tab_content.append(None)
        utilities.print_tab(tab_content)
        
    def get_release(self,version):
        assert version in self.releases.keys(), f"Version {version} of driver {self.name} doesn't exist"
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
        
    def connect(self):
        return 'instance'
        
    def summary(self):
        print(f'Driver {self.driver.name}')
        print(f'Release {self.version} (self.date)')
        print(f'Releases notes: {self.notes}')


    
        