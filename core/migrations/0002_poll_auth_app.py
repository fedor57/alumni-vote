# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-05-22 21:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='auth_app',
            field=models.CharField(default='', max_length=30),
        ),
    ]
