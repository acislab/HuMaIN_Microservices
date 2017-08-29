# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-29 02:32
from __future__ import unicode_literals

import api.extrafunc
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_remove_parameters_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameters',
            name='image',
            field=models.ImageField(help_text='the uploaded image need to be binarized', null=True, upload_to='', validators=[api.extrafunc.validate_image_extension]),
        ),
    ]
