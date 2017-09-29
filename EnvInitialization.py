import os
import Config
import DbHelper

dbCollection = None

def main():
	global dbCollection
	dbCollection = DbHelper.connectMongoCollection('keyvalues')
	createAppDirs()
	createKeyValues()

def createAppDirs():
	pathes = [Config.BACKUP_PATH, Config.TMP_PATH]
	print "checking app dirs..."
	for path in pathes:
		if not os.path.exists(path):
			print "directory " + path + "created."
			os.makedirs(path)

def createKeyValues():
	global dbCollection
	keys = ['part_time_lastPage']
	vals = [1]

	print "checking keyvalues collection..."
	for i in range(len(keys)):
		if (dbCollection.find({'_key': keys[i]}).count() == 0):
			dbCollection.insert_one({'_key': keys[i], '_val': vals[i]})
			print "keyvalue inserted: " + keys[i]

if __name__ == "__main__":
	try:
	   input = raw_input
	except NameError:
	   pass
	main()
