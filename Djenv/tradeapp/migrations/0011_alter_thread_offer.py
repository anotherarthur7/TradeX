# Generated by Django 5.1.6 on 2025-03-13 14:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradeapp', '0010_offer_is_open_thread_offer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thread',
            name='offer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='threads', to='tradeapp.offer'),
        ),
    ]
