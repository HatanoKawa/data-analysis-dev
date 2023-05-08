import sqlite3
import logger_helper
import utils
import os

logger = logger_helper.get_logger()

# check if database exists
if not os.path.exists(os.path.join(os.path.dirname(__file__), 'file-database')):
    # generate sqlite file
    logger.info('database file doesn\'t exist, an empty database file will be generated.')
    con = sqlite3.connect('file-database')
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS file_dict')
    cur.execute('''CREATE TABLE file_dict
    (
        FILE_ID         INT         PRIMARY KEY     NOT NULL,
        SOURCE_PATH     TEXT        NOT NULL,
        CRC             TEXT        NOT NULL,
        UPDATE_TIME     CHAR(20)    NOT NULL,
        VERSION_MARK    CHAR(30)    NOT NULL 
    );''')
    con.commit()
    con.close()
else:
    logger.info('sqlite database file already exists, skip generating database file.')


# check if version_hash file exists and if it's valid
if os.path.exists(os.path.join(os.path.dirname(__file__), 'version_hash')):
    # check version file
    logger.info('version_hash file detected.')
    utils.try_get_version_hash()
else:
    logger.info('version_hash file doesn\'t exist, an example file will be generated.')
    with open(os.path.join(os.path.dirname(__file__), 'version_hash'), 'w') as version_hash_file:
        version_hash_file.write('r' + ''.join(['0' for x in range(2)]) + '_' + ''.join(['x' for x in range(20)]))
        version_hash_file.close()

