# -*- coding: utf-8 -*-
##########################################################################################
# Developer: Luan,Jingchao        Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#	Given the original image's or images' path, the script will call OCR Tesseract microservice for
# the image or each image under the path. Return extracted text file(s).
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
import argparse, os, sys, subprocess
import multiprocessing as mp


# Tesseract service URL
IP = "10.5.146.92"
PORT = "8104"
URL_TESSERACT = "http://" + IP + ":" + PORT + "/tesseractapi"
SESSION = requests.Session()


def arg_parse():
	"""Parse argumentes input by user.
	
	Returns:
		A dictionary-like type viriable 'args' which contains all arguments input by user
	"""

	parser = argparse.ArgumentParser("Call Tesseract Service")

	parser.add_argument('input', help="The path of an image, or a folder containing all images.")
	parser.add_argument('-o','--output', default=None, help="output directory, without the last slash")
	parser.add_argument('-lang','--language', default=argparse.SUPPRESS, help='language(s) involved in the image')

	args = parser.parse_args()

	# Set the default output folder
	default_output = ""
	if os.path.isfile(args.input):
		default_output = os.path.dirname(args.input)
	elif os.path.isdir(args.input):
		default_output = args.input
	else:
		parser.print_help()
		sys.exit(0)
	# Verify or create the output folder
	if args.output is None:
		args.output = default_output
	else:
		if not os.path.isdir(args.output):
			subprocess.call(["mkdir -p " + args.output], shell=True)
			if not os.path.isdir(args.output):
				print("Error: Destination folder %s could not be created" % (args.output))
				sys.exit(0)

	args = vars(args) # Convert the Namespace object "args" to a dict-like object
	return args

def call_tesseract(job):
	"""Call tesseract Service.

	Call the Tesseract service, and store the result locally.

	Args:
		job: a tuple variable (image path, local path to store result, parametes customed by user).
	"""
	imagepath, dst_dir, parameters = job
	

	# Uploaded iamges
	image = {'image': open(imagepath, 'rb')}

	# Call tesseract service
	resp = SESSION.get(URL_TESSERACT, files=image, data=parameters, stream=True)

	# Save the result
	image = os.path.basename(imagepath)
	image_name, image_ext = os.path.splitext(image)
	dstimage = image_name + ".txt"
	dstpath = os.path.join(dst_dir, dstimage)

	if resp.status_code == 200:
		with open(dstpath, 'wb') as fd:
			for chunk in resp:
				fd.write(chunk)
		print("[OK] '%s' Tesseract success!" % image)
	else:
		print("[ERROR] '%s' Tesseract error!" % image)


def main(args):
	"""Main function.

	Call Tesseract service for each image sequencially or parallelly.
	"""
	input_ = args['input']
	output = args['output']

	# Only keep the setable parameters
	del args['input']
	del args['output']

	# Call binarization service
	if os.path.isfile(input_):
		# one image using a single process
		call_tesseract((input_, output, args))
		SESSION.close()
	elif os.path.isdir(input_):
		# multiple images using multiple processes to call binarization parallelly
		jobs = []
		for img in os.listdir(input_):
			img_path = os.path.join(input_, img)
			jobs.append((img_path, output, args))
		pool = mp.Pool(processes=8) # #processes = #CPU by default
		pool.map(call_tesseract, jobs)
		# Close processes pool after it is finished
		pool.close()
		pool.join()
		SESSION.close()


if __name__ == '__main__':
	args = arg_parse()
	main(args)