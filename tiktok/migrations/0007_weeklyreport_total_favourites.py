# Generated by Django 4.2.4 on 2023-09-06 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tiktok', '0006_tiktok_favourite_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='weeklyreport',
            name='total_favourites',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
