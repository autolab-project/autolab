# -*- coding: utf-8 -*-

import configparser
import os

from . import paths,utilities



class DriverManager() :
    
    def __init__(self):
        self.drivers = {}
        self.refresh()
        
    def list_drivers(self):
        return list(self.drivers.keys())
    
    def list_categories(self):
        return list(set([d.category for d in self.drivers.keys()]))
    
    def refresh(self):
        self.drivers = {}
        for source_path in [paths.DRIVERS_OFFICIAL,paths.DRIVERS_LOCAL]:
            for item in os.listdir(source_path) :
                try : driver = Driver(os.path.join(source_path,item))
                except : driver = None
                if driver is not None and len(driver.list_versions())>0 :
                    assert driver.name not in self.drivers.keys()
                    self.drivers[driver.name] = driver
                    
    def summary(self):
        
        # Prepare list
        drivers = {}
        for driver_name in self.list_drivers() :
            category = self.drivers[driver_name].category
            if category not in drivers.keys() : drivers[category] = []
            drivers[category].append(driver_name)
            
        # Print
        tab_content = [['Driver category','Driver name','Last version'],None]
        for category in drivers.keys() :
            init = 0
            for driver_name in drivers[category] :
                if init == 0 : 
                    tab_content.append([category,driver_name,self.drivers[driver_name].last_version()])
                    init = 1
                else : 
                    tab_content.append(['',driver_name,self.drivers[driver_name].last_version()])
                tab_content.append(None)
        if len(tab_content) == 2 : 
            print('No drivers yet, download them using the update() function.')
        else :
            utilities.print_tab(tab_content)
        
    def update(self):
        
        from . import repo
        repo.sync()   
        self.refresh()
                    

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
            try : release = Release(os.path.join(self.path,item))
            except : release = None
            if release is not None :
                assert release.name not in self.releases.keys()
                self.releases[release.version] = release
                
    def list_versions(self):
        return list(self.releases.keys())
    
    def last_version(self):
        return max(self.list_versions())
                    
    def instantiate(self,connection_infos,version=None) :
        if version is None: version = max(self.versions())
        assert version in self.versions(), f"Version {version} of driver {self.name} doesn't exist"
        return self.releases[version].instantiate(connection_infos)
        
    
    def summary(self):
        print(f" Driver {self.name}")
        print('')
        tab_content = [['Version (date)','Release notes'],None]
        for version in sorted(self.releases.keys()) :
            tab_content.append([f'{version} ({self.releases[version].date})',self.releases[version].notes])
        tab_content.append(None)
        utilities.print_tab(tab_content)
    
    
    
class Release():
    
    def __init__(self,path):
    
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
        
    def instantiate(self,connection_infos):
        pass
        # return instance
        
        


    
        