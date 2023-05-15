import datetime
import json
import re
import os
import base64
import sqlite3
import requests
import logger_helper

logger = logger_helper.get_logger()
DATABASE_NAME = 'file-database'


def try_get_version_hash():
    # check version file
    with open(os.path.join(os.path.dirname(__file__), 'version_hash')) as version_hash_file:
        version_hash = version_hash_file.readlines()[0].strip()
        match_res = re.match(r'^r[0-9]{2}_[a-zA-Z0-9]{20}$', version_hash)
        if not match_res:
            logger.error('version string is invalid, please check version_hash file')
            return ''
        else:
            logger.info('version string is valid.')
            return version_hash


def get_b64_data(source_str: bytes):
    return base64.b64decode(source_str).decode('utf-8')


def get_base_from_json(json_data: dict):
    td = json_data[[x for x in json_data][0]][0]
    tk = [x for x in td]
    tk.sort()
    td = td[[x for x in tk][-3]][-1]
    tk = [x for x in td]
    tk.sort()
    return td[[x for x in tk][-2]]


def get_cur_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_json_from_file(file_path: str):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    else:
        return None


def get_newest_catalog_local_path(catalog_type: str, cur: sqlite3.Cursor):
    query_res = cur.execute(
        "SELECT CATALOG_FULL_PATH FROM catalog_dict WHERE CATALOG_TYPE=(?) ORDER BY UPDATE_TIME DESC",
        (catalog_type,)
    ).fetchone()
    if not query_res:
        return None
    else:
        return get_json_from_file(query_res[0])


def get_newest_catalog(catalog_type: str, cur: sqlite3.Cursor, catalog_url: str, session: requests.Session, use_local=False):
    catalog_json = None
    catalog_source = 'local'
    if use_local:
        catalog_json = get_newest_catalog_local_path(catalog_type, cur)
    if not catalog_json:
        catalog_source = 'remote'
        catalog_json = session.get(catalog_url).json()
    return catalog_json, catalog_source
