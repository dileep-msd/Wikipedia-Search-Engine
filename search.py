from collections import defaultdict
import re
import time
from Stemmer import Stemmer
import sys
import math
import bisect
import sys
import os
import nltk
from nltk.tokenize import word_tokenize 

#load stopwords
nltk.download('stopwords')
stop_words = set(nltk.corpus.stopwords.words('english'))

secondaryIndex = defaultdict(lambda:0)
secondaryIndexIndices = []

try:
	indexFolder = sys.argv[1]
except:
	print("Unable to locate index folder")
	sys.exit(0)

if indexFolder[-1] == '/':
	indexFolder = indexFolder[:-1]

count_words = 1
docFolder = indexFolder + "/docTitle/" 
idfFolder = indexFolder + "/IDF"

secondary = open(indexFolder + "/secondary.txt","r") 
# higher weightage to title
weights = {'t':1000, 'b':10, "r":10, "c":10, "i":10}
	
# porter stemmer
ps = Stemmer("porter")

regEx = re.compile(r'[.,:;_\[\]{}()"/\']',re.DOTALL)
regSym = re.compile(r'[~`!@#$%-^*+{\[}\]\|\\<>/?_\"]',re.DOTALL)

# clean text
def reg_word(word):
	word = re.sub(r"([\n\t ]) *", r" ", word)
	word = regEx.sub(' ', word)
	return word
# load secondary index
def init():
	global secondaryIndexIndices
	for line in secondary:
		split = line.split('@')
		secondaryIndex[split[0]] = split[1][:-1]
	secondaryIndexIndices = list(secondaryIndex)
# print results
def printToFile(freq):
	if len(freq) == 0:
		print("No result found")
		print("")
		return
	result_count = 0
	for x, y in freq:
		result_count += 1
		fptr = open(docFolder + x + ".txt", "r")
		print(fptr.readline(), end = '')
		fptr.close()
		if result_count == 10:
			break
	print("")
# query proceesing
def process(query):
	query = str(query)
	query = query.lower()
	query = reg_word(query)
	words = word_tokenize(query)
	modified_query = []
	for word in words:
		# neglects stopwords and words with length < 3 
		if len(word) >= 3 and word not in stop_words:
			word = ps.stemWord(word)
			modified_query.append(word)
	return modified_query
# fields
# c - category
# r - references
# i - infobox
# b - body
# t - title
fields = ['c', 'r', 'i', 'b', 't']
def search(query):
	query = process(query)
	queryFreq = defaultdict(lambda:0)
	for q in query:
		try:
			# find secondary index corresponding to current query
			ptr = bisect.bisect_left(secondaryIndexIndices, q)
			# primary index for current query
			primaryFile = open(indexFolder + "/primary/primary" + str(secondaryIndex[secondaryIndexIndices[ptr-1]]) + ".txt")
			doc = primaryFile.read()
			# search for current word
			start = doc.find("!" + q + "@")
			wordDocCount = 0
			curType = 'x'
			# find all occurences of word within the loop
			while start != -1:
				end = doc.find("\n", start + 1)
				line = doc[start+1:end]
				line = line.split("@")[1]
				line = line.split(":")
				curType = line[0]
				line = line[1]
				line = line.split(",")
				for x in line:
					cur_split = x.split("-")
					if len(cur_split) != 2:
						continue
					# tf-idf computation
					wordDocCount += 1
					idfval = 180000000/float(len(line))
					queryFreq[cur_split[0]] += math.log10(float(cur_split[1]) * weights[curType]) * math.log10(idfval)
				start = doc.find("!" + str(q) + "@", end + 1)
		except:
			pass
	# return result sorted by tf-idf val
	queryFreq = sorted(queryFreq.items() , reverse=True, key=lambda x: x[1])
	printToFile(queryFreq)

def fieldQueryHelper(query, cur_type, relevance, factor, printFlag):
	query = process(query)
	for q in query:
		try:
			ptr = bisect.bisect_left(secondaryIndexIndices, q)
			if ptr >= len(secondaryIndexIndices):
				return relevance
			primaryFile = open(indexFolder + "/primary/primary" + str(secondaryIndex[secondaryIndexIndices[ptr-1]]) + ".txt")
			doc = primaryFile.read()
			# find current word correponding to given category
			start = doc.find("!" + str(q) + "@" + cur_type + ":")
			if start == -1:
				continue
			end = doc.find("\n", start + 1)
			line = doc[start:end]
			line = line.split("@")[1]
			line = line.split(":")[1]
			line = line.split(",")
			for x in line:
				cur_split = x.split("-")
				if len(cur_split) != 2:
					continue
				idfval = 18000000/float(len(line))
				relevance[cur_split[0]] += math.log10(int(cur_split[1]) + 1) * math.log10(idfval)* factor[cur_split[0]] * weights[cur_type]
				factor[cur_split[0]] *= 10
		except:
			pass
	if printFlag == 1:
		relevance = sorted(relevance.items() , reverse=True, key=lambda x: x[1])
		printToFile(relevance)
	else:
		return relevance
# parse fields
def parse_field(query):
	split = query.split(' ')
	parsed = {}
	prev = '1'
	for data in split:
		cur_split = data.split(':')
		if len(cur_split) < 2:
			parsed[prev] = parsed[prev] + ' ' + cur_split[0]
			continue
		prev = cur_split[0][0]
		parsed[cur_split[0][0]] = cur_split[1]
	return parsed	
def fieldQuery(query):
	size = len(query)
	printToFileLength = 0
	printFlag = 0
	relevance = defaultdict(lambda:0)
	factor = defaultdict(lambda:1)
	for cur_type in query:
		size -= 1
		if size == 0:
			printFlag = 1
		relevance = fieldQueryHelper(query[cur_type], cur_type, relevance, factor, printFlag)
print("Preprocessing...")
init()
print("Preprocessing Done")
while True:
	query = input()
	start_time = time.time()
	if ':' not in query:
		search(query)
	else:
		field = parse_field(query)
		fieldQuery(field)
	end_time = time.time()
	t = float("{0:.4f}".format(end_time - start_time))
	print("Time taken = ", t, "s")
	print("")