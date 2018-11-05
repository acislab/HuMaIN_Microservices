# -*- coding: utf-8 -*-
##########################################################################################
# Developer: Luan,Jingchao        Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#     Receive a request from client, forward it to the ocropy module, get return from ocropy
# and then return the response to client.
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
from django.http import HttpResponse
from django.conf import settings
from .extrafunc import del_service_files
from .ocropy import ocropy_exec
import os, logging

# Get the directory which stores the model set by user
dataDir = settings.MEDIA_ROOT

def index(request):
    return render(request, 'index.html')

@csrf_exempt
@api_view(['GET', 'POST'])
def ocropyView(request, format=None):
    logger = logging.getLogger('ocropy')
    if request.data.get('image') is None:
        logger.error("Please upload only one image")
        return Response("ERROR: Please upload only one image", status=status.HTTP_400_BAD_REQUEST)

    # Receive parameters
    parameters = request.data.dict() 
    del parameters['image'] # parameter 'image' will be processed seperately
    keys = parameters.keys()
    if 'seg_usegauss' in keys:
        keys.remove('seg_usegauss')
    if 'recog_model' in keys:
        keys.remove('recog_model')
    if 'recog_nonormalize' in keys:
        keys.remove('recog_nonormalize')
    for key in keys:
        parameters[key] = float(parameters[key])

    ### Seperately receive and save model set by user
    modelpath = None
    if request.data.get('recog_model') is not None: 
        model = request.data.get('recog_model')
        modelpath = dataDir+"/"+str(model)
        default_storage.save(modelpath, model)
    
    ### Call OCRopy binarization function
    image_object = request.FILES['image']
    extract_result = ocropy_exec(image_object, parameters)
    if extract_result is None:
        if modelpath is not None:
            del_service_files(modelpath)
        logger.error("sth wrong with ocropy")
        return Response("ERROR: sth wrong with OCRopy", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # Return result from memory directly
    img_base, img_ext = os.path.splitext(str(image_object))
    extract_name = img_base + ".txt"
    response = HttpResponse(extract_result, content_type="text/plain")
    response['Content-Disposition'] = 'attachment; filename=%s' % extract_name

    # Delete recognized model if it was uploaded by user
    if modelpath is not None:
            del_service_files(modelpath)

    return response