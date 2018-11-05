# -*- coding: utf-8 -*-
##########################################################################################
# Developer: Luan,Jingchao        Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#	Script to invoke the OCRopy application. Given an image or the images' directory, 
# return extracted files.
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
import multiprocessing as mp


# OCRopy application URL
#IP = "10.5.146.92"
IP = "localhost"
PORT = "8100"
URL_OCROPY = "http://" + IP + ":" + PORT + "/ocropyapi"
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

	Three kinds of parametes: bin_*, seg_*, and recog_* related to binarization, segmentation and
	recognition respectively.

	Returns:
		A dictionary-like type viriable 'args' which contains all arguments input by user
	"""
	parser = argparse.ArgumentParser("Call OCRopy Application")

	parser.add_argument('input', help="The path of an image, or a folder containing all pre-process images.")
	parser.add_argument('-o','--output', default=None, help="output directory, without the last slash")

	### Parameters for Binarization service (#10)
	group_bin = parser.add_argument_group('Binarization arguments')
	group_bin.add_argument('--bin_threshold', type=float, default=argparse.SUPPRESS, help='threshold, determines lightness')
	group_bin.add_argument('--bin_zoom', type=float, default=argparse.SUPPRESS, help='zoom for page background estimation, smaller=faster')
	group_bin.add_argument('--bin_escale', type=float, default=argparse.SUPPRESS, help='scale for estimating a mask over the text region')
	group_bin.add_argument('--bin_bignore', type=float, default=argparse.SUPPRESS, help='ignore this much of the border for threshold estimation')
	group_bin.add_argument('--bin_perc', type=float, default=argparse.SUPPRESS, help='percentage for filters')
	group_bin.add_argument('--bin_range', type=int, default=argparse.SUPPRESS, help='range for filters')
	group_bin.add_argument('--bin_maxskew', type=float, default=argparse.SUPPRESS, help='skew angle estimation parameters (degrees)')
	group_bin.add_argument('--bin_lo', type=float, default=argparse.SUPPRESS, help='percentile for black estimation')
	group_bin.add_argument('--bin_hi', type=float, default=argparse.SUPPRESS, help='percentile for white estimation')
	group_bin.add_argument('--bin_skewsteps', type=int, default=argparse.SUPPRESS, help='steps for skew angle estimation (per degree)')

	### Parameters for Segmentation service (#14)
	group_seg = parser.add_argument_group('Segmentation arguments')
	group_seg.add_argument('--seg_minscale', type=float, default=argparse.SUPPRESS, help='minimum scale permitted')
	group_seg.add_argument('--seg_maxlines', type=float, default=argparse.SUPPRESS, help='maximum # lines permitted')
	group_seg.add_argument('--seg_scale', type=float, default=argparse.SUPPRESS, help='the basic scale of the document (roughly, xheight) 0=automatic')
	group_seg.add_argument('--seg_hscale', type=float, default=argparse.SUPPRESS, help='non-standard scaling of horizontal parameters')
	group_seg.add_argument('--seg_vscale', type=float, default=argparse.SUPPRESS, help='non-standard scaling of vertical parameters')
	group_seg.add_argument('--seg_threshold', type=float, default=argparse.SUPPRESS, help='baseline threshold')
	group_seg.add_argument('--seg_noise', type=int, default=argparse.SUPPRESS, help="noise threshold for removing small components from lines")
	group_seg.add_argument('--seg_usegauss', type=str2bool, default=argparse.SUPPRESS, help='use gaussian instead of uniform')
	group_seg.add_argument('--seg_maxseps', type=int, default=argparse.SUPPRESS, help='maximum black column separators')
	group_seg.add_argument('--seg_sepwiden', type=int, default=argparse.SUPPRESS, help='widen black separators (to account for warping)')
	group_seg.add_argument('--seg_maxcolseps', type=int, default=argparse.SUPPRESS, help='maximum # whitespace column separators')
	group_seg.add_argument('--seg_csminheight', type=float, default=argparse.SUPPRESS, help='minimum column height (units=scale)')
	group_seg.add_argument('--seg_pad', type=int, default=argparse.SUPPRESS, help='adding for extracted lines')
	group_seg.add_argument('--seg_expand', type=int, default=argparse.SUPPRESS, help='expand mask for grayscale extraction')

	### Parameters for Segmentation service (#4)
	group_recog = parser.add_argument_group('Recognition arguments')
	group_recog.add_argument('--recog_model', default=argparse.SUPPRESS, help="line recognition model")
	group_recog.add_argument('--recog_height', type=int, default=argparse.SUPPRESS, help="target line height (overrides recognizer)")
	group_recog.add_argument('--recog_pad', type=int, default=argparse.SUPPRESS, help="extra blank padding to the left and right of text line")
	group_recog.add_argument('--recog_nonormalize', type=str2bool, default=argparse.SUPPRESS, help="don't normalize the textual output from the recognizer")


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


### Call OCRopy service
def call_ocropy(job):
	"""Call OCRopy Service.

	Args:
		job: a tuple variable (image path, local path to store result, parametes customed by user).

	Return:
		The extracted file containing text information of the input image.
	"""
	imagepath, dstDir, parameters = job
	
	# Uploaded iamges
	image = {'image': open(imagepath, 'rb')}

	# Call ocropy service
	resp = SESSION.get(URL_OCROPY, files=image, data=parameters, stream=True)

	# Save the responsed extracted text
	img_name = os.path.basename(imagepath)
	img_base, img_ext = os.path.splitext(img_name)
	output_fname = img_base + ".txt"
	dstpath = os.path.join(dstDir, output_fname)

	if resp.status_code == 200:
		with open(dstpath, 'wb') as fd:
			for chunk in resp:
				fd.write(chunk)
		print("[OK] '%s' OCRopy success!" % img_name)
	else:
		print("[ERROR] '%s' OCRopy error!" % img_name)
	return


def main(args):
	"""Main function.

	Call OCRopy application for each image sequencially or parallelly.
	"""
	input_ = args['input']
	output = args['output']

	# Only keep the setable parameters
	del args['input']
	del args['output']

	# Call binarization service
	if os.path.isfile(input_):
		# one image using a single process
		call_ocropy((input_, output, args))
		SESSION.close()
	elif os.path.isdir(input_):
		# multiple images using multiple processes to call binarization parallelly
		jobs = []
		for img in os.listdir(input_):
			img_path = os.path.join(input_, img)
			jobs.append((img_path, output, args))
		pool = mp.Pool() # #processes = #CPU by default
		pool.map(call_ocropy, jobs)
		# Close processes pool after it is finished
		pool.close()
		pool.join()
		SESSION.close()

if __name__ == '__main__':

	args = arg_parse()
	main(args)