# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-11 11:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0025_auto_20161211_1621'),
    ]

    operations = [
        migrations.RenameField(
            model_name='email',
            old_name='default',
            new_name='default_template',
        ),
    ]
