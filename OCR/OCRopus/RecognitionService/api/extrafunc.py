# -*- coding: utf-8 -*-
import os, os.path, shutil

'''
This module rpovides extra functions
'''

### Check the validation of the uploaded images
def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


# Delete all files related to this service time, including inputs and outputs
def del_service_files(path):
    try:
        if os.path.isfile(path):
            os.unlink(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        else:
            print("Error: Path %s was not found" % (path))
            sys.exit()
    except Exception as e:
        print(e)