# url-test

url-test is a Python module for scaning all url in a project distributed under the MIT license.

The project was started in 2021 by Johan Hansson and Niklas Hansson.

## Installation

### Dependencies

- pyyaml
- regex
- PyYAML

### User installation

pip install -U url-test

## Source code

git clone https://github.com/JohanWork/url-test

## How to use

To run it in you comand line type

```mysql

url-test

```

There are three diffrent input that can be stated to utl-test

- -config_path file to configurations se more blow.
- -verbose if more exstenstive logging is wanted
- -crash if the package should raise an exseption if any 404 are found

There are a number of configuration options possibale by providing a path to a yaml config file.

```python

url-test -config_path config.yaml

```

- url_regex -> customize the regex experesions used to find all url.
- file_types -> what type of file do you want to scan. By default it will only scan .md
- whitelisted_files -> white listed file we don't want to scan.
- whitelisted_urls -> white listed url we don't want to check for exampole https://127.0.0.1/test

A example of a confige file can be found in [config.yaml]() and could be somthing like below:

```yanl

file_types:
  - \.md

whitelisted_files:
  - README.md

whitelisted_urls:
  - https://127.0.0.1/test

```

## Github action

A prebuild github action of the library can be found [here](https://github.com/JohanWork/url-test-github-action).
