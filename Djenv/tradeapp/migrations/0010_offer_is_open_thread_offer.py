# Generated by Django 5.1.6 on 2025-03-13 12:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradeapp', '0009_thread_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='is_open',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='thread',
            name='offer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tradeapp.offer'),
        ),
    ]
