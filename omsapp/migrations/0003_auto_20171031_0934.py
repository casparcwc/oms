# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-10-31 09:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omsapp', '0002_userlog'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='omsuser',
            options={'permissions': (('read_monitor', 'Can read zabbix'), ('change_monitor', 'Can change monitor'), ('opjenkins', 'Can operation jenkins'), ('opredis', 'Can operation redis'))},
        ),
    ]