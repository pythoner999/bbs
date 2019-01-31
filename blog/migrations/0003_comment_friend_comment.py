# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-01-31 12:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20190127_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='friend_comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='friend', to='blog.Comment'),
        ),
    ]