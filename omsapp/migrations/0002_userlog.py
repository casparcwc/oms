# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-08 14:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('omsapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='userLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20, verbose_name='username')),
                ('log_msg', models.TextField()),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
            ],
        ),
    ]
