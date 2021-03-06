# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-12 05:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20161212_1114'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='status',
        ),
        migrations.AddField(
            model_name='team',
            name='status_choices',
            field=models.CharField(choices=[('AUTO', 'Automatic'), ('RED', 'Major issues!!!'), ('YELLOW', 'Some minor issues!'), ('GREEN', 'All good!')], default='AUTO', max_length=7, verbose_name='Team status choices'),
        ),
        migrations.AddField(
            model_name='team',
            name='status_color',
            field=models.CharField(choices=[('G', 'Green'), ('Y', 'Yellow'), ('R', 'Red')], default='G', max_length=3, verbose_name='Team status color'),
        ),
    ]
