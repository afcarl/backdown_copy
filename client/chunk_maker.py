'''
Handles all chunks
'''

import json
import os
import md5
import zipfile
from stat import * # ST_SIZE etc
class chunk_maker:
	def __init__(self, chunk_size, key, output_dir):
		self.CHUNK_SIZE = chunk_size
		self.key = key
		self.output_dir = output_dir
	
	def make_chunk(self, filepath):
		#first encrypt the file
		#TODO
		#then hash the metadata and make the filename
		meta = os.stat(filepath)
		filename = md5.new(str(meta[ST_SIZE]) + str(meta[ST_MTIME]) + filepath)
		chunk = zipfile.ZipFile(self.output_dir + '/' + filename.hexdigest(), mode='w')
		try:
			import zlib
			compression = zipfile.ZIP_DEFLATED
		except:
			print"not defalted"
			compression = zipfile.ZIP_STORED
   		try: #attempt to write with compression
			chunk.write(filepath, compress_type=compression)
		finally:
			chunk.close()

	

	