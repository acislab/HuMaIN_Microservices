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
import PIL.Image
import io, os, subprocess, cv2

### OCRopus services information
IP = "10.5.146.92"
BIN_PORT = "8001"
SEG_PORT = "8002"
RECOG_PORT = "8003"

### Global variables
dataDir = settings.MEDIA_ROOT
BIN_IMAGE_PATH = "" # BIN_IMAGE_PATH will be used to store binarization resault, and as a input of cropping image
CROP_IMAGE_DIR = ""


def ocr_exec(image, parameters):
	### Default 3 threshold values
	threshold_1 = 0.4
	threshold_2 = 0.5
	threshold_3 = 0.6

	if 'threshold1' in parameters:
		threshold_1 = parameters['threshold1']
	if 'threshold2' in parameters:
		threshold_2 = parameters['threshold2']
	if 'threshold3' in parameters:
		threshold_3 = parameters['threshold3']

	""" 
	Create 3 processes to execute binarization and segmentation.
	Return 3 segmented images' coordinates lists.
	coord_lists[i] elements format: [x0, y0, x1, y1]
	"""
	args = [image, threshold_1, image, threshold_2, image, threshold_3]
	coord_lists = []
	with poolcontext(processes=3) as pool:
		coord_lists = pool.map(bin_seg_unpack, product(args))
	print("=========")
	print(coord_lists)
	print("=========")
	return


	# Get the common coordinates list
	cmn_coord_list = getCommonItem(coord_lists)

	### crop image according to the coordinates list returned from segmentation service
	for i in range(len(cmn_coord_list)):
		x = cmn_coord_list[i][0]
		y = cmn_coord_list[i][1]
		width = cmn_coord_list[i][2] - cmn_coord_list[i][0]
		height = cmn_coord_list[i][3] - cmn_coord_list[i][1]
		cropImage(BIN_IMAGE_PATH, i, x, y, width, height)

def bin_seg_unpack(args):
    return bin_seg(*args)

@contextmanager
def poolcontext(*args, **kwargs):
    pool = Pool(*args, **kwargs)
    yield pool
    pool.terminate()


"""
Call binarization and segmentation service in one process.
Return the segmented images' coordinates list
"""
def bin_seg(image, bin_threshold):
	global BIN_IMAGE_PATH
	url_bin = "http://" + IP + ":" + BIN_PORT + "/binarizationapi"
	url_seg = "http://localhost:8002" + "/segmentationapi"

	### Call binarization service, return binarized image
	paras_bin = {'threshold': bin_threshold}
	resp_bin = requests.get(url_bin, files={'image': image}, data=paras_bin)
	# Save the responsed binarized image
	image_base, image_ext = os.path.splitext(str(image))
	bin_image = image_base + "_bin.png"
	BIN_IMAGE_PATH = os.path.join(dataDir, bin_image)

	if resp_bin.status_code == 200:
		with open(BIN_IMAGE_PATH, 'wb') as fd:
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
	resp_seg = requests.get(url_seg, files={'image': open(BIN_IMAGE_PATH, 'rb')}, data=paras_seg)
	coord_list = None
	if resp_seg.status_code == 200:
		coord_list = resp_seg.json()
	else:
		print("Error: OCRopus segmentation failed.")
		return None

	return coord_list

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