
# -*- coding: utf-8 -*-
##########################################################################################
# Developer: Luan,Jingchao        Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#	Given the original image's or images' path, the script will call OCR Tesseract microservice for
# the image or each image under the path. 
#	It will return a folder containing the outputs of binarization service.
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
import requests, StringIO
import argparse, os, sys, subprocess

### The server IP and PORT in lab ACIS deploying HuMaIN OCRopus microservices (Only accessable for ACIS members)
### Please Replace with your server IP when testing
IP = "10.5.146.92"
PORT = "8000"

### Configuarable parameters
parser = argparse.ArgumentParser("Call Tesseract Service")

parser.add_argument('image', help="The path of an image, or a folder containing all images.")
parser.add_argument('-o','--output', default=None, help="output directory, without the last slash")
parser.add_argument('-lang','--language', default=argparse.SUPPRESS, help='language(s) involved in the image')

args = parser.parse_args()

### The existence of the destination folder is verified or created
if args.output is None:
	# If output folder is not set, save output image to current directory
	args.output = os.getcwd()
else:
	if not os.path.isdir(args.output):
		subprocess.call(["mkdir -p " + args.output], shell=True)
		if not os.path.isdir(args.output):
			print("Error: Destination folder %s could not be created" % (args.output))
			sys.exit(0)

args = vars(args)

def call_tesseract_ms(imagepath, dstDir, parameters):
	url_tesseract = "http://" + IP + ":" + PORT + "/tesseractapi"

	# Uploaded iamges
	image = {'image': open(imagepath, 'rb')}

	# Call tesseract service
	resp = requests.get(url_tesseract, files=image, data=parameters, stream=True)

	# Save the result
	image = os.path.basename(imagepath)
	image_name, image_ext = os.path.splitext(image)
	dstimage = image_name + ".txt"
	dstpath = os.path.join(dstDir, dstimage)

	if resp.status_code == 200:
		with open(dstpath, 'wb') as fd:
			for chunk in resp:
				fd.write(chunk)
	else:
		print("Tesseract service error for image '%s'!" % imagepath)
        return

if __name__ == '__main__':
	image = args['image']
	dstDir = args['output']

	### Only keep the setable parameters
	del args['image']
	del args['output']

	### Call binarization service
	if os.path.isfile(image):
		call_tesseract_ms(image, dstDir, args)
	elif os.path.isdir(image):
		for image_name in os.listdir(image):
			image_path = os.path.join(image, image_name)
			# One image failed do not affect the process of other images
			try:
				call_tesseract_ms(image_path, dstDir, args)
			except:
				pass
	else:
		parser.print_help()
		sys.exit(0)