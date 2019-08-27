from xml.sax import parse, ContentHandler
import nltk
from collections import defaultdict
import re
from nltk.corpus import stopwords
from spacy.lang.en import English
import time
import spacy

nlp = English()
tokenizer = nlp.Defaults.create_tokenizer(nlp)

# invertedIndex = defaultdict(lambda:defaultdict(int))
invertedIndex = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
dictionary = {}
count_words = 1
docTitle = open("docTitle.txt","w") 

# storing stopwords
f = open("stopwords.txt","r")
stopWords = set()
for line in f:
	line = line.strip()
	stopWords.add(line)
print(stopWords)

# porter stemmer
ps = nltk.stem.PorterStemmer()

regEx = re.compile(r'[.,:;_\[\]{}()"/\']',re.DOTALL)
regSym = re.compile(r'[~`!@#$%-^*+{\[}\]\|\\<>/?_\"]',re.DOTALL)
regCateg = re.compile(r'\[\[category:(.*?)\]\]', re.DOTALL)
regInfo = re.compile(r'{{infobox(.*?)}}', re.DOTALL)
regRef = re.compile(r'== ?references ?==(.*?)==', re.DOTALL)

size_limit = 5000
def addToIndex(words, ID, cur_type):
	global count_words
	for word in words:
		if len(word) >= 3 and word not in stopWords:
			word = ps.stem(word.text)
			if word not in dictionary:
				dictionary[word] = count_words
				count_words += 1
			invertedIndex[dictionary[word]][ID][cur_type] += 1
def reg_word(word):
	word = regSym.sub(' ', word)
	word = regEx.sub(' ', word)
	return word
# Takes a sentence as input and calls the addtoindex function
def parse_sentence(word, ID, title, text):
	word = word.lower()
	if title:
		word = regEx.sub('', word)
		words = tokenizer(word)
		addToIndex(words, ID, 't')
	elif text:
		# finding categories
		categories = re.findall(r'\[\[category:(.*?)\]\]', word, flags=re.MULTILINE)
		word = regCateg.sub('',word)
		categories = ' '.join(categories)
		categories = reg_word(categories)
		categories = tokenizer(categories)
		addToIndex(categories, ID, 'c')
		
		# finding references
		references = re.findall(r'== ?references ?==(.*?)==', word, flags=re.DOTALL)
		word = regRef.sub('',word)
		references = ' '.join(references)
		references = reg_word(references)
		references = tokenizer(references)
		addToIndex(references, ID, 'r')
		
		# content in infobox
		infobox = re.findall(r'{{infobox(.*?)}}', word, flags=re.DOTALL)
		word = regInfo.sub('',word)
		infobox = ' '.join(infobox)
		infobox = reg_word(infobox)
		infobox = tokenizer(infobox)
		addToIndex(infobox, ID, 'i')
		
		# body of content
		word = reg_word(word)
		words = tokenizer(word)
		addToIndex(words, ID, 'b')
class WikipediaHandler(ContentHandler):
	def __init__(self):
		self.buffer = ""
		self.ID = 0
		self.titleFlag = 0
		self.textFlag = 0
		self.idFlag = 0
		self.title = ""
		self.text = ""
	def startElement(self, tag, attributes):
		if tag == "title":
			self.buffer = ""
			self.titleFlag = 1
		if tag == "page":
			self.ID += 1
		if tag == "text":
			self.buffer = ""
			self.textFlag = 1
		if tag == "id":
			self.buffer = ""
			self.idFlag = 1
	def endElement(self, tag):
		if self.titleFlag:
			docTitle.write(str(self.ID) + "@" + self.buffer + "\n")
			parse_sentence(self.buffer, self.ID, 1, 0)
			self.titleFlag = 0
			self.title = self.buffer
			self.buffer = ""
		elif self.textFlag:
			parse_sentence(self.buffer, self.ID, 0, 1)
			self.text = self.buffer
			self.textFlag = 0
			self.buffer = ""
		elif self.idFlag:
			self.buffer = ""
			self.idFlag = 0
	def characters(self,content):
		self.buffer = self.buffer + content
start = time.time()
parse("test_data.xml", WikipediaHandler())
# for key,val in sorted(invertedIndex.items()):
# 	for k,v in sorted(val.items()):
# 		for k1,v1 in v.items():
# 			print(key,k,k1,v1)
# stores the 
fptr1 = open("word_hash.txt","a+")
fptr = open('indexes/1.txt',"w+")
# dictionary[word]@ID:field#freq,
for word, list1 in sorted(invertedIndex.items()):
	output = str(word) + "@"
	for ID, list2 in sorted(list1.items()):
		output += str(ID) + ":"
		for field,freq in list2.items():
			output = output + str(field) + "-" + str(freq) + "#"
	output += ","
	output += "\n"
	fptr.write(output)
fptr.close()
invertedIndex.clear()
for word in dictionary:
	output = word + '#' + str(dictionary[word]) + '\n'
	fptr1.write(output)
fptr1.close()
print(time.time()-start)