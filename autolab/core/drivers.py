# -*- coding: utf-8 -*-

from git import Repo
from git.remote import RemoteProgress
from . import paths
import os

class Progress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(op_code, cur_count, max_count, message)


def clone_repo():
    Repo.clone_from('https://github.com/qcha41/autolab-drivers.git',paths.DRIVERS_OFFICIAL,progress=Progress())

def sync_repo() :
    print('Syncing drivers repository...')
    try : clone_repo()
    except : pass
    # load local repo
    repo = Repo(paths.DRIVERS_OFFICIAL)
    # discard any current changes (mandatory)
    repo.git.reset('--hard')
    # pull in the changes from from the remote repo 
    repo.remotes.origin.pull()
    print('Drivers repository up-to-date!')
    
    
    
def load_paths():

    ''' Returns a dictionary with drivers {name:path} values '''

    drivers_paths = {}
    
    for source_path in [paths.DRIVERS_OFFICIAL,paths.DRIVERS_LOCAL] :
        for driver_name in os.listdir(source_path) :
            path = os.path.join(source_path,driver_name)
            if os.path.isdir(path) :
                assert driver_name not in drivers_paths.keys(), f"Two drivers where found with the name '{driver_name}'. Each driver must have a unique name."
                drivers_paths[driver_name] = path

    return drivers_paths