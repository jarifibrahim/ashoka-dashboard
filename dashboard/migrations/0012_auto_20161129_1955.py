# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-29 14:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_auto_20161129_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='role',
            field=models.CharField(choices=[('LRP', 'LRP'), ('SA', 'Senior Advisor'), ('SC', 'Senior Consultant'), ('JC', 'Junior Consultant'), ('C', 'Consultant'), ('F', 'Fellow'), ('FC', 'Fellow Colleague')], max_length=3, verbose_name='Role'),
        ),
    ]
