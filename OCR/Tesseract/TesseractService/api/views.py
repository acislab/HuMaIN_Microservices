# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from tesseract import tesseract_exec
import os, StringIO


# Get the directory which stores all input and output files
projectDir = settings.BASE_DIR
dataDir = settings.MEDIA_ROOT

def index(request):
	return render(request, 'index.html')

@csrf_exempt
@api_view(['GET', 'POST'])
def tesseractView(request, format=None):
    if request.data.get('image') is None:
        return Response("ERROR: Please upload an image", status=status.HTTP_400_BAD_REQUEST)

    ### Receive parameters set by user
    parameters = request.data.dict()
    del parameters['image'] # parameter 'image' will be processed seperately
    
    image_object = request.FILES['image']

    ### Call tesseract function
    text = tesseract_exec(image_object, parameters)

    ### Return tesseract result from memory
    imagename_base, ext = os.path.splitext(str(image_object))
    fname = imagename_base + ".txt"
    strio = StringIO.StringIO()
    strio.write(text)
    response = HttpResponse(strio.getvalue(), content_type="application/force-download")
    response["Content-Disposition"] = 'attachment; filename=%s' % fname

    return response
