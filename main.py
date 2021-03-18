import regex as re
import os
import requests
import argparse
files = []
types = ['\.py', '\.md']
cwd = os.getcwd()
# TODO check a regex that is fine to steal?
urls_regex = '(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'


def extract_urls(file: str, rows: list, dirs: str) -> list:
    output = []
    for index, row in enumerate(rows):
        if re.search(urls_regex, row):
            output.append({'url': re.search(urls_regex, row).group(
                0), 'row': index, 'file': file, 'dirs': dirs})
    return output


def get_urls():
    output = []
    for root, dirs, files in os.walk(cwd):
        for file in files:
            if re.search("|".join(types), file):
                with open(root+'/'+file, 'r') as f:
                    lines = f.readlines()
                urls = extract_urls(file, lines, dirs)
                if urls != []:
                    output.append(urls[0])
    return output


def extract_404(urls):
    errors = {}
    for url in urls:
        try:
            r = requests.get(url.get('url'))
            if r.status_code == 404:
                errors[url.get('url'))]=url
        except:
            errors[url.get('url'))]=url

    return errors


def main(crash: bool=False):
    urls=get_urls()
    errors=extract_404(urls)
    if crash and len(errors) > 0:
        raise Exception("The directory contains broken links")
    logging.warrning('Following errors was found in the directory')
    logging.warrning(errors)



if __name__ == "__main__":

    arg_parser=argparse.ArgumentParser(
        description='check all links in spec file types in the directory')
    arg_parser.add_argument('-crash', '--crash', required=False,
                            help='crash if any broken links are found')
    args=vars(arg_parser.parse_args())
    main(args['crash'])
