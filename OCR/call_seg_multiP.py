# -*- coding: utf-8 -*-
##########################################################################################
# Developer: Luan,Jingchao        Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#	Script to invoke the OCRopus Segmentation microservice. Given the binarized images'  
# directory or an image, for each image return a folder containing all segemnted 
# single-line images.
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
import time, argparse, os
import multiprocessing as mp

# Segmentation service URL
IP = "10.5.146.92"
PORT = "8102"
URL_SEG = "http://" + IP + ":" + PORT + "/segmentationapi"
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
	parser = argparse.ArgumentParser("Call OCRopy Segmentation Service")

	parser.add_argument('input', help="The path of an image file, or a folder containing all pre-process images.")
	# output parameters
	parser.add_argument('-o', '--output', default=None, help="output directory, without the last slash")
	# limits
	group_limits = parser.add_argument_group('limits')
	group_limits.add_argument('--minscale',type=float,default=argparse.SUPPRESS, help='minimum scale permitted')
	group_limits.add_argument('--maxlines',type=float,default=argparse.SUPPRESS, help='maximum # lines permitted')
	# scale parameters
	group_scale = parser.add_argument_group('scale parameters')
	group_scale.add_argument('--scale',type=float,default=argparse.SUPPRESS, help='the basic scale of the document (roughly, xheight) 0=automatic')
	group_scale.add_argument('--hscale',type=float,default=argparse.SUPPRESS, help='non-standard scaling of horizontal parameters')
	group_scale.add_argument('--vscale',type=float,default=argparse.SUPPRESS, help='non-standard scaling of vertical parameters')
	# line parameters
	group_line = parser.add_argument_group('line parameters')
	group_line.add_argument('--threshold',type=float,default=argparse.SUPPRESS, help='baseline threshold')
	group_line.add_argument('--noise',type=int,default=argparse.SUPPRESS, help="noise threshold for removing small components from lines")
	group_line.add_argument('--usegauss', type=str2bool, default=argparse.SUPPRESS, help='use gaussian instead of uniform')
	# column parameters
	group_column = parser.add_argument_group('column parameters')
	group_column.add_argument('--maxseps',type=int,default=argparse.SUPPRESS, help='maximum black column separators')
	group_column.add_argument('--sepwiden',type=int,default=argparse.SUPPRESS, help='widen black separators (to account for warping)')
	group_column.add_argument('--maxcolseps',type=int,default=argparse.SUPPRESS, help='maximum # whitespace column separators')
	group_column.add_argument('--csminheight',type=float,default=argparse.SUPPRESS, help='minimum column height (units=scale)')
	# output parameters
	group_column = parser.add_argument_group('output parameters')
	group_column.add_argument('--pad',type=int,default=argparse.SUPPRESS, help='adding for extracted lines')
	group_column.add_argument('--expand',type=int,default=argparse.SUPPRESS, help='expand mask for grayscale extraction')

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

	args = vars(args) # Convert the Namespace object "args" to a dict=like object
	return args


def call_seg(job):
	"""Call Segmentation Service.

	Call the Segmentation service, and store the segmented result locally.

	Args:
		job: a tuple variable (image path, local path to store result, parametes customed by user).
	"""
	imagepath, dst_dir, parameters = job

	# Uploaded iamges
	image = {'image': open(imagepath, 'rb')}

	# Call segmentation service and get response
	resp = SESSION.get(URL_SEG, files=image, data=parameters)

	# Unpress the zip file responsed from segmentation service, and save it
	if resp.status_code == 200:
		# For python 3+, replace with io.BytesIO(resp.content)
		z = zipfile.ZipFile(StringIO.StringIO(resp.content)) 
		z.extractall(dst_dir)
		print("[OK] '%s' segmentation success!" % os.path.basename(imagepath))
	else:
		print("[ERROR] '%s' segmentation error!" % os.path.basename(imagepath))


def main(args):
	"""Main function.

	Call Segmentation service for each image sequencially or parallelly.
	"""
	input_ = args['input']
	output = args['output']

	# Only keep the setable parameters
	del args['input']
	del args['output']

	# Call segmentation service
	if os.path.isfile(input_):
		# one image using a single process
		call_seg((input_, output, args))
		SESSION.close()
	elif os.path.isdir(input_):
		# multiple images using multiple processes to call segmentation parallelly
		jobs = []
		for img in os.listdir(input_):
			img_path = os.path.join(input_, img)
			jobs.append((img_path, output, args))
		pool = mp.Pool(processes=8) # #processes = #CPU by default
		pool.map(call_seg, jobs)
		# Close processes pool after it is finished
		pool.close()
		pool.join()
		SESSION.close()


if __name__ == '__main__':
	args = arg_parse()
	main(args)