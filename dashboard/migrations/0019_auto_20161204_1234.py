# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-04 07:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0018_auto_20161204_0054'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FellowSurvey',
            new_name='ConsultantSurvey',
        ),
    ]
