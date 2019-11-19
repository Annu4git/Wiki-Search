import xml.sax
import spacy
from nltk.stem import *
from nltk.stem.snowball import SnowballStemmer
import re
import sys
from helper import *
import math

nlp = spacy.load('en')
stemmer = SnowballStemmer("english")
stop_words = spacy.lang.en.stop_words.STOP_WORDS

path_to_data_dump = ""
path_to_index_folder = ""
path_to_title_folder = ""

inverted_index = {}
doc_id_word_count = {}

index_file_count = 0
title_file_count = 0
doc_count = 0
title_count = 0

MAX_DOC_COUNT=5000
MAX_TITLE_COUNT=1000

inverted_index_file = ""
title_file = ""

regExp1 = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',re.DOTALL)
regExp2 = re.compile(r'{\|(.*?)\|}',re.DOTALL)
regExp3 = re.compile(r'{{v?cite(.*?)}}',re.DOTALL)
regExp4 = re.compile(r'[-.,:;_?()"/\']',re.DOTALL)
regExp5 = re.compile(r'\[\[file:(.*?)\]\]',re.DOTALL)
regExp6 = re.compile(r'[\'~` \n\"_!=@#$%-^*+{\[}\]\|\\<>/?]',re.DOTALL)
catRegExp = r'\[\[category:(.*?)\]\]'
infoRegExp = r'{{infobox(.*?)}}'
refRegExp = r'== ?references ?==(.*?)=='
regExp7 = re.compile(infoRegExp,re.DOTALL)
regExp8 = re.compile(refRegExp,re.DOTALL)
regExp9 = re.compile(r'{{(.*?)}}',re.DOTALL)
regExp10 = re.compile(r'<(.*?)>',re.DOTALL)

def isValid(word):
	if word == "" or word in stop_words or len(word) < 3:
			return False
	try:
		word.encode(encoding='utf-8').decode('ascii')
	except UnicodeDecodeError:
		return False
	else:
		return True

def remove_new_line(text):
	text = text.replace('\'', '')
	text = text.strip()
	return text.replace('\n', ' ')

def replace_square_brackets(text):
	text = text.replace('[', ' ')
	text = text.replace(']', ' ')
	return text

def clean(tokenList):
	tokenList = ' '.join(tokenList)
	tokenList = regExp4.sub(' ',tokenList)
	tokenList = regExp5.sub(' ',tokenList)
	tokenList = regExp6.sub(' ',tokenList)
	tokenList = replace_square_brackets(tokenList)
	tokenList = tokenList.split()
	return tokenList

def create_inverted_index(obj):

	word_count_in_curr_doc = 0

	global index_file_count, title_count, title_file_count, doc_count
	global inverted_index, inverted_index_file, path_to_data_dump
	global path_to_index_folder, title_file, path_to_title_folder
	global MAX_TITLE_COUNT, MAX_DOC_COUNT, doc_id_word_count

	doc_id = obj.id
	title = obj.title
	body = obj.body

	doc_map = {}
	title_map = {}
	body_map = {}
	infobox_map = {}
	category_map = {}
	external_link_map = {}
	reference_map = {}
	
	
	title_to_write = title

	title = title.lower()
	flag = 0
	
	title = regExp4.sub(' ', title)
	title = regExp5.sub(' ', title)
	title = regExp6.sub(' ', title)
	title = regExp10.sub(' ', title)
	title = remove_new_line(title)
	
	title = title.split()
	for token in title:
		word = stemmer.stem(token)
		if isValid(word):
			word_count_in_curr_doc += 1
			if word not in title_map:
				title_map[word] = 1
			else:
				title_map[word] += 1

	body = body.lower()
	body = regExp1.sub(' ', body)
	body = regExp2.sub(' ', body)
	body = regExp3.sub(' ', body)
	body = regExp10.sub(' ', body)
	body = remove_new_line(body)

	infobox = re.findall(infoRegExp, body, re.DOTALL)
	
	for infoList in infobox:
		tokenList = re.findall(r'=(.*?)\|',infoList,re.DOTALL)
		tokenList = clean(tokenList)
		for token in tokenList:
			word = stemmer.stem(token)
			word = remove_new_line(word)
			if isValid(word):
				word_count_in_curr_doc += 1
				if word not in infobox_map:
					infobox_map[word] = 1
				else:
					infobox_map[word] += 1

	categories = re.findall(catRegExp, body, flags=re.MULTILINE)
	
	for category in categories:
		tokenList = category.split()
		tokenList = clean(tokenList)
		for token in tokenList:
			word = stemmer.stem(token)
			word = remove_new_line(word)
			if isValid(word):
				word_count_in_curr_doc += 1
				if word not in category_map:
					category_map[word] = 1
				else:
					category_map[word] += 1

	category_index = -1
	try:
		category_index = body.index('[[category:')+20
	except:
		pass
	
	if category_index == -1:
		category_index = len(body)

	external_links = []
	external_links_index = -1
	try:
		external_links_index = body.index('=external links=')+20
	except:
		pass
	if external_links_index != -1:
		external_links = body[external_links_index : category_index]
		external_links = re.findall(r'\[(.*?)\]', external_links, flags=re.MULTILINE)

		tokenList = external_links
		tokenList = clean(tokenList)
		for token in tokenList:
			word = stemmer.stem(token)
			word = remove_new_line(word)
			if isValid(word):
				word_count_in_curr_doc += 1
				if word not in external_link_map:
					external_link_map[word] = 1
				else:
					external_link_map[word] += 1

		references = []
		references = re.findall(refRegExp, body, flags=re.DOTALL)
		tokenList = clean(references)
		not_references = ['reflist', 'ref', 'em', 'colwidth']

		for token in tokenList:
			word = stemmer.stem(token)
			word = remove_new_line(word)
			if isValid(word) and word not in not_references:
				word_count_in_curr_doc += 1
				if word not in reference_map:
					reference_map[word] = 1
				else:
					reference_map[word] += 1

	body = regExp4.sub(' ', body)
	body = regExp5.sub(' ', body)
	body = regExp6.sub(' ', body)
	body = regExp7.sub(' ', body)
	body = body.split()

	for token in body:
		word = stemmer.stem(token)
		word = remove_new_line(word)
		if isValid(word):
			word_count_in_curr_doc += 1
			if word not in body_map:
				body_map[word] = 1
			else:
				body_map[word] += 1
	
	title_count += 1
	# line_to_write = str(doc_id) + "#" + str(word_count_in_curr_doc) + "#" + str(title_to_write)
	line_to_write_in_title_file = str(title_to_write)
	line_to_write_in_title_file = line_to_write_in_title_file.strip() + "\n"
	title_file.write(line_to_write_in_title_file)

	doc_id_word_count[doc_id] = word_count_in_curr_doc

	add_in_inverted_index(title_map, "title", doc_id)
	add_in_inverted_index(body_map, "body", doc_id)
	add_in_inverted_index(infobox_map, "infobox", doc_id)
	add_in_inverted_index(category_map, "category", doc_id)
	add_in_inverted_index(external_link_map, "external_links", doc_id)
	add_in_inverted_index(reference_map, "references", doc_id)

	doc_count += 1
	if doc_count == MAX_DOC_COUNT:
		print("Dump inverted index into file : " + str(index_file_count))
		dump_inverted_index()
		doc_id_word_count = {}
		doc_count = 0
		index_file_count += 1
		inverted_index = {}
	
	if title_count == MAX_TITLE_COUNT:
		print("Title file : " + str(title_file_count) + " ended on doc id : " + str(doc_id))
		title_count = 0
		title_file_count += 1
		title_file.close()
		title_file = open(path_to_title_folder + "/" + "title_" + str(title_file_count) + ".txt","w")

	

	# end of create_inverted_index function

def add_in_inverted_index(curr_map, curr_type, doc_id):
	global inverted_index

	for word in curr_map:
		if word not in inverted_index:
			inverted_index[word] = {}
		if doc_id not in inverted_index[word]:
			inverted_index[word][doc_id] = {}
		inverted_index[word][doc_id][curr_type] = curr_map[word]

def dump_inverted_index():
	global index_file_count, doc_count, inverted_index, inverted_index_file, path_to_data_dump, path_to_index_folder
	global doc_id_word_count

	inverted_index_file = open(path_to_index_folder + "/" + "inverted_index_" + str(index_file_count) + ".txt","w")

	words = sorted(inverted_index.keys())
	for word in words:
		
		line_to_write = "" + str(word)
		doc_id_freq_map = inverted_index[word]
		for doc_id in sorted(doc_id_freq_map.keys()):
			word_count = 0
			line_to_write += "#" + str(doc_id)
			if "title" in inverted_index[word][doc_id]:
				title_freq = inverted_index[word][doc_id]["title"]
				word_count += title_freq
				line_to_write += "t" # + str(title_freq)
			if "body" in inverted_index[word][doc_id]:
				body_freq = inverted_index[word][doc_id]["body"]
				word_count += body_freq
				line_to_write += "b" # + str(body_freq)
			if "infobox" in inverted_index[word][doc_id]:
				infobox_freq = inverted_index[word][doc_id]["infobox"]
				word_count += infobox_freq
				line_to_write += "i" # + str(infobox_freq)
			if "category" in inverted_index[word][doc_id]:
				category_freq = inverted_index[word][doc_id]["category"]
				word_count += category_freq
				line_to_write += "c" # + str(category_freq)
			if "external_links" in inverted_index[word][doc_id]:
				external_link_freq = inverted_index[word][doc_id]["external_links"]
				word_count += external_link_freq
				line_to_write += "e" # + str(external_link_freq)
			if "references" in inverted_index[word][doc_id]:
				reference_freq = inverted_index[word][doc_id]["references"]
				word_count += reference_freq
				line_to_write += "r" # + str(reference_freq)

			tf = word_count/doc_id_word_count[doc_id]
			tf = round(math.log(1 + tf, 10), 3)
			tf = int(tf*1000)
			print(tf)
			line_to_write += "@" + str(tf)
			
		# input("here")
		# print(int(line_to_write[0]))
		inverted_index_file.write(line_to_write + "\n")
	
	inverted_index_file.close()
	
	#end of func

class Wiki( xml.sax.ContentHandler ):
	def __init__(self):
		self.current_tag = ""
		self.title = ""
		self.id = 0
		self.body = ""
	
	def startElement(self, tag, attributes):
		self.current_tag = tag
	
	def endElement(self, tag):
		if tag == "page":
			create_inverted_index(self)
			self.title = ""
			self.id += 1
			self.body = ""

	def characters(self, content):
		if self.current_tag == "title":
			self.title += content
		if self.current_tag == "text":
			self.body += content

		# if self.current_tag == "id":
		# 	if self.id == "":
		# 		self.id = content

def parse_xml(path_to_data_dump):
	parser = xml.sax.make_parser()
	parser.setFeature(xml.sax.handler.feature_namespaces, 0)
	wiki = Wiki()
	parser.setContentHandler(wiki)
	parser.parse(path_to_data_dump)


def main():

	global index_file_count, doc_count, inverted_index, inverted_index_file
	global path_to_data_dump, path_to_index_folder, title_file, path_to_title_folder

	path_to_data_dump = sys.argv[1]
	path_to_index_folder = sys.argv[2]

	if not os.path.exists(path_to_index_folder):
		os.makedirs(path_to_index_folder)

	path_to_title_folder = path_to_index_folder + "/" + "title_folder"
	if not os.path.exists(path_to_title_folder):
		os.makedirs(path_to_title_folder)

	global MAX_TITLE_COUNT, MAX_DOC_COUNT
	# read config.txt
	config_file = open("config.txt","r")
	line = config_file.readline()
	MAX_DOC_COUNT = int(line[line.find("=")+1:])
	line = config_file.readline()
	MAX_TITLE_COUNT = int(line[line.find("=")+1:])
	# print(MAX_DOC_COUNT)
	# print(MAX_TITLE_COUNT)

	inverted_index_file = open(path_to_index_folder + "/" + "inverted_index_" + str(index_file_count) + ".txt","w")
	title_file = open(path_to_title_folder + "/" + "title_" + str(title_file_count) + ".txt","w")

	parse_xml(path_to_data_dump)

	dump_inverted_index()
	doc_count = 0
	index_file_count += 1
	inverted_index = {}
	inverted_index_file.close()

	#print(sorted(inverted_index.keys()))
	#print(inverted_index)

	merge_inverted_index(path_to_index_folder, index_file_count)

if __name__ == "__main__": 
	main() 
