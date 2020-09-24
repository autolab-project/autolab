# -*- coding: utf-8 -*-

from git import Repo
from . import paths

class RepoSyncer :
    
    def __init__(self) :
        
        self.url = 'https://github.com/qcha41/autolab-drivers.git'
        self.path = paths.DRIVERS_OFFICIAL
        
    def clone(self) :
        Repo.clone_from(self.url,self.path)

    def sync(self) :
        print('Syncing drivers repository...')
        # Try to clone repo if it is not already done
        try : self.clone()
        except : pass
        # load local repo
        repo = Repo(paths.DRIVERS_OFFICIAL)
        # discard any current changes (mandatory)
        repo.git.reset('--hard')
        # pull in the changes from from the remote repo 
        repo.remotes.origin.pull()
        print('Drivers repository up-to-date!')
           
    