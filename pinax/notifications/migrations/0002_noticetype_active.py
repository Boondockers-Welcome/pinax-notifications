# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-30 17:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pinax_notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='noticetype',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]