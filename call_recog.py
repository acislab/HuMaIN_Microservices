# -*- coding: utf-8 -*-
##########################################################################################
# Developer: Luan,Jingchao        Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#	Script to invoke the OCRopus Recognition microservice. Given the images' directory or
# an image, return recognized file(s).
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
import requests, zipfile, StringIO
import time, argparse, os, subprocess
import multiprocessing as mp

# Recognition service URL
IP = "10.5.146.92"
PORT = "8103"
URL_RECOG = "http://" + IP + ":" + PORT + "/recognitionapi"
SESSION = requests.Session()


def str2bool(v):
	"""Transfer String to Boolean.
	
	Normalizing all positive string to "True" and all negative string to "False".

	Args:
		v: original string.
	Returns:
		Return the original string related boolean. For example, return "True" if the original string is "yes".
	"""
	if v.lower() in ('yes', 'true', 't', 'y', '1'):
		return True
	elif v.lower() in ('no', 'false', 'f', 'n', '0'):
		return False
	else:
		raise argparse.ArgumentTypeError('Boolean value expected.')


def arg_parse():
	"""Parse argumentes input by user.
	Returns:
		A dictionary-like type viriable 'args' which contains all arguments input by user
	"""
	parser = argparse.ArgumentParser("Call OCRopy Recognition Service")

	parser.add_argument('input', help="The path of an image file, or a folder containing all pre-process images.")
	parser.add_argument('-o','--output',default=None,help="output directory, without the last slash")
	parser.add_argument('-m','--model',default=argparse.SUPPRESS, help="line recognition model")
	parser.add_argument("-l","--height",default=argparse.SUPPRESS,type=int, help="target line height (overrides recognizer)")
	parser.add_argument("-p","--pad",default=argparse.SUPPRESS,type=int, help="extra blank padding to the left and right of text line")
	parser.add_argument('-N',"--nonormalize", type=str2bool, help="don't normalize the textual output from the recognizer")
	parser.add_argument('-llocs','--llocs', type=str2bool, help="output LSTM locations for characters")
	parser.add_argument('-prob','--probabilities', type=str2bool, help="output probabilities for each letter")

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

	args = vars(args) # Convert the Namespace object "args" to a dic-like object
	return args


def call_recog(job):
	"""Call Recognition Service.

	Call the Recognition service, and store the recognized result locally.

	Args:
		job: a tuple variable (image path, local path to store result, parametes customed by user).
	"""
	imagepath, dst_path, parameters = job
	
	# Uploaded iamges
	multiple_files = [('image', (imagepath, open(imagepath, 'rb')))]
	if 'model' in parameters.keys():
		multiple_files.append(('model', (parameters['model'], open(parameters['model'], 'rb'))))
		del parameters['model']
	# Call recognition service and get response
	resp = SESSION.get(URL_RECOG, files=multiple_files, data=parameters)

	# Unpress the zip file responsed from recognition service
	if resp.status_code == 200:
		# For python 3+, replace with io.BytesIO(resp.content)
		z = zipfile.ZipFile(StringIO.StringIO(resp.content)) 
		z.extractall(dst_path) 
		print("[OK] '%s' recognition success!" % os.path.basename(imagepath))
	else:
		print("[ERROR] '%s' recognition error!" % os.path.basename(imagepath))


def main(args):
	"""Main function.

	Call Recognition service for each image sequencially or parallelly.
	"""
	input_ = args['input']
	output = args['output']

	# Only keep the setable parameters
	del args['input']
	del args['output']

	# Call recognition service
	if os.path.isfile(input_):
		# one image using a single process
		call_recog((input_, output, args))
		SESSION.close()
	elif os.path.isdir(input_):
		# multiple images using multiple processes to call recognition parallelly
		jobs = []
		for img in os.listdir(input_):
			img_path = os.path.join(input_, img)
			jobs.append((img_path, output, args))
		pool = mp.Pool(processes=8) # #processes = #CPU by default
		pool.map(call_recog, jobs)
		# Close processes pool after it is finished
		pool.close()
		pool.join()
		SESSION.close()


if __name__ == '__main__':
	args = arg_parse()
	main(args)