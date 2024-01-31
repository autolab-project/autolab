# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 18:16:20 2023

@author: Jonathan
"""

import os
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
    try:
        import requests
        from tqdm import tqdm
    except:
        print("Package tqdm or requests not found, can't display download progression")
        print(f"Downloading {url}")
        import urllib.request
        with urllib.request.urlopen(url) as github_repo_zip:
            with open(output_dir, 'wb') as repo_zip:
                repo_zip.write(github_repo_zip.read())
    else:
        """https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests"""
        # Streaming, so we can iterate over the response.
        response = requests.get(url, stream=True)

        # Sizes in bytes.
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024

        with tqdm(total=total_size, unit="B", unit_scale=True,
                  desc=f"Downloading {url}") as progress_bar:
            with open(output_dir, "wb") as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)

        if total_size != 0 and progress_bar.n != total_size:
            raise RuntimeError("Could not download file")


def _unzip_repo(repo_zip: str, output_dir: str):
    """ Unzip repo_zip to output_dir using a temporary folder"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    temp_dir = tempfile.mkdtemp()
    try:
        from tqdm import tqdm
    except:
        print("Package tqdm not found, can't display progression")
        with zipfile.ZipFile(repo_zip, 'r') as zip_open:
            repo_name = zip_open.namelist()[0][:-1]
            print(f'Extracting {repo_name}')
            zip_open.extractall(temp_dir)

        temp_unzip_repo = os.path.join(temp_dir, repo_name)
        print(f'Moving drivers to {output_dir}')
        for filename in os.listdir(temp_unzip_repo):
            _copy_move(temp_unzip_repo, filename, output_dir)
    else:
        """https://stackoverflow.com/questions/4341584/extract-zipfile-using-python-display-progress-percentage"""
        with zipfile.ZipFile(repo_zip, 'r') as zf:
            repo_name = str(zf.namelist()[0])[:-1]
            for member in tqdm(zf.infolist(),
                               desc=f'Extracting {repo_name}'):
                zf.extract(member, temp_dir)

        temp_unzip_repo = os.path.join(temp_dir, repo_name)
        for filename in tqdm(os.listdir(temp_unzip_repo),
                             desc=f'Moving drivers to {output_dir}'):
            _copy_move(temp_unzip_repo, filename, output_dir)

    os.rmdir(temp_unzip_repo)
    os.rmdir(temp_dir)


def _copy_move(temp_unzip_repo, filename, output_dir):
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


def install_drivers(*github_url: str, skip_input=False):
    """ Ask if want to install drivers from all the given github_url.
    If no argument passed, use the official drivers url. """
    temp_folder = os.environ['TEMP']  # This variable can be changed at autolab start-up
    temp_repo_folder = tempfile.mkdtemp(dir=temp_folder)

    list_github_url = list(github_url) if len(github_url) != 0 else paths.DRIVER_GITHUB.values()

    for github_repo_url in list_github_url:
        github_repo_zip_url = _format_url(github_repo_url)
        repo_name = github_repo_url.split(r"github.com/")[1].split("/")[1]
        zip_name = "-".join((repo_name, os.path.basename(github_repo_zip_url)))
        temp_repo_zip = os.path.join(temp_repo_folder, zip_name)

        if skip_input: ans = 'yes'
        else:
            ans = input_wrap(f'Do you want to install all the drivers from {github_repo_url}? [default:yes] > ')

        if ans.strip().lower() == 'no': continue
        else:
            _download_repo(github_repo_zip_url, temp_repo_zip)
            _unzip_repo(temp_repo_zip, paths.DRIVER_SOURCES["official"])
            os.remove(temp_repo_zip)
    os.rmdir(temp_repo_folder)
