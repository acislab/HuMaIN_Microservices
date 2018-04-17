# -*- coding: utf-8 -*-
##########################################################################################
# Developer: Luan,Jingchao        Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#     Receive OCRopus binarization service requests from user, call binarization function 
# and get the output, and then return the output or error info to user.
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

from __future__ import unicode_literals
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from wsgiref.util import FileWrapper
from .binarization import binarization_exec
from .extrafunc import resize_image, del_service_files
import sys, os, os.path
import logging

# Set encoding
reload(sys)
sys.setdefaultencoding('utf8')

# Get the directory which stores all input and output files
projectDir = settings.BASE_DIR
dataDir = settings.MEDIA_ROOT

def index(request):
    return render(request, 'index.html')

### New version: process image in-memory => response output image from memory
@csrf_exempt
@api_view(['GET', 'POST'])
def binarizationView(request, format=None):
    logger = logging.getLogger('binarization')
    if request.data.get('image') is None:
        logger.error("Please upload only one image")
        return Response("ERROR: Please upload only one image", status=status.HTTP_400_BAD_REQUEST)

    ### Receive parameters set by user
    parameters = request.data.dict()
    del parameters['image'] # parameter 'image' will be processed later
    for key in parameters:
        parameters[key] = float(parameters[key])
    
    ### Receive and resize the image if its size smaller than 600*600
    image_object = request.FILES['image']
    try:
        image_object = resize_image(image_object)
    except:
        return Response("ERROR: Re-size image error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    ### Call OCR binarization function
    output_file = binarization_exec(image_object, parameters)
    if output_file is None:
        logger.error("sth wrong with binarization")
        return Response("ERROR: sth wrong with binarization", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    ### Return image object (in memory)
    response = HttpResponse(content_type="image/png")
    output_file.save(response, "PNG")
    
    return response