# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-04 06:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0021_auto_20170404_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='reminder_emails_day',
            field=models.PositiveIntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')], default=0, verbose_name='Reminder emails on'),
        ),
    ]
