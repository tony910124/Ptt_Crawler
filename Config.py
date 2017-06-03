import os

scriptPath = os.path.dirname(os.path.realpath(__file__))

DB_HOST = '140.118.70.162'
DB_USER = 'jobguide'
DB_PASSWD = 'zNW3hw1HjMsQvOc9'
DB_NAME = 'jobguide'
DB_PORT = 13306

DB = 'workfair-jobrobot'
COLLECTION = 'ptt_part_times'
BACKUP_PATH = '%s/RawData' % scriptPath
TMP_PATH = '%s/tmp' % scriptPath
