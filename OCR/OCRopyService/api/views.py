# -*- coding: utf-8 -*-
##########################################################################################
# Developer: Luan,Jingchao        Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#     Interface to receive an image and 3 binarization thresholds parameter values set by 
# user, create 3 processes to call binarization and segmentation services in parallel, and 
# then find the common segmented single-line iamges to call recognition services.
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
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, FileResponse
from .ocr import ocr_exec
import os

def index(request):
    return render(request, 'index.html')

@csrf_exempt
@api_view(['GET', 'POST'])
def ocrView(request, format=None):
    if request.data.get('image') is None:
        return Response("ERROR: Please upload only one image", status=status.HTTP_400_BAD_REQUEST)

    ### Receive parameters set by user
    # For now, we only process 3 parameters: threshold1, threshold2, and threshold3, which are 3 binarization thresholds 
    # used to create 3 processes calling binarization services with different threshold values.
    parameters = request.data.dict() 
    del parameters['image'] # parameter 'image' will be processed seperately
    
    image_object = request.FILES['image']


    extract_result = ocr_exec(image_object, parameters)
    if extract_result is None:
        return Response("ERROR: sth wrong with OCRopus service", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # Return result from memory directly
    img_base, img_ext = os.path.splitext(str(image_object))
    extract_name = img_base + ".txt"
    response = HttpResponse(extract_result, content_type="text/plain")
    response['Content-Disposition'] = 'attachment; filename=%s' % extract_name
    
    return response