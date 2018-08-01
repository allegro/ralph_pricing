# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-08-01 10:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ralph_scrooge', '0016_backofficeassetinfo_dailybackofficeassetinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalservice',
            name='business_line',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='ralph_scrooge.BusinessLine', verbose_name='business line'),
        ),
        migrations.AddField(
            model_name='service',
            name='business_line',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='services', to='ralph_scrooge.BusinessLine', verbose_name='business line'),
        ),
        migrations.RemoveField(
            model_name='profitcenter',
            name='business_line',
        ),
    ]
