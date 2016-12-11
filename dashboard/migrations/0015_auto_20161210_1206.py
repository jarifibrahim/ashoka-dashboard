# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-10 06:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_auto_20161210_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weekwarning',
            name='calls_red_warning',
            field=models.PositiveIntegerField(help_text='Number of calls less than this value leads to Red warning (Should be greater than yellow warning call count) ', verbose_name='Call count - Red warning'),
        ),
        migrations.AlterField(
            model_name='weekwarning',
            name='calls_yellow_warning',
            field=models.PositiveIntegerField(help_text='Number of calls less than this value leads to Yellow warning.', verbose_name='Call count - Yellow warning'),
        ),
        migrations.AlterField(
            model_name='weekwarning',
            name='kick_off_red_warning',
            field=models.BooleanField(help_text='Kick-off not happened in this week leads to Red warning.', verbose_name='Kick Off - Red warning'),
        ),
        migrations.AlterField(
            model_name='weekwarning',
            name='kick_off_yellow_warning',
            field=models.BooleanField(help_text='Kick-off not happened in this week leads to Yellow warning.', verbose_name='Kick Off - Yellow warning'),
        ),
        migrations.AlterField(
            model_name='weekwarning',
            name='member_call_red_warning',
            field=models.PositiveIntegerField(help_text='Person missing calls: > leads to Red warning (Should be greater than yellow warning member call count) ', verbose_name='Member call count - Red warning'),
        ),
        migrations.AlterField(
            model_name='weekwarning',
            name='member_call_yellow_warning',
            field=models.PositiveIntegerField(help_text='Person missing calls: > leads to Yellow warning', verbose_name='Member call count - Yellow warning'),
        ),
        migrations.AlterField(
            model_name='weekwarning',
            name='mid_term_red_warning',
            field=models.BooleanField(help_text='Mid-term not happened in this week leads to Red warning', verbose_name='Mid Term - Red warning'),
        ),
        migrations.AlterField(
            model_name='weekwarning',
            name='mid_term_yellow_warning',
            field=models.BooleanField(help_text='Mid-term not happened in this week leads to Yellow warning', verbose_name='Mid Term - Yellow warning'),
        ),
        migrations.AlterField(
            model_name='weekwarning',
            name='phase_red_warning',
            field=models.ForeignKey(help_text='Red warning if in less than this Phase', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='red_warning_phase', to='dashboard.AdvisoryPhase'),
        ),
        migrations.AlterField(
            model_name='weekwarning',
            name='phase_yellow_warning',
            field=models.ForeignKey(help_text='Yellow warning if in this Phase', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='yellow_warning_phase', to='dashboard.AdvisoryPhase'),
        ),
    ]