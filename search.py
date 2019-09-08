from collections import defaultdict
import re
from spacy.lang.en import English
import time
import spacy
from Stemmer import Stemmer
import sys
import math
import bisect

# dump = sys.argv[1]
# indexFolder = sys.argv[2]
indexFolder = "./indexes"
secondaryIndex = defaultdict(lambda:0)
secondaryIndexIndices = []
totalDocs = 0

nlp = English()
tokenizer = nlp.Defaults.create_tokenizer(nlp)

# indexFolder = sys.argv[1]
# testFile = sys.argv[2]
# outputFile = sys.argv[3]
# outputWrite = open(outputFile,"w+") 


invertedIndex = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
dictionary = {}
count_words = 1
docTitle = open(indexFolder + "/docTitle.txt","r") 
secondary = open(indexFolder + "/secondary.txt","r") 
wordh = open(indexFolder+"/word_hash.txt","r") 
idfVal = open(indexFolder+"/idf.txt","r") 
docTitleMapping = []
wordHash = []
idf = []
weights = {'t':1000, 'b':1, "r":10, "c":10, "i":10}


	
# porter stemmer
ps = Stemmer("porter")

regEx = re.compile(r'[.,:;_\[\]{}()"/\']',re.DOTALL)
regSym = re.compile(r'[~`!@#$%-^*+{\[}\]\|\\<>/?_\"]',re.DOTALL)

def reg_word(word):
	word = re.sub(r"([\n\t ]) *", r" ", word)
	word = regSym.sub(' ', word)
	word = regEx.sub(' ', word)
	return word
def init():
	global secondaryIndexIndices, totalDocs
	docTitleMapping.append("No result found")
	for line in docTitle:
		docTitleMapping.append(line.split("@")[1])
		totalDocs += 1
	wordHash.append("No record")
	for line in wordh:
		wordHash.append(line.split('#')[0])
	idf.append("No record")
	for line in idfVal:
		idf.append(float(line.split('#')[1]))
	co = 0
	for line in secondary:
		split = line.split('@')
		secondaryIndex[int(split[0])] = split[1][:-1]
	secondaryIndexIndices = list(secondaryIndex)
def process(query):
	query = query.lower()
	query = reg_word(query)
	words = tokenizer(query)
	modified_query = []
	for word in words:
		if len(word) >= 2 and not nlp.vocab[word.text].is_stop:
			word = ps.stemWord(word.text)
			if word not in wordHash:
				continue
			modified_query.append(wordHash.index(word))
	return modified_query
fields = ['c', 'r', 'i', 'b', 't']
printToFileLength = 0
def printToFile(freq):
	result_count = 0
	for x, y in freq:
		result_count += 1
		# print(x, y)
		print(docTitleMapping[int(x)], end='')
		# print(freq[x])
		# outputWrite.write(docTitleMapping[x])
		if result_count == 10:
			break
def search(query):
	query = process(query)
	freq = defaultdict(lambda:0)
	intersect = defaultdict(lambda:0)
	flag = defaultdict(lambda:0)
	queryFreq = defaultdict(lambda:0)
	for q in query:
		ptr = bisect.bisect_left(secondaryIndexIndices, q)
		if secondaryIndexIndices[ptr] != q:
			continue
		primaryFile = open(indexFolder + "/primary/primary" + str(secondaryIndex[ptr]) + ".txt")
		doc = primaryFile.read()
		start = doc.find(str(q) + "@")
		wordDocCount = 0
		curType = 'x'
		while start != -1:
			end = doc.find("\n", start + 1)
			line = doc[start:end]
			line = line.split("@")[1]
			line = line.split(":")
			curType = line[0]
			line = line[1]
			line = line.split(",")
			for x in line:
				cur_split = x.split("-")
				if len(cur_split) != 2:
					continue
				wordDocCount += 1
				queryFreq[cur_split[0]] += math.log10(int(cur_split[1]) * weights[curType]) * idf[q]	
			start = doc.find(str(q) + "@", end + 1)
	queryFreq = sorted(queryFreq.items() , reverse=True, key=lambda x: x[1])
	printToFile(queryFreq)

def fieldQueryHelper(query, cur_type, relevance, factor, printFlag):
	query = process(query)
	for q in query:
		ptr = bisect.bisect_left(secondaryIndexIndices, q)
		if secondaryIndexIndices[ptr] != q:
			continue
		primaryFile = open(indexFolder + "/primary/primary" + str(secondaryIndex[ptr]) + ".txt")
		doc = primaryFile.read()
		start = doc.find(str(q) + "@" + cur_type + ":")
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
			relevance[cur_split[0]] += math.log10(int(cur_split[1]) + 1) * idf[q]* factor[cur_split[0]] * weights[cur_type]
			factor[cur_split[0]] *= 10
			# print(docTitleMapping[int(cur_split[0])], end='')
			# print(cur_split[1], cur_type,  math.log10(int(cur_split[1])+1) * idf[q])
	if printFlag == 1:
		relevance = sorted(relevance.items() , reverse=True, key=lambda x: x[1])
		printToFile(relevance)
	else:
		return relevance
def parse_field(query):
	split = query.split(' ')
	parsed = {}
	prev = '1'
	for data in split:
		cur_split = data.split(':')
		if len(cur_split) < 2:
			parsed[prev] = parsed[prev] + ' ' + 	cur_split[0]
			continue
		prev = cur_split[0][0]
		parsed[cur_split[0][0]] = cur_split[1]
	return parsed	
def fieldQuery(query):
	size = len(query)
	printToFileLength = 0
	printFlag = 0
	freq = defaultdict(lambda:0)
	intersect = defaultdict(lambda:0)
	relevance = defaultdict(lambda:0)
	factor = defaultdict(lambda:1)
	for cur_type in query:
		size -= 1
		if size == 0:
			printFlag = 1
		relevance = fieldQueryHelper(query[cur_type], cur_type, relevance, factor, printFlag)
# def read_file(testfile):
#     with open(testfile, 'r') as file:
#         queries = file.readlines()
#     return queries
init()
# query = "title:gandhi body:arjun infobox:gandhi category:gandhi ref:gandhi"
# fieldQuery(parse_field(query))
search("new york mayor")
# queries = read_file(testFile)
# for query in queries:
# 	if ':' not in query:
# 		search(query)
# 	else:
# 		field = parse_field(query)
# 		fieldQuery(field)
