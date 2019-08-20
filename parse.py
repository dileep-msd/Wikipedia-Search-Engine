from xml.sax import parse, ContentHandler
import nltk
from collections import defaultdict
import re
nltk.download('punkt')


invertedIndex = defaultdict(lambda:defaultdict(int))

# storing stopwords
stopWords = set()
try:
	f = open('stop_words.txt', "r")
	line = f.readline()
	while line:
		line = line.strip()
		stopWords.add(line)
		line = f.readline()
	f.close()
except:
	print("Unable to open stopwords.txt")

# remove punctuations, dotall matches all characters including a new line
regEx = re.compile(r'[.,:;_\[\]{}()"/\']',re.DOTALL)

def addToIndex(words, ID):
	ps = nltk.stem.PorterStemmer()
	for word in words:
		if word not in stopWords:
			word = ps.stem(word)
			invertedIndex[word][ID] += 1
			# print(word, ID,invertedIndex[word][ID])

# Takes a sentence as input and calls the addtoindex function
def parse_sentence(word, ID, title, text):
	word = regEx.sub(' ', word)
	word = word.lower()
	words = nltk.tokenize.word_tokenize(word)
	if title:
		addToIndex(words, ID)
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
			parse_sentence(self.buffer, self.ID, 1, 0)
			self.titleFlag = 0
			self.Title = self.buffer
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
parse("enwiki-latest-pages-articles26.xml-p42567204p42663461", WikipediaHandler())