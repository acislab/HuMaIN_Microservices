# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-29 02:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parameters',
            name='image',
        ),
    ]