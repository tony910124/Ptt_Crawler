#coding=utf-8
import sys
sys.path.append('../src')
import testing
import pymysql

testing.load_training_data('../model/','../dict/ntusd-full.dic')
db = pymysql.connect(host='140.118.70.162', user='jobguide',
                port=13306, password='zNW3hw1HjMsQvOc9',
                db='jobguide', charset='utf8')

checkSql = "show full processlist"
sql = "SELECT id, push_content FROM ptt_comments"
cursor = db.cursor()
cursor.execute(sql)
rs = cursor.fetchall()
for row in rs:
    result = testing.test_sentance(row[1])
    if result['pos'] > result['neg']:
        temp = result['pos']
    elif result['neg'] > result['pos']:
       temp = result['neg'] * -1
    else:
        temp = 0.0
    cursor.execute("UPDATE ptt_comments SET ranking = %s WHERE id = %s", (temp, row[0]))

db.commit()
cursor.close()
db.close()
