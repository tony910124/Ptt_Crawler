
# -*- coding: utf-8 -*-
import re
import os
import json
import unicodedata
from pprint import pprint

CLEAR_OLD_DATA = False


def main():
        #global dbCollection
        #dbCollection = DbHelper.connectMongoCollection()
        problem_doc = []
        question_doc = []
        city_title = [
            u'^(\[北部\])',
            u'^(\[中部\])',
            u'^(\[南部\])',
            u'^(\[台北\])',
            u'^(\[台中\])',
            u'^(\[高雄\])',
            u'^(\[南投\])',
            u'^(\[北縣\])',
            u'^(\[中市\])',
            u'^(\[高市\])',
            u'^(\[澎湖\])',
            u'^(\[基隆\])',
            u'^(\[彰化\])',
            u'^(\[屏東\])',
            u'^(\[金門\])',
            u'^(\[桃園\])',
            u'^(\[雲林\])',
            u'^(\[宜蘭\])',
            u'^(\[馬祖\])',
            u'^(\[苗栗\])',
            u'^(\[台南\])',
            u'^(\[台東\])',
            u'^(\[海外\])'
        ]

        issue_title = [
            u'黑名',
            u'說明',
            u'惡劣',
            u'分享',
            u'關於',
            u'公告',
            u'注意',
            u'問題',
            u'請益',
            u'請問',
            u'分享',
            u'心得',
            u'建議',
            u'更正聲',
            u'請大家',
            u'道歉啟事'
        ]

        if CLEAR_OLD_DATA:
                dbCollection.update_many(
                        {'extractedInfo': {'$exists': True}},
                        {'$unset': {'extractedInfo':""}}, False)
                print 'All extractedInfo deleted.'
        errorCount = 0
        docs = json.load(open(r'C:\Users\user\Desktop\PTTCrawler\PttJobCrawler\JobRobot_ver.2\JobRobot\tmp\job-1-303.json'))
        print len(docs)
        for i in range(5493, 5494):#len(docs)):
            print 'Now on %dth file' % (i)
            print '-' * 100
            """判斷issue用"""
            error = False
            #print "%s" % docs[i]['article_title']
            try:
                """判斷開頭是否為地區，不是回復或黑名單等等"""
                for regex in city_title:

                    if re.match( regex, docs[i]['article_title']) != None:
                        for issue in issue_title:
                            if issue in docs[i]['article_title']:
                                print '\n\n' + '|*'*50
                                print "\t\t%s - %s" % (docs[i]['article_id'], docs[i]['article_title'])
                                print '|*'*50 + '\n\n'
                                error = True
                                break
                        if error:
                            error = False
                            continue
                        print "%s - %s\n" % (docs[i]['article_id'], docs[i]['article_title'])
                        errorCount += analyzeContent(docs[i])
                        break
            except Exception as e:

                print '|'*30
                if 'error' in docs[i]:
                    print u'error'
                else:
                    print "%s - %s\n" % (docs[i]['article_id'], docs[i]['article_title'])
                print '|'*30

        print "Finished with %d article(s) having error." % (errorCount)
        #for doc in problem_doc:
        #    print doc["article_title"]

def analyzeContent(doc):
        #global dbCollection, regexEmail
        """
        try:
                #print doc
                pprint.pprint(doc)
        except Exception as e:
                print 'error'
        """
        hasError = False
        content = doc['content']
        #print content
        blocksTitle = [
                [u'([\【\[]公司名稱[\】\]])', u'公司名稱\w{0,}[︰：:]'],
                [u'([\【\[]工作職缺[\】\]])', u'工作職缺\w{0,}[︰：:]'],
                [u'([\【\[]工作內容[\】\]])', u'工作內容\w{0,}[︰：:]'],
                [u'([\【\[]徵求條件[\】\]])', u'徵求條件\w{0,}[︰：:]'],
                [u'([\【\[]工作地點[\】\]])', u'工作地點\w{0,}[︰：:]'],
                [u'([\【\[]工作時間[\】\]])', u'工作時間\w{0,}[︰：:]'],
                [u'([\【\[]月\s{0,}休[\】\]])', u'月\s{0,}休\w{0,}[︰：:]'],
                [u'([\【\[]公司福利[\】\]])', u'公司福利\w{0,}[︰：:]'],
                [u'([\【\[]薪資範圍[\】\]])', u'([\【\[]薪資待遇[\】\]])', u'([\【\[]薪資[\】\]])', u'薪資範圍\w{0,}[︰：:]', u'薪資待遇\w{0,}[︰：:]'],
                [u'([\【\[]需求人數[\】\]])', u'需求人數\w{0,}[︰：:]'],
                [u'([\【\[]聯絡人\/連絡方式[\】,\]])', u'[\【\[]聯絡方式[\】\]]', u'聯絡人\/連絡方式\w{0,}[︰：:]'],
                [u'[\【\[]截止日期[\】\]]'],
                [u'([\【\[]其他備註[\】\]])', u'備註\w{0,}[︰：:]'],
                [u'※ 發信站: 批踢踢實業坊\(ptt.cc\)']
        ]

        topics = [
                '【公司名稱】',
                '【工作職缺】',
                '【工作內容】',
                '【徵求條件】',
                '【工作地點】',
                '【工作時間】',
                '【月休】',
                '【公司福利】',
                '【薪資範圍】',
                '【需求人數】',
                '【聯絡人/連絡方式】',
                '【截止日期】',
                '【其他備註】'
        ]

        content = removeUnnecessaryCharacter(content)
        # Seperate text to blocks
        blocks = []
        blankBlocks = []
        tmp = content
        #print content
        foundCount = 0
        for i in range(len(blocksTitle)):
                regResult = None
                for regex in blocksTitle[i]:
                        regResult = re.search(regex, tmp)
                        if regResult != None:
                                foundCount += 1
                                break
                if regResult == None:
                        print "%s: unable to find block: '%s'\n" % (doc['article_id'], blocksTitle[i][0])
                        blankBlocks.append('')
                        hasError = True
                        continue
                if foundCount > 1:
                        #print foundCount
                        #print tmp[:regResult.start()]
                        val = tmp[:regResult.start()].strip()
                        #print blocksTitle[i - 1][0]
                        #print val
                        #print '-------------------------------\n'
                        if len(blocks) == 0 and len(blankBlocks) > 0:
                                blocks = blocks + blankBlocks
                                blankBlocks = []
                        blocks.append(val)
                        if len(blankBlocks) > 0:
                                blocks = blocks + blankBlocks
                                blankBlocks = []

                tmp = tmp[regResult.end():]
        if len(blankBlocks) > 0:
                blocks = blocks + blankBlocks
                blankBlocks = []
        #for block in blocks:
            #print block.encode('utf-8')

        blocks[len(blocks) - 1] = re.sub('--+(.?)+--', "", blocks[len(blocks) - 1])
        blocks = doubleCheck(blocksTitle, blocks)
        
        """
        9/21 coding
        """
        
        print blocks[8].encode('utf-8')
        blocks[8] = analyzeSalary(blocks[8])
        print blocks[8]

        #extractedInfo = {}
        #print len(blocks)
        for i in range(len(blocks)):
                try:
                    if blocks[i] != '':
                            #print '\tNow on %d block' % (i)
                            #print len(blocks[i])
                            if i == 8:
                                if len(blocks[i][0]) > 1:
                                    for salary in blocks[i]:
                                        #print salary
                                        #print 'you got wrong place'
                                        print '%s: %s - %s' % (topics[i], salary[0].encode('utf-8'), salary[1].encode('utf-8'))
                                else:
                                    print '%s: %s' % (topics[i], int(blocks[i][0][0]))
                            else:
                                print '%s: %s' % (topics[i], blocks[i].encode('utf-8'))
                                ##extractedInfo[topics[i]] = blocks[i]
                            print "-"*30
                except Exception as e:
                    print 'error'
        return hasError
        # Write back
        #f = open('test.txt', 'w')
        #f.write(extractedInfo)


def doubleCheck(blocksTitle, blocks):

    for block_i in range(len(blocks)):
        for blocksTitle_i in range(len(blocksTitle)):
            for regex in blocksTitle[blocksTitle_i]:
                regResult = re.search(regex, blocks[block_i])
                if regResult != None:
                    try:
                        #if find the A title in A title block then break
                        if blocksTitle_i == block_i:
                            break
                        if blocks[blocksTitle_i] == '':
                            val = blocks[block_i][regResult.end():].strip()
                            blocks[block_i] = blocks[block_i][:regResult.start()]
                            blocks[blocksTitle_i] = val
                            return doubleCheck(blocksTitle, blocks)
                        else :
                            blocks[block_i] = blocks[block_i][:regResult.start()]
                    except Exception as e:
                        print blocks[block_i]
                        print 'YUP it\'s break'
    return blocks



def removeUnnecessaryCharacter(content):
    unnecessary = [
            u'job版禁止張貼違反「就業服務法」、「性別平等工作法」、「勞基法」與其他法律之文章發文者已同意一切遵循現行法律，並確知文責自負。本工作確實勞健保!此兩行刪除，文章會被刪除不另通知。※請各位資方配合遵守。',
            u'job版禁止張貼違反「就業服務法」、「性別平等工作法」、「勞基法」與其他法律之文章發文者已同意一切遵循現行法律，並確知文責自負。本工作確實勞健保!!此兩行刪除，文章會被刪除不另通知。※請各位資方配合遵守。',
            u'備註：以上兩行標語刪除，文章會被刪除不另通知。',
            u'※請各位資方配合遵守。',
            u'※人資沒有填寫人資公司名稱將會被刪文。',
            u'※沒有填寫公司名稱將會被刪文。',
            u'※人資沒有填寫人資公司以及原徵人公司(共2公司)名稱將會被刪文。',
            u'※人資沒有填寫人資公司名稱以及原徵人公司(共2公司)將會被刪文。',
            u'※沒有填寫公司名稱將會被刪文; 民意代表請寫民代全名; 個人徵人請寫全名。',
            u'※人資條款: 沒有填寫人資公司名稱以及原徵人公司(共2公司)將會被水桶。',
            u'備註：[約聘]一定要填寫。',
            u'沒有內容會被刪文',
            u'沒有內容 會被刪文!!',
            u'※為保障板友就業機會平等，雇主對求職人或所僱用員工，不得以種族、階級、語言、思想、宗教、黨派、籍貫、出生地、性別、性傾向、年齡、婚姻、容貌、五官、身心障礙或以往工會會員身分為由，予以歧視。',
            u'※為保障板友就業機會平等，雇主對求職人或所僱用員工，不得以種族、階級、語言、思想、宗教、黨派、籍貫、出生地、性別、性傾向、年齡、婚姻、 容貌、五官、身心障礙或以往工會會員身分為由，予以歧視。',
            u'※沒有填寫工作時間將會被刪文。',
            u'備註：一定要填寫清楚 午休時間也請註明。',
            u'※沒有填寫月休或排班制度將會被刪文。',
            u'※沒有填寫月休及排班制度將會被刪文。',
            u'※沒有填寫月休或排班制度 或月休過低將會被刪文。',
            u'※沒有填寫月休及排班制度 或月休過低將會被刪文。',
            u'備註：一定要填寫天數。',
            u'請勿寫勞健保',
            u'勿寫勞健保',
            u'此欄請寫額外的福利',
            u'無勞健保是違法的',
            u'這欄請寫額外福利',
            u'※行政院勞委會於102年4月1日起調漲基本工資為月薪19,047元',
            u'※行政院勞委會於103年7月1日起調漲基本工資為月薪19,273元',
            u'※行政院勞委會於104年7月1日起調漲基本工資為月薪20,008元',
            u'※行政院勞委會於106年1月1日起調漲基本工資為月薪21,009元，',
            u'※行政院勞委會於106年1月1日起調漲基本工資為月薪21,009元',
            u'※行政院勞委會於106年1月1日起調漲基本工資為月薪21,000元',
            u'月薪未達20008元 會被刪文',
            u'月薪未達20008元會被刪文',
            u'月薪未達21009元 會被刪文',
            u'月薪未達21009元會被刪文',
            u'月薪未達21009一樣會被刪文',
            u'月薪未達20008一樣會被刪文',
            u'月薪未達19047一樣會被刪文',
            u'時薪工作請貼Part-Time板',
            u'※無薪資、比照國科會、比照本校規定、面議、電議，薪資不清等水桶一週',
            u'備註：一定要填寫。',
            u'兩週工時超過80小時請寫加班費，一例一休上班也要加班費，沒有寫清楚加班費計算方式，一律刪文 不另通知',
            u'[email protected]/* <![CDATA[ */!function(t,e,r,n,c,a,p){try{t=document.currentScript||function(){for(t=document.getElementsByTagName(\'script\'),e=t.length;e--;)if(t[e].getAttribute(\'data-cfhash\'))return t[e]}();if(t&&(c=t.previousSibling)){p=t.parentNode;if(a=c.getAttribute(\'data-cfemail\')){for(e=\'\',r=\'0x\'+a.substr(0,2)|0,n=2;a.length-n;n+=2)e+=\'%\'+(\'0\'+(\'0x\'+a.substr(n,2)^r).toString(16)).slice(-2);p.replaceChild(document.createTextNode(decodeURIComponent(e)),c)}p.removeChild(t)}}catch(u){}}()/* ]]> */'
    ]
    #縮減上方的regx
    """
    unnecessary_regex = [
        u'(job版+(\s{0,}.+配合遵守\s{0,})+。)',
        u'(※+(\s{0,}為保障+.+予以歧視\s{0,})+。)',
        u'※+(\s{0,}行政院勞委會於\d{3,}年\d{1,}月\d{1,}日起調漲基本工資為月薪\d{2,},\d{2,}元)+。{0,1}',
        u'\s{0,}月薪未達\d{2,},{0,}\d{3,}.+刪文。{0,1}'
    ]
    """
    for i in range(len(unnecessary)):
        content = content.replace(unnecessary[i], '')

    return content

def analyzeSalary(salary_content):
    #print salary_content
    #有的工作有分碩士及學士
    title = [
        [u'博士', u'碩士', u'學士', u'大學', u'專科'],
        [u'有經驗', u'無經驗']
    ]
    salary_type = [
         #xx,xxxx - xx,xxx
        '\d{2,3},\d{3}\s{0,}[-－~～]\s{0,}\d{2,3},\d{3}',
         #ＸＸ,ＸＸＸ － ＸＸ,ＸＸＸ
        u'[０-９]{2,3},[０-９]{3}\s{0,}[-－~～]\s{0,}[０-９]{2,3},[０-９]{3}',
         #xxxxx - xxxxx
        '\d{5,}\s{0,}[-－~～]\s{0,}\d{5,}',
         #ＸＸＸＸＸ - ＸＸＸＸＸ
        u'[０-９]{5,}\s{0,}[-－~～][０-９]{5,}', 
         #xxk ~ xxk
        u'\d{2,3}[kK]\s{0,}[~-]\s{0,}\d{2,3}[kK]',
         #xx,xxx
        '\d{2,3}[,.]\d{3}',
         #xxxxx
        '\d{5,}',
         #ＸＸ,ＸＸＸ
        u'[０-９]{2,3},[０-９]{3}',
         #ＸＸＸＸＸ
        u'[０-９]{5,}',
         # 一萬一 or 一萬
        u'[一二三四五六七八九十]{1,}[萬ＷｗWw][一二三四五六七八九十]{0,1}',
         # X萬X
        u'\d[萬ＷｗWw]\d',
         # Ｘ萬Ｘ
        u'[０-９][萬ＷｗWw][０-９]',
         #ＸＸ萬
        u'[０-９]{1,}[萬ＷｗWw]', 
         # X萬
        u'\d{1,}[萬ＷｗWw]',
         # xxk
        u'\d{2,}[kK]',
         #ＸＸK
        u'[０-９]{2,}[kＫ]'
    ]
    salary_blocks = []

    #找到的總數，用於判斷第一個條件的薪水還是第二個條件的薪水
    findOrder = []

    #先找有無分碩士學士or有無經驗
    for i in range(len(title)):
        regResult = None
        for regex in title[i]:
            regResult = re.search(regex, salary_content)
            if regResult == None:
                continue
            else:
                findOrder = checkOrder(salary_content, title[i])
                #print findOrder
                break
                

    #findCount == 0, so there is only salary no type
    if len(findOrder) == 0:
        salary_blocks.append([analyzeSalaryType(salary_type, salary_content, 0)])
        #print salary_blocks
    else:
        for job_salary in findOrder:
            #print job_salary
            salary_blocks.append([job_salary[0], u'%s' % analyzeSalaryType(salary_type, salary_content, job_salary[1])])
            #print salary_blocks
            
    return salary_blocks




#check the order
def checkOrder(context, title):
    regResult = None
    new_regex_list = []
    titleOrder = []
    for regex in title:
        #print regex
        regResult = re.search(regex, context)
        if regResult == None:
            continue
        else:
            #print new_regex_list
            new_regex_list.append([regex, regResult.start()])
            insertionSort(new_regex_list)
            #print new_regex_list

    # give the title find order number
    for title_name in title:
        for j in range(len(new_regex_list)):
            #print new_regex_list
            if title_name == new_regex_list[j][0]:
                titleOrder.append([title_name, j])
    return titleOrder

def insertionSort(unOrderlist):
    for i in range(1, len(unOrderlist)):
        tmp = unOrderlist[i]
        position = i
        while position > 0 and unOrderlist[position - 1] > tmp:
            unOrderlist[position] = unOrderlist[position - 1]
            position -= 1
        unOrderlist[position] = tmp

#find ?th salary
def analyzeSalaryType(salary_type, salary_content, findCount):
    regResult = None
    #print salary_content
    for regex in salary_type:
        #print regex
        regResult = re.search(regex, salary_content)
        #print regResult
        if regResult == None:
            continue
        regResult = re.findall(regex, salary_content)

        print regResult
        #print analyzeSalartNumber(unicodedata.normalize('NFKC', regResult[findCount]))
        return analyzeSalartNumber(unicodedata.normalize('NFKC', regResult[findCount]))
    return 'Not find Salary Type'

#normalize numbers
def analyzeSalartNumber(salary):
    chineseNumber = u'[一二三四五六七八九十]'
    print 'YEEE'
    print salary
    
    if ',' in salary or '.' in salary:
        salary = re.sub('[,.]', '', salary)
        print salary

    regResult = re.findall(u'\d{5,}', salary)
    print regResult
    #判斷是否兩組數字
    if len(regResult) > 1:
        return (int(regResult[0]) + int(regResult[1])) / 2
    elif len(regResult) == 1:
        return salary
    else :
        #判斷是否有W
        regResult = re.search(u'[萬ＷｗWw]', salary)
        print regResult
        temp = 0
        total = 0
        if regResult > 1:
            #判斷後面是否接國字數字
            if re.search(chineseNumber, salary[regResult.end():]) != None:
                print '後國字'
                temp = convertToInt(salary[regResult.end():]) * 1000
            #判斷後面是否接羅馬數字
            elif re.search('\d{1}', salary[regResult.end():]) != None:
                print '後數字'
                temp = int(salary[regResult.end():]) * 1000

            #處理二位數以上的國字
            front_result = re.findall(chineseNumber, salary[:regResult.start()])
            if len(front_result) > 0:
                multi = len(front_result) - 1
                if len(front_result) > 1:
                    for num in front_result:
                        total += convertToInt(num) * (10 ** multi)
                        multi -= 1
                else:
                    total = convertToInt(front_result[0])
            else:
                front_result = re.findall('\d{1,}', salary[:regResult.start()])
                total = front_result[0]
            
            return int(total) * 10000 + temp
        
        #判斷是否有K
        regResult = re.search(u'\d{2,3}[kK]', salary)
        if regResult != None:
            front_result = re.findall('\d{2,3}[kK]', salary)
            if len(front_result) > 1:
                print front_result
                return int(((float(re.sub(u'[kK]', '', front_result[0])) + float(re.sub(u'[kK]', '', front_result[1]))) / 2) * 1000)
            else:
                return int(float(re.sub(u'[kK]', '', front_result[0])) * 1000)



def convertToInt(num_string):

    if u'一' in num_string:
        return 1
    if u'二' in num_string or u'兩' in num_string:
        return 2
    if u'三' in num_string:
        return 3
    if u'四' in num_string:
        return 4
    if u'五' in num_string:
        return 5
    if u'六' in num_string:
        return 6
    if u'七' in num_string:
        return 7
    if u'八' in num_string:
        return 8
    if u'九' in num_string:
        return 9
    if u'十' in num_string:
        return 10

    return num_string


if __name__ == "__main__":
        try:
           input = raw_input
        except NameError:
           pass
        main()




"""

5266
5352
5429
5493

5041

5001
5006
5013
5026
5027


5313th

5305th
5312th


M.1494309887.A.F3A


765


385  M.1476081764.A.2AA
584  M.1476898098.A.399(不照格式)
1406 M.1480501182.A.412(不照格式)
1553 M.1481169878.A.6D0(不照格式)
1686 M.1481696843.A.33B(不照格式)
1788 M.1482195562.A.561(格式正確，抓不到薪資)
1811 M.1482221994.A.A98(不照格式)
1848 M.1482325671.A.477(PT)
2107 M.1483441604.A.889(不照格式)
2363 M.1484450984.A.3B0(以徵到刪文)
2439 M.1484668442.A.FCB(PT)
3726 M.1489143769.A.308(不照格式)
3921 M.1489850443.A.738(不照格式= =)
4274 M.1490924233.A.CE3
4277 M.1490926482.A.D94
4285 M.1490938695.A.D9F(格式不對)
4560 M.1491993915.A.7E8(PT版)
4615 M.1492141435.A.A67(格式不對)
4662 M.1492365697.A.54F(格式不對)
4818 M.1492739618.A.705(格式不對)
5211 M.1493968570.A.A2A
5222 M.1493985242.A.F06
5237
5243
5271
5951 M.1496313841.A.DB7 (完全不照格式)







[一-九]{0,}百{0,1}[一-十]{1,}\s{0,}萬 
"""
















"""
import json
import os
import re
import pymysql
import Config
import requests
import random
from os.path import isfile, join
from shutil import copyfile
from pprint import pprint

DB_HOST = '140.118.70.162'
DB_USER = 'jobguide'
DB_PASSWD = 'zNW3hw1HjMsQvOc9'
DB_NAME = 'jobguide'
TMP_PATH = Config.TMP_PATH


DB = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWD, db=DB_NAME, port=13306, charset='utf8')

CURSOR = DB.cursor()

SQL = "INSERT INTO ptt_articles(title, author, board, content, date, ip, article_uuid) VALUES (%s, %s, %s, %s, %s, %s, %s)

def main():
    #f_2015 = open('2015.txt', 'w')
    #f_2016 = open('2016.txt', 'w')
    job_type = ['資訊科技', '傳產製造', '工商服務', '民生服務', '文教傳播']
    salary = [31000, 32000, 33000, 34000, 35000, 36000, 37000, 38000, 39000, 40000, 41000, 42000, 43000, 44000,45000, 46000, 47000, 48000, 49000, 50000, 51000, 52000, 53000, 54000, 55000, 56000, 57000, 58000, 59000, 60000]

    for i in range(0, 2000):
        print '%s,%d' % (job_type[random.randint(0,len(job_type) - 1)], salary[random.randint(0,len(salary) - 1)])


    mathe.append(random.randint(1, 12))

    for i in range(0, 6000):
        f_2015.writelines('%d,%d ' %  (id_list[i], mathe[i]))



    id_list = random.sample(range(10000000, 99999999), 6000)
    mathe = []
    for i in range(0, 6000):
        mathe.append(random.randint(1, 12))

    for i in range(0, 6000):
        f_2016.writelines('%d,%d ' % (id_list[i], mathe[i]))



    command = "cd %s && python ../pttcrawler.py -b %s -i %d %d" % (os.path.basename(TMP_PATH), 'job', 1, -1)
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
    file = open("job-200-300.json", 'r')
    lines = file.readlines()
    lines[0] = '[\n'
    lines[len(lines) - 1] = '}\n]'
    file.close()

    file = open("job-200-300_update.json", 'w')
    file.writelines(lines)
    file.close()
    with open('job-200-300_update.json','r') as json_file:
        data = json.open(json_file)

    regex = re.compile(r".+-[0-9]+_parsed\.json")
    jsonFiles = [f for f in os.listdir(TMP_PATH) if isfile(join(TMP_PATH, f)) and regex.match(f)]
    regex = re.compile(r"[0-9]+")

    for filename in jsonFiles:
        fullPath = join(TMP_PATH, filename)
        temp = json.load(open(fullPath))

        #data = json.open('C:\Users\user\Desktop\PTTCrawler\PttJobCrawler\JobRobot\job-200-300_update.json')

        for data in temp:
            if data['author'] == '' or data['article_title'] == '' or data['date'] == '':
                CURSOR.execute(SQL, (data['article_title'],
                         data['author'],
                         data['board'],
                         data['content'],
                         data['date'],
                         data['ip'],
                         data['article_id'] ))

    CURSOR.execute(SQL, (data[0]['article_title'],
                         data[0]['author'],
                         data[0]['board'],
                         data[0]['content'],
                         date_time,
                         data[0]['ip'],
                         data[0]['article_id'] ))
    #json_data[0]['date'][0] = ' '

    #DB.commit()
    for data in json_data:
        print (data['author'])

def format_date(datetime):
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




if __name__ == "__main__":
        main()
        """
