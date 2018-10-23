# -*- coding: utf-8 -*-
#!/usr/bin/env python
##########################################################################################
# Developer: Luan,Jingchao        Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#     This module rpovides extra functions like intermedia data
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
import os, os.path, shutil

### Check the validation of the uploaded images
def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


### Delete all files related to this service time, including inputs and outputs
def del_service_files(dataDir):
    for the_file in os.listdir(dataDir):
        file_path = os.path.join(dataDir, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)