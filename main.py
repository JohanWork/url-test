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

files = []
types = ['\.py', '\.md']
types = ['\.md']

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
    print(config_file)
    if os.path.isfile(config_file):
        with open(config_file, 'r') as f:
            return  yaml.load(f, Loader=yaml.FullLoader)
    else:
        logging.warning('config file could not be found, using defaults')


def extract_urls(rows: list, file_path: str) -> List[str]:
    """Function to find url:s in a file

    Args:
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
                'file_path': file_path})
    return output


def get_urls() -> List[str]:
    """Function to find

    Returns:
        List[str]: [description]
    """
    output = []
    start_time = time.time()
    for root, dirs, files in os.walk(CWD):
        for file in files:
            if re.search("|".join(types), file):
                file_path = root + '/' + file
                output.append(file_path)
    print(f"Time to get all files: {time.time()- start_time}")
    return output


def extract_404(file_path: str):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    urls = extract_urls(lines, file_path)
    output = []
    for url in urls: 
        try:
            response = requests.get(url.get('url'))
            if response.status_code == 404:
                output.append(url)
            response.close()
        except: # TODO if it crash we should take that as an error link
            output.append(url)
    return output


def main(crash: bool, directory: str, config_path: str):
    start_time = time.time()
    if directory:
        CWD = directory
    #[TODO] fix use configs or defaults for all things
    # replace the had code types for example. 
    #configs = read_configs(config_path)
    num_cores = max(multiprocessing.cpu_count()-1, 1)
    print(f"Nbr of cores used: {num_cores}")
    pool = Pool(num_cores)
    errors = pool.map(extract_404, get_urls())
    errors = [error for error in errors if len(error)>0]
    for error in errors:
        logging.warning(error)
    if crash and errors:
        raise Exception('There are broken urls in the directory')
    print(f"Total run time: {time.time() - start_time }")
