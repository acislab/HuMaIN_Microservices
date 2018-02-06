# -*- coding: utf-8 -*-
##########################################################################################
# Developer: Luan,Jingchao        Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#	Given the images' directory, return extracted files
##########################################################################################
# Copyright 2017    Advanced Computing and Information Systems (ACIS) Lab - UF
#                   (https://www.acis.ufl.edu/)
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##########################################################################################

import requests
import time, argparse, os

start_time = time.time()

IP = "10.5.146.92"
PORT = "8000"

LICHENS = "/home/jingchao/HuMaIN/label-data-master/lichens/gold/inputs" # 200 images
HERB = "/home/jingchao/HuMaIN/label-data-master/herb/gold/inputs" # 100 images
ENT = "/home/jingchao/HuMaIN/label-data-master/ent/gold/inputs" # 100 images


### Call OCRopy service
def call_ocropy(imagepath, dstDir):
	url_ocr = "http://" + IP + ":" + PORT + "/ocrapi"

	# Uploaded iamges
	image = {'image': open(imagepath, 'rb')}

	# Call ocropy service
	resp = requests.get(url_ocr, files=image)

	# Save the responsed binarized image
	img_name = os.path.basename(imagepath)
	img_base, img_ext = os.path.splitext(img_name)
	output_fname = img_base + ".txt"
	dstpath = os.path.join(dstDir, output_fname)

	if resp.status_code == 200:
		with open(dstpath, 'wb') as fd:
			for chunk in resp:
				fd.write(chunk)
	else:
		print("Image %s OCRopy error!" % img_name)
        return

if __name__ == '__main__':
	for img in os.listdir(LICHENS):
		img_path = os.path.join(LICHENS, img)
		try:
			call_ocropy(img_path, LICHENS)
		except:
			pass
	lichens_end = time.time()
	
	for img in os.listdir(HERB):
		img_path = os.path.join(HERB, img)
		try:
			call_ocropy(img_path, HERB)
		except:
			pass
	herb_end = time.time()

	for img in os.listdir(ENT):
		img_path = os.path.join(ENT, img)
		try:
			call_ocropy(img_path, ENT)
		except:
			pass
	ent_end = time.time()

	with open("400iDigBio_OCRopyS_time.txt", 'wb') as fd:
		fd.write("\n*** 200 lichens images' time cost: %.2f seconds ***\n" % (lichens_end - start_time))
		fd.write("\n*** 100 herb images' time cost: %.2f seconds ***\n" % (herb_end - lichens_end))
		fd.write("\n*** 100 ent images' time cost: %.2f seconds ***\n" % (ent_end - herb_end))

	print("\n*** 200 lichens images' time cost: %.2f seconds ***\n" % (lichens_end - start_time))
	print("\n*** 100 herb images' time cost: %.2f seconds ***\n" % (herb_end - lichens_end))
	print("\n*** 100 ent images' time cost: %.2f seconds ***\n" % (ent_end - herb_end))