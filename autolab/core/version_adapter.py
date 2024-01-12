# -*- coding: utf-8 -*-

import os
import shutil


def process_all_changes():
    ''' Apply all changes '''
    rename_old_devices_config_file()
    move_driver()


def rename_old_devices_config_file():
    ''' Rename local_config.ini into devices_config.ini'''
    from .paths import USER_FOLDER
    if os.path.exists(os.path.join(USER_FOLDER, 'local_config.ini')):
        os.rename(os.path.join(USER_FOLDER, 'local_config.ini'),
                  os.path.join(USER_FOLDER, 'devices_config.ini'))


def move_driver():
    """ Move old driver directory to new one """
    from .paths import USER_FOLDER, DRIVERS, DRIVER_LEGACY, DRIVER_SOURCES
    from .repository import install_drivers

    if os.path.exists(os.path.join(USER_FOLDER)) and not os.path.exists(DRIVERS):
        os.mkdir(DRIVERS)
        print(f"The new driver directory has been created: {DRIVERS}")

        # Inside os.path.exists(DRIVERS) condition to avoid moving drivers from current repo everytime autolab is started
        if os.path.exists(DRIVER_LEGACY['official']):
            shutil.move(DRIVER_LEGACY['official'], DRIVERS)
            os.rename(os.path.join(DRIVERS, os.path.basename(DRIVER_LEGACY['official'])),
                      DRIVER_SOURCES['official'])
            print(f"Old official drivers directory has been moved from: {DRIVER_LEGACY['official']} to: {DRIVER_SOURCES['official']}")
            install_drivers()  # Ask if want to download official drivers

        if os.path.exists(DRIVER_LEGACY["local"]):
            shutil.move(DRIVER_LEGACY['local'], DRIVERS)
            os.rename(os.path.join(DRIVERS, os.path.basename(DRIVER_LEGACY['local'])),
                      DRIVER_SOURCES['local'])
            print(f"Old local drivers directory has been moved from: {DRIVER_LEGACY['local']} to: {DRIVER_SOURCES['local']}")
