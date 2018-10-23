# -*- coding: utf-8 -*-
##########################################################################################
# Developer: Luan,Jingchao        Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#     Receive OCRopus recognition service requests from user, call recognition function and
# get the output, and then return the output or error info to user.
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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from .recognition import recognition_exec
from .extrafunc import del_service_files
import sys, os, os.path, zipfile, StringIO
import logging

# Get the directory which stores the model set by user
dataDir = settings.MEDIA_ROOT

def index(request):
    return render(request, 'index.html')

@csrf_exempt
@api_view(['GET', 'POST'])
def recognitionView(request, format=None):
    logger = logging.getLogger('recognition')
    if request.data.get('image') is None:
        logger.error("Please upload only one image")
        return Response("ERROR: Please upload an image", status=status.HTTP_400_BAD_REQUEST)
	
    ### Receive parameters set by user
    parameters = request.data.dict()
    del parameters['image'] # parameter 'image' will be processed later
    keys = parameters.keys()
    for key in parameters.keys():
        if key == "height" or key == "pad":
            parameters[key] = int(parameters[key])

    ### Seperately receive and save model set by user
    modelpath = None
    if request.data.get('model') is not None: 
        model = request.data.get('model')
        modelpath = dataDir+"/"+str(model)
        default_storage.save(modelpath, model)

    ### Call OCR recognition function to recognize image in memory
    image_object = request.FILES['image']
    # output dic. key: file type (e.g., content-.txt, locaton-.llocs, and probability-.prob). value: contents in memory
    recog_dic = recognition_exec(image_object, parameters, modelpath)
    if recog_dic is None: # if output is empty
        if modelpath is not None:
            del_service_files(modelpath)
        logger.error("sth wrong with recognition")
        return Response("ERROR: sth wrong with recognition", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    ### Return the multiple files in zip type
    # Folder name in ZIP archive which contains the above files
    imagename_base, ext = os.path.splitext(str(image_object))
    zip_dir = imagename_base+"_recog"
    zip_name = "%s.zip" % zip_dir
    strio = StringIO.StringIO()      # Open StringIO to grab in-memory ZIP contents
    zf = zipfile.ZipFile(strio, "w") # The zip compressor

    for key in recog_dic:
        filename = imagename_base + '.' + key 
        zip_path = os.path.join(zip_dir, filename)
        zf.writestr(zip_path, recog_dic[key])

    zf.close()
    # Grab ZIP file from in-memory, make response with correct MIME-type
    response = HttpResponse(strio.getvalue(), content_type="application/x-zip")
    # And correct content-disposition
    response["Content-Disposition"] = 'attachment; filename=%s' % zip_name

    # Delete recognized model if it was uploaded by user
    if modelpath is not None:
            del_service_files(modelpath)

    return response