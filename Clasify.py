# -*- coding: utf-8 -*-
import os
import codecs
import re

def getJobType(job):
	clasifyType = getClasifyType()
	#print job

	for jobType in clasifyType:
		for regex in jobType[1:]:
			#print regex
			regResult = re.search(regex, job)
			if regResult != None:
				return jobType[0]
	return u'其他'



def getClasifyType():
	clasify = []
	f = codecs.open('clasify.txt', 'r', encoding = 'utf-8')
	for line in f:
		tmp = line.split('  ')
		clasify += [tmp]
		if line == '':
			break
	#print clasify
	f.close()
	return clasify
