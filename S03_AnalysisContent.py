# -*- coding: utf-8 -*-
import re
import os
import json
import pymysql
import unicodedata
import Config
import Clasify
from os.path import isfile, join
from os import sep

from pprint import pprint
#import DbHelper



db = pymysql.connect(host=Config.DB_HOST, user=Config.DB_USER,
                port=Config.DB_PORT, password=Config.DB_PASSWD,
                db=Config.DB_NAME, charset='utf8')
cursor = db.cursor()

CLEAR_OLD_DATA = False


#插入依順序是 (article_id, 公司名稱, 公司職缺, 工作內容, 徵求條件, 工作地點, 工作時間, 月休, 公司福利, 薪水, 需要人數, 聯絡人, 期限, 備註)
sql = "INSERT INTO ptt_content_analyze(article_id,\
                                       corporation,\
                                       work, \
                                       work_type, \
                                       work_content, \
                                       work_sufficient, \
                                       work_location, \
                                       work_time, \
                                       day_off, \
                                       allowance, \
                                       salary, \
                                       vacancy, \
                                       contact, \
                                       deadline, \
                                       remark) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
sql_print = "INSERT INTO ptt_content_analyze(title) VALUES (%s)"
TMP_PATH = Config.TMP_PATH
#dbCollection = None
#regexEmail = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

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

    errorCount = 0
    regex = re.compile(r".+_[0-9]+_parsed\.json")
    file = [f for f in os.listdir(TMP_PATH) if isfile(join(TMP_PATH, f)) and regex.match(f)]
    #print TMP_PATH

    for filename in file:
        #print len(file)

        """判斷issue用"""
        fullPath = join(TMP_PATH, filename)
        docs = json.load(open(fullPath))
        print len(docs)
        for i in range(len(docs)):
            error = False
            #print "%s" % docs[i]['article_title']
            try:
                """判斷開頭是否為地區，不是回復或黑名單等等"""
                for regex in city_title:
                    if re.match( regex, docs[i]['article_title']) != None:
                        print 'Now on %dth file' % (i)
                        print '-' * 150
                        for issue in issue_title:
                            #print 'FKFKFK'

                            if issue in docs[i]['article_title']:
                                #print '\n\n' + '|*'*50
                                #print docs[i]['article_id']+'\t'+docs[i]['article_title']
                                #print "\t\t%s - %s" % (docs[i]['article_id'], docs[i]['article_title'])
                                #print '|*'*50 + '\n\n'
                                error = True
                                break
                        if error:
                            error = False
                            continue
                        #print "%s - %s\n" % (docs[i]['article_id'], docs[i]['article_title'])
                        #print docs[i]
                        #analyzeContent(docs[i])
                        errorCount += analyzeContent(docs[i])
                        break
            except Exception as e:

                print '|*'*30 + '|'
                if 'error' in docs[i]:
                    print u'error'
                else:
                    print '%s' % (e)
                    #print docs[i]['article_id'].encode('utf-8')+'\t'+docs[i][article_title].encode('utf-8')
                    print "ERROR on %s -\n" % (docs[i]['article_id'])
                    raise
                print '|*'*30 + '|'
    db.commit()
    db.close()
    print "Finished with %d article(s) having error." % (errorCount)


def analyzeContent(doc):
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
    foundCount = 0
    for i in range(len(blocksTitle)):
            regResult = None
            for regex in blocksTitle[i]:
                    regResult = re.search(regex, tmp)
                    if regResult != None:
                            foundCount += 1
                            break
            if regResult == None:
                    #print "%s: unable to find block: '%s'\n" % (doc['article_id'], blocksTitle[i][0])
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
    
    blocks[len(blocks) - 1] = re.sub('--+(.?)+--', "", blocks[len(blocks) - 1])
    blocks = doubleCheck(blocksTitle, blocks)
    blocks[8] = analyzeSalary(blocks[8])
    
    tmp = Clasify.getJobType(blocks[2])
    blocks.insert( 2, tmp)
    #print blocks[3]
    updateToSQL(blocks, doc['article_id'])
    
    #print the content in blocks (for debugging)
    """
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
    """
    return hasError


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
                        print "DOBLE_CHECK ERROR ON :" + blocks[block_i]
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
        salary_blocks.append([u'%s' % analyzeSalaryType(salary_type, salary_content, 0)])
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
        #print regResult
        return analyzeSalartNumber(unicodedata.normalize('NFKC', regResult[findCount] if len(regResult) < findCount else regResult[0]))
    return None

#normalize numbers
def analyzeSalartNumber(salary):
    chineseNumber = u'[一二三四五六七八九十]'
    
    if ',' in salary or '.' in salary:
        salary = re.sub('[,.]', '', salary)

    regResult = re.findall(u'\d{5,}', salary)

    #判斷是否兩組數字
    if len(regResult) > 1:
        return (int(regResult[0]) + int(regResult[1])) / 2
    elif len(regResult) == 1:
        return salary
    else :
        #判斷是否有W
        regResult = re.search(u'[萬ＷｗWw]', salary)
        temp = 0
        total = 0
        if regResult > 1:
            #判斷後面是否接國字數字
            if re.search(chineseNumber, salary[regResult.end():]) != None:
                #print '後國字'
                temp = convertToInt(salary[regResult.end():]) * 1000
            #判斷後面是否接羅馬數字
            elif re.search('\d{1}', salary[regResult.end():]) != None:
                #print '後數字'
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
                #print front_result
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

def updateToSQL(blocks, article_id):
    

    
    try:
        cursor.execute(sql, (article_id,
                             None if blocks[0] == '' else blocks[0], 
                             None if blocks[1] == '' else blocks[1],
                             None if blocks[2] == '' else blocks[2], 
                             None if blocks[3] == '' else blocks[3],
                             None if blocks[4] == '' else blocks[4],
                             None if blocks[5] == '' else blocks[5], 
                             None if blocks[6] == '' else blocks[6],
                             None if blocks[7] == '' else blocks[7], 
                             None if blocks[8] == '' else blocks[8],
                             None if blocks[9][0][0] == '' or blocks[9][0][0] == None \
                                    else \
                                        str(blocks[9][0][-1]).decode('utf-8'), 
                             None if blocks[10] == '' else blocks[10],
                             None if blocks[11] == '' else blocks[11], 
                             None if blocks[12] == '' else blocks[12],
                             None if blocks[13] == '' else blocks[13], 
                             ))
        print sql_print % (article_id)
    except Exception as e:
        print "\t\t" + "|*" * 50 + "|"
        #print blocks[3]
        #print blocks[9][0][0]
        print '%s' % (e)
        print "\t\t\t\tSQL UPLOAD FAIL ON : %s" % (article_id)
        print "\t\t" + "|*" * 50 + "|"

    


if __name__ == "__main__":
    try:
        input = raw_input
    except NameError:
        pass
    main()