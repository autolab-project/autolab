# -*- coding: utf-8 -*-


def process_all_changes() :

    ''' Apply all changes '''

    rename_old_devices_config_file()


def rename_old_devices_config_file() :

    ''' Rename local_config.ini into devices_config.ini'''

    from .paths import USER_FOLDER
    if os.path.exists(os.path.join(USER_FOLDER,'local_config.ini')) :
        os.path.rename(os.path.join(USER_FOLDER,'local_config.ini'),
                        os.path.join(USER_FOLDER,'devices_config.ini'))
