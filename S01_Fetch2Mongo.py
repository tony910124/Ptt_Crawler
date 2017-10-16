import os
import re
import time
from os.path import isfile, join
from shutil import copyfile
import Config
import DbHelper
import Util
import S02_ErrorDocCrawler
import S03_AnalysisContent_part_time

PTT_BOARD = 'part-time'
BACKUP_PATH = Config.BACKUP_PATH
TMP_PATH = Config.TMP_PATH

EXECUTE_CRAWLER = True
IMPORT_CHECK_EXISTED = True
EXECUTE_ERROR_DOC_CRAWLER = True
EXECUTE_ANALYZER = True
BACKUP_DATA = False

def main():
	if EXECUTE_CRAWLER:
		# Clear tmp directory
		tmpFiles = [join(TMP_PATH,f) for f in os.listdir(TMP_PATH) if isfile(join(TMP_PATH, f))]
		for file in tmpFiles:
			os.remove(file)

		firstPage = int(Util.readKV('part_time_lastPage'))
		print "Start from page %d" % (firstPage)
		doCrawler(firstPage, -1)
		#import2Mongo(IMPORT_CHECK_EXISTED)

		print "Last page number is %d" % (int(Util.readKV('part_time_lastPage')))

	if EXECUTE_ERROR_DOC_CRAWLER:
		S02_ErrorDocCrawler.main()

	if EXECUTE_ANALYZER:
		S03_AnalysisContent_part_time.main()

	print "Finished."

def doCrawler(pageStart, pageEnd):
	command = "cd %s; python ../pttcrawler.py -b %s -i %d %d;" % (TMP_PATH, PTT_BOARD, pageStart, pageEnd)
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

		newFilename = u"%s_%d_parsed.json" % (filename[:-5], int(time.time()))
		newFullpath = join(TMP_PATH, newFilename)
		file = open(newFullpath, 'w')
		file.writelines(lines)
		file.close()
		if BACKUP_DATA:
			copyfile(newFullpath, join(BACKUP_PATH, newFilename))
		os.remove(fullPath)

def import2Mongo(checkExsisted):
	regex = re.compile(r".+_[0-9]+_parsed\.json")
	jsonFiles = [f for f in os.listdir(TMP_PATH) if isfile(join(TMP_PATH, f)) and regex.match(f)]
	regex = re.compile(r"[0-9]+")
	tmpCollectionName = DbHelper.COLLECTION + "_tmp"

	for filename in jsonFiles:
		fullPath = join(TMP_PATH, filename)
		collection = tmpCollectionName if checkExsisted else DbHelper.COLLECTION
		command = "mongoimport --db '%s' --collection '%s' --type json --file %s --jsonArray" % (DbHelper.DB, collection, fullPath)
		print command
		os.system(command)
		nums = regex.findall(filename)
		# startPage = nums[0]
		endPage = nums[1]
		Util.writeKV('part_time_lastPage', endPage)
		os.remove(fullPath)
	
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

if __name__ == "__main__":
	try:
	   input = raw_input
	except NameError:
	   pass
	main()
