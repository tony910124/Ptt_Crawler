# vim: set ts=4 sw=4 et: -*- coding: utf-8 -*-

# !!! MODIFIED from original github version by cchi !!!

from __future__ import absolute_import
from __future__ import print_function
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
    from urllib2 import Request
import re
import sys
import json
import requests
import argparse
import time
import codecs
import time
from bs4 import BeautifulSoup
from six import u

__version__ = '1.0'

# if python 2, disable verify flag in requests.get()
VERIFY = True
if sys.version_info[0] < 3:
    VERIFY = False
    requests.packages.urllib3.disable_warnings()


def crawler(cmdline=None):
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='''
        A crawler for the web version of PTT, the largest online community in Taiwan.
        Input: board name and page indices (or articla ID)
        Output: BOARD_NAME-START_INDEX-END_INDEX.json (or BOARD_NAME-ID.json)
    ''')
    parser.add_argument('-b', metavar='BOARD_NAME', help='Board name', required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', metavar=('START_INDEX', 'END_INDEX'), type=int, nargs=2, help="Start and end index")
    group.add_argument('-a', metavar='ARTICLE_ID', help="Article ID")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    if cmdline:
        args = parser.parse_args(cmdline)
    else:
       args = parser.parse_args()
    board = args.b
    PTT_URL = 'https://www.ptt.cc'
    if args.i:
        start = args.i[0]
        if args.i[1] == -1:
            end = getLastPage(board)
        else:
            end = args.i[1]
        index = start
        filename = board + '-' + str(start) + '-' + str(end) + '.json'
        store(filename, u'{"articles": [\n', 'w')
        for i in range(end-start+1):
            index = start + i
            print('Processing index:', str(index))

            while (True):
                try:
                    resp = requests.get(
                        url=PTT_URL + '/bbs/' + board + '/index' + str(index) + '.html',
                        cookies={'over18': '1'}, verify=VERIFY
                    )
                    #'''檢查網頁是否正常200 = 正常，其他就重整'''
                    if (resp.status_code == 200):
                        break
                    else:
                        print('Retrying url:', resp.url)
                        time.sleep(1)
                except Exception, e:
                    print('Retrying url:', resp.url)
                    time.sleep(1)
                    continue

            soup = BeautifulSoup(resp.text)
            divs = soup.find_all("div", "r-ent")
            for div in divs:
                try:
                    # ex. link would be <a href="/bbs/PublicServan/M.1127742013.A.240.html">Re: [問題] 職等</a>
                    href = div.find('a')['href']
                    link = PTT_URL + href
                    article_id = re.sub('\.html', '', href.split('/')[-1])
                    #'''     ////////'''
                    if div == divs[-1] and i == end-start:  # last div of last page
                        store(filename, parse(link, article_id, board) + '\n', 'a')
                    else:
                        store(filename, parse(link, article_id, board) + ',\n', 'a')
                except:
                    pass
            time.sleep(0.1)
        store(filename, u']}', 'a')
    else:  # args.a
        article_id = args.a
        link = PTT_URL + '/bbs/' + board + '/' + article_id + '.html'
        filename = board + '-' + article_id + '.json'
        store(filename, parse(link, article_id, board), 'w')


def parse(link, article_id, board):
    print('Processing article:', article_id)

    resp = requests.get(url=link, cookies={'over18': '1'}, verify=VERIFY)
    if resp.status_code != 200:
        print('invalid url:', resp.url)
        output = {
            "article_id": article_id,
            "board": board,
            "error": "invalid url"
        }
        time.sleep(1)
        return json.dumps(output, indent=4, sort_keys=True, ensure_ascii=False)

    soup = BeautifulSoup(resp.text)
    main_content = soup.find(id="main-content")
    metas = main_content.select('div.article-metaline')
    author = ''
    title = ''
    date = ''
    if metas:
        add_row = 0
        #有可能有白癡寫錯格式 這裡的情況是判斷是否一二行相同(發現這行是因為發現時間的地方有輸錯)
        if metas[0].select('span.article-meta-value')[0].string in metas[1].select('span.article-meta-value')[0].string:
             add_row = 1
        author = metas[0].select('span.article-meta-value')[0].string if metas[0].select('span.article-meta-value')[0] else author
        title = metas[add_row + 1].select('span.article-meta-value')[0].string if metas[add_row + 1].select('span.article-meta-value')[0] else title
        date = metas[add_row + 2].select('span.article-meta-value')[0].string if metas[add_row + 2].select('span.article-meta-value')[0] else date
        # remove meta nodes
        for meta in metas:
            meta.extract()
        for meta in main_content.select('div.article-metaline-right'):
            meta.extract()

    # remove and keep push nodes
    pushes = main_content.find_all('div', class_='push')
    for push in pushes:
        push.extract()

    try:
        ip = main_content.find(text=re.compile(u'※ 發信站:'))
        ip = re.search('[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*', ip).group()
    except:
        ip = "None"
    """
    # 移除 '※ 發信站:' (starts with u'\u203b'), '◆ From:' (starts with u'\u25c6'), 空行及多餘空白
    # 保留英數字, 中文及中文標點, 網址, 部分特殊符號
    filtered = [ v for v in main_content.stripped_strings if v[0] not in [u'※', u'◆'] and v[:2] not in [u'--'] ]
    expr = re.compile(u(r'[^\u4e00-\u9fa5\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\s\w:/-_.?~%()]'))
    for i in range(len(filtered)):
        filtered[i] = re.sub(expr, '', filtered[i])

    filtered = [_f for _f in filtered if _f]  # remove empty strings
    filtered = [x for x in filtered if article_id not in x]  # remove last line containing the url of the article
    content = ' '.join(filtered)
    content = re.sub(r'(\s)+', ' ', content)
    """
    content = ''.join(main_content.stripped_strings)
    content = re.sub(r'([\s\n])+', ' ', content)

    #----8/22 coding---
    emails = main_content.find_all("a", class_ = '__cf_email__')
    #print len(emails)
    #tmp = '  ||'
    for email in emails:
        #tmp += deCFEmail(email["data-cfemail"]) + '||  '
        regResult = re.findall('\[ema.+.tected\]', content)
        if len(regResult) > 1:
            tmp = re.find('\[ema.+.tected\]', content)
            content = re.sub('\[ema.+.tected\]', deCFEmail(email['data-cfemail']), content[:tmp.end()])
        else:
            content = re.sub('\[ema.+.tected\]', deCFEmail(email['data-cfemail']), content)
    #content += str(len(regResult)) + deCFEmail(email['data-cfemail'])
    #------------------


    # print 'content', content

    # push messages
    p, b, n = 0, 0, 0
    messages = []
    for push in pushes:
        if not push.find('span', 'push-tag'):
            continue
        push_tag = push.find('span', 'push-tag').string.strip(' \t\n\r')
        push_userid = push.find('span', 'push-userid').string.strip(' \t\n\r')
        # if find is None: find().strings -> list -> ' '.join; else the current way
        push_content = push.find('span', 'push-content').strings
        push_content = ' '.join(push_content)[1:].strip(' \t\n\r')  # remove ':'
        push_ipdatetime = push.find('span', 'push-ipdatetime').string.strip(' \t\n\r')
        messages.append( {'push_tag': push_tag, 'push_userid': push_userid, 'push_content': push_content, 'push_ipdatetime': push_ipdatetime} )
        if push_tag == u'推':
            p += 1
        elif push_tag == u'噓':
            b += 1
        else:
            n += 1

    # count: 推噓文相抵後的數量; all: 推文總數
    message_count = {'all': p+b+n, 'count': p-b, 'push': p, 'boo': b, "neutral": n}

    # print 'msgs', messages
    # print 'mscounts', message_count

    # json data
    data = {
        'board': board,
        'article_id': article_id,
        'article_title': title,
        'author': author,
        'date': date,
        'content': content,
        'ip': ip,
        'message_conut': message_count,
        'messages': messages
    }
    # print 'original:', d
    return json.dumps(data, indent=4, sort_keys=True, ensure_ascii=True)

def getLastPage(board):
    site = 'https://www.ptt.cc/bbs/' + board + '/index.html'
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    req = Request(site, headers = hdr)
    content = urlopen(req).read().decode('utf-8')
    first_page = re.search(r'href="/bbs/' + board + '/index(\d+).html">&lsaquo;', content).group(1)
    return int(first_page) + 1

def store(filename, data, mode):
    with codecs.open(filename, mode, encoding='utf-8') as f:
        f.write(data)

def deCFEmail(decodedEmail):
    r = int(decodedEmail[:2],16)
    EMAIL = ''.join([chr(int(decodedEmail[i:i+2], 16) ^ r) for i in range(2, len(decodedEmail), 2)])
    #print EMAIL.encode('utf-8')
    return EMAIL

if __name__ == '__main__':
    crawler()
