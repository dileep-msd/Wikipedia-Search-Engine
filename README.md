# Wikipedia-Search-Engine
A Mini-Wikipedia search engine, which creates the inverted index of a given wikipedia dump, queries on the index and retrieves top 10 results via relevance ranking of the documents(implemented via tf-idf scoring).

### Requirements
* python 3
### Setting up conda environment
* Use [environment.yml](../master/environment.yml)
* Install conda
* Run``` conda env create -f environment.yml```
*  Run ```conda activate wiki-search```
### Instructions for running
* **Index creation**
```
bash index.sh <path_to_dump> <index folder>
```
* **Searching**
```
bash search.sh <path_to_index>
```
* [enwiki-latest-pages-articles26.xml-p42567204p42663461.bz2](../master/enwiki-latest-pages-articles26.xml-p42567204p42663461.bz2) contains about 100MB of wiki dump. Download entire Wiki dump from [https://dumps.wikimedia.org/enwiki/latest/](https://dumps.wikimedia.org/enwiki/latest/).

### Query Format
  * **Normal query** - Enter words
  * **Field query** - title:TITLE category:CATEGORY infobox:INFO ref:REFERENCE body:BODY
