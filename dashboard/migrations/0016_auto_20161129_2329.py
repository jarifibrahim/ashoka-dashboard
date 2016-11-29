# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-29 17:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0015_member_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvisoryPhases',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phase', models.CharField(max_length=200, verbose_name='Phases')),
                ('reached_in_week', models.IntegerField(verbose_name='Reached in Week')),
                ('expected_calls', models.IntegerField(verbose_name='Expected calls')),
            ],
        ),
        migrations.AlterField(
            model_name='role',
            name='long_name',
            field=models.CharField(max_length=18, verbose_name='Role'),
        ),
    ]
