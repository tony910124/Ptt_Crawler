# -*- coding: utf-8 -*-
import re
import DbHelper

CLEAR_OLD_DATA = False

dbCollection = None
regexEmail = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

def main():
	global dbCollection
	dbCollection = DbHelper.connectMongoCollection()

	if CLEAR_OLD_DATA:
		dbCollection.update_many(
			{'extractedInfo': {'$exists': True}},
			{'$unset': {'extractedInfo':""}}, False)
		print 'All extractedInfo deleted.'

	# docs = dbCollection.find({'article_id': 'M.1467342583.A.165'}).limit(1)
	errorCount = 0
	docs = dbCollection.find({'extractedInfo': {'$exists': False}})
	for doc in docs:
		if re.match(u'.*(([0-9]+\/)).+', doc['article_title']):
			print "%s - %s\n" % (doc['article_id'], doc['article_title'])
			errorCount += analyzeContent(doc)
	print "Finished with %d article(s) having error." % (errorCount)

def analyzeContent(doc):
	global dbCollection, regexEmail

	hasError = False
	content = doc['content']
	blocksTitle = [
		[u'★《工作期間》'],
		[u'★《工作待遇》'],
		[u'★《工作內容》'],
		[u'★《事業登記資料》', u'◎《事業相關資料》', u'★《舉辦單位相關資料》'],
		[u'★《聯絡資訊》'],
		[u'◎《其他資訊》'],
		[u'強烈建議雇主徵到人會在這篇標題註明（大寫T修改標題）\(資方徵到人請改標題或是通知應徵者 多多體諒勞方等待心情\)(\s)*--※ 發信站: 批踢踢實業坊\(ptt.cc\)']
	]
	topics = [
		u'工作日期&排班方式', u'每日工作&休息時間', u'休息有無計薪&供餐',
		u'平常日薪資', u'國定假日薪資', u'超時加班費', u'勞健保、勞退', u'薪資發放日',
		u'工作地點', u'工作內容',
		u'統一編號', u'單位名稱',
		u'地址／網址', u'醫療醫藥相關單位代碼/代班公司統編', u'農林漁牧業登記字號/公司名稱', u'補教業立案文號/公司地址',
		u'聯絡人姓氏', u'Email／電話', u'履歷上要有', u'是否回信給報名者',
		u'需求人數', u'通知方式', u'面試時間', u'受訓時間', u'截止時間', u'備註'
	]
	identifiers = [ # index is corresponded to blocksTitle index
		[[u'工作日期&排班方式'], [u'\s*每日工作&休息時間'], [u'休息有無計薪&供餐']],
		[[u'平常日薪資'], [u'國定假日薪資'], [u'超時加班費'], [u'勞健保、勞退'], [u'薪資發放日']],
		[[u'工作地點'], [u'工作內容']],
		[[u'統一編號'], [u'單位名稱'], [u'單位地址', u'地址／網址'], [u'醫療醫藥相關單位代碼', u'代班公司統編'], [u'農林漁牧業登記字號', u'公司名稱'], [u'補教業立案文號', u'公司地址']],
		[[u'聯絡人姓氏'], [u'Email／電話'], [u'履歷上要有'], [u'是否回信給報名者']],
		[[u'需求人數'], [u'通知方式'], [u'面試時間'], [u'受訓時間'], [u'截止時間'], [u'備註']]
	]

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
			print "%s: unable to find block: '%s'\n" % (doc['article_id'], blocksTitle[i][0])
			blankBlocks.append('')
			hasError = True
			continue
		if foundCount > 1:
			val = tmp[:regResult.start()].strip()
			blocks.append(val)
			if len(blankBlocks) > 0:
				blocks = blocks + blankBlocks
				blankBlocks = []
			# print val
			# print '-------------------------------\n'
		tmp = tmp[regResult.end():]
	if len(blankBlocks) > 0:
		blocks = blocks + blankBlocks
		blankBlocks = []

	# Find titles in each block
	descriptions = []
	blankDescriptions = []
	for i in range(len(identifiers)):
		tmp = blocks[i]
		foundCount = 0
		for j in range(len(identifiers[i])):
			regResult = None
			for regex in identifiers[i][j]:
				regResult = re.search(regex + (u'[︰：:\s]+'), tmp)
				if regResult != None:
					foundCount += 1
					break
			if regResult == None:
				print "%s: unable to find title: '%s'\n" % (doc['article_id'], identifiers[i][j][0])
				blankDescriptions.append(None)
				hasError = True
				continue
			if foundCount > 1:
				val = tmp[:regResult.start()].strip()
				descriptions.append(val if (val != u'無' and val != '') else None)
				if len(blankDescriptions) > 0:
					descriptions = descriptions + blankDescriptions
					blankDescriptions = []
			tmp = tmp[regResult.end():]
		if foundCount > 0:
			val = tmp.strip()
			descriptions.append(val if (val != u'無' and val != '') else None)
			if len(blankDescriptions) > 0:
				descriptions = descriptions + blankDescriptions
				blankDescriptions = []

	extractedInfo = {}
	for i in range(len(descriptions)):
		if descriptions[i] != None:
			extractedInfo[topics[i]] = descriptions[i]
		# print "%s : %s\n" % (topics[i], descriptions[i])
	# print '-------------------------------\n'

	# Write back
	dbCollection.update_one(
		{'_id': doc['_id']},
		{
			'$set': {
				'extractedInfo': extractedInfo
			}
		}, upsert=False
	)
	return hasError

if __name__ == "__main__":
	try:
	   input = raw_input
	except NameError:
	   pass
	main()
