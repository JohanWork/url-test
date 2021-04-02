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

CWD = os.getcwd()

# TODO check a regex that is fine to steal?


def read_configs(config_file: str) -> dict:
    """Function to parse the config file. 

    Args:
        config_file (str): File path to the config file. 

    Returns:
        dict: The configurations in the form of a dict
    """
    file_types = ['\.md']
    whitelisted_files = []
    whitelisted_urls = []
    url_regex = """(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"""
    if config_file and os.path.isfile(config_file):
        with open(config_file, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        if 'file_types' in data:
            file_types = data['file_types']
            logging.info('file_types')
            logging.info(file_types)
        if 'whitelisted_files' in data:
            whitelisted_files = data['whitelisted_files']
        if 'whitelisted_urls' in data:
            whitelisted_urls = data['whitelisted_urls']
        if 'url_regex' in data:
            url_regex = data['url_regex']

    else:
        logging.warning('config file could not be found, using defaults')
    return {'file_types': file_types, 'whitelisted_files': whitelisted_files, 'whitelisted_urls': whitelisted_urls, 'url_regex': url_regex}


def extract_urls(file: str, rows: list, file_path: str, urls_regex: str) -> List[str]:
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
            url = re.search(urls_regex, row).group(0)
            logging.info('address found: {}'.format(url))
            output.append({
                'url': url,
                'row': index,
                'file': file,
                'file_path': file_path})
    return output


def get_urls(configs: dict) -> List[str]:
    """Function to find

    Returns:
        List[str]: [description]
    """
    start_time = time.time()
    output = []
    whitelisted_files = configs.get('whitelisted_files')
    urls_regex = configs.get('url_regex')
    file_types = configs.get('file_types')
    for root, dirs, files in os.walk(CWD):
        for file in files:
            if file not in whitelisted_files and re.search("|".join(file_types), file):
                file_path = root + '/' + file
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                urls = extract_urls(file, lines, file_path, urls_regex)
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
            logging.info('404 on url {}'.format(url))
            errors['output'] = url
        response.close()
    except:
        errors['output'] = url
    return errors.get('output')


def main(crash: bool, config_path: str, verbose: bool):
    start_time = time.time()
    # [TODO] fix use configs or defaults for all things
    # replace the had code types for example.
    if verbose:
        logging.basicConfig(level=logging.INFO)

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
    errors = pool.map(extract_404, get_urls(configs))
    errors = [error for error in errors if error != None]
    for error in errors:
        logging.warning(error)
    if crash and errors:
        raise Exception('There are broken urls in the directory')
    print(f"Total run time: {time.time()- start_time}")
