import xml.sax
import spacy
from nltk.stem import *
from nltk.stem.snowball import SnowballStemmer
import re
from collections import OrderedDict
import sys
import bisect
import heapq
import math
import time

MAX_TITLE_COUNT = 0
MAX_DOC_COUNT = 0

regExp1 = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',re.DOTALL)
regExp2 = re.compile(r'{\|(.*?)\|}',re.DOTALL)
regExp3 = re.compile(r'{{v?cite(.*?)}}',re.DOTALL)
regExp4 = re.compile(r'[.,;_()"/\']',re.DOTALL)
regExp5 = re.compile(r'\[\[file:(.*?)\]\]',re.DOTALL)
regExp6 = re.compile(r"[~`'!@#$%-^*+{\[}\]\|\\<>/?]",re.DOTALL)
catRegExp = r'\[\[category:(.*?)\]\]'
infoRegExp = r'{{infobox(.*?)}}'
refRegExp = r'== ?references ?==(.*?)=='
regExp7 = re.compile(infoRegExp,re.DOTALL)
regExp8 = re.compile(refRegExp,re.DOTALL)
regExp9 = re.compile(r'{{(.*?)}}',re.DOTALL)
regExp10 = re.compile(r'<(.*?)>',re.DOTALL)
regExp11 = re.compile(r"[~`!@#$%-^*+{\[}\]\|\\<>/?]",re.DOTALL)

nlp = spacy.load('en')
stemmer = SnowballStemmer("english")
stop_words = spacy.lang.en.stop_words.STOP_WORDS

def get_types(word):
	return [char for char in word]

def get_secondary_index_list(secondary_index_path):
	secondary_index_path += "/" + "secondary_index.txt"
	secondary_index = open(secondary_index_path,"r")

	secondary_index_list = []
	for word in secondary_index:
		secondary_index_list.append(word[:-1])

	return secondary_index_list

def get_postings(secondary_index_list, word_to_search, path_to_final_index):
	
	final_index_no = bisect.bisect(secondary_index_list, word_to_search)

	# print(word_to_search)
	# print("")
	# print(final_index_no)

	if final_index_no > 0:
		final_index_no -= 1

	# path_to_final_index = "/home/anurag/Desktop/IRE/Mini_Project/Updated/index1/final_index"

	final_index_file = open(path_to_final_index + "/" + "final_" + str(final_index_no) + ".txt", "r")

	postings_to_return = ""
	for postings in final_index_file:
		#print(postings.split("#")[0])
		if postings[:postings.find("#")] == word_to_search:
			# print("Found")
			# print(postings)
			postings_to_return = postings[postings.find("#")+1:-1]

	return postings_to_return

def build_index(path_to_index_folder):
	inverted_index_file = open(path_to_index_folder + "/" + "inverted_index.txt","r")
	page_id_page_title_file = open(path_to_index_folder + "/" + "page_id_page_title.txt","r")

	inverted_index = OrderedDict()
	page_id_page_title_map = OrderedDict()

	for line in inverted_index_file:
		tokens = line.split('#')
		i = 1
		n = len(tokens)
		doc_id_freq_map = OrderedDict()
		word = tokens[0]
		if word == "" or word == " ":
			continue
		while i < n:
			doc_id = -1
			token = tokens[i]
			token = token.strip()
			j = 0
			temp = ""
			while j < len(token) and token[j:j+1].isdigit():
				temp += token[j]
				j+=1
			doc_id = int(temp)
			temp = ""
			page_map = {}
			last_type = ""

			while j < len(token):
				last_type = token[j]
				j+=1
				temp=""
				while j < len(token) and token[j].isdigit():
					temp += token[j]
					j+=1
				page_map[last_type] = int(temp)

			page_total_freq = 0
			for page_type in page_map:
				page_total_freq += page_map[page_type]

			page_map["total"] = page_total_freq
			doc_id_freq_map[doc_id] = page_map
			i = i+1

		inverted_index[word] = doc_id_freq_map
	p=0
	for line in page_id_page_title_file:
		tokens = line.split('#')
		p=p+1
		if len(tokens) > 1:
			page_id_page_title_map[tokens[0]] = tokens[1]
	return inverted_index, page_id_page_title_map

# def get_top_10_doc_ids(doc_id_tfidf_map, doc_id_freq_map):
def get_top_10_doc_ids(doc_id_freq_tfidf_map):

	doc_ids_to_return = []

	list_to_sort = []

	for doc_id in doc_id_freq_tfidf_map:
		list_to_sort.append([[doc_id_freq_tfidf_map[doc_id][0], doc_id_freq_tfidf_map[doc_id][1]], doc_id])
	
	list_to_sort.sort(reverse=True)

	i=0
	for item in list_to_sort:
		doc_ids_to_return.append(item[1])
		i+=1
		if i == 10:
			break

	# list_for_heap = []
	
	# list_for_heap_freq = []
	# for doc_id in doc_id_freq_map:
	# 	freq = doc_id_freq_map[doc_id]
	# 	temp_tuple = (-1*freq, doc_id)
	# 	list_for_heap_freq.append(temp_tuple)

	# heapq.heapify(list_for_heap_freq)

	# i = 0
	# while len(list_for_heap_freq) > 0:
	# 	next_tuple = heapq.heappop(list_for_heap_freq)
	# 	# doc_ids_to_return.append(next_tuple[1])
	# 	doc_id = next_tuple[1]
	# 	tfidf = doc_id_tfidf_map[doc_id]
	# 	temp_tuple = (-1*tfidf, doc_id)
	# 	list_for_heap.append(temp_tuple)
	# 	i+=1
	# 	if i == 10:
	# 		break
	
	# heapq.heapify(list_for_heap)

	# # print("****************************************")
	# # print("")
	# # print(list_for_heap)
	# # print("")
	# # print("****************************************")

	# # print("docids here")
	# # print(list_for_heap)

	# doc_ids_to_return = []

	# while len(list_for_heap) > 0:
	# 	next_tuple = heapq.heappop(list_for_heap)
	# 	doc_ids_to_return.append(next_tuple[1])

	return doc_ids_to_return

def get_title_of_doc(doc_id, path_to_title_folder):

	title_file_no = math.floor(doc_id / MAX_TITLE_COUNT)
	title_no = doc_id % MAX_TITLE_COUNT

	title_file = open(path_to_title_folder + "/" + "title_" + str(title_file_no) + ".txt","r")

	i = 0
	for title in title_file:
		if i == title_no:
			return title
		i+=1

def search(path_to_final_index, path_to_title_folder, query, secondary_index_list):

	global MAX_TITLE_COUNT, MAX_DOC_COUNT

	outputs = []
	
	search_query = query.lower()
	if ":" in search_query:
		query_tokens = search_query.split(":")
		query_types = []
		query_values = []
		i=0
		for token in query_tokens:
			if i == 0:
				query_types.append(token[0:1])
				i += 1
				continue
			if i == len(query_tokens)-1:
				query_values.append(token)
				i += 1
				continue
			query_types.append(token[token.rfind(" ")+1:len(token)][0:1])
			query_values.append(token[0:token.rfind(" ")])
			i+=1
		
		doc_id_freq_tfidf_map = {}
		
		i=0
		while i < len(query_values):
			word = query_values[i].strip()

			word = regExp1.sub(' ', word)
			word = regExp2.sub(' ', word)
			word = regExp3.sub(' ', word)
			word = regExp4.sub(' ', word)
			word = regExp5.sub(' ', word)
			word = regExp6.sub(' ', word)
			word = regExp10.sub(' ', word)
			word = stemmer.stem(word)

			words = word.split()

			for word in words:
				# print("+" + word + "+")
				if word not in stop_words:
					field = query_types[i].strip()
					postings = get_postings(secondary_index_list, word, path_to_final_index)

					# print("word : " + word)

					if len(postings) > 0:
						postings = postings.split("#")
						
						for posting in postings:
							posting = posting.split("@")
							# print(posting)
							if posting != "":
								doc_id = int(re.search(r'\d+', posting[0]).group())
								types = posting[0][len(str(doc_id)):]

								types = get_types(types)
								# print("types")
								# print(types)
								if len(types) > 0 and query_types[i] in types:
									tfidf = int(posting[1])
									if doc_id not in doc_id_freq_tfidf_map:
										temp_tuple = [1, tfidf]
										doc_id_freq_tfidf_map[doc_id] = temp_tuple
										# doc_id_tfidf_map[doc_id] = tfidf
										# doc_id_freq_map[doc_id] = 1
									else:
										temp_tuple = doc_id_freq_tfidf_map[doc_id]
										temp_tuple[0] += 1
										temp_tuple[1] += tfidf
										doc_id_freq_tfidf_map[doc_id] = temp_tuple
									# if doc_id not in doc_id_tfidf_map:
									# 	doc_id_tfidf_map[doc_id] = tfidf
									# 	doc_id_freq_map[doc_id] = 1
									# else:
									# 	doc_id_tfidf_map[doc_id] += tfidf
									# 	doc_id_freq_map[doc_id] += 1

			i+=1

		doc_ids = get_top_10_doc_ids(doc_id_freq_tfidf_map)


		for doc_id in doc_ids:
			doc_id = int(doc_id)
			title = get_title_of_doc(doc_id, path_to_title_folder)
			outputs.append(title[:-1])

	else:
		search_query = regExp1.sub(' ', search_query)
		search_query = regExp2.sub(' ', search_query)
		search_query = regExp3.sub(' ', search_query)
		search_query = regExp4.sub(' ', search_query)
		search_query = regExp5.sub(' ', search_query)
		search_query = regExp6.sub(' ', search_query)
		search_query = regExp10.sub(' ', search_query)
		search_query = search_query.split()

		search_query_keywords = []

		for token in search_query:
			word = stemmer.stem(token)
			# print("+" + word + "+")
			if word not in stop_words:
				search_query_keywords.append(word)

		doc_id_freq_tfidf_map = {}
		for word in search_query_keywords:
			
			postings = get_postings(secondary_index_list, word, path_to_final_index)

			# print("here")
			if len(postings) == 0:
				continue
			# print("word : " + word)
			postings = postings.split("#")
			# print(len(postings))
			for posting in postings:
				posting = posting.split("@")
				# print(posting)
				# print("here")
				if posting == "":
					continue
				doc_id = int(re.search(r'\d+', posting[0]).group())
				tfidf = int(posting[1])
				if doc_id not in doc_id_freq_tfidf_map:
					# print("if")
					temp_tuple = [1, tfidf]
					doc_id_freq_tfidf_map[doc_id] = temp_tuple
					# print(doc_id_freq_tfidf_map[doc_id])
					# doc_id_tfidf_map[doc_id] = tfidf
					# doc_id_freq_map[doc_id] = 1
				else:
					# print("else")
					# print(doc_id_freq_tfidf_map[doc_id])
					temp_tuple = doc_id_freq_tfidf_map[doc_id]
					temp_tuple[0] += 1
					temp_tuple[1] += tfidf
					doc_id_freq_tfidf_map[doc_id] = temp_tuple
					
					
					# doc_id_tfidf_map[doc_id] += tfidf
					# doc_id_freq_map[doc_id] += 1

		# doc_ids = get_top_10_doc_ids(doc_id_tfidf_map, doc_id_freq_map)
		doc_ids = get_top_10_doc_ids(doc_id_freq_tfidf_map)
		
		# print(doc_ids)
		for doc_id in doc_ids:
			doc_id = int(doc_id)
			title = get_title_of_doc(doc_id, path_to_title_folder)
			outputs.append(title[:-1])
		
	return outputs

def write_file(outputs, output_file):
	output_file_handle = open(output_file,"w")
	for output_list in outputs:
		for output in output_list:
			output_file_handle.write(output + "\n")
		output_file_handle.write("\n")

def read_file(query_file):
	query_file_handle = open(query_file,"r")
	queries = []
	for line in query_file_handle:
		queries.append(line)
	return queries

def main():

	global MAX_TITLE_COUNT, MAX_DOC_COUNT

	try:
		path_to_index_folder = sys.argv[1]
		# query_file = sys.argv[2]
		# output_file = sys.argv[3]

		if path_to_index_folder[len(path_to_index_folder)-1] == '/':
			path_to_index_folder = path_to_index_folder[:-1]
		path_to_final_index = path_to_index_folder + "/final_index"
		path_to_title_folder = path_to_index_folder + "/title_folder"

	except:
		print("Please provide 3 args : path to index folder, query file & output file")
		exit()

	try:
		# read config.txt
		config_file = open("config.txt","r")
		line = config_file.readline()
		MAX_DOC_COUNT = int(line[line.find("=")+1:])
		line = config_file.readline()
		MAX_TITLE_COUNT = int(line[line.find("=")+1:])
	except:
		print("Error in reading config file")

	secondary_index_list = get_secondary_index_list(path_to_final_index)
	try:
		print("")
	except:
		print("Issue in build index")
		exit()

	query = "start"
	while query != "exit":
		try:
			query = input("Enter query : ")
			t1 = time.time()
			outputs = search(path_to_final_index, path_to_title_folder, query, secondary_index_list)
			t2 = time.time()
			if len(outputs) > 0:
				print("\nSearch results are : \n")
				for output in outputs:
					if output != "":
						print(output)
			else:
				print("\nNo results found. Please modify query. \n")
			print("\n************* Time taken by search : "+ str(round(t2-t1, 3)) + " seconds.*************** \n")
		except:
			print("Issue in search.\n\n")
	# end of while
	# try:
	# 	queries = read_file(query_file)
	# except:
	# 	print("Query file not found or is corrupted")
	# 	exit()

	# outputs = search(path_to_final_index, path_to_title_folder, queries, secondary_index_list)
	# try:
	# 	print("")
	# except:
	# 	print("Issue in search..")

	# try:
	# 	write_file(outputs, output_file)
	# except:
	# 	print("Output file not created")	


if __name__ == '__main__':
    main()