import glob
import os
from heapq import heapify, heappush, heappop
from collections import defaultdict

indexFolder = "./indexes/"
index = glob.glob("./indexes/Harsh_Index/*")
fptr = dict()
totalFiles = len(index)
heapObj = list()
line = dict()
words = dict()
invertedIndex = defaultdict(lambda:defaultdict(lambda:""))
secondaryIndex = defaultdict(lambda:0)
secondary = open(indexFolder + "secondary.txt","w+") 
limit = 10000
indexFile = 0

if not os.path.exists(indexFolder + "/primary"):
    os.makedirs(indexFolder + "/primary")

# Creates secondary index word@primary index file no
def writeSecondary():
	for key, val in secondaryIndex.items():
		secondary.write(str(key) + "@" + str(val) + '\n')
	secondaryIndex.clear()

# Creates primary index as word@type:docid-freq
def writePrimary():
	global indexFile
	indexFile += 1
	primary = open(indexFolder + "primary/" + "primary" + str(indexFile) + ".txt" ,"w+") 
	for word, dict1 in invertedIndex.items():
		for curType, val in dict1.items():
			primary.write(word + "@" + curType + ":" + val + '\n')
			secondaryIndex[word] = indexFile
	invertedIndex.clear()
	primary.close()

# initialises heap
for i in range(len(index)):
	fptr[i] = open(index[i], "r")
	line[i] = fptr[i].readline()
	words[i] = line[i].split("@")
	if [words[i][0], words[i][1][0]] not in heapObj:
		heappush(heapObj, [words[i][0], words[i][1][0]])
done = [0] * (totalFiles)
filesDone = 0
primaryBufferSize = 0
# invertedIndex[dictionary[word]] = "string"
# dictionary[word]@field:docid-freq,
prevWord = -1
# Main index merge logic
while filesDone < totalFiles:
	cur = heappop(heapObj)
	# write to primary if buffer size exceeds the limit
	if prevWord != cur[0] and primaryBufferSize > limit: 
		writePrimary()
		primaryBufferSize = 0
	prevWord = cur[0]
	for i in range(totalFiles):
		if done[i] == 1 or words[i][0] != cur[0] or words[i][1][0] != cur[1]:
			continue
		primaryBufferSize += 1
		invertedIndex[cur[0]][cur[1]] += (words[i][1].split(":")[1])
		invertedIndex[cur[0]][cur[1]] = invertedIndex[cur[0]][cur[1]][:-1]
		line[i] = fptr[i].readline()
		if line[i]:
			words[i] = line[i].split("@")
			if [words[i][0], words[i][1][0]] not in heapObj:
				heappush(heapObj, [words[i][0], words[i][1][0]])
		else:
			filesDone += 1
			fptr[i].close()
			done[i] = 1
			# os.remove(index[i])

writePrimary()
writeSecondary()