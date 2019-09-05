from collections import defaultdict
import re
from spacy.lang.en import English
import time
import spacy
from Stemmer import Stemmer
import sys
from bisect import bisect

# dump = sys.argv[1]
# indexFolder = sys.argv[2]
indexFolder = "./indexes"
secondaryIndex = defaultdict(lambda:0)

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
	for line in secondary:
		split = line.split('@')
		secondaryIndex[int(split[0])] = split[1][:-1]
		# split = split[1].split(':')
		# field = split[0]
		# split = split[1].split(',')
		# for x in split:
		# 	try:
		# 		docfreq = x.split('-')
		# 		invertedIndex[word][field][int(docfreq[0])] += int(docfreq[1])
		# 	except:
		# 		pass
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
def search(query):
	query = process(query)
	freq = defaultdict(lambda:0)
	intersect = defaultdict(lambda:0)
	flag = defaultdict(lambda:0)
	# print(query)
	for q in query:
		len(secondaryIndex)
		# ptr = bisect(secondaryIndex.items(), q)
	# print(secondaryIndex)
	# for q in query:
	# 	for field in fields:
	# 		check = invertedIndex.get(q, "None")
	# 		if check == "None":
	# 			continue
	# 		check = check.get(field, "None")
	# 		if check == "None":
	# 			continue
	# 		docFreq = check
	# 		for x,y in docFreq.items():
	# 			freq[x] += y
	# 			if flag[x] == 0:
	# 				intersect[x] += 1
	# 				flag[x] = 1
	# 	flag.clear()
	# result_count = 0
	# freq = sorted(freq.items() , reverse=True, key=lambda x: x[1])
	# for x,y in freq:
	# 	if len(query) - intersect[x] != 0:
	# 		continue
	# 	result_count += 1
	# 	print(docTitleMapping[x])
	# 	# outputWrite.write(docTitleMapping[x])
	# 	if result_count == 10:
	# 		break
	# cur_lim = 1
	# while result_count < 5 and cur_lim < len(query):
	# 	for x,y in freq:
	# 		if len(query) - intersect[x] != cur_lim:
	# 			continue
	# 		result_count += 1
	# 		print(docTitleMapping[x])
	# 		# outputWrite.write(docTitleMapping[x])
	# 		if result_count == 10:
	# 			break
	# 	cur_lim += 1
	# outputWrite.write('\n')
printToFileLength = 0
def printToFile(freq, intersect):
	result_count = 0
	for x,y in freq:
		if printToFileLength - intersect[x] > 1:
			continue
		result_count += 1
		print(docTitleMapping[x])
		# outputWrite.write(docTitleMapping[x])
		if result_count == 10:
			break
	cur_lim = 2
	while result_count < 5 and cur_lim < printToFileLength:
		for x,y in freq:
			if printToFileLength - intersect[x] != cur_lim:
				continue
			result_count += 1
			print(docTitleMapping[x])
			# outputWrite.write(docTitleMapping[x])
			if result_count == 10:
				break
		cur_lim += 1
	# outputWrite.write('\n')
def fieldQueryHelper(query, cur_type, docs, printFlag, freq, intersect):
	new_docs = []
	query = process(query)
	global printToFileLength
	printToFileLength += len(query)
	flag = defaultdict(lambda:0)
	if len(docs) == 0:
		for q in query:
			check = invertedIndex.get(q, "None")
			if check == "None":
				continue
			check = check.get(cur_type, "None")
			if check == "None":
				continue
			docFreq = check
			for x,y in docFreq.items():
				freq[x] += y
				if flag[x] == 0:
					intersect[x] += 1
					flag[x] = 1
			flag.clear()
	else:
		for q in query:
			for x in docs:
				check = invertedIndex.get(q, "None")
				if check == "None":
					continue
				check = check.get(cur_type, "None")
				if check == "None":
					continue
				check = check.get(x, "None")
				if check == "None":
					continue
				freq[x] += check
				if flag[x] == 0:
					intersect[x] += 1
					flag[x] = 1
			flag.clear()
	if printFlag == 1:
		freq = sorted(freq.items() , reverse=True, key=lambda x: x[1])
		printToFile(freq, intersect)
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
	for cur_type in query:
		size -= 1
		if size == -1:
			printFlag = 1
		docs = fieldQueryHelper(query[cur_type], cur_type, [], printFlag, freq, intersect)
		break
	for cur_type in query:
		size -= 1
		if size == -1:
			printFlag = 1
		docs = fieldQueryHelper(query[cur_type], cur_type, docs, printFlag, freq, intersect)
# def read_file(testfile):
#     with open(testfile, 'r') as file:
#         queries = file.readlines()
#     return queries
init()
# secondaryIndex = list(secondaryIndex)
query = "new york mayor"
search(query)
# queries = read_file(testFile)
# for query in queries:
# 	if ':' not in query:
# 		search(query)
# 	else:
# 		field = parse_field(query)
# 		fieldQuery(field)
