import logging
import os
import requests
import utils
import logger_helper
import json

version_hash = utils.try_get_version_hash()

logger = logger_helper.get_logger(logging.DEBUG)
session = requests.Session()

METADATA_TEMPLATE = utils.get_b64_data(b'aHR0cHM6Ly95b3N0YXItc2VydmVyaW5mby5ibHVlYXJjaGl2ZXlvc3Rhci5jb20ve30uanNvbg==')
A_PACKAGE_CATALOG_TEMPLATE = utils.get_b64_data(b'e30vQW5kcm9pZC9idW5kbGVEb3dubG9hZEluZm8uanNvbg==')
A_PACKAGE_BASE_TEMPLATE = utils.get_b64_data(b'e30vQW5kcm9pZC8=')
I_PACKAGE_CATALOG_TEMPLATE = utils.get_b64_data(b'e30vaU9TL2J1bmRsZURvd25sb2FkSW5mby5qc29u')
I_PACKAGE_BASE_TEMPLATE = utils.get_b64_data(b'e30vaU9TLw==')
BINARY_CATALOG_TEMPLATE = utils.get_b64_data(b'e30vTWVkaWFSZXNvdXJjZXMvTWVkaWFDYXRhbG9nLmpzb24=')
BINARY_BASE_TEMPLATE = utils.get_b64_data(b'e30vTWVkaWFSZXNvdXJjZXMv')
DATA_CATALOG_TEMPLATE = utils.get_b64_data(b'e30vVGFibGVCdW5kbGVzL1RhYmxlQ2F0YWxvZy5qc29u')
DATA_BASE_TEMPLATE = utils.get_b64_data(b'e30vVGFibGVCdW5kbGVzLw==')

logger.debug(METADATA_TEMPLATE)
logger.debug(A_PACKAGE_CATALOG_TEMPLATE)
logger.debug(A_PACKAGE_BASE_TEMPLATE)
logger.debug(I_PACKAGE_CATALOG_TEMPLATE)
logger.debug(I_PACKAGE_BASE_TEMPLATE)
logger.debug(BINARY_CATALOG_TEMPLATE)
logger.debug(BINARY_BASE_TEMPLATE)
logger.debug(DATA_CATALOG_TEMPLATE)
logger.debug(DATA_BASE_TEMPLATE)

RAW_BASE_PATH = os.path.join(os.path.dirname(__file__), 'raw', version_hash)
PACKAGE_FILES_DIR = os.path.join(RAW_BASE_PATH, 'packages')
BINARY_FILES_DIR = os.path.join(RAW_BASE_PATH, 'binary')
DATA_FILES_DIR = os.path.join(RAW_BASE_PATH, 'data')
CATALOG_FILES_DIR = os.path.join(RAW_BASE_PATH, 'catalogs')
dirs = [PACKAGE_FILES_DIR, BINARY_FILES_DIR, DATA_FILES_DIR, CATALOG_FILES_DIR]
for d in dirs:
    os.makedirs(d, exist_ok=True)


def collect_package_files():
    pass


def collect_binary_files():
    pass


def collect_data_files():
    pass


def collect_all_catalogs():
    # collect main catalog
    catalog_json = requests.get(METADATA_TEMPLATE.format(version_hash)).json()
    with open(os.path.join(CATALOG_FILES_DIR, 'main-catalog.json'), 'w') as catalog_file:
        catalog_file.write(json.dumps(catalog_json, indent=4))
        logger.info('main catalog collected.')
    # with open(os.path.join(RAW_BASE_PATH, 'main-catalog.json'), 'r') as f:
    #     catalog_json = json.load(f)
    data_base = utils.get_base_from_json(catalog_json)
    # logger.info(data_base)

    # collect child catalogs
    package_catalog_json = requests.get(A_PACKAGE_CATALOG_TEMPLATE.format(data_base)).json()
    with open(os.path.join(CATALOG_FILES_DIR, 'package-catalog.json'), 'w') as package_catalog_file:
        package_catalog_file.write(json.dumps(package_catalog_json, indent=4))
        logger.info('package file catalog collected.')
    binary_catalog_json = requests.get(BINARY_CATALOG_TEMPLATE.format(data_base)).json()
    with open(os.path.join(CATALOG_FILES_DIR, 'binary-catalog.json'), 'w') as binary_catalog_file:
        binary_catalog_file.write(json.dumps(binary_catalog_json, indent=4))
        logger.info('binary file catalog collected.')
    data_catalog_json = requests.get(DATA_CATALOG_TEMPLATE.format(data_base)).json()
    with open(os.path.join(CATALOG_FILES_DIR, 'data-catalog.json'), 'w') as data_catalog_file:
        data_catalog_file.write(json.dumps(data_catalog_json, indent=4))
        logger.info('data file catalog collected.')

    collect_package_files()
    collect_binary_files()
    collect_data_files()


if version_hash:
    collect_all_catalogs()
else:
    logger.error('please set version hash first.')
