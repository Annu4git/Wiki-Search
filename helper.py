import heapq
import os
import math

def merge_inverted_index(path_to_index_folder, index_file_count):

	final_index_count = 0
	word_count = 0

	config_file = open("config.txt","r")
	line = config_file.readline()
	line = config_file.readline()
	line = config_file.readline()
	MAX_WORD_COUNT = int(line[line.find("=")+1:])
	line = config_file.readline()
	TOTAL_DOCS = int(line[line.find("=")+1:])

	if path_to_index_folder[len(path_to_index_folder)-1] == '/':
		path_to_index_folder = path_to_index_folder[:-1]
	path_to_final_index_folder = path_to_index_folder + "/final_index"

	# print(path_to_final_index_folder)

	if not os.path.exists(path_to_final_index_folder):
		os.makedirs(path_to_final_index_folder)

	file_writer = open(path_to_final_index_folder + "/" + "final_" + str(final_index_count) + ".txt","w")
	secondary_index_file = open(path_to_final_index_folder + "/" + "secondary_index.txt","w")

	file_pointers = []
	list_for_heap = []

	i = 0
	while i < index_file_count:
		inverted_index_file = open(path_to_index_folder + "/" + "inverted_index_" + str(i) + ".txt","r")
		file_pointers.append(inverted_index_file)
		i += 1

	i = 0
	while i < index_file_count:
		line = file_pointers[i].readline()
		word = line[:line.index("#")]
		word_info = line[line.index("#")+1:]
		temp_tuple = (word, i, word_info)
		list_for_heap.append(temp_tuple)
		i += 1

	heapq.heapify(list_for_heap) 

	last_tuple = heapq.heappop(list_for_heap)
	last_word = last_tuple[0]
	last_index = last_tuple[1]
	last_info = last_tuple[2]
	last_info = last_info[:-1]

	while len(list_for_heap) > 0:
		# print("last_index : " + str(last_index))
		line = file_pointers[last_index].readline()
		if line != "":
			word = line[:line.index("#")]
			word_info = line[line.index("#")+1:]
			temp_tuple = (word, last_index, word_info)
			heapq.heappush(list_for_heap, temp_tuple)

		next_tuple = heapq.heappop(list_for_heap)		

		if last_word == next_tuple[0]:
			last_index = next_tuple[1]
			last_info = last_info + "#" + next_tuple[2]
			last_info = last_info[:-1]
		else:
			print("write last_tuple in file")
			info_list = last_info.split("#")
			idf = TOTAL_DOCS/len(info_list)
			idf = round(math.log(1 + idf, 10), 3)
			print(idf)
			line_to_write = last_word

			for info in info_list:
				info = info.split("@")
				tf = int(info[1])
				# tf = tf/1000.0
				tfidf = int(math.floor(tf*idf))
				if tfidf == 0:
					continue
				line_to_write += "#" + info[0] + "@" + str(tfidf)

			if line_to_write != last_word:
				file_writer.write(line_to_write + "\n")
			
			if word_count == 0:
				print("Final index : " + str(final_index_count) + "starts with word : " + last_word)
				# secondary_index_file.write(last_word + "#" + str(final_index_count) + "\n")
				secondary_index_file.write(last_word + "\n")
			
			word_count += 1
			
			if word_count == MAX_WORD_COUNT:
				word_count = 0
				final_index_count += 1
				file_writer = open(path_to_final_index_folder + "/" + "final_" + str(final_index_count) + ".txt","w")
			
			last_tuple = next_tuple
			last_word = last_tuple[0]
			last_index = last_tuple[1]
			last_info = last_tuple[2]
			last_info = last_info[:-1]

	delete_index_files(path_to_index_folder, index_file_count)

def delete_index_files(path_to_index_folder, index_file_count):
	i=0
	while i < index_file_count:
		file_to_delete = path_to_index_folder + "/" + "inverted_index_" + str(i) + ".txt"
		if os.path.exists(file_to_delete):
			os.remove(file_to_delete)
		else:
			print("The file : " + file_to_delete + " does not exist")
		i += 1

def main():
	print()
	print()
	print("Merging of indexes begin..")
	merge_inverted_index("/home/anurag/Desktop/IRE/Mini_Project/Updated/index1", 28)
	

if __name__ == "__main__": 
	main() 
