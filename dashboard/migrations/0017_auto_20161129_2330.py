# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-29 18:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0016_auto_20161129_2329'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AdvisoryPhases',
            new_name='AdvisoryPhase',
        ),
    ]
