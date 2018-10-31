# -*- coding: utf-8 -*-
##########################################################################################
# Developer: Luan,Jingchao        Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#     Receive OCRopus segmentation service requests from user, call segmentation function
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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.shortcuts import render
from .segmentation import segmentation_exec
import sys, os, os.path, zipfile, StringIO
import logging

reload(sys)
sys.setdefaultencoding('utf8')

def index(request):
    return render(request, 'index.html')

@csrf_exempt
@api_view(['GET', 'POST'])
def segmentationView(request, format=None):
    logger = logging.getLogger('segmentation')
    if request.data.get('image') is None:
        logger.error("Please upload only one image")
        return Response("ERROR: Please upload an image", status=status.HTTP_400_BAD_REQUEST)

    ### Receive parameters set by user
    parameters = request.data.dict()
    del parameters['image'] # parameter 'image' will be processed later
    keys = parameters.keys()
    if 'usegauss' in keys:
        keys.remove('usegauss')
    for key in keys:
        parameters[key] = float(parameters[key])
    
    image_object = request.FILES['image']
    ### Call segmentation function
    seg_result = segmentation_exec(image_object, parameters)
    if not seg_result: # if output_list is empty
        logger.error("sth wrong with segmentation")
        return Response("ERROR: sth wrong with segmentation", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    ### Else return the segmented images in zip type
    # Folder name in ZIP archive which contains the above files
    imagename_base, ext = os.path.splitext(str(image_object))
    zip_dir = imagename_base+"_seg"
    zip_name = "%s.zip" % zip_dir
    strio = StringIO.StringIO()      # Open StringIO to grab in-memory ZIP contents
    zf = zipfile.ZipFile(strio, "w") # The zip compressor

    # Zip multiple image objects from memory
    for key in seg_result:
        # Save single-line image object in memory as png format
        line_image_io = StringIO.StringIO()
        seg_result[key].save(line_image_io, 'png')
        zip_path = os.path.join(zip_dir, key)
        zf.writestr(zip_path, line_image_io.getvalue())
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    response = HttpResponse(strio.getvalue(), content_type="application/x-zip")
    # And correct content-disposition
    response["Content-Disposition"] = 'attachment; filename=%s' % zip_name
    
    return response