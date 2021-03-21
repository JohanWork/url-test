import regex as re
import os
import requests
import argparse
import yaml
import logging
import time
import multiprocessing
from multiprocessing import Pool
from typing import List

requests.adapters.DEFAULT_RETRIES = 1

global file_types
file_types = ['\.md']
global whitelisted_files
whitelisted_files = []
global whitelisted_urls
whitelisted_urls = []


CWD = os.getcwd()

# TODO check a regex that is fine to steal?
urls_regex = """(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"""


def read_configs(config_file: str) -> dict:
    """Function to parse the config file. 

    Args:
        config_file (str): File path to the config file. 

    Returns:
        dict: The configurations in the form of a dict
    """
    if os.path.isfile(config_file):
        with open(config_file, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        if 'file_types' in data:
            file_types = data['file_types']
        if 'whitelisted_files' in data:
            whitelisted_files = data['whitelisted_files']
        if 'whitelisted_urls' in data:
            whitelisted_urls = data['whitelisted_urls']
    else:
        logging.warning('config file could not be found, using defaults')


def extract_urls(file: str, rows: list, file_path: str) -> List[str]:
    """Function to find url:s in a file

    Args:
        file (str): The file name
        rows (list): The number of lines in the file
        file_path (str): The complete file path

    Returns:
        List[str]: List with all the URL:s in a file
    """
    output = []
    for index, row in enumerate(rows):
        if re.search(urls_regex, row):
            output.append({
                'url': re.search(urls_regex, row).group(0),
                'row': index,
                'file': file,
                'file_path': file_path})
    return output


def get_urls() -> List[str]:
    """Function to find

    Returns:
        List[str]: [description]
    """
    start_time = time.time()
    output = []
    for root, dirs, files in os.walk(CWD):
        for file in files:
            if file not in whitelisted_files and re.search("|".join(file_types), file):
                file_path = root + '/' + file
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                urls = extract_urls(file, lines, file_path)
                if len(urls) > 0:
                    output.extend(urls)
    print(f"The time to get all urls: {time.time() - start_time}")
    return output


def extract_404(url: str):
    # TODO if it crahses we should take that as an error link
    errors = {}
    try:
        response = requests.get(url.get('url'))
        if response.status_code == 404:
            errors['output'] = url
        response.close()
    except:
        errors['output'] = url
    return errors.get('output')


def main(crash: bool, config_path: str):
    start_time = time.time()
    # [TODO] fix use configs or defaults for all things
    # replace the had code types for example.
    configs = read_configs(config_path)
    num_cores = multiprocessing.cpu_count()
    print(f"nbr of cores={num_cores}")
    pool = Pool(num_cores)
    # Currently we are first getting all the URL:s
    # Then we are testing them,
    # I think that the testing is super fast but finding the stuff is not
    # I think we should move around the parallism to a lower layer instead.
    # list_of_things = []
    # Get all the links then run a function for each of them
    # This will make it work fine.
    errors = pool.map(extract_404, get_urls())
    errors = [error for error in errors if error != None]
    for error in errors:
        logging.warning(error)
    if crash and errors:
        raise Exception('There are broken urls in the directory')
    print(f"Total run time: {time.time()- start_time}")
