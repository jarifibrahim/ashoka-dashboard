# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-05 13:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_auto_20161213_2314'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='teamstatus',
            options={'verbose_name': 'Team status', 'verbose_name_plural': 'Team status'},
        ),
        migrations.AddField(
            model_name='dashboard',
            name='overall_r',
            field=models.PositiveIntegerField(default=0, help_text='Total Number of Red warnings greater than this value will mark the Team as Red.', verbose_name='Overall - Red'),
        ),
        migrations.AddField(
            model_name='dashboard',
            name='overall_y',
            field=models.PositiveIntegerField(default=0, help_text='Total Number of Yellow warnings greater than this value will mark the Team as Yellow.', verbose_name='Overall - Yellow'),
        ),
        migrations.AlterField(
            model_name='dashboard',
            name='reminder_emails_after',
            field=models.PositiveIntegerField(default=9, verbose_name='Reminder emails should be sent after how many days from last response submit'),
        ),
    ]
