# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-09 12:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_auto_20161209_1732'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('call_change_count', models.IntegerField(verbose_name='Add/Subtract Total Calls count')),
                ('automatic_reminder', models.BooleanField(default=True, verbose_name='Send Automatic Reminders?')),
                ('last_automatic_reminder', models.DateTimeField(verbose_name='Last automatic reminder sent on')),
                ('kick_off', models.CharField(choices=[('NS', 'Not Started'), ('IMS', 'IMS'), ('DA', 'Date Arranged'), ('CH', 'Call Happened')], default='NS', max_length=5, verbose_name='Kick Off Status')),
                ('kick_off_comment', models.TextField(verbose_name='Kick Off Comment')),
                ('mid_term', models.CharField(choices=[('NS', 'Not Started'), ('IMS', 'IMS'), ('DA', 'Date Arranged'), ('CH', 'Call Happened')], default='NS', max_length=5, verbose_name='Mid Term Status')),
                ('mid_term_comment', models.TextField(verbose_name='Mid Term Comment')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_status', to='dashboard.Team')),
            ],
        ),
    ]
