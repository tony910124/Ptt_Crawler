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



sql_update = "UPDATE ptt_articles SET year = %s WHERE article_uuid = %s"
sql_update_print = "UPDATE ptt_articles SET year = %s WHERE article_uuid = %s"



sql = "INSERT INTO ptt_articles(title, author, board, content, year, month, ip, article_uuid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
sql_print = "INSERT INTO ptt_articles(title) VALUES(%s)"
PTT_BOARD = 'job'
BACKUP_PATH = Config.BACKUP_PATH
TMP_PATH = Config.TMP_PATH

EXECUTE_CRAWLER = True
IMPORT_CHECK_EXISTED = True
BACKUP_DATA = True

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
                doAnalyze()
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
                #os.remove(fullPath)

def doAnalyze():
    command = "cd %s && python ../S03_AnalysisContent.py" % (os.path.basename(TMP_PATH))
    print TMP_PATH
    #command = "python pttcrawler.py -b %s -i %d %d" % (PTT_BOARD, pageStart, pageEnd)
    print command
    os.system(command)


def import2SQL(checkExsisted):
        db = pymysql.connect(host=Config.DB_HOST, user=Config.DB_USER,
                port=Config.DB_PORT, password=Config.DB_PASSWD,
                db=Config.DB_NAME, charset='utf8')

        cursor = db.cursor()
        regex = re.compile(r".+_[0-9]+_parsed\.json")
        jsonFiles = [f for f in os.listdir(TMP_PATH) if isfile(join(TMP_PATH, f)) and regex.match(f)]
        print jsonFiles

        #tmpCollectionName = DbHelper.COLLECTION + "_tmp"

        for filename in jsonFiles:
                fullPath = join(TMP_PATH, filename)
                temp = json.load(open(fullPath))
                for data in temp:
                    if 'error' in data:
                        print 'error'
                    else:
                        #print data
                        date = format_date(data['date'])
                        
                        #IMPORT TO SERVER
                        
                        #year = 'NULL' if date == None else date[4]
                        #month = 'NULL' if date == None else month(date[1]) 
                        cursor.execute(sql, (data['article_title'],
                             data['author'],
                             data['board'],
                             data['content'],
                             None if date == None else None if date == None or len(date[-1]) > 4 else date[-1],
                             None if date == None else month(date[1]),
                             data['ip'],
                             data['article_id'] ))
                        print sql_print % (data['article_title'])
                        
                        """
                        #UPDATE TO SERVER
                        cursor.execute(sql_update, (None if date == None or len(date[-1]) > 4 else date[-1], data['article_id']))
                        print sql_update_print % (None if date == None or len(date[-1]) > 4 else date[-1], data['article_id'])
                        """
                os.remove(fullPath)
        db.commit()
        db.close()

def format_date(datetime):
    if datetime == '':
        return None
    temp = datetime.split(' ')
    if '' in temp:
        temp.remove('')

    #format_datetime = '%s-%s-%s %s' %(temp[4], month(temp[1]), temp[2], temp[3])
    return temp

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
