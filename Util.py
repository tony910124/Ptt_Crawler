# -*- coding: utf-8 -*-
import codecs
import DbHelper

def store(filename, data, mode):
    with codecs.open(filename, mode, encoding='utf-8') as f:
        f.write(data)

def writeKV(key, value):
	dbCollection = DbHelper.connectMongoCollection('keyvalues')
	dbCollection.update_one(
		{'_key': key},
		{
			'$set': {
				'_val': value
			}
		}
	)

def readKV(key):
	dbCollection = DbHelper.connectMongoCollection('keyvalues')
	result = dbCollection.find({'_key': key})
	return result[0]['_val']

# writeKV('part_time_lastPage', 5755)
