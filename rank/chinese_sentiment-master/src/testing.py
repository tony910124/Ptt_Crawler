#coding=utf-8
import json
import datetime
import jieba
import math
import sqlite3
from decimal import *

pos_sentiment_dic = {}
neg_sentiment_dic = {}
pos_word_count = 0
neg_word_count = 0
pos_prior = 0
neg_prior = 0

def load_training_data(model_path,user_dic_name=''):
	if user_dic_name != '':
		jieba.load_userdict(user_dic_name)
	global pos_sentiment_dic
	global neg_sentiment_dic
	global pos_word_count
	global neg_word_count
	global pos_prior
	global neg_prior
	cnx = sqlite3.connect(model_path+'model.db')
	cur = cnx.cursor()
	cur.execute('SELECT word,value FROM sentiment_positive_word')
	results = cur.fetchall()
	for result in results:
		pos_sentiment_dic[result[0]] = result[1]
	cur.execute('SELECT word,value FROM sentiment_negative_word')
	results = cur.fetchall()
	for result in results:
		neg_sentiment_dic[result[0]] = result[1]
	cur.execute('SELECT positive_word_count,negative_word_count,positive_document_count,negative_document_count FROM sentiment_baseline',)
	result = cur.fetchone()
	pos_word_count = int(result[0])
	neg_word_count = int(result[1])
	positive_document_count = float(result[2])
	negative_document_count = float(result[3])
	pos_prior = positive_document_count/(negative_document_count+positive_document_count)
	neg_prior = negative_document_count/(negative_document_count+positive_document_count)

def test_sentance(input_sentence):
	word_list = jieba.cut(input_sentence.strip())
	#print ','.join(word_list).encode('utf-8')
	pos_result = 0
	neg_result = 0
	temp_list = []
	for word in word_list:
		word = word.strip()
		if len(word) > 0:
			temp_list.append(word)
			if word in pos_sentiment_dic:
                                #print 'pos:' + word
                                pos_result += pos_sentiment_dic[word]
				#pos_result += math.log(pos_sentiment_dic[word])
			#else:
                                #print 'not in pos:' + word
				#pos_result += math.log(float(1)/pos_word_count)
			if word in neg_sentiment_dic:
                                neg_result += neg_sentiment_dic[word]
				#neg_result += math.log(neg_sentiment_dic[word])
			#else:
				#neg_result += math.log(float(1)/neg_word_count)
	#print ','.join(temp_list).encode('utf-8')
	return {'pos':pos_result,'neg':neg_result}
