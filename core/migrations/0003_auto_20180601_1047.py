# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-06-01 10:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_poll_auth_app'),
    ]

    operations = [
        migrations.AlterField(
            model_name='polloption',
            name='open_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
