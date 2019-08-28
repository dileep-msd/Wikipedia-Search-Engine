from collections import defaultdict
import re
from spacy.lang.en import English
import time
import spacy
from Stemmer import Stemmer

nlp = English()
tokenizer = nlp.Defaults.create_tokenizer(nlp)

# invertedIndex = defaultdict(lambda:defaultdict(int))
invertedIndex = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
dictionary = {}
count_words = 1
docTitle = open("docTitle.txt","r") 
index = open("indexes/1.txt","r") 
wordh = open("word_hash.txt","r") 
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
				print(x)
				if flag[x] == 0:
					intersect[x] += 1
					flag[x] = 1
		flag.clear()
	co = 0
	freq = sorted(freq.items() , reverse=True, key=lambda x: x[1])
	for x,y in freq:
		if len(query) - intersect[x] > 1:
			continue
		co += 1
		print(docTitleMapping[x], end='')
		if co == 10:
			break
start = time.time()
init()
query = "new york mayor"
search(query)
print(time.time()-start)