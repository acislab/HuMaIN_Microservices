# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-24 02:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20170723_2228'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parameters',
            name='model',
        ),
    ]