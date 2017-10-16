#coding=utf-8
import pymysql

db = pymysql.connect(host='140.118.70.162', user='jobguide',
                port=13306, password='zNW3hw1HjMsQvOc9',
                db='jobguide', charset='utf8')
cursor = db.cursor()

#insert company list into company_list
company_list = []
index = 0
sql="SELECT corporation FROM ptt_corporation_rank"
cursor.execute(sql)
result = cursor.fetchall()
for each in result:
    company_list.insert(index, each[0])
    index += 1

#calculate
sql = "UPDATE ptt_corporation_rank SET rank = %s WHERE id = %s"
for i in range(2000, len(company_list)):
    cursor.execute("SELECT ranking, c.article_id FROM ptt_comments c, ptt_articles a WHERE (c.article_id = a.id) and a.content LIKE %s", ("%" + company_list[i] + "%"))
    rs = cursor.fetchall()
    temp = 0
    for row in rs:
        temp += row[0]
    cursor.execute(sql,(temp, i+1))

db.commit()
cursor.close()
db.close()
