
# ErrorDocCrawler - Re-fetch error pages (may caused by connection limitations) from db

import os
import re
from os.path import isfile, join
from datetime import datetime
import Config
import DbHelper

TMP_PATH = Config.TMP_PATH

PERFORM_CRAWLER = True
IMPORT_TO_MONGO = True
REMOVE_ERROR_DOCS = True
DATE_CORRECTION = True

dbCollection = None

def main():
	global dbCollection
	dbCollection = DbHelper.connectMongoCollection()

	if (PERFORM_CRAWLER):
		docs = dbCollection.find({'error': {'$exists': True}})
		for doc in docs:
			command = "cd %s; python ../pttcrawler.py -b %s -a %s;" % (TMP_PATH, doc['board'], doc['article_id'])
			os.system(command)
	
	if (IMPORT_TO_MONGO):
		import2Mongo()

	if (REMOVE_ERROR_DOCS):
		dbCollection.delete_many({'error': {'$exists': True}})
		print "All error docs deleted"

	if (DATE_CORRECTION):
		dateCorrection()

def dateCorrection():
	global dbCollection

	docs = dbCollection.find({
		'date': {'$exists': True},
		'date': {'$ne': ''}
	})
	for doc in docs:
		if not isinstance(doc['date'], unicode):
			continue
		try:
			dateObject = datetime.strptime(doc['date'], '%a %b %d %H:%M:%S %Y')
		except ValueError, e:
			print "%s '%s'" % (doc['article_id'], doc['date'])
			continue
		# write back
		dbCollection.update_one(
			{'_id': doc['_id']},
			{
				'$set': {
					'date': dateObject
				}
			}
		)

def import2Mongo():
	regex = re.compile(".+-M\..+\.json")
	jsonFiles = [join(TMP_PATH, f) for f in os.listdir(TMP_PATH) if isfile(join(TMP_PATH, f)) and regex.match(f)]

	regex = re.compile("[^\/][^-M]+\..+[^\.json]")
	for filename in jsonFiles:
		command = "mongoimport --db '%s' --collection '%s' --type json --file %s" % (DbHelper.DB, DbHelper.COLLECTION, filename)
		print command
		os.system(command)

		# extract article_id from filename and delete error doc in DB
		article_id = regex.search(filename).group()
		dbCollection.delete_one({'article_id': article_id})
		print "Deleted error doc: %s" % (article_id)

if __name__ == "__main__":
	try:
	   input = raw_input
	except NameError:
	   pass
	main()
