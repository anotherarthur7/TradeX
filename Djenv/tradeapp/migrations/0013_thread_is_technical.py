# Generated by Django 5.1.6 on 2025-03-16 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradeapp', '0012_alter_offer_posted_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='is_technical',
            field=models.BooleanField(default=False),
        ),
    ]
