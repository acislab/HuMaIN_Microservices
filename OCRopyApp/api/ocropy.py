#!/usr/bin/env python
##########################################################################################
# Developer: Luan,Jingchao        Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#     Extract text information from an image, implemented by invoking Binarization, 
# and Recognition services respectively.
##########################################################################################
# Copyright 2017    Advanced Computing and Information Systems (ACIS) Lab - UF
#                   (https://www.acis.ufl.edu/)
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##########################################################################################

import requests
import multiprocessing as mp
from django.conf import settings
from itertools import product
from contextlib import contextmanager
import cv2, zipfile, StringIO
import io, os, subprocess, glob, shutil
import logging

### URL of Binarization/Segmentation/Recognition services
URL_BIN = "http://" + settings.BIN_IP + ":" + settings.BIN_PORT + "/binarizationapi"
URL_SEG = "http://" + settings.SEG_IP + ":" + settings.SEG_PORT + "/segmentationapi"
URL_RECOG = "http://" + settings.RECOG_IP + ":" + settings.RECOG_PORT + "/recognitionapi"

logger = logging.getLogger('ocropy')

def ocropy_exec(image, parameters):
	dataDir = settings.MEDIA_ROOT

	paras_bin = {}
	paras_seg = {}
	paras_recog = {}

	### Seperate parameters to bin/seg/recog parameters dict. respectively
	keys = parameters.keys()
	for key in keys:
		if key.startswith("bin_"):
			paras_bin[key[4:]] = parameters[key]
		elif key.startswith("seg_"):
			paras_seg[key[4:]] = parameters[key]
		elif key.startswith("recog_"):
			paras_recog[key[4:]] = parameters[key]
		else:
			continue
	# Create a floder for this image to store the intermediate data
	img_base, img_ext = os.path.splitext(str(image))
	path_data = dataDir + "/" + img_base

	if not os.path.isdir(path_data):
		subprocess.call(["mkdir -p " + path_data], shell=True)
	
	#####################################
	##### Call binarization service #####
	#####################################
	resp_bin = requests.get(URL_BIN, files={'image': image}, data=paras_bin)
	img_bin_name = img_base + "_bin.png"
	img_bin_path = os.path.join(path_data, img_bin_name)
	# Save the responsed binarized image
	if resp_bin.status_code == 200:
		with open(img_bin_path, 'wb') as fd:
			for chunk in resp_bin:
				fd.write(chunk)
	else:
		logger.error("Image %s Binarization failed!" % image)
		shutil.rmtree(path_data)
		return None
	logger.info("Binarization over!!!")


	#####################################
	##### Call segmentation service #####
	#####################################
	resp_seg = requests.get(URL_SEG, files={'image': open(img_bin_path, 'rb')}, data=paras_seg)
	path_seg = path_data + "/" + "seg" # Unzip segmented images floder under this folder
	if not os.path.isdir(path_seg):
		subprocess.call(["mkdir -p " + path_seg], shell=True)
	# Unpress the zip file responsed from segmentation service, and save it
	if resp_seg.status_code == 200:
		# For python 3+, replace with io.BytesIO(resp.content)
		z = zipfile.ZipFile(StringIO.StringIO(resp_seg.content)) 
		z.extractall(path_seg)
	else:
		logger.error("Image %s Segmentation error!" % bin_img_name)
		shutil.rmtree(path_data)
		return None
	logger.info("Segmentation over!!!")

	#####################################
	##### Call recognition service ######
	#####################################
	# Folder that stores recognized results of all segmented line-images
	path_recog = path_data + "/" + "recog"
	if not os.path.isdir(path_recog):
		subprocess.call(["mkdir -p " + path_recog], shell=True)
	# The internal folder that stored the segmented images
	folder_seg_images = os.listdir(path_seg)[0]
	path_seg_images = path_seg + "/" + folder_seg_images
	# Call recognition service for each segmented images
	jobs = []
	for img_seg in os.listdir(path_seg_images):
		img_seg_path = os.path.join(path_seg_images, img_seg)
		#call_recog((img_seg_path, paras_recog, path_recog)) # single process
		jobs.append((img_seg_path, paras_recog, path_recog))
	# Call recognition service with multiple processes, # processes = # CPU by default
	pool = mp.Pool()
	pool.map(call_recog, jobs)
	# Close pool of processes after they are finished
	pool.close()
	pool.join()
	logger.info("Recognition over!!!")

	
	##########################################################
	##### Concatenate all reconition results in sequence #####
	##########################################################
	recog_list = glob.glob(path_recog+"/*/*.txt")
	# sort by alphabetical order followed by length of string
	recog_list.sort()
	recog_list.sort(key=len)
	# Combine all of the recognized results.
	# Write all recognized results into one String object, and return this object
	# from memory to user directly. Reducing 2 times accessing disk
	extract_result = ""
	for f in recog_list:
		with open(f, "rb") as infile:
			extract_result = extract_result + infile.read() + "\n"
	if extract_result == "":
		extract_result = None

	##### Delete the intermediate data #####
	shutil.rmtree(path_data)

	return extract_result


def call_recog(job):
	image, parameters, dstDir = job
	# Package image and model specified by user
	upload_files = []
	if 'model' in parameters:
		multiple_files.append(('model', (parameters['model'], open(parameters['model'], 'rb'))))
		del parameters['model']	
	upload_files.append(('image', (image, open(image, 'rb'))))
	resp_recog = requests.get(URL_RECOG, files=upload_files, data=parameters)
	# Unpress the zip file responsed from recognition service
	if resp_recog.status_code == 200:
		# For python 3+, replace with io.BytesIO(resp.content)
		z = zipfile.ZipFile(StringIO.StringIO(resp_recog.content))
		z.extractall(dstDir)
	else:
		logger.error("Image %s Recognition error!" % str(image))


def cropImage(imagepath, index, x, y, width, height):
	global CROP_IMAGE_DIR
	img = cv2.imread(imagepath, cv2.IMREAD_GRAYSCALE)
	crop_img = img[y:y+height, x:x+width]

	### Create destination folder to store cropped images, and set the name format of the cropped images
	img_name_ext = os.path.basename(imagepath)
	base_name, ext = img_name_ext.split('.')
	CROP_IMAGE_DIR = dataDir + "/" + base_name
	if not os.path.isdir(CROP_IMAGE_DIR):
		subprocess.call(["mkdir -p " + CROP_IMAGE_DIR], shell=True)
	crop_img_name = base_name + '_' + str(index) + '.png'
	crop_img_path = CROP_IMAGE_DIR + "/" + crop_img_name
	cv2.imwrite(crop_img_path, crop_img)