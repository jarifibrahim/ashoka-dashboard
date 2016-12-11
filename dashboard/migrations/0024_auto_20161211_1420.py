# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-11 08:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0023_auto_20161211_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weekwarning',
            name='fellow_rating_red_warning',
            field=models.PositiveIntegerField(default=7, help_text='Red warning if last rating by fellow is less than this value ', verbose_name='Fellow Phase Rating Red Warning'),
        ),
    ]
