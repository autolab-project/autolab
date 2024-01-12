# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 18:16:20 2023

@author: Jonathan
"""

import os
import urllib.request
import zipfile
import tempfile
import shutil

from . import paths

# Removed the possibility to download drivers individually due to the restriction of Github requests
# Removed the small driver installer GUI made to select which driver to install
# This implementation can be found in commit https://github.com/autolab-project/autolab/tree/98b29fb43c8026f40967e5751ce90ff62132a711


def _format_url(url: str):
    """ Change github repo name to download link """

    if url.endswith(".zip"):
        format_url = url
    else:
        format_url = url if "/tree/" in url else url + "/tree/master"
        format_url = format_url.replace("/tree/", "/archive/refs/heads/")
        format_url += ".zip"
    return format_url


def _download_repo(url: str, output_dir: str):
    with urllib.request.urlopen(url) as github_repo_zip:
        with open(output_dir, 'wb') as repo_zip:
            repo_zip.write(github_repo_zip.read())


def _unzip_repo(repo_zip: str, output_dir: str):
    """ Unzip repo_zip to output_dir using a temporary folder"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    temp_dir = tempfile.mkdtemp()

    with zipfile.ZipFile(repo_zip, 'r') as zip_open:
        repo_name = zip_open.namelist()[0]
        zip_open.extractall(temp_dir)

    temp_unzip_repo = os.path.join(temp_dir, repo_name)

    for filename in os.listdir(temp_unzip_repo):
        temp_file = os.path.join(temp_unzip_repo, filename)
        output_file = os.path.join(output_dir, filename)

        if os.path.isfile(temp_file):
            shutil.copy(temp_file, output_file)
            os.remove(temp_file)
        else:
            try:
                shutil.copytree(temp_file, output_file, dirs_exist_ok=True)  # python >=3.8 only
            except:
                if os.path.exists(output_file):
                    shutil.rmtree(output_file, ignore_errors=True)
                shutil.copytree(temp_file, output_file)

            shutil.rmtree(temp_file, ignore_errors=True)

    os.rmdir(temp_unzip_repo)
    os.rmdir(temp_dir)


def input_wrap(*args):

    """ Wrap input function to avoid crash with Spyder using Qtconsole=5.3 """

    input_allowed = True
    try:
        import spyder_kernels
        import qtconsole
    except ModuleNotFoundError:
        pass
    else:
        if hasattr(spyder_kernels, "console") and hasattr(qtconsole, "__version__"):
            if qtconsole.__version__.startswith("5.3"):
                print("Warning: Spyder crashes with input() if Qtconsole=5.3, skip user input.")
                input_allowed = False
    if input_allowed:
        ans = input(*args)
    else:
        ans = "yes"

    return ans


def _check_empty_driver_folder():
    if not os.listdir(paths.DRIVER_SOURCES['official']):
        print(f"No drivers found in {paths.DRIVER_SOURCES['official']}")
        install_drivers()


def install_drivers(*github_url: str):
    """ Ask if want to install drivers from all the given github_url.
    If no argument passed, use the official drivers url. """
    temp_folder = os.environ['TEMP']  # This variable can be changed at autolab start-up
    temp_repo_folder = tempfile.mkdtemp(dir=temp_folder)

    if len(github_url) != 0:
        list_github_url = list(github_url)
    else:
        list_github_url = paths.DRIVER_GITHUB.values()

    for github_repo_url in list_github_url:
        github_repo_zip_url = _format_url(github_repo_url)
        repo_name = github_repo_url.split(r"github.com/")[1].split("/")[1]
        zip_name = "-".join((repo_name, os.path.basename(github_repo_zip_url)))
        temp_repo_zip = os.path.join(temp_repo_folder, zip_name)

        ans = input_wrap(f'Do you want to install all the drivers from {github_repo_url}? [default:yes] > ')
        if ans.strip().lower() == 'no':
            continue
        else:
            print(f"Downloading {github_repo_zip_url}")
            _download_repo(github_repo_zip_url, temp_repo_zip)
            print(f'Moving drivers to {paths.DRIVER_SOURCES["official"]}')
            _unzip_repo(temp_repo_zip, paths.DRIVER_SOURCES["official"])
            os.remove(temp_repo_zip)
    os.rmdir(temp_repo_folder)
