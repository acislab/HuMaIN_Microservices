#!/usr/bin/env python
##########################################################################################
# Developer: Luan,Jingchao        Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#     Extract text information from an image, based on Python Tesseract wrapper 'pyocr'.
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

from __future__ import print_function
from PIL import Image
import sys
import pyocr
import pyocr.builders


def tesseract_exec(image, parameters):
	# Using Tesseract (sh) tool by default
	tesseract_tool = pyocr.get_available_tools()[0]

	lang = 'eng' # defaul language: English
	if 'lang' in parameters:
		lang = parameters['lang']

	### Image to string
	txt = tesseract_tool.image_to_string(Image.open(image), lang=lang, builder=pyocr.builders.TextBuilder())
	return txt