from xml.sax import parse, ContentHandler
from collections import defaultdict
import re
from spacy.lang.en import English
import time
import spacy
from Stemmer import Stemmer

nlp = English()
tokenizer = spacy.tokenizer.Tokenizer(nlp.vocab)

# invertedIndex = defaultdict(lambda:defaultdict(int))
invertedIndex = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
dictionary = {}
count_words = 1
docTitle = open("docTitle.txt","w") 

# porter stemmer
ps = Stemmer("porter")

regEx = re.compile(r'[.,:;_\[\]{}()"/\']',re.DOTALL)
regSym = re.compile(r'[~`!@#$%-^*+{\[}\]\|\\<>/?\_\"]',re.DOTALL)
regCateg = re.compile(r'\[\[category:(.*?)\]\]', re.DOTALL)
regInfo = re.compile(r'{{infobox(.*?)}}', re.DOTALL)
regRef = re.compile(r'== ?references ?==(.*?)==', re.DOTALL)

def addToIndex(words, ID, cur_type):
	global count_words
	for word in words:
		if len(word) >= 3 and not nlp.vocab[word.text].is_stop:
			word = ps.stemWord(word.text)
			if len(word) < 3:
				continue
			if word not in dictionary:
				dictionary[word] = count_words
				count_words += 1
			invertedIndex[dictionary[word]][cur_type][ID] += 1
def reg_word(word):
	word = re.sub(r"([\n\t ]) *", r" ", word)
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
		categories = ' '.join(categories)
		categories = reg_word(categories)
		categories = tokenizer(categories)
		addToIndex(categories, ID, 'c')
		
		# finding references
		references = re.findall(r'== ?references ?==(.*?)==', word, flags=re.DOTALL)
		references = ' '.join(references)
		references = reg_word(references)
		references = tokenizer(references)
		addToIndex(references, ID, 'r')
		
		# content in infobox
		infobox = re.findall(r'{{infobox(.*?)}}', word, flags=re.DOTALL)
		infobox = ' '.join(infobox)
		infobox = reg_word(infobox)
		infobox = tokenizer(infobox)
		addToIndex(infobox, ID, 'i')
		
		# body of content
		word = reg_word(word)
		# words = nlp(word)
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
print(start)
parse("enwiki-latest-pages-articles26.xml-p42567204p42663461", WikipediaHandler())
fptr1 = open("word_hash.txt","a+")
fptr = open('indexes/1.txt',"w+")
# dictionary[word]@field:docid-freq,
for word, list1 in sorted(invertedIndex.items()):
	for field, list2 in sorted(list1.items()):
		output = str(word) + "@" + str(field) + ":"
		for ID,freq in list2.items():
			output += (str(ID) + '-' + str(freq) + ',')
		fptr.write(output + '\n')
fptr.close()
invertedIndex.clear()
for word in dictionary:
	output = word + '#' + str(dictionary[word]) + '\n'
	fptr1.write(output)
fptr1.close()
print(time.time()-start)