from collections import defaultdict
import re
from spacy.lang.en import English
import time
import spacy
from Stemmer import Stemmer
import sys

dump = sys.argv[1]
indexFolder = sys.argv[2]


nlp = English()
tokenizer = nlp.Defaults.create_tokenizer(nlp)

indexFolder = sys.argv[1]
testFile = sys.argv[2]
outputFile = sys.argv[3]
outputWrite = open(outputFile,"w+") 


invertedIndex = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
dictionary = {}
count_words = 1
docTitle = open(indexFolder + "/docTitle.txt","r") 
index = open(indexFolder + "/1.txt","r") 
wordh = open(indexFolder+"/word_hash.txt","r") 
docTitleMapping = []
wordHash = []




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
	docTitleMapping.append("No result found")
	for line in docTitle:
		docTitleMapping.append(line.split("@")[1])
	wordHash.append("No record")
	for line in wordh:
		wordHash.append(line.split('#')[0])
	co = 0
	for line in index:
		split = line.split('@')
		word = int(split[0])
		split = split[1].split(':')
		field = split[0]
		split = split[1].split(',')
		for x in split:
			try:
				docfreq = x.split('-')
				invertedIndex[word][field][int(docfreq[0])] += int(docfreq[1])
			except:
				pass
def process(query):
	query = query.lower()
	query = reg_word(query)
	words = tokenizer(query)
	modified_query = []
	for word in words:
		if len(word) >= 3 and not nlp.vocab[word.text].is_stop:
			word = ps.stemWord(word.text)
			if word not in wordHash:
				continue
			modified_query.append(wordHash.index(word))
	return modified_query
fields = ['c', 'r', 'i', 'b', 't']
def search(query):
	query = process(query)
	freq = defaultdict(lambda:0)
	intersect = defaultdict(lambda:0)
	flag = defaultdict(lambda:0)
	for q in query:
		for field in fields:
			docFreq = invertedIndex[q][field]
			for x,y in docFreq.items():
				freq[x] += y
				if flag[x] == 0:
					intersect[x] += 1
					flag[x] = 1
		flag.clear()
	result_count = 0
	freq = sorted(freq.items() , reverse=True, key=lambda x: x[1])
	for x,y in freq:
		if len(query) - intersect[x] > 1:
			continue
		result_count += 1
		outputWrite.write(docTitleMapping[x])
		if result_count == 10:
			break
	outputWrite.write('\n')
def printToFile(freq, intersect, length):
	result_count = 0
	for x,y in freq:
		if length - intersect[x] > 1:
			continue
		result_count += 1
		outputWrite.write(docTitleMapping[x])
		if result_count == 10:
			break
	outputWrite.write('\n')
def fieldQueryHelper(query, cur_type, docs, printFlag):
	new_docs = []
	query = process(query)
	freq = defaultdict(lambda:0)
	intersect = defaultdict(lambda:0)
	flag = defaultdict(lambda:0)
	if len(docs) == 0:
		for q in query:
			docFreq = invertedIndex[q][cur_type]
			for x,y in docFreq.items():
				freq[x] += y
				if flag[x] == 0:
					intersect[x] += 1
					flag[x] = 1
			flag.clear()
	else:
		for q in query:
			for x in docs:
				freq[x] += invertedIndex[q][cur_type][x]
				if flag[x] == 0:
					intersect[x] += 1
					flag[x] = 1
			flag.clear()
	if printFlag == 1:
		freq = sorted(freq.items() , reverse=True, key=lambda x: x[1])
		printToFile(freq, intersect, len(query))
	else:
		freq = sorted(freq.items() , reverse=True, key=lambda x: x[1])
		for x,y in freq:
			if len(query) - intersect[x] > 1:
				continue
			new_docs.append(x)
		return new_docs
def parse_field(query):
	split = query.split(' ')
	parsed = {}
	for data in split:
		cur_split = data.split(':')
		parsed[cur_split[0][0]] = cur_split[1]
	return parsed	
def fieldQuery(query):
	size = len(query)
	printFlag = 0
	for cur_type in query:
		size -= 1
		if size == -1:
			printFlag = 1
		docs = fieldQueryHelper(query[cur_type], cur_type, [], printFlag)
		break
	for cur_type in query:
		size -= 1
		if size == -1:
			printFlag = 1
		docs = fieldQueryHelper(query[cur_type], cur_type, docs, printFlag)
def read_file(testfile):
    with open(testfile, 'r') as file:
        queries = file.readlines()
    return queries
start = time.time()
init()
queries = read_file(testFile)
for query in queries:
	if ':' not in query:
		search(query)
	else:
		field = parse_field(query)
		fieldQuery(field)
print(time.time()-start)