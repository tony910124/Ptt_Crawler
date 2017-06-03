import os
import re
import time
import json
import pymysql
import requests
from os.path import isfile, join
from os import sep
from shutil import copyfile
import Config


db = pymysql.connect(host=Config.DB_HOST, user=Config.DB_USER,
        port=Config.DB_PORT, password=Config.DB_PASSWD,
        db=Config.DB_NAME, charset='utf8')

cursor = db.cursor()

sql = "INSERT INTO ptt_articles(title, author, board, content, date, ip, article_uuid) VALUES (%s, %s, %s, %s, %s, %s, %s)"
sql_print = "INSERT INTO ptt_articles(title) VALUES(%s)"
PTT_BOARD = 'part-time'
BACKUP_PATH = Config.BACKUP_PATH
TMP_PATH = Config.TMP_PATH

EXECUTE_CRAWLER = True
IMPORT_CHECK_EXISTED = True
BACKUP_DATA = False

def main():
        if EXECUTE_CRAWLER:
                # Clear tmp directory
                tmpFiles = [join(TMP_PATH,f) for f in os.listdir(TMP_PATH) if isfile(join(TMP_PATH, f))]
                for file in tmpFiles:
                        print TMP_PATH
                        os.remove(file)

                firstPage = 1
                print "Start from page %d" % (firstPage)
                doCrawler(firstPage, -1)
                import2SQL(IMPORT_CHECK_EXISTED)

                #print "Last page number is %d" % (int(Util.readKV('part_time_lastPage')))

        print "Finished."

def doCrawler(pageStart, pageEnd):
        command = "cd %s && python ../pttcrawler.py -b %s -i %d %d" % (os.path.basename(TMP_PATH), PTT_BOARD, pageStart, pageEnd)
        #command = "python pttcrawler.py -b %s -i %d %d" % (PTT_BOARD, pageStart, pageEnd)
        print command
        os.system(command)

        # Modify JSON Format
        regex = re.compile(".+-[0-9]+\.json")
        jsonFiles = [f for f in os.listdir(TMP_PATH) if isfile(join(TMP_PATH, f)) and regex.match(f)]
        for filename in jsonFiles:
                fullPath = join(TMP_PATH, filename)
                file = open(fullPath, 'r')
                lines = file.readlines()
                lines[0] = '[\n'
                lines[len(lines) - 1] = ']'
                file.close()

                newFilename = "%s_%d_parsed.json" % (filename[:-5], int(time.time()))
                newFullpath = join(TMP_PATH, newFilename)
                file = open(newFullpath, 'w')
                file.writelines(lines)
                file.close()
                if BACKUP_DATA:
                        copyfile(newFullpath, join(BACKUP_PATH, newFilename))
                os.remove(fullPath)

def import2SQL(checkExsisted):
        regex = re.compile(r".+_[0-9]+_parsed\.json")
        jsonFiles = [f for f in os.listdir(TMP_PATH) if isfile(join(TMP_PATH, f)) and regex.match(f)]
        regex = re.compile(r"[0-9]+")
        #tmpCollectionName = DbHelper.COLLECTION + "_tmp"

        for filename in jsonFiles:
                fullPath = join(TMP_PATH, filename)
                temp = json.load(open(fullPath))
                for data in temp:
                    cursor.execute(sql, (data['article_title'],
                         data['author'],
                         data['board'],
                         data['content'],
                         format_date(data['date']),
                         data['ip'],
                         data['article_id'] ))
                    print sql_print % (data['article_title'])
                os.remove(fullPath)
        db.commit()

def format_date(datetime):
    if datetime == '':
        return None
    temp = datetime.split(' ')
    format_datetime = '%s-%s-%s %s' %(temp[4], month(temp[1]), temp[2], temp[3])
    return format_datetime

def month(month):
    return{
        'Jan' : '01',
        'Feb' : '02',
        'Mar' : '03',
        'Apr' : '04',
        'May' : '05',
        'Jun' : '06',
        'Jul' : '07',
        'Aug' : '08',
        'Sep' : '09',
        'Oct' : '10',
        'Nov' : '11',
        'Dec' : '12'
    }[month]
    """
        if checkExsisted:
                global dbCollection
                dbCollection = DbHelper.connectMongoCollection()
                tmpCollection = DbHelper.connectMongoCollection(tmpCollectionName)
                tmpDocs = tmpCollection.find({})
                for tmpDoc in tmpDocs:
                        if (dbCollection.find({'article_id': tmpDoc['article_id']}).count() == 0):
                                dbCollection.insert_one(tmpDoc)
                                print "Import article %s on first page." % (tmpDoc['article_id'])
                        else:
                                print "Article %s existed." % (tmpDoc['article_id'])
                tmpCollection.drop()
    """
if __name__ == "__main__":
        main()
