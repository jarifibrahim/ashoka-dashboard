# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-24 15:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0019_auto_20170124_2105'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teamstatus',
            old_name='systemic_vision',
            new_name='sys_vision',
        ),
        migrations.RenameField(
            model_name='teamstatus',
            old_name='systemic_vision_comment',
            new_name='sys_vision_comment',
        ),
    ]