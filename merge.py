import glob
import os
from heapq import heapify, heappush, heappop

index = glob.glob("./indexes/Harsh_Index/*")
fptr = dict()
totalFiles = len(index)
heapObj = list()
line = dict()
words = dict()
invertedIndex = dict()

for i in range(len(index)):
	fptr[i] = open(index[i], "r")
	line[i] = fptr[i].readline()
	words[i] = line[i].split("@")
	if [words[i][0], words[i][1][0]] not in heapObj:
		heappush(heapObj, [words[i][0], words[i][1][0]])
done = [0] * (totalFiles + 1)
# invertedIndex[dictionary[word]][cur_type][ID] += 1
# dictionary[word]@field:docid-freq,
while totalFiles > 0:
	print("size ",len(heapObj), totalFiles)
	cur =  heappop(heapObj)
	for i in range(totalFiles):
		if done[i] == 1 or words[i][0] != cur[0] or words[i][1][0] != cur[1]:
			continue
		if cur[0] not in invertedIndex:
			invertedIndex[cur[0]] = words[i][1]
		else:
			invertedIndex[cur[0]] += ("," + words[i][1].split(":")[1])
		line[i] = fptr[i].readline()
		if line[i]:
			words[i] = line[i].split("@")
			if [words[i][0], words[i][1][0]] not in heapObj:
				heappush(heapObj, [words[i][0], words[i][1][0]])
		else:
			totalFiles -= 1
			fptr[i].close()
			# os.remove(index[i])