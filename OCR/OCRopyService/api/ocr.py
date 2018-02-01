#!/usr/bin/env python
##########################################################################################
# Developer: Luan,Jingchao        Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#     For each image, create 3 processes to call binarization and segmentation services 
# respectively, then call recognition service for the common segmented images.
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
from multiprocessing import Pool
from django.conf import settings
from itertools import product
from contextlib import contextmanager
import cv2, zipfile, StringIO
import io, os, subprocess, glob, shutil

### OCRopus services information
IP = "10.5.146.92"
BIN_PORT = "8001"
SEG_PORT = "8003"
RECOG_PORT = "8004"
URL_BIN = "http://" + IP + ":" + BIN_PORT + "/binarizationapi"
URL_SEG = "http://" + IP + ":" + SEG_PORT + "/segmentationapi"
URL_RECOG = "http://" + IP + ":" + RECOG_PORT + "/recognitionapi"

### Global variables

# Record the # of images, creating intermediate folder with CT, in case of processing images with same name
CT = 0 

def ocr_exec(image, parameters):
	dataDir = settings.MEDIA_ROOT
	global CT

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
	path_data = dataDir + "/" + img_base + "_" + str(CT)
	CT += 1
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
		print("Image %s Binarization failed!" % image)
		return None
	
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
		print("Image %s Segmentation error!" % bin_img_name)
		return None

	#####################################
	##### Call recognition service ######
	#####################################
	# Folder that stores recognized results of all segmented line-images
	path_recog = path_data + "/" + "recog"
	if not os.path.isdir(path_recog):
		subprocess.call(["mkdir -p " + path_recog], shell=True)
	# Package image and model specified by user
	upload_files = []
	if 'model' in paras_recog:
		multiple_files.append(('model', (paras_recog['model'], open(paras_recog['model'], 'rb'))))
		del paras_recog['model']
	# The internal folder that stored the segmented images
	folder_seg_images = os.listdir(path_seg)[0]
	path_seg_images = path_seg + "/" + folder_seg_images
	# Call recognition service for each segmented images
	for img_seg in os.listdir(path_seg_images):
		img_seg_base, img_seg_ext = str(img_seg).split(".")
		img_seg_path = os.path.join(path_seg_images, img_seg)
		upload_files.append(('image', (img_seg_path, open(img_seg_path, 'rb'))))
		resp_recog = requests.get(URL_RECOG, files=upload_files, data=paras_recog)
		# Unpress the zip file responsed from recognition service
		if resp_recog.status_code == 200:
			# For python 3+, replace with io.BytesIO(resp.content)
			z = zipfile.ZipFile(StringIO.StringIO(resp_recog.content))
			z.extractall(path_recog)
		else:
			print("Image %s Recognition error!" % str(img_seg))
        	continue
	
    ##########################################################
	##### Concatenate all reconition results in sequence #####
	##########################################################
	recog_list = glob.glob(path_recog+"/*/*.txt")
	# sort by alphabetical order followed by length of string
	recog_list.sort()
	recog_list.sort(key=len)
	# combine all of the recognized results
	### Write all recognizaed files into one file and return this file
	#extract_file = path_data + "/" + img_base + ".txt"
	#with open(extract_file, "wb") as outfile:
	#    for f in recog_list:
	#        with open(f, "rb") as infile:
	#            outfile.write(infile.read())
	#            outfile.write("\n")
	### Write all recognized results into one String object, and return this object
	### from memory to user directly. Reducing 2 times accessing disk
	extract_result = ""
	for f in recog_list:
		with open(f, "rb") as infile:
			extract_result = extract_result + infile.read() + "\n"
	if extract_result == "":
		extract_result = None

	##### Delete the intermediate data #####
	shutil.rmtree(path_data)

	return extract_result


def ocr_exec_mulP(image, parameters):
	### Default 3 threshold values
	threshold_1 = 0.2
	threshold_2 = 0.5
	threshold_3 = 0.8

	if 'threshold1' in parameters:
		threshold_1 = parameters['threshold1']
	if 'threshold2' in parameters:
		threshold_2 = parameters['threshold2']
	if 'threshold3' in parameters:
		threshold_3 = parameters['threshold3']

	###############################################################
	# Create 3 processes to execute binarization and segmentation.
	# Return 3 segmented images' coordinates lists.
	# coord_lists[i] elements format: [x0, y0, x1, y1]
	###############################################################
	args = [(image, threshold_1), (image, threshold_2), (image, threshold_3)]
	pool = Pool(3)
	coord_lists = pool.map(bin_seg, args)
	print("+++++++++")
	print(coord_lists)
	print("+++++++++")
	return


	# Get the common coordinates list
	cmn_coord_list = getCommonItem(coord_lists)

	### crop image according to the coordinates list returned from segmentation service
	for i in range(len(cmn_coord_list)):
		x = cmn_coord_list[i][0] # x0
		y = cmn_coord_list[i][1] # y0
		width = cmn_coord_list[i][2] - cmn_coord_list[i][0] # x1 - x0
		height = cmn_coord_list[i][3] - cmn_coord_list[i][1] # y1 - y0
		cropImage(BIN_IMAGE_PATH, i, x, y, width, height)


def bin_seg_wrapper(args):
    return bin_seg(*args)


"""
Call binarization and segmentation service in one process.
Return an dictionary object, which indludes the binarized image path and related segmented images' coordinates list
"""
def bin_seg(job):
	image, bin_threshold = job
	url_bin = "http://localhost:" + BIN_PORT + "/binarizationapi"
	url_seg = "http://" + IP + ":" + SEG_PORT + "/segmentationapi"

	### Call binarization service, return binarized image
	paras_bin = {'threshold': bin_threshold}
	resp_bin = requests.get(url_bin, files={'image': image}, data=paras_bin)
	# Save the responsed binarized image
	img_base, img_ext = os.path.splitext(str(image))
	bin_img_name = img_base + "_bin.png"
	bin_img_dir = dataDir + "/" + img_base + "_threshold" + str(bin_threshold)
	if not os.path.isdir(bin_img_dir):
		subprocess.call(["mkdir -p " + bin_img_dir], shell=True)
	bin_img_path = os.path.join(bin_img_dir, bin_img_name)

	if resp_bin.status_code == 200:
		with open(bin_img_path, 'wb') as fd:
			for chunk in resp_bin:
				fd.write(chunk)
	else:
		print("Image %s Binarization failed!" % image)
		return None

	"""
	img_bin = None
	if resp_bin.status_code == 200:
		img_bin = PIL.Image.open(io.BytesIO(resp_bin.content))
	else:
		print("Error: OCRopus binarization failed.")
		return resp_bin.status_code
	"""

	### Call segmentation service, return segmented images' coordinates
	paras_seg = {'coordinate': True}
	print("==== image ====")
	print(bin_img_path)
	resp_seg = requests.get(url_seg, files={'image': open(bin_img_path, 'rb')}, data=paras_seg)
	print(resp_seg.json())
	print("===============")
	coord_list = None
	if resp_seg.status_code == 200:
		coord_list = resp_seg.json()
	else:
		print("Error: OCRopus segmentation failed.")
		return None
	return {"bin_img_path": bin_img_path, "coord_list": coord_list}

"""
Crop an image according to given (x, y, width, height). 
Parameter 'index' indicates the index of the cropped part, default is the 1st part.
"""
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


def getCommonItem(lists):
	list_1 = lists[0]
	list_2 = lists[1]
	list_3 = lists[2]

	# Find the common coordinates in list_1 and list_2
	cmn_list_12 = []
	for item_1 in list_1:
		similar_item_2 = None
		for item_2 in list_2:
			x0_dif = item_1[0] - item_2[0]
			x1_dif = item_1[1] - item_2[1]
			y0_dif = item_1[2] - item_2[2]
			y0_dif = item_1[3] - item_2[3]
			if (-5<=x0_dif<=5 and -5<=x1_dif<=5 and -5<=y0_dif<=5 and -5<=y1_dif<=5):
				similar_item_2 = item_2
				cmn_list_12.append(item_1)
				break
			else:
				if item_2 != list_2[-1]:
					continue
				else:
					break
		# Remove the similar coordinate element from coordinate_list_2. Thus reduce the traverse element in the next loop
		if similar_item is not None:
			list_2.Remove(similar_item_2)

	# Find the common coordinates list_1, list_2, and list_3
	cmn_list= []
	for item_12 in cmn_list_12:
		similar_item_3 = None
		for item_3 in list_3:
			x0_dif = item_12[0] - item_3[0]
			x1_dif = item_12[1] - item_3[1]
			y0_dif = item_12[2] - item_3[2]
			y0_dif = item_12[3] - item_3[3]
			if (-5<=x0_dif<=5 and -5<=x1_dif<=5 and -5<=y0_dif<=5 and -5<=y1_dif<=5):
				similar_item_3 = item_3
				cmn_list.append(item_12)
				break
			else:
				if item_3 != list_3[-1]:
					continue
				else:
					break
		# Remove the similar coordinate element from coordinate_list_2. Thus reduce the traverse element in the next loop
		if similar_item_3 is not None:
			list_3.Remove(similar_item_3)

	return cmn_list