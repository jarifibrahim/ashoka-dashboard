# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-11 15:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0028_auto_20161211_1856'),
    ]

    operations = [
        migrations.AddField(
            model_name='advisoryphase',
            name='short',
            field=models.CharField(default='A', help_text='Short name should be less than 10 characters.', max_length=10, verbose_name='Short name'),
            preserve_default=False,
        ),
    ]
