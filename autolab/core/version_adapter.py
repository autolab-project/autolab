# -*- coding: utf-8 -*-

import os
import shutil

from .paths import PATHS, DRIVER_LEGACY, DRIVER_SOURCES
from .repository import install_drivers


def process_all_changes():
    ''' Apply all changes '''
    rename_old_devices_config_file()
    move_driver()


def rename_old_devices_config_file():
    ''' Rename local_config.ini into devices_config.ini'''
    if (not os.path.exists(os.path.join(PATHS['user_folder'], 'devices_config.ini'))
            and os.path.exists(os.path.join(PATHS['user_folder'], 'local_config.ini'))):
        os.rename(os.path.join(PATHS['user_folder'], 'local_config.ini'),
                  os.path.join(PATHS['user_folder'], 'devices_config.ini'))


def move_driver():
    """ Move old driver directory to new one """
    if os.path.exists(os.path.join(PATHS['user_folder'])) and not os.path.exists(PATHS['drivers']):
        os.mkdir(PATHS['drivers'])
        print(f"The new driver directory has been created: {PATHS['drivers']}")

        # Inside os.path.exists(PATHS['drivers']) condition to avoid moving drivers from current repo everytime autolab is started
        if os.path.exists(DRIVER_LEGACY['official']):
            shutil.move(DRIVER_LEGACY['official'], PATHS['drivers'])
            os.rename(os.path.join(PATHS['drivers'], os.path.basename(DRIVER_LEGACY['official'])),
                      DRIVER_SOURCES['official'])
            print(f"Old official drivers directory has been moved from: {DRIVER_LEGACY['official']} to: {DRIVER_SOURCES['official']}")
            install_drivers()  # Ask if want to download official drivers

        if os.path.exists(DRIVER_LEGACY["local"]):
            shutil.move(DRIVER_LEGACY['local'], PATHS['drivers'])
            os.rename(os.path.join(PATHS['drivers'], os.path.basename(DRIVER_LEGACY['local'])),
                      DRIVER_SOURCES['local'])
            print(f"Old local drivers directory has been moved from: {DRIVER_LEGACY['local']} to: {DRIVER_SOURCES['local']}")
