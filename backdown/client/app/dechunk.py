
import sys
import os
import chunk_maker
import uuid
import shutil
from app import log

'''
dechunks all chunks in the given directory
'''

def dechunk(dir):
	for chunk in os.listdir(dir):
		with zipfile.ZipFile(chunk) as zip_file:
   			check = zip_file.testzip()
   			if check is not None:
   				#NOT A CHUNK OR CORRUPT
   				pass
   			else:
    			for member in zip_file.namelist():
       				filename = os.path.basename(member)
       				zip_file.extract(filename) #add a path as second param if we don't want to unchunk here
	return