import sqlite3
import logger_helper
import utils
import os

logger = logger_helper.get_logger()


def create_database():
    # generate sqlite file
    con = sqlite3.connect(utils.DATABASE_NAME)
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS table_dict')
    cur.execute('''CREATE TABLE table_dict
    (
        FILE_ID         INTEGER     PRIMARY KEY     NOT NULL,
        FILE_FULL_PATH  TEXT        NOT NULL,
        SIZE            INT         NOT NULL,
        CRC             INT         NOT NULL,
        FILE_NAME       TEXT        NOT NULL,
        UPDATE_TIME     CHAR(20)    NOT NULL,
        VERSION_MARK    CHAR(30)    NOT NULL 
    );''')
    cur.execute('DROP TABLE IF EXISTS binary_dict')
    cur.execute('''CREATE TABLE binary_dict
    (
        FILE_ID             INTEGER     PRIMARY KEY     NOT NULL,
        FILE_FULL_PATH      TEXT        NOT NULL,
        SOURCE_FILE_PATH    TEXT        NOT NULL,
        SIZE                INT         NOT NULL,
        CRC                 INT         NOT NULL,
        BYTES               INT         NOT NULL,
        MIDIA_TYPE          INT         NOT NULL,
        FILE_NAME           TEXT        NOT NULL,
        UPDATE_TIME         CHAR(20)    NOT NULL,
        VERSION_MARK        CHAR(30)    NOT NULL 
    );''')
    cur.execute('DROP TABLE IF EXISTS bundle_dict')
    cur.execute('''CREATE TABLE bundle_dict
    (
        FILE_ID         INTEGER     PRIMARY KEY     NOT NULL,
        FILE_FULL_PATH  TEXT        NOT NULL,
        SIZE            INT         NOT NULL,
        CRC             INT         NOT NULL,
        FILE_NAME       TEXT        NOT NULL,
        UPDATE_TIME     CHAR(20)    NOT NULL,
        VERSION_MARK    CHAR(30)    NOT NULL 
    );''')
    cur.execute('DROP TABLE IF EXISTS catalog_dict')
    cur.execute('''CREATE TABLE catalog_dict
    (
        CATALOG_ID          INTEGER                                                         PRIMARY KEY     NOT NULL,
        CATALOG_TYPE        TEXT CHECK( CATALOG_TYPE IN ('BIN', 'BUN', 'TABLE', 'MAIN') )   NOT NULL,
        CATALOG_FULL_PATH   TEXT                                                            NOT NULL,
        CATALOG_MD5         TEXT                                                            NOT NULL,
        UPDATE_TIME         CHAR(20)                                                        NOT NULL,
        VERSION_MARK        CHAR(30)                                                        NOT NULL 
    );''')
    con.commit()
    con.close()


def create_version_hash_file():
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


def create_struct_dir():
    struct_dir = os.path.join(os.path.dirname(__file__), 'table_struct')
    os.makedirs(struct_dir)
    with open(os.path.join(struct_dir), 'dump.cs') as dump_file:
        dump_file.write(' ')


create_database()
create_version_hash_file()
create_struct_dir()
