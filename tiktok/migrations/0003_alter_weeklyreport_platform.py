# Generated by Django 4.1.11 on 2023-12-11 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tiktok', '0002_weeklyreport_platform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklyreport',
            name='platform',
            field=models.TextField(blank=True, null=True),
        ),
    ]
