import regex as re
import os
import requests
import argparse
import yaml
import logging
import multiprocessing
from multiprocessing import Pool
files = []
types = ['\.py', '\.md']
types = ['\.md']

CWD = os.getcwd()

# TODO check a regex that is fine to steal?
urls_regex = """(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"""


def read_configs(config_file: str):
    configs = None
    try:
        if os.path.isfile(config_file):
            with open('config_file', 'r') as f:
                configs = yaml.load(f, Loader=yaml.FullLoader)
        else:
            logging.warning('congfig file could not be opend')
    except:
        logging.info('no config file is used')
    return configs


def extract_urls(file: str, rows: list, dirs: str) -> list:
    output = []
    for index, row in enumerate(rows):
        if re.search(urls_regex, row):
            output.append({'url': re.search(urls_regex, row).group(
                0), 'row': index, 'file': file, 'dirs': dirs})
    return output


def get_urls():
    output = []
    for root, dirs, files in os.walk(CWD):
        for file in files:
            if re.search("|".join(types), file):
                # TODO fix this
                try:
                    with open(root+'/'+file, 'r') as f:
                        lines = f.readlines()
                    urls = extract_urls(file, lines, dirs)
                    if urls != []:
                        output.append(urls[0])
                except:
                    pass
    return output


def extract_404(url):
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


def get_urls_extract_404(crash: bool, config_path: str):
    configs = read_configs(config_path)
    urls = get_urls()
    return urls


def main(crash: bool = False, directory: str = None, config_path: str = '',):
    if directory:
        CWD = directory

    num_cores = multiprocessing.cpu_count()
    print(f"num_cores={num_cores}")
    pool = Pool(num_cores)
    errors = pool.map(extract_404, get_urls_extract_404(crash, config_path))
    errors = [error for error in errors if error != None]
    if crash and len(errors) > 0:
        raise Exception("The directory contains broken links")
    for error in errors:
        logging.warning(error)
    if crash and errors:
        raise Exception('There are broken urls in the directory')


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        description='check all links in spec file types in the directory')
    arg_parser.add_argument('-crash', '--crash', required=False,
                            help='crash if any broken links are found')
    arg_parser.add_argument('-config_path', '--config_path', required=False,
                            help='path to config file')
    args = vars(arg_parser.parse_args())
    main(args['crash'], args['config_path'])
