from xml.sax import parse, ContentHandler
import nltk
from collections import defaultdict
import re
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')


# invertedIndex = defaultdict(lambda:defaultdict(int))
invertedIndex = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
docTitle = open("docTitle.txt","w") 

# storing stopwords
stopWords = set(stopwords.words('english'))

# porter stemmer
ps = nltk.stem.PorterStemmer()

regEx = re.compile(r'[.,:;_\[\]{}()"/\']',re.DOTALL)
regSym = re.compile(r"[~`!@#$%-^*+{\[}\]\|\\<>/?_\"]",re.DOTALL)

def addToIndex(words, ID, cur_type):
	for word in words:
		if len(word) >= 3 and word not in stopWords:
			word = ps.stem(word)
			invertedIndex[word][ID][cur_type] += 1
def reg_word(word):
	word = regSym.sub(' ', word)
	word = regEx.sub(' ', word)
	return word
# Takes a sentence as input and calls the addtoindex function
def parse_sentence(word, ID, title, text):
	word = word.lower()
	if title:
		word = regEx.sub(' ', word)
		words = nltk.tokenize.word_tokenize(word)
		addToIndex(words, ID, 't')
	elif text:
		# finding categories
		categories = re.findall(r'\[\[category:(.*?)\]\]', word, flags=re.MULTILINE)
		addToIndex(categories, ID, 'c')
		
		# finding references
		references = re.findall(r'== ?references ?==(.*?)==', word, flags=re.DOTALL)
		references = ' '.join(references)
		references = regSym.sub(' ',references)
		references = references.split()
		addToIndex(references, ID, 'r')
		
		# content in infobox
		infobox = re.findall(r'{{infobox(.*?)}}', word, flags=re.DOTALL)
		infobox = ' '.join(infobox)
		infobox = regSym.sub(' ',infobox)
		infobox = infobox.split()
		addToIndex(infobox, ID, 'i')
		
		# body of content
		word = reg_word(word)
		words = nltk.tokenize.word_tokenize(word)
		addToIndex(infobox, ID, 'b')
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
parse("test_data.xml", WikipediaHandler())