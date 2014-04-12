#!/usr/bin/python

import sys
import os
import chunk_maker
import uuid
import shutil
from app import log

#Usage 

def get_filepaths(directory):
	"""
	This function will generate the file names in a directory 
	tree by walking the tree either top-down or bottom-up. For each 
	directory in the tree rooted at directory top (including top itself), 
	it yields a 3-tuple (dirpath, dirnames, filenames).
	"""
	file_paths = []	 # List which will store all of the full filepaths.

	# Walk the tree.
	for root, directories, files in os.walk(directory):
		for filename in files:
			# Join the two strings in order to form the full filepath.
			filepath = os.path.join(root, filename)
			file_paths.append(filepath)	 # Add it to the list.

	return file_paths  # Self-explanatory.


def chunkify(input_dirs, key, output_dir):
	old_list = []	 
	if os.path.exists(output_dir):
		old_list = set(os.listdir(output_dir))
		shutil.rmtree(output_dir)
	os.makedirs(output_dir)

	#chunk the files in the input dir
	chunker = chunk_maker.chunk_maker(10, key, output_dir)
	for input_dir in input_dirs:
		for filepath in get_filepaths(input_dir):
			chunker.make_chunk(filepath)

	#check the new list of files against the old and get the differences
	new_list = set(os.listdir(output_dir))
	old_files = list(old_list.difference(new_list))
	new_files = list(new_list.difference(old_list))

	return (old_files, new_files)
