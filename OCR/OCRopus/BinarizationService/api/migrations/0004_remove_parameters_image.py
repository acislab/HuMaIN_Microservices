# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-29 16:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_parameters_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parameters',
            name='image',
        ),
    ]
